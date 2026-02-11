from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Department
from django.core import validators
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter email address"
        }),
        validators=[validators.EmailValidator(message="Enter a valid email address.")]
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter password"
        })
    )





class CustomUserCreationForm(UserCreationForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'registration_number',
            'department',
            'session',
            'gender',
            'blood',
            'whatsapp_number',
            'social_profile',
            'username',
            'password1',
            'password2',
            "student_proof",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            field.required = True        
            

        # Optional: Add helper text for social profile
        self.fields['username'].help_text = None
        self.fields['username'].label = "Email address"
        self.fields['username'].widget.input_type = 'email'
        self.fields['username'].widget.attrs.pop("autofocus", None)
        
        self.fields['first_name'].label = "Full Name"
        self.fields['social_profile'].help_text = "Enter link to your most active social profile (e.g., LinkedIn, Facebook, Portfolio)."
        self.fields['whatsapp_number'].help_text = "Enter full phone number with country code (e.g., +8801712345678, +14155552671)."
        self.fields['student_proof'].help_text = "Upload proof of SUST enrollment (any document, e.g., student ID card, certificate, transcript, testimonial, or bank receipt). Supported formats: JPG, JPEG, PNG. Maximum file size: 5 MB."

        self.fields['student_proof'].required = False
        

class CustomUserProfileForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Leave blank to keep current password'}),
        required=False,
        label="New Password"
    )

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'registration_number',
            'department',
            'session',
            'gender',
            'blood',
            'whatsapp_number',
            'social_profile',
            'password',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field_name != 'password':
                field.required = True

        self.fields['first_name'].label = "Full Name"

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user



                