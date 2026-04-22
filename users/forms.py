from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, PatientProfile, DoctorProfile

class PatientRegistrationForm(UserCreationForm):
    # Patient profile fields - optional for initial registration
    BLOOD_TYPE_CHOICES = [
        ('', 'Select Blood Type'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    blood_type = forms.ChoiceField(choices=BLOOD_TYPE_CHOICES, required=False)
    emergency_contact = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Name and phone'}))
    allergies = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Allergies')
    medical_history = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Medical History')

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
            'username': forms.TextInput(attrs={'autocomplete': 'off'}),
            'email': forms.EmailInput(),
            'phone_number': forms.TextInput(),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        import logging
        logger = logging.getLogger(__name__)
        
        user = super().save(commit=False)
        user.user_type = 'patient'
        logger.info(f"[FORM] Created user object: {user.username}")
        
        if commit:
            try:
                logger.info(f"[FORM] Saving user to database...")
                user.save()
                logger.info(f"[FORM] User saved successfully (ID: {user.id})")
                
                logger.info(f"[FORM] Creating PatientProfile...")
                blood_type = self.cleaned_data.get('blood_type', '')
                emergency_contact = self.cleaned_data.get('emergency_contact', '')
                allergies = self.cleaned_data.get('allergies', '')
                medical_history = self.cleaned_data.get('medical_history', '')
                
                logger.info(f"[FORM] Profile data: blood_type={blood_type}, emergency_contact={emergency_contact}")
                
                profile = PatientProfile.objects.create(
                    user=user,
                    blood_type=blood_type,
                    emergency_contact=emergency_contact,
                    allergies=allergies,
                    medical_history=medical_history
                )
                logger.info(f"[FORM] PatientProfile created successfully")
                
            except Exception as e:
                logger.error(f"[FORM] Error during profile creation: {type(e).__name__}: {str(e)}", exc_info=True)
                try:
                    user.delete()
                    logger.info(f"[FORM] User deleted due to profile creation failure")
                except:
                    pass
                raise
        
        return user


class DoctorRegistrationForm(UserCreationForm):
    # Doctor profile fields
    license_number = forms.CharField(max_length=50, help_text='Medical license number')
    specialization = forms.CharField(max_length=100, help_text='Your medical specialization')
    years_of_experience = forms.IntegerField(min_value=0, max_value=50, initial=0)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label='Professional Bio')

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
            'username': forms.TextInput(attrs={'autocomplete': 'off'}),
            'email': forms.EmailInput(),
            'phone_number': forms.TextInput(),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if DoctorProfile.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError('This license number is already registered.')
        return license_number

    def save(self, commit=True):
        import logging
        logger = logging.getLogger(__name__)
        
        user = super().save(commit=False)
        user.user_type = 'doctor'
        logger.info(f"[FORM] Created user object: {user.username}")
        
        if commit:
            try:
                logger.info(f"[FORM] Saving user to database...")
                user.save()
                logger.info(f"[FORM] User saved successfully (ID: {user.id})")
                
                logger.info(f"[FORM] Creating DoctorProfile...")
                license_number = self.cleaned_data['license_number']
                specialization = self.cleaned_data['specialization']
                years_of_experience = self.cleaned_data['years_of_experience']
                consultation_fee = self.cleaned_data['consultation_fee']
                bio = self.cleaned_data.get('bio', '')
                
                logger.info(f"[FORM] Profile data: license={license_number}, spec={specialization}, exp={years_of_experience}, fee={consultation_fee}")
                
                profile = DoctorProfile.objects.create(
                    user=user,
                    license_number=license_number,
                    specialization=specialization,
                    years_of_experience=years_of_experience,
                    consultation_fee=consultation_fee,
                    bio=bio
                )
                logger.info(f"[FORM] DoctorProfile created successfully")
                
            except Exception as e:
                logger.error(f"[FORM] Error during profile creation: {type(e).__name__}: {str(e)}", exc_info=True)
                try:
                    user.delete()
                    logger.info(f"[FORM] User deleted due to profile creation failure")
                except:
                    pass
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