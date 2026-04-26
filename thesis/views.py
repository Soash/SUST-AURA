from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse
from django.db.models import Count

from .models import ResearchWork, ThesisAccessLog
from .forms import ResearchWorkForm

# @login_required
@login_required
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

    # Annotate each work with its unique viewer count from ThesisAccessLog
    works_list = works_list.annotate(unique_viewers=Count('access_logs__user', distinct=True))

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
@login_required
def thesis_detail(request, pk):
    work = get_object_or_404(ResearchWork, pk=pk)

    # Log this user's visit — get_or_create ensures one record per unique user
    ThesisAccessLog.objects.get_or_create(user=request.user, thesis=work)

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
            return redirect('thesis_detail', pk=work.pk)
    else:
        form = ResearchWorkForm()

    return render(request, 'thesis/researchwork_form.html', {'form': form, 'action': 'Add'})


@login_required
def thesis_edit(request, pk):
    work = get_object_or_404(ResearchWork, pk=pk)

    # Only authors (or staff) may edit
    if request.user not in work.authors.all() and not request.user.is_staff:
        messages.error(request, "You do not have permission to edit this work.")
        return redirect('thesis_detail', pk=pk)

    if request.method == 'POST':
        form = ResearchWorkForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
            messages.success(request, "Research work updated successfully!")
            return redirect('thesis_detail', pk=work.pk)
    else:
        form = ResearchWorkForm(instance=work)

    return render(request, 'thesis/researchwork_form.html', {
        'form': form,
        'action': 'Edit',
        'work': work,
    })

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


# ─── Embargo & Access Tracking ────────────────────────────────────────────────

@login_required
def request_thesis_access(request, pk):
    """
    POST-only view. Sends an email to the first author with:
      - Requester's full details (name, dept, session, reg. no., profile link)
      - Reply-To set to the requester's email so the author can reply directly.
    """
    if request.method != 'POST':
        return redirect('thesis_detail', pk=pk)

    work      = get_object_or_404(ResearchWork, pk=pk)
    requester = request.user

    # Determine the recipient — first author in the M2M set
    author = work.authors.first()
    if not author or not author.email:
        messages.error(request, "Could not find a contact address for this work's author.")
        return redirect('thesis_detail', pk=pk)

    # Build the requester's profile URL
    profile_url = request.build_absolute_uri(
        reverse('profile_view', kwargs={'username': requester.username})
    )

    dept    = getattr(requester.department, 'name', 'N/A') if requester.department else 'N/A'
    school  = getattr(requester.school, 'name', 'N/A') if requester.school else 'N/A'

    body = f"""Dear {author.first_name or author.username},

A member of SUST AURA has requested access to the full text of your embargoed research work.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Research Work: {work.title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Requester Details:
  • Name:                {requester.get_full_name() or requester.username}
  • Email:               {requester.email}
  • Department:          {dept}
  • School:              {school}
  • Session:             {requester.session or 'N/A'}
  • Registration No.:    {requester.registration_number or 'N/A'}
  • Profile:             {profile_url}

You can reply directly to this email to send them the document, or ignore this message if you prefer not to share it at this time.

— SUST AURA Platform
"""

    email = EmailMessage(
        subject=f"[SUST AURA] Full-Text Access Request: {work.title[:60]}",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[author.email],
        reply_to=[requester.email],   # ← Author's reply goes directly to the requester
    )
    try:
        email.send()
        messages.success(
            request,
            f"Your request has been sent to the author. "
            f"They may reply to your email ({requester.email}) directly."
        )
    except Exception as e:
        messages.error(request, f"Failed to send access request: {e}")

    return redirect('thesis_detail', pk=pk)


@login_required
def track_and_redirect_thesis(request, pk):
    """
    Enforces the embargo gate, then logs the access and redirects to the
    external document link (e.g., Google Drive).
    """
    work = get_object_or_404(ResearchWork, pk=pk)

    # Security: reject if the document is still under embargo
    if work.is_currently_embargoed:
        messages.error(
            request,
            f"This document is under embargo until {work.embargo_until.strftime('%B %d, %Y')}. "
            "Use the 'Request Full Text' button to contact the author."
        )
        return redirect('thesis_detail', pk=pk)

    if not work.link:
        messages.warning(request, "No external document link has been set for this work.")
        return redirect('thesis_detail', pk=pk)

    # Log the access
    ThesisAccessLog.objects.create(user=request.user, thesis=work)

    # Redirect to the external document
    return redirect(work.link)
