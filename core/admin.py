from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import User


@admin.register(User)
class CoreUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Rôle", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rôle", {"fields": ("role",)}),
    )
    list_display = UserAdmin.list_display + ("role",)
