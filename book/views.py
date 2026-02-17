from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Book

def book_list(request):
    query = request.GET.get('q')
    books = Book.objects.all().order_by('title')

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(writer__icontains=query)
        )

    paginator = Paginator(books, 5)  # Show 5 books per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'book/book_list.html', {
        'books': page_obj,
        'page_obj': page_obj,
        'query': query,
    })
