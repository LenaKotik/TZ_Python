from django.db import models
from datetime import date
# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronism = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    access_level = models.SmallIntegerField(default=0, choices={0:"Стандартный", 1:"VIP", 2:"Продавец"})
    last_recovery_code = models.SlugField(max_length=6, null=True)
    def get_hash(self):
        return hex(hash(self)+hash(self.first_name)+hash(self.last_name)+hash(str(self)))[2:]
    def get_full_name(self):
        return self.first_name+' '+(self.patronism if self.patronism else self.last_name)
    def __str__(self):
        return self.get_full_name()

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    birthday = models.DateField()
    access_req = models.SmallIntegerField(default=0, choices={0:"Стандартный", 1:"VIP", 2:"Продавец"})
    color = models.CharField(max_length=30)
    pic = models.ImageField(null=True, upload_to="images/products")
    def get_age(self):
        return date.today().year - self.birthday.year # adasda

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # we won't be deleting users anyway
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=1024)
    datetime = models.DateTimeField()