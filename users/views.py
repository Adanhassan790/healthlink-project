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
            logger.info(f"POST request received for patient registration")
            logger.info(f"POST data keys: {list(request.POST.keys())}")
            
            form = PatientRegistrationForm(request.POST)
            logger.info(f"Form is valid: {form.is_valid()}")
            
            if not form.is_valid():
                logger.warning(f"Form validation failed")
                logger.warning(f"Form errors: {form.errors}")
                logger.warning(f"Non-field errors: {form.non_field_errors()}")
                return render(request, 'healthlink/users/patient_register.html', {'form': form})
            
            logger.info(f"Form is valid, attempting save...")
            try:
                user = form.save()
                logger.info(f"✓ User created successfully: {user.username} (ID: {user.id})")
                logger.info(f"✓ User type set to: {user.user_type}")
                
                if hasattr(user, 'patientprofile'):
                    logger.info(f"✓ Patient profile exists with blood type: {user.patientprofile.blood_type}")
                else:
                    logger.warning(f"✗ Patient profile does NOT exist after save")
                
                logger.info(f"Logging in user: {user.username}")
                login(request, user)
                logger.info(f"✓ User logged in successfully")
                
                messages.success(request, f'Welcome {user.first_name}! Your account has been created.')
                
                logger.info(f"Redirecting to dashboard...")
                return redirect('dashboard')
                
            except Exception as e:
                logger.error(f"✗ Error creating/saving user: {str(e)}", exc_info=True)
                messages.error(request, f'Error creating account: {str(e)}')
                return render(request, 'healthlink/users/patient_register.html', {'form': form, 'error': str(e)})
        else:
            form = PatientRegistrationForm()
            return render(request, 'healthlink/users/patient_register.html', {'form': form})
            
    except Exception as e:
        logger.error(f"✗ Unexpected error in patient_register: {str(e)}", exc_info=True)
        return render(request, 'healthlink/users/patient_register.html', {'error': f'An unexpected error occurred: {str(e)}'})

def doctor_register(request):
    try:
        if request.method == 'POST':
            logger.info(f"POST request received for doctor registration")
            logger.info(f"POST data keys: {list(request.POST.keys())}")
            
            form = DoctorRegistrationForm(request.POST)
            logger.info(f"Form is valid: {form.is_valid()}")
            
            if not form.is_valid():
                logger.warning(f"Form validation failed")
                logger.warning(f"Form errors: {form.errors}")
                logger.warning(f"Non-field errors: {form.non_field_errors()}")
                return render(request, 'healthlink/users/doctor_register.html', {'form': form})
            
            logger.info(f"Form is valid, attempting save...")
            try:
                user = form.save()
                logger.info(f"✓ User created successfully: {user.username} (ID: {user.id})")
                logger.info(f"✓ User type set to: {user.user_type}")
                
                if hasattr(user, 'doctorprofile'):
                    logger.info(f"✓ Doctor profile exists with specialization: {user.doctorprofile.specialization}")
                else:
                    logger.warning(f"✗ Doctor profile does NOT exist after save")
                
                logger.info(f"Logging in user: {user.username}")
                login(request, user)
                logger.info(f"✓ User logged in successfully")
                
                messages.success(request, f'Welcome Dr. {user.first_name}! Your account has been created.')
                
                logger.info(f"Redirecting to dashboard...")
                return redirect('dashboard')
                
            except Exception as e:
                logger.error(f"✗ Error creating/saving user: {str(e)}", exc_info=True)
                messages.error(request, f'Error creating account: {str(e)}')
                return render(request, 'healthlink/users/doctor_register.html', {'form': form, 'error': str(e)})
        else:
            form = DoctorRegistrationForm()
            return render(request, 'healthlink/users/doctor_register.html', {'form': form})
            
    except Exception as e:
        logger.error(f"✗ Unexpected error in doctor_register: {str(e)}", exc_info=True)
        return render(request, 'healthlink/users/doctor_register.html', {'error': f'An unexpected error occurred: {str(e)}'})

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