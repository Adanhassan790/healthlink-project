from django import forms
from .models import Appointment

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['symptoms', 'appointment_date', 'appointment_time']
        widgets = {
            'symptoms': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Please describe your symptoms in detail...',
                'class': 'form-control'
            }),
            'appointment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': ''  # Will set dynamically in view
            }),
            'appointment_time': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today
        from datetime import date
        self.fields['appointment_date'].widget.attrs['min'] = date.today().isoformat()