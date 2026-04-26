from django import forms
from .models import Publication


INPUT_CLASS = 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
TEXTAREA_CLASS = INPUT_CLASS + ' resize-y'

class PublicationForm(forms.ModelForm):
    class Meta:
        model  = Publication
        fields = [
            'title', 'abstract', 'pub_type', 'journal_name',
            'year', 'doi', 'link', 'external_authors', 'is_public',
        ]
        widgets = {
            'title':            forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Full title of the publication'}),
            'abstract':         forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 5, 'placeholder': 'Brief abstract (optional)'}),
            'pub_type':         forms.Select(attrs={'class': INPUT_CLASS}),
            'journal_name':     forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Nature, IEEE ICCIT 2024'}),
            'year':             forms.NumberInput(attrs={'class': INPUT_CLASS, 'placeholder': '2024'}),
            'doi':              forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '10.1000/xyz123'}),
            'link':             forms.URLInput(attrs={'class': INPUT_CLASS, 'placeholder': 'https://...'}),
            'external_authors': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'John Doe, Jane Smith'}),
            'is_public':        forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
        }
        labels = {
            'pub_type':         'Publication Type',
            'journal_name':     'Journal / Conference Name',
            'doi':              'DOI',
            'link':             'External URL',
            'external_authors': 'External Co-authors',
            'is_public':        'Make this public',
        }
