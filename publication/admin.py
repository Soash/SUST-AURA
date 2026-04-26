from django.contrib import admin
from .models import Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display  = ('title', 'pub_type', 'year', 'journal_name', 'uploaded_by', 'is_public', 'uploaded_at')
    list_filter   = ('pub_type', 'year', 'is_public')
    search_fields = ('title', 'abstract', 'journal_name', 'external_authors')
    filter_horizontal = ('authors',)
    list_editable = ('is_public',)
    readonly_fields = ('uploaded_at',)
