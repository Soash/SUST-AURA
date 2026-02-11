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
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from .models import CustomUser, ProfileVisit, PrimarySetting
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
            user = form.save(commit=False)
            # Deactivate account till it is verified
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = "Activate your account."

            domain = current_site.domain
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            message = render_to_string(
                "users/email_user_activation.html",
                {
                    "user": user,
                    "domain": domain,
                    "uid": uid,
                    "token": token,
                    "timestamp": timezone.now(),
                },
            )
            # User wants to use the username field as the email address
            to_email = form.cleaned_data.get("username")

            # Ensure email field is also populated on the user object if needed,
            # though user.save() was already called above.
            # If the model expects email in user.email, we might need to update it:
            if not user.email and "@" in to_email:
                user.email = to_email
                user.save()

            email = EmailMessage(mail_subject, message, to=[to_email])
            try:
                sent = email.send()
                if sent:
                    print(f"\n[SUCCESS] Activation email sent to {to_email}\n")
                    # messages.success(request, 'Please confirm your email address to complete the registration')
                    return render(request, "users/user_check_email.html", {"email": to_email})
                else:
                    print(
                        f"\n[FAILURE] Activation email failed to send to {to_email}\n"
                    )
                    user.delete()
                    messages.error(request, f"Failed to send activation email to {to_email}. Please check the email address and try again.")
            except Exception as e:
                print(f"\n[ERROR] Exception sending email to {to_email}: {e}\n")
                user.delete()
                # messages.warning(request, f"An error occurred while sending email: {e}")
                messages.warning(request, f"An error occurred while sending email to {to_email}. Please try again.")
            
    else:
        form = CustomUserCreationForm()

    return render(request, "users/signup.html", {"form": form})

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.email_verified = True
        user.save()

        # Check Primary Setting for Auto Approval
        primary_setting = PrimarySetting.objects.first()
        if primary_setting and primary_setting.auto_approve:
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(
                request, "Thank you for your email confirmation. You are now logged in."
            )
            return redirect("profile_view", username=user.username)
        else:
            # Send wait for approval email
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
            to_email = user.email
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            # Notify Staff
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
                email_staff = EmailMessage(
                    mail_subject_staff, message_staff, to=staff_emails
                )
                email_staff.send()

            # Reusing template structure or just render wait message
            # return render(request, 'users/account_approved_email.html')
            # Actually, let's render a simple message or redirect to login with a message
            messages.info(request, "Email verified! Please wait for admin approval.")
            return redirect("user_login")

    else:
        return render(request, "users/user_activation_invalid.html")

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
    context = {
        "user": user,
        "recent_visitors": recent_visitors,
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

