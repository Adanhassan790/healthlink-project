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
    logger.warning("=" * 70)
    logger.warning("PATIENT REGISTRATION - START")
    logger.warning("=" * 70)
    
    try:
        if request.method == 'POST':
            logger.warning(f"[1] POST request received")
            logger.warning(f"[2] POST keys: {list(request.POST.keys())}")
            logger.warning(f"[2a] POST Data keys: {request.POST.keys()}")
            for key in request.POST.keys():
                logger.warning(f"    {key} = {request.POST.get(key)}")
            
            try:
                form = PatientRegistrationForm(request.POST)
                is_valid = form.is_valid()
                logger.warning(f"[3] Form created, is_valid: {is_valid}")
                logger.warning(f"[3a] Form errors dict: {dict(form.errors)}")
                logger.warning(f"[3b] Form non_field_errors: {list(form.non_field_errors())}")
                
                if not is_valid:
                    logger.warning(f"[4] Form validation failed!")
                    logger.warning(f"[4a] Returning form with errors. Total errors: {len(form.errors)}")
                    return render(request, 'healthlink/users/patient_register.html', {'form': form})
                
                logger.info(f"[5] Form is valid, attempting save...")
                user = form.save()
                logger.info(f"[6] User saved successfully: {user.username}")
                
                login(request, user)
                logger.info(f"[7] User logged in")
                
                messages.success(request, f'Welcome {user.first_name}! Your account has been created.')
                logger.info(f"[8] Success message added, redirecting to dashboard")
                
                return redirect('dashboard')
                
            except Exception as e:
                logger.error(f"[ERROR] Form processing error: {type(e).__name__}: {str(e)}", exc_info=True)
                messages.error(request, f'Registration failed: {str(e)}')
                form = PatientRegistrationForm() if 'form' not in locals() else form
                return render(request, 'healthlink/users/patient_register.html', {'form': form})
        else:
            logger.warning("[GET] Displaying registration form (GET request)")
            form = PatientRegistrationForm()
            return render(request, 'healthlink/users/patient_register.html', {'form': form})
            
    except Exception as e:
        logger.error(f"[CRITICAL] Unexpected error in patient_register: {type(e).__name__}: {str(e)}", exc_info=True)
        return render(request, 'healthlink/users/patient_register.html', {
            'error': f'Critical error: {str(e)}',
            'form': PatientRegistrationForm()
        })

def doctor_register(request):
    logger.warning("=" * 70)
    logger.warning("DOCTOR REGISTRATION - START")
    logger.warning("=" * 70)
    
    try:
        if request.method == 'POST':
            logger.warning(f"[1] POST request received")
            logger.warning(f"[2] POST keys: {list(request.POST.keys())}")
            logger.warning(f"[2a] POST Data keys: {request.POST.keys()}")
            for key in request.POST.keys():
                logger.warning(f"    {key} = {request.POST.get(key)}")
            
            try:
                form = DoctorRegistrationForm(request.POST)
                is_valid = form.is_valid()
                logger.warning(f"[3] Form created, is_valid: {is_valid}")
                logger.warning(f"[3a] Form errors dict: {dict(form.errors)}")
                logger.warning(f"[3b] Form non_field_errors: {list(form.non_field_errors())}")
                
                if not is_valid:
                    logger.warning(f"[4] Form validation failed!")
                    logger.warning(f"[4a] Returning form with errors. Total errors: {len(form.errors)}")
                    return render(request, 'healthlink/users/doctor_register.html', {'form': form})
                
                logger.info(f"[5] Form is valid, attempting save...")
                user = form.save()
                logger.info(f"[6] User saved successfully: {user.username}")
                
                login(request, user)
                logger.info(f"[7] User logged in")
                
                messages.success(request, f'Welcome Dr. {user.first_name}! Your account has been created.')
                logger.info(f"[8] Success message added, redirecting to dashboard")
                
                return redirect('dashboard')
                
            except Exception as e:
                logger.error(f"[ERROR] Form processing error: {type(e).__name__}: {str(e)}", exc_info=True)
                messages.error(request, f'Registration failed: {str(e)}')
                form = DoctorRegistrationForm() if 'form' not in locals() else form
                return render(request, 'healthlink/users/doctor_register.html', {'form': form})
        else:
            logger.warning("[GET] Displaying doctor registration form (GET request)")
            form = DoctorRegistrationForm()
            return render(request, 'healthlink/users/doctor_register.html', {'form': form})
            
    except Exception as e:
        logger.error(f"[CRITICAL] Unexpected error in doctor_register: {type(e).__name__}: {str(e)}", exc_info=True)
        return render(request, 'healthlink/users/doctor_register.html', {
            'error': f'Critical error: {str(e)}',
            'form': DoctorRegistrationForm()
        })

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