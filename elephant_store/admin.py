from django.contrib import admin
from .models import User, Product

class UserAdmin(admin.ModelAdmin):
    exclude = ["last_recovery_code"]
    readonly_fields = ["first_name", "last_name", "patronism"]


admin.site.register(User, UserAdmin)
admin.site.register(Product)