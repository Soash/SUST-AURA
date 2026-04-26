from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Book, BookTag


@login_required
def book_list(request):
    query = request.GET.get('q', '').strip()
    active_tag = request.GET.get('tag', '').strip()

    books = Book.objects.prefetch_related('tags').order_by('title')

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(writer__icontains=query)
        )

    if active_tag:
        books = books.filter(tags__slug=active_tag)

    all_tags = BookTag.objects.all()

    paginator = Paginator(books, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'book/book_list.html', {
        'page_obj': page_obj,
        'query': query,
        'all_tags': all_tags,
        'active_tag': active_tag,
    })
