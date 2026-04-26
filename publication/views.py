from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Publication
from .forms import PublicationForm


@login_required
def publication_list(request):
    query    = request.GET.get('q', '').strip()
    pub_type = request.GET.get('type', '').strip()
    year     = request.GET.get('year', '').strip()

    pubs = Publication.objects.filter(is_public=True).prefetch_related('authors')

    if query:
        pubs = pubs.filter(
            Q(title__icontains=query)       |
            Q(abstract__icontains=query)    |
            Q(journal_name__icontains=query)|
            Q(external_authors__icontains=query)
        )
    if pub_type:
        pubs = pubs.filter(pub_type=pub_type)
    if year:
        pubs = pubs.filter(year=year)

    paginator = Paginator(pubs, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))

    years      = Publication.objects.filter(is_public=True).values_list('year', flat=True).distinct().order_by('-year')
    type_choices = Publication.TYPE_CHOICES

    return render(request, 'publication/publication_list.html', {
        'page_obj':     page_obj,
        'query':        query,
        'active_type':  pub_type,
        'active_year':  year,
        'years':        years,
        'type_choices': type_choices,
    })


@login_required
def publication_detail(request, pk):
    pub = get_object_or_404(Publication, pk=pk, is_public=True)
    return render(request, 'publication/publication_detail.html', {'pub': pub})


@login_required
def publication_create(request):
    if request.method == 'POST':
        form = PublicationForm(request.POST)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.uploaded_by = request.user
            pub.save()
            form.save_m2m()
            # Auto-add the uploader as an author
            pub.authors.add(request.user)
            messages.success(request, 'Publication added successfully.')
            return redirect('publication_detail', pk=pub.pk)
    else:
        form = PublicationForm()
    return render(request, 'publication/publication_form.html', {'form': form, 'action': 'Add'})


@login_required
def publication_edit(request, pk):
    pub = get_object_or_404(Publication, pk=pk)
    if pub.uploaded_by != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this publication.')
        return redirect('publication_detail', pk=pk)
    if request.method == 'POST':
        form = PublicationForm(request.POST, instance=pub)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publication updated.')
            return redirect('publication_detail', pk=pk)
    else:
        form = PublicationForm(instance=pub)
    return render(request, 'publication/publication_form.html', {'form': form, 'action': 'Edit', 'pub': pub})


@login_required
def publication_delete(request, pk):
    pub = get_object_or_404(Publication, pk=pk)
    if pub.uploaded_by != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this publication.')
        return redirect('publication_detail', pk=pk)
    if request.method == 'POST':
        pub.delete()
        messages.success(request, 'Publication deleted.')
        return redirect('publication_list')
    return render(request, 'publication/publication_confirm_delete.html', {'pub': pub})
