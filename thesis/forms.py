from django import forms
from .models import ResearchWork, Report

class ResearchWorkForm(forms.ModelForm):
    class Meta:
        model = ResearchWork
        fields = ['title', 'abstract', 'work_type', 'supervisor_name', 'link', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'placeholder': 'Enter title'}),
            'abstract': forms.Textarea(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'rows': 5, 'placeholder': 'Enter abstract'}),
            'work_type': forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'supervisor_name': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'placeholder': 'Supervisor Name'}),
            'link': forms.URLInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'placeholder': 'Project/Thesis Link'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
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
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 
                'rows': 4, 
                'placeholder': 'Please explain why you are reporting this work...'
            }),
        }
