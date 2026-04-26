from django import forms
from .models import ResearchWork, Report

SELECT_CLASS = 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'

class ResearchWorkForm(forms.ModelForm):
    # Replace the boolean checkbox with a human-friendly dropdown
    is_public = forms.TypedChoiceField(
        label='Visibility',
        choices=[
            (True,  '🌐 Public — visible to all members'),
            (False, '🔒 Only Me — hidden from others'),
        ],
        coerce=lambda v: v == 'True' or v is True,
        widget=forms.Select(attrs={'class': SELECT_CLASS}),
        help_text='Choose who can see this research work.',
    )
    class Meta:
        model = ResearchWork
        fields = ['title', 'abstract', 'work_type', 'supervisor_name', 'link', 'embargo_until', 'is_public']
        widgets = {
            'title':           forms.TextInput(attrs={'class': SELECT_CLASS, 'placeholder': 'Enter title'}),
            'abstract':        forms.Textarea(attrs={'class': SELECT_CLASS, 'rows': 5, 'placeholder': 'Enter abstract'}),
            'work_type':       forms.Select(attrs={'class': SELECT_CLASS}),
            'supervisor_name': forms.TextInput(attrs={'class': SELECT_CLASS, 'placeholder': 'Supervisor Name'}),
            'link':            forms.URLInput(attrs={'class': SELECT_CLASS, 'placeholder': 'Project/Thesis Link'}),
            'embargo_until':   forms.DateInput(attrs={'class': SELECT_CLASS, 'type': 'date'}),
            # is_public intentionally omitted — overridden above as TypedChoiceField
        }
        help_texts = {
            'supervisor_name': 'Enter the name of your research supervisor (e.g., Prof. Dr. John Doe).',
            'link':            'Upload your thesis/project file to Google Drive, set access to "Anyone with the link", and paste the link here.',
            'embargo_until':   'Optional. Hide the document link until this date (e.g. for journal publication delays). Leave blank for immediate access.',
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 
                'rows': 4, 
                'placeholder': 'Please explain why you are reporting this work...'
            }),
        }
