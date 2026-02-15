from django.contrib import admin
from .models import ResearchWork, Report

@admin.register(ResearchWork)
class ResearchWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'work_type', 'supervisor_name', 'uploaded_at', 'is_public')
    list_filter = ('work_type', 'is_public', 'uploaded_at')
    search_fields = ('title', 'abstract', 'supervisor_name')
    date_hierarchy = 'uploaded_at'
    list_per_page = 20

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('work', 'reporter', 'reason', 'timestamp', 'is_resolved')
    list_filter = ('is_resolved', 'timestamp')
    search_fields = ('work__title', 'reporter__username', 'reason')
    date_hierarchy = 'timestamp'
    list_per_page = 20
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_as_resolved.short_description = "Mark selected reports as resolved"
