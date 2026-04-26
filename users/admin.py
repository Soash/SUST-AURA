from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, School, PrimarySetting


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'department', 'school', 'email_verified', 'is_staff']
    list_filter = UserAdmin.list_filter + ('department', 'school', 'email_verified', 'gender', 'blood')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Academic Info', {
            'fields': ('registration_number', 'department', 'school', 'session', 'student_proof')
        }),
        ('Personal Info', {
            'fields': ('gender', 'blood', 'hometown', 'whatsapp_number', 'social_profile')
        }),
        ('Status', {
            'fields': ('email_verified',)
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', 'school')
    search_fields = ('name', 'full_name')
    list_filter = ('school',)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(PrimarySetting)
class PrimarySettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'auto_approve')
    list_editable = ('auto_approve',)
    list_display_links = ('id',)
