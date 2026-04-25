from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Department
from django.core import validators
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
            "placeholder": "Enter email address"
        }),
        validators=[validators.EmailValidator(message="Enter a valid email address.")]
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
            "placeholder": "Enter password"
        })
    )





class CustomUserCreationForm(UserCreationForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'})
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
            'hometown',
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
            if type(field.widget) in (forms.CheckboxInput, forms.RadioSelect):
                field.widget.attrs.update({'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'})
            elif type(field.widget) == forms.ClearableFileInput:
                field.widget.attrs.update({'class': 'mt-1 block w-full text-sm text-gray-500 border border-gray-300 rounded-md p-2 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'})
            else:
                field.widget.attrs.update({'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'})
            field.required = True        
            

        # Optional: Add helper text for social profile
        self.fields['username'].help_text = None
        self.fields['username'].label = "Email address"
        self.fields['username'].widget.input_type = 'email'
        self.fields['username'].widget.attrs.pop("autofocus", None)
        
        self.fields['registration_number'].label = "Registration Number"
        self.fields['registration_number'].help_text = "Enter your 10 digit registration number of Honours (e.g., 2022140101)."
        self.fields['department'].help_text = "Select your department name of Honours."
        self.fields['session'].help_text = "Select your session of Honours."


        self.fields['first_name'].label = "Full Name"
        self.fields['username'].help_text = "If you have a SUST email address, we encourage you to use it."
        self.fields['social_profile'].help_text = "Enter link to your most active social profile (e.g., LinkedIn, Facebook, Portfolio)."
        self.fields['whatsapp_number'].help_text = "Enter full phone number with country code (e.g., +8801712345678, +14155552671). If you do not use WhatsApp, please provide an alternative contact method."
        self.fields['student_proof'].help_text = "Upload proof of SUST enrollment (any document, e.g., student ID card, certificate, transcript, testimonial, or bank receipt). Supported formats: JPG, JPEG, PNG. Maximum file size: 5 MB."

        self.fields['student_proof'].required = False
        

class CustomUserProfileForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'})
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
            'hometown',
            'whatsapp_number',
            'social_profile',
            'password',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if type(field.widget) in (forms.CheckboxInput, forms.RadioSelect):
                field.widget.attrs.update({'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'})
            elif type(field.widget) == forms.ClearableFileInput:
                field.widget.attrs.update({'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'})
            else:
                field.widget.attrs.update({'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'})
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



                