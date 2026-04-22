from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, PatientProfile, DoctorProfile

class PatientRegistrationForm(UserCreationForm):
    # Patient profile fields
    blood_type = forms.ChoiceField(
        choices=[('', 'Select Blood Type'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), 
                 ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')],
        required=False
    )
    emergency_contact = forms.CharField(max_length=100, required=False)
    allergies = forms.CharField(widget=forms.Textarea, required=False)
    medical_history = forms.CharField(widget=forms.Textarea, required=False)

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
            try:
                # Create patient profile with additional information
                PatientProfile.objects.create(
                    user=user,
                    blood_type=self.cleaned_data.get('blood_type', ''),
                    emergency_contact=self.cleaned_data.get('emergency_contact', ''),
                    allergies=self.cleaned_data.get('allergies', ''),
                    medical_history=self.cleaned_data.get('medical_history', '')
                )
            except Exception as e:
                # If profile creation fails, still return the user but log the error
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create PatientProfile for {user.username}: {str(e)}")
                raise
        return user


class DoctorRegistrationForm(UserCreationForm):
    # Doctor profile fields
    license_number = forms.CharField(max_length=50)
    specialization = forms.CharField(max_length=100)
    years_of_experience = forms.IntegerField(min_value=0, max_value=50)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    bio = forms.CharField(widget=forms.Textarea, required=False)

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
            try:
                # Create doctor profile with all information
                DoctorProfile.objects.create(
                    user=user,
                    license_number=self.cleaned_data['license_number'],
                    specialization=self.cleaned_data['specialization'],
                    years_of_experience=self.cleaned_data['years_of_experience'],
                    consultation_fee=self.cleaned_data['consultation_fee'],
                    bio=self.cleaned_data.get('bio', '')
                )
            except Exception as e:
                # If profile creation fails, still return the user but log the error
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create DoctorProfile for {user.username}: {str(e)}")
                raise
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