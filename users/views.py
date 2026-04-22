from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    PatientRegistrationForm, 
    DoctorRegistrationForm, 
    UserUpdateForm, 
    PatientProfileForm, 
    DoctorProfileForm
)
from .models import PatientProfile, DoctorProfile

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    PatientRegistrationForm, 
    DoctorRegistrationForm, 
    UserUpdateForm, 
    PatientProfileForm, 
    DoctorProfileForm
)
from .models import PatientProfile, DoctorProfile
import logging

logger = logging.getLogger(__name__)

def patient_register(request):
    try:
        if request.method == 'POST':
            form = PatientRegistrationForm(request.POST)
            if form.is_valid():
                try:
                    user = form.save()
                    logger.info(f"Patient registered successfully: {user.username}")
                    login(request, user)
                    messages.success(request, f'Welcome {user.first_name}! Your account has been created.')
                    return redirect('dashboard')
                except Exception as e:
                    logger.error(f"Error creating patient profile: {str(e)}", exc_info=True)
                    messages.error(request, f'Error creating account: {str(e)}')
            else:
                logger.warning(f"Patient form validation failed: {form.errors}")
        else:
            form = PatientRegistrationForm()
        
        return render(request, 'healthlink/users/patient_register.html', {'form': form})
    except Exception as e:
        logger.error(f"Patient registration view error: {str(e)}", exc_info=True)
        return render(request, 'healthlink/users/patient_register.html', {'error': 'An error occurred. Please try again.'})

def doctor_register(request):
    try:
        if request.method == 'POST':
            form = DoctorRegistrationForm(request.POST)
            if form.is_valid():
                try:
                    user = form.save()
                    logger.info(f"Doctor registered successfully: {user.username}")
                    login(request, user)
                    messages.success(request, f'Welcome Dr. {user.first_name}! Your account has been created.')
                    return redirect('dashboard')
                except Exception as e:
                    logger.error(f"Error creating doctor profile: {str(e)}", exc_info=True)
                    messages.error(request, f'Error creating account: {str(e)}')
            else:
                logger.warning(f"Doctor form validation failed: {form.errors}")
        else:
            form = DoctorRegistrationForm()
        
        return render(request, 'healthlink/users/doctor_register.html', {'form': form})
    except Exception as e:
        logger.error(f"Doctor registration view error: {str(e)}", exc_info=True)
        return render(request, 'healthlink/users/doctor_register.html', {'error': 'An error occurred. Please try again.'})

@login_required
def dashboard(request):
    context = {}
    if request.user.user_type == 'patient':
        context['appointments'] = request.user.patient_appointments.all().order_by('-appointment_date')[:5]
    elif request.user.user_type == 'doctor':
        context['appointments'] = request.user.doctor_appointments.all().order_by('-appointment_date')[:5]
    
    return render(request, 'healthlink/users/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
    
    # Add profile-specific forms
    patient_profile = None
    doctor_profile = None
    patient_form = None
    doctor_form = None
    
    if hasattr(request.user, 'patientprofile'):
        patient_profile = request.user.patientprofile
        patient_form = PatientProfileForm(instance=patient_profile)
    elif hasattr(request.user, 'doctorprofile'):
        doctor_profile = request.user.doctorprofile
        doctor_form = DoctorProfileForm(instance=doctor_profile)
    
    context = {
        'user_form': user_form,
        'patient_form': patient_form,
        'doctor_form': doctor_form,
        'patient_profile': patient_profile,
        'doctor_profile': doctor_profile,
    }
    
    return render(request, 'healthlink/users/profile.html', context)

@login_required
def update_patient_profile(request):
    if request.method == 'POST' and hasattr(request.user, 'patientprofile'):
        form = PatientProfileForm(request.POST, instance=request.user.patientprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your medical information has been updated!')
    return redirect('profile')

@login_required
def update_doctor_profile(request):
    if request.method == 'POST' and hasattr(request.user, 'doctorprofile'):
        form = DoctorProfileForm(request.POST, instance=request.user.doctorprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your professional information has been updated!')
    return redirect('profile')