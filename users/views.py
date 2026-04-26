from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import random
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from .models import CustomUser, ProfileVisit, PrimarySetting, PendingRegistration
from .forms import CustomUserCreationForm, CustomUserProfileForm
from .forms import UserLoginForm

def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Login successful!")
            return redirect("home")
        else:
            messages.warning(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, "users/signin.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("user_login")

def user_registration(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            to_email = form.cleaned_data.get("username")

            # Remove any stale pending registration for this email
            PendingRegistration.objects.filter(username=to_email).delete()

            # Store form data temporarily — no real user created yet
            pending = PendingRegistration(
                first_name=form.cleaned_data['first_name'],
                username=to_email,
                hashed_password=make_password(form.cleaned_data['password1']),
                registration_number=form.cleaned_data.get('registration_number') or '',
                department=form.cleaned_data.get('department'),
                session=form.cleaned_data.get('session') or '',
                gender=form.cleaned_data.get('gender') or '',
                blood=form.cleaned_data.get('blood') or '',
                hometown=form.cleaned_data.get('hometown') or '',
                whatsapp_number=form.cleaned_data.get('whatsapp_number') or '',
                social_profile=form.cleaned_data.get('social_profile') or '',
            )
            if form.cleaned_data.get('student_proof'):
                pending.student_proof = form.cleaned_data['student_proof']
            pending.save()

            # Send activation email with a link containing the single random token
            current_site = get_current_site(request)
            activation_url = request.build_absolute_uri(
                reverse('activate', kwargs={'token': pending.token})
            )
            mail_subject = "Activate your SUST AURA account."
            message = render_to_string(
                "users/email_user_activation.html",
                {
                    "user": pending,
                    "domain": current_site.domain,
                    "activation_url": activation_url,
                    "timestamp": timezone.now(),
                },
            )

            email = EmailMessage(mail_subject, message, to=[to_email])
            try:
                sent = email.send()
                if sent:
                    print(f"\n[SUCCESS] Activation email sent to {to_email}\n")
                    return render(request, "users/user_check_email.html", {"email": to_email})
                else:
                    pending.delete()
                    print(f"\n[FAILURE] Activation email failed to send to {to_email}\n")
                    messages.error(request, f"Failed to send activation email to {to_email}. Please check the email address and try again.")
            except Exception as e:
                pending.delete()
                print(f"\n[ERROR] Exception sending email to {to_email}: {e}\n")
                messages.warning(request, f"An error occurred while sending email to {to_email}. Please try again.")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/signup.html", {"form": form})

def activate(request, token):
    try:
        pending = PendingRegistration.objects.get(token=token)
    except PendingRegistration.DoesNotExist:
        return render(request, "users/user_activation_invalid.html")

    if pending.is_expired():
        pending.delete()
        return render(request, "users/user_activation_invalid.html")

    User = get_user_model()

    # Guard: if user already exists (double-click), just redirect
    if User.objects.filter(username=pending.username).exists():
        pending.delete()
        messages.info(request, "Your account is already activated. Please log in.")
        return redirect("user_login")

    # Create the actual user from pending data
    user = User(
        first_name=pending.first_name,
        username=pending.username,
        email=pending.username,
        password=pending.hashed_password,   # already hashed — do NOT use set_password
        registration_number=pending.registration_number or '',
        department=pending.department,
        session=pending.session or '',
        gender=pending.gender or '',
        blood=pending.blood or '',
        hometown=pending.hometown or '',
        whatsapp_number=pending.whatsapp_number or '',
        social_profile=pending.social_profile or '',
        is_active=False,
        email_verified=True,
    )
    if pending.student_proof:
        user.student_proof = pending.student_proof
    user.save()
    pending.delete()

    # Check Primary Setting for Auto Approval
    primary_setting = PrimarySetting.objects.first()
    if primary_setting and primary_setting.auto_approve:
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Thank you for your email confirmation. You are now logged in.")
        return redirect("profile_view", username=user.username)
    else:
        # Send wait-for-approval email
        current_site = get_current_site(request)
        mail_subject = "Account Verification Success - Pending Approval"
        message = render_to_string(
            "users/email_user_wait.html",
            {
                "user": user,
                "domain": current_site.domain,
                "timestamp": timezone.now(),
            },
        )
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.send()

        # Notify staff
        staff_emails = settings.STAFF_EMAILS
        if staff_emails:
            mail_subject_staff = "New User Waiting for Approval"
            message_staff = render_to_string(
                "users/email_admin_notification.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "timestamp": timezone.now(),
                },
            )
            EmailMessage(mail_subject_staff, message_staff, to=staff_emails).send()

        messages.info(request, "Email verified! Please wait for admin approval.")
        return redirect("user_login")

# Staff Approval List
@login_required
@user_passes_test(lambda u: u.is_staff)
def staff_approval_list(request):
    users = CustomUser.objects.filter(is_active=False, email_verified=True)
    return render(request, "users/staff_approval_list.html", {"users": users})

# Approve User
@login_required
@user_passes_test(lambda u: u.is_staff)
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    user.is_active = True
    user.save()

    # Send approval email
    current_site = get_current_site(request)
    mail_subject = "Account Approved"
    message = render_to_string(
        "users/email_user_approved.html",
        {
            "user": user,
            "domain": current_site.domain,
            "timestamp": timezone.now(),
        },
    )
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()

    messages.success(request, f"User {user.username} approved successfully.")
    return redirect("staff_approval_list")

# Reject User
@login_required
@user_passes_test(lambda u: u.is_staff)
def reject_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    
    # Send rejection email
    current_site = get_current_site(request)
    mail_subject = "Account Application Update"
    message = render_to_string(
        "users/account_rejected_email.html",
        {
            "user": user,
            "domain": current_site.domain,
            "timestamp": timezone.now(),
        },
    )
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()

    username = user.username
    user.delete()
    messages.warning(request, f"User {username} has been rejected and removed.")
    return redirect("staff_approval_list")

# Password Reset
def password_reset(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            new_password = generate_password()
            user.set_password(new_password)
            user.save()
            
            # Send password reset email
            current_site = get_current_site(request)
            mail_subject = "Account Password Reset"
            message = render_to_string(
                "users/email_user_password_reset.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "password": new_password,
                    "timestamp": timezone.now(),
                    "login_url": request.build_absolute_uri(reverse("user_login")),    
                },
            )
            to_email = user.email
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            
            messages.success(request, "Login credentials have been sent to your email.")
        except CustomUser.DoesNotExist:
            messages.warning(request, "No user found with this email address.")
    return render(request, "users/password_reset.html")

# Profile View
@login_required
def profile_view(request, username):
    user = get_object_or_404(CustomUser, username=username)
    # Record visit if the visitor is not the profile owner
    if request.user != user:
        ProfileVisit.objects.create(profile=user, visitor=request.user)

    # Get last 10 visitors
    recent_visitors = user.visits_received.select_related("visitor")[:10]
    
    # Get user's research works (public or if viewing own profile)
    from thesis.models import ResearchWork
    from publication.models import Publication
    user_works = ResearchWork.objects.filter(authors=user).order_by('-uploaded_at')
    user_publications = Publication.objects.filter(authors=user, is_public=True).order_by('-year', '-uploaded_at')

    context = {
        "user": user,
        "recent_visitors": recent_visitors,
        "user_works": user_works,
        "user_publications": user_publications,
    }
    return render(request, "users/profile.html", context)

# Profile Edit
@login_required
def profile_edit(request):
    """
    Allow a user to edit their own profile
    """
    if request.method == "POST":
        form = CustomUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile_view", username=request.user.username)
    else:
        form = CustomUserProfileForm(instance=request.user)

    return render(request, "users/profile_edit.html", {"form": form})


# Generate Password
def generate_password(length=8):
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    password = "".join(random.choice(characters) for _ in range(length))
    return password

