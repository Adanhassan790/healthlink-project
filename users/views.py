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

def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create patient profile
            PatientProfile.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'healthlink/users/patient_register.html', {'form': form})

def doctor_register(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create doctor profile
            DoctorProfile.objects.create(
                user=user,
                license_number=form.cleaned_data['license_number'],
                specialization=form.cleaned_data['specialization']
            )
            login(request, user)
            return redirect('dashboard')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'healthlink/users/doctor_register.html', {'form': form})

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