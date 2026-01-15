from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden
from .forms import SignUpForm, LogInForm, EmailForm, RestorePasswordForm, UpdateUserForm
from .models import User, Product, Comment
from datetime import date, datetime

def index(request : HttpRequest):
    if ("python-requests" in request.META["HTTP_USER_AGENT"]): # add more sus agents
        return redirect('/', True) # trap parser scripts in endless loop of torment
    login = request.get_signed_cookie("login", "", date.today().ctime())
    if login == "":
        return redirect('login/')
    try:
        #ip = request.META["REMOTE_ADDR"]
        #user_agent = request.META["HTTP_USER_AGENT"]
        #host = request.get_host()
        user = User.objects.get(email = login)
        products = Product.objects.filter(access_req__lte = user.access_level)
        return render(request, "index.html", context={"user":user, "products":products})
    except:
        res = redirect('/login/')
        res.delete_cookie("login")
        return res

def sign_up(request : HttpRequest):
    if request.method == "GET":
        form = SignUpForm()
        return render(request, "sign_up.html", context={"form": form})
    elif request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            resp = redirect('/')
            resp.set_signed_cookie("login", form.cleaned_data["email"], date.today().ctime())
            u = User.objects.create(
                first_name = form.cleaned_data["first_name"],
                last_name = form.cleaned_data["last_name"],
                patronism = form.cleaned_data["patronism"],
                email = form.cleaned_data["email"],
                password = form.cleaned_data["password"]
            )
            return resp
        else:
            return render(request, "sign_up.html", context={"form": form})
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

def log_in(request : HttpRequest):
    if request.method == "GET":
        form = LogInForm()
        return render(request, "log_in.html", context={"form": form})
    elif request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            resp = redirect('/')
            resp.set_signed_cookie("login", form.cleaned_data["email"], date.today().ctime())
            return resp
        else:
            return render(request, "log_in.html", context={"form": form})
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

def restore_password(request : HttpRequest):
    if request.method == "GET":
        form = EmailForm()
        return render(request, "restorepassword.html", context={"form": form})
    elif request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            u = User.objects.get(email=form.cleaned_data["email"])
            code = "111111" # TODO: actually make codes
            u.last_recovery_code = code
            u.save(force_update=True)
            h = hex(hash(u.email)+hash(code)+hash(date.today().ctime()))[2:]
            resp = redirect("/restore/"+h)
            resp.set_signed_cookie("re", u.email, date.today().ctime(), max_age=30)
            return resp
        else:
            return render(request, "restorepassword.html", context={"form": form})
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

def restore_password2(request : HttpRequest, hsh : str):
    if request.method == "GET":
        email = request.get_signed_cookie("re", "", date.today().ctime())
        resp = HttpResponse()
        try:
            u = User.objects.get(email=email)
            if hsh != hex(hash(u.email)+hash(u.last_recovery_code)+hash(date.today().ctime()))[2:]:
                raise ValueError()
            form = RestorePasswordForm(initial={"email":u.email})
            resp = render(request, "restorepassword2.html", context={"form": form, "email": u.email})
        except Exception as e:
            print(e)
            resp = redirect("/restorepassword/")
        resp.delete_cookie("re")
        return resp
    elif request.method == "POST":
        form = RestorePasswordForm(request.POST)
        if form.is_valid():
            u = User.objects.get(email=form.cleaned_data["email"])
            u.last_recovery_code = None
            u.password = form.cleaned_data["password"]
            u.save(force_update=True)
            return redirect("/login/")
        else:
            resp = render(request, "restorepassword2.html", context={"form": form, "email": form.cleaned_data["email"]})
            resp.set_signed_cookie("re", form.cleaned_data["email"], date.today().ctime(), max_age=30)
            return resp
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

def product(request : HttpRequest, prod_id : int):
    login = request.get_signed_cookie("login", "", date.today().ctime())
    if login == "":
        return redirect("/login/")
    try:
        prod = Product.objects.get(id=prod_id)
        u = User.objects.get(email=login)
        if u.access_level < prod.access_req:
            return HttpResponseForbidden()
        if request.method == "GET":
            return render(request, "product.html", context={"product":prod, "user":u, "comments":prod.comments.all()})
        elif request.method == "POST":
            Comment.objects.create(user=u, product=prod, datetime=datetime.now(), text=request.POST.get("text"))
            return redirect(request.path)
        else:
            return HttpResponseNotAllowed(["GET", "POST"])
    except Product.DoesNotExist:
        return render(request, "not_found.html", status=404)
    except User.DoesNotExist:
        return HttpResponseBadRequest()

def profile(request : HttpRequest, hsh : str):
    try:
        login = request.get_signed_cookie("login", "", date.today().ctime())
        user = User.objects.get(email=login)
        if hsh != user.get_hash():
            raise ValueError()
        if request.method == "GET":
            return render(request, "profile.html", context={"user":user})
        elif request.method == "POST":
            match (request.POST.get("action")):
                case "update":
                    form = UpdateUserForm(
                        {
                            "first_name" : user.first_name,
                            "last_name" : user.last_name,
                            "patronism" : user.patronism
                        }
                    )
                    return render(request, "update_user.html", context={"user":user,"form":form})
                case "logout":
                    resp = redirect("/")
                    resp.delete_cookie("login")
                    return resp
                case "delete":
                    resp = redirect("/")
                    resp.delete_cookie("login")
                    user.is_active = False
                    user.save(force_update=True)
                    return resp
        else:
            return HttpResponseNotAllowed(["GET", "POST"])
    except (User.DoesNotExist, ValueError):
        return redirect("/")

def update_profile(request : HttpRequest, hsh : str):
    try:
        login = request.get_signed_cookie("login", "", date.today().ctime())
        user = User.objects.get(email=login)
        if hsh != user.get_hash():
            raise ValueError()
        if request.method == "POST":
            form = UpdateUserForm(request.POST)
            if form.is_valid():
                user.first_name = form.cleaned_data["first_name"]
                user.last_name = form.cleaned_data["last_name"]
                user.patronism = form.cleaned_data["patronism"]
                user.save(force_update=True)
                return redirect("/")
            else:
                return render(request, "update_user.html", context={"form":form})
        else:
            return HttpResponseNotAllowed(["POST"])
    except (User.DoesNotExist, ValueError):
        return redirect("/")