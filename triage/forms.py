# triage/forms.py - CORRECTED VERSION
from django import forms
from .models import Symptom

class TriageForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force fresh queryset every time
        self.fields['symptoms'] = forms.ModelMultipleChoiceField(
            queryset=Symptom.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=True,
            label="Select your symptoms"
        )
    
    additional_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Describe your symptoms in more detail...',
            'class': 'notes-textarea'
        }),
        required=False,
        label="Additional Details"
    )