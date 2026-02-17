from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import ResearchWork
from .forms import ResearchWorkForm

# @login_required
def thesis_list(request):
    works_list = ResearchWork.objects.filter(is_public=True)

    # Filtering
    query = request.GET.get('q')
    work_types = request.GET.getlist('work_type')
    department_ids = request.GET.getlist('department')
    supervisor = request.GET.get('supervisor')
    sessions = request.GET.getlist('session')

    if query:
        works_list = works_list.filter(title__icontains=query)
    
    if work_types:
        works_list = works_list.filter(work_type__in=work_types)
    
    if department_ids:
        works_list = works_list.filter(authors__department__id__in=department_ids)

    if supervisor:
        works_list = works_list.filter(supervisor_name__icontains=supervisor)

    if sessions:
        works_list = works_list.filter(authors__session__in=sessions)

    works_list = works_list.order_by('-uploaded_at').distinct()

    paginator = Paginator(works_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get departments for filter dropdown
    from users.models import Department, CustomUser
    departments = Department.objects.all()

    # Custom Pagination Range (Display 5 pages)
    page_range = paginator.page_range
    start_index = max(1, page_obj.number - 2)
    end_index = min(start_index + 4, paginator.num_pages)
    
    # Adjust start if we are near the end to ensure 5 pages are shown if possible
    if end_index - start_index < 4:
        start_index = max(1, end_index - 4)
        
    custom_page_range = range(start_index, end_index + 1)

    context = {
        'works': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
        'departments': departments,
        'work_types': ResearchWork.WORK_TYPES,
        'sessions': CustomUser.SESSION_CHOICES,
        'filter_params': request.GET.urlencode(),
        'selected_work_types': work_types,
        'selected_departments': [int(id) for id in department_ids if id.isdigit()],
        'selected_sessions': sessions,
        'custom_page_range': custom_page_range,
    }
    return render(request, 'thesis/researchwork_list.html', context)

# @login_required
def thesis_detail(request, pk):
    work = get_object_or_404(ResearchWork, pk=pk)
    context = {'work': work}
    return render(request, 'thesis/researchwork_detail.html', context)

@login_required
def thesis_create(request):
    if request.method == 'POST':
        form = ResearchWorkForm(request.POST)
        if form.is_valid():
            work = form.save()
            # Ensure the creator is added as an author
            if request.user not in work.authors.all():
                work.authors.add(request.user)
            messages.success(request, "Research work added successfully!")
            return redirect('thesis_list')
    else:
        form = ResearchWorkForm()
    
    return render(request, 'thesis/researchwork_form.html', {'form': form})

@login_required
def thesis_delete(request, pk):
    work = get_object_or_404(ResearchWork, pk=pk)
    
    # Check if user is an author
    if request.user not in work.authors.all():
        messages.error(request, "You do not have permission to delete this work.")
        return redirect('thesis_list')

    if request.method == 'POST':
        title = work.title
        work.delete()
        messages.success(request, f"Research work '{title}' deleted successfully.")
        return redirect('profile_view', username=request.user.username)
    
    # Using 'object' context variable to match existing template
    return render(request, 'thesis/researchwork_confirm_delete.html', {'object': work})

from .models import Report
from .forms import ReportForm

@login_required
def report_thesis(request, pk):
    work = get_object_or_404(ResearchWork, pk=pk)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.work = work
            report.reporter = request.user
            report.save()
            messages.success(request, "Thank you. Your report has been submitted for review.")
            return redirect('thesis_list')
    else:
        form = ReportForm()
    
    return render(request, 'thesis/report_form.html', {'form': form, 'work': work})



