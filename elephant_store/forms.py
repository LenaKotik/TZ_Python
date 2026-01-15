from django import forms
from django.core.exceptions import ValidationError
from .models import User

class UpdateUserForm(forms.Form):
    first_name = forms.CharField(label="Имя", max_length=100)
    last_name = forms.CharField(label="Фамилия", max_length=100)
    patronism = forms.CharField(label="Отчество*", max_length=100, required=False)

class SignUpForm(UpdateUserForm):
    email = forms.EmailField(label="Почта", max_length=100)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput, max_length=100, min_length=8)
    rep_password = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput, max_length=100, min_length=8)

    def clean(self):
        data = super().clean()
        p1 = data.get("password")
        p2 = data.get("rep_password")
        email = data.get("email")
        if p1 != p2:
            self.add_error("rep_password", "Пароли должны совпадать!")
        if User.objects.filter(email=email).exists(): # idk if this is optimal
            self.add_error("email", "Пользователь с этой почтой уже сущестует")
        return data

class EmailForm(forms.Form):
    email = forms.EmailField(label="Почта", max_length=100)
    def clean(self):
        data = super().clean()
        email = data.get("email")
        if not User.objects.filter(email=email).exists():
            self.add_error("email", "Пользователя с этой почтой не существует!")
        
        return data

class LogInForm(EmailForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput, max_length=100, min_length=8)
    def clean(self):
        data = super().clean()
        pas = data.get("password")
        email = data.get("email")
        try:
            u = User.objects.get(email=email)
            if u.password != pas:
                self.add_error("password", "Неправильный пароль")
            if not u.is_active:
                self.add_error("email", "Пользователь с этой почтой удалён, свяжитесь с поддержкой чтобы вернуть доступ")
        except User.DoesNotExist:
            pass # error already reported by super
        return data

class RestorePasswordForm(forms.Form):
    email = forms.EmailField(label="Почта", max_length=100, widget=forms.HiddenInput)
    code = forms.SlugField(help_text="Введите код из письма")
    password = forms.CharField(help_text="Введите новый пароль", widget=forms.PasswordInput, max_length=100, min_length=8)
    rep_password = forms.CharField(help_text="Повторите новый пароль", widget=forms.PasswordInput, max_length=100, min_length=8)
    def clean(self):
        data = super().clean()
        p1 = data.get("password")
        p2 = data.get("rep_password")
        email = data.get("email")
        code = data.get("code")
        if p1 != p2:
            self.add_error("rep_password", "Пароли должны совпадать!")
        try:
            u = User.objects.get(email=email)
            if u.last_recovery_code != code:
                self.add_error("code", "Неправильный код, проверьте почту")
        except:
            raise ValidationError("Неправильная почта, перезагрузите страницу и попробуйте ещё раз")
        return data
