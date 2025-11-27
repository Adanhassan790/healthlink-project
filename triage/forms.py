from django import forms
from .models import Symptom

class TriageForm(forms.Form):
    symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select your symptoms"
    )
    additional_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Describe your symptoms in more detail...'
        }),
        required=False,
        label="Additional Details"
    )