from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from users.models import CustomUser, DoctorProfile, PatientProfile
from users.forms import PatientProfileForm, DoctorProfileForm

@login_required
def dashboard(request):
    """Admin dashboard"""
    # Check if user is admin
    if not request.user.is_staff:
        raise Http404("You don't have permission to access this page")
    
    return render(request, 'administration/dashboard.html')

@login_required
def user_management(request):
    """Manage all users"""
    if not request.user.is_staff:
        raise Http404("You don't have permission to access this page")
    
    users = CustomUser.objects.all()
    return render(request, 'administration/user_management.html', {'users': users})

@login_required
def user_detail(request, user_id):
    """View user details"""
    if not request.user.is_staff:
        raise Http404("You don't have permission to access this page")
    
    viewed_user = get_object_or_404(CustomUser, id=user_id)
    doctor_profile = getattr(viewed_user, 'doctorprofile', None)
    patient_profile = getattr(viewed_user, 'patientprofile', None)
    
    return render(request, 'administration/user_detail.html', {
        'viewed_user': viewed_user,
        'doctor_profile': doctor_profile,
        'patient_profile': patient_profile,
    })

@login_required
def edit_user(request, user_id):
    """Edit user information"""
    if not request.user.is_staff:
        raise Http404("You don't have permission to access this page")
    
    viewed_user = get_object_or_404(CustomUser, id=user_id)
    doctor_profile = getattr(viewed_user, 'doctorprofile', None)
    patient_profile = getattr(viewed_user, 'patientprofile', None)
    
    if request.method == 'POST':
        # Update basic user info
        viewed_user.first_name = request.POST.get('first_name', viewed_user.first_name)
        viewed_user.last_name = request.POST.get('last_name', viewed_user.last_name)
        viewed_user.email = request.POST.get('email', viewed_user.email)
        viewed_user.is_active = request.POST.get('is_active') == 'on'
        
        if 'phone_number' in request.POST:
            viewed_user.phone_number = request.POST.get('phone_number')
        
        if 'user_type' in request.POST:
            viewed_user.user_type = request.POST.get('user_type')
        
        viewed_user.save()
        
        # Update doctor profile if exists
        if doctor_profile:
            doctor_profile.specialization = request.POST.get('specialization', doctor_profile.specialization)
            doctor_profile.license_number = request.POST.get('license_number', doctor_profile.license_number)
            doctor_profile.consultation_fee = request.POST.get('consultation_fee', doctor_profile.consultation_fee)
            doctor_profile.years_of_experience = request.POST.get('years_of_experience', doctor_profile.years_of_experience)
            doctor_profile.bio = request.POST.get('bio', doctor_profile.bio)
            doctor_profile.save()
        
        # Update patient profile if exists
        if patient_profile:
            patient_profile.blood_type = request.POST.get('blood_type', patient_profile.blood_type)
            patient_profile.emergency_contact = request.POST.get('emergency_contact', patient_profile.emergency_contact)
            patient_profile.allergies = request.POST.get('allergies', patient_profile.allergies)
            patient_profile.medical_history = request.POST.get('medical_history', patient_profile.medical_history)
            patient_profile.save()
        
        messages.success(request, 'User updated successfully!')
        return redirect('administration:user_detail', user_id=user_id)
    
    return render(request, 'administration/edit_user.html', {
        'viewed_user': viewed_user,
        'doctor_profile': doctor_profile,
        'patient_profile': patient_profile,
    })
