from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Prescription, PrescriptionItem, Medication


class PrescriptionForm(forms.ModelForm):
    """Form for creating/editing prescriptions"""
    
    class Meta:
        model = Prescription
        fields = ['patient', 'appointment', 'diagnosis', 'notes', 'valid_until']
        widgets = {
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter diagnosis or condition...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes for patient or pharmacist (optional)...'
            }),
            'valid_until': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'appointment': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default validity to 30 days from now
        if not self.instance.pk:
            self.initial['valid_until'] = (timezone.now() + timedelta(days=30)).date()
        
        # Filter patients for this doctor's appointments
        if doctor:
            from appointments.models import Appointment
            from users.models import CustomUser
            
            # Get patients who have had appointments with this doctor
            patient_ids = Appointment.objects.filter(
                doctor=doctor
            ).values_list('patient_id', flat=True).distinct()
            
            self.fields['patient'].queryset = CustomUser.objects.filter(
                id__in=patient_ids,
                user_type='patient'
            )
            
            # Filter appointments for this doctor
            self.fields['appointment'].queryset = Appointment.objects.filter(
                doctor=doctor,
                status__in=['confirmed', 'completed']
            ).order_by('-appointment_date')
            self.fields['appointment'].required = False


class PrescriptionItemForm(forms.ModelForm):
    """Form for adding medication items to prescription"""
    
    class Meta:
        model = PrescriptionItem
        fields = [
            'medication', 'dosage', 'frequency', 
            'duration_value', 'duration_unit', 'quantity',
            'special_instructions', 'refills_allowed', 'allow_generic'
        ]
        widgets = {
            'medication': forms.Select(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1 tablet, 5ml, 2 puffs'
            }),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'duration_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Duration'
            }),
            'duration_unit': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Total quantity'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'e.g., Take with food, Avoid alcohol...'
            }),
            'refills_allowed': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 12
            }),
            'allow_generic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medication'].queryset = Medication.objects.filter(is_active=True)
        self.fields['special_instructions'].required = False
        self.fields['refills_allowed'].initial = 0
        self.fields['allow_generic'].initial = True


class QuickPrescriptionForm(forms.Form):
    """Simplified form for quick prescriptions"""
    
    patient = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    diagnosis = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Diagnosis...'
        })
    )
    
    # Medication 1
    medication_1 = forms.ModelChoiceField(
        queryset=Medication.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    dosage_1 = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1 tablet'})
    )
    frequency_1 = forms.ChoiceField(
        choices=PrescriptionItem.FREQUENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    duration_1 = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '7'})
    )
    
    # Medication 2 (optional)
    medication_2 = forms.ModelChoiceField(
        queryset=Medication.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    dosage_2 = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1 tablet'})
    )
    frequency_2 = forms.ChoiceField(
        choices=[('', '---')] + list(PrescriptionItem.FREQUENCY_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    duration_2 = forms.IntegerField(
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '7'})
    )
    
    # Medication 3 (optional)
    medication_3 = forms.ModelChoiceField(
        queryset=Medication.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    dosage_3 = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1 tablet'})
    )
    frequency_3 = forms.ChoiceField(
        choices=[('', '---')] + list(PrescriptionItem.FREQUENCY_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    duration_3 = forms.IntegerField(
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '7'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Additional notes...'
        })
    )
    
    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if doctor:
            from appointments.models import Appointment
            from users.models import CustomUser
            
            patient_ids = Appointment.objects.filter(
                doctor=doctor
            ).values_list('patient_id', flat=True).distinct()
            
            self.fields['patient'].queryset = CustomUser.objects.filter(
                id__in=patient_ids,
                user_type='patient'
            )


class MedicationSearchForm(forms.Form):
    """Form for searching medications"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search medications...'
        })
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + list(Medication.CATEGORY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    form_type = forms.ChoiceField(
        choices=[('', 'All Forms')] + list(Medication.FORM_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
