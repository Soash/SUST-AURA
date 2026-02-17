from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'edition_number', 'link')
    search_fields = ('title', 'writer')
    list_filter = ('edition_number',)
