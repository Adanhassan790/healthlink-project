from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, PatientProfile, DoctorProfile

class PatientRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'date_of_birth',
            'password1',
            'password2',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'patient'
        if commit:
            user.save()
        return user


class DoctorRegistrationForm(UserCreationForm):
    license_number = forms.CharField(max_length=50)
    specialization = forms.CharField(max_length=100)

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'date_of_birth',
            'password1',
            'password2',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'doctor'
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['emergency_contact', 'blood_type', 'allergies', 'medical_history']
        widgets = {
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medical_history': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_type': forms.Select(attrs={'class': 'form-control'}),
        }

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['license_number', 'specialization', 'years_of_experience', 'bio', 'consultation_fee']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }