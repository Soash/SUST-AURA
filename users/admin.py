from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, PrimarySetting


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name')
    search_fields = ('name', 'full_name')


@admin.register(PrimarySetting)
class PrimarySettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'auto_approve')
    list_editable = ('auto_approve',)
    list_display_links = ('id',)
