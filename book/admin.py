from django.contrib import admin
from .models import Book, BookTag


@admin.register(BookTag)
class BookTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'book_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = 'Books'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'edition_number', 'tag_list')
    search_fields = ('title', 'writer')
    list_filter = ('edition_number', 'tags')
    filter_horizontal = ('tags',)

    def tag_list(self, obj):
        return ', '.join(t.name for t in obj.tags.all())
    tag_list.short_description = 'Tags'
