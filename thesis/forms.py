from django import forms
from .models import ResearchWork, Report

class ResearchWorkForm(forms.ModelForm):
    class Meta:
        model = ResearchWork
        fields = ['title', 'abstract', 'work_type', 'supervisor_name', 'link', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter abstract'}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'supervisor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supervisor Name'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Project/Thesis Link'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'supervisor_name': 'Enter the name of your research supervisor (e.g., Prof. Dr. John Doe).',
            'link': 'Upload your thesis/project file to Google Drive, set access to "Anyone with the link", and paste the link here.',
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Please explain why you are reporting this work...'
            }),
        }
