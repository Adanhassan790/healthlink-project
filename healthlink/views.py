from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from users.models import DoctorProfile
from triage.models import SavedAssessment
from appointments.models import Appointment  # ADD THIS

def home(request):
    """Home page - shows the landing page for everyone"""
    return render(request, 'healthlink/home.html')

def login_view(request):  # ADD THIS FUNCTION
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'healthlink/users/login.html', {'form': form})

@login_required
def dashboard(request):
    """Updated dashboard view with saved assessments and prescriptions"""
    from prescriptions.models import Prescription
    from notifications.models import Notification
    from payments.models import MpesaTransaction
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Get user's saved assessments (for patients only)
    saved_assessments = []
    prescriptions = []
    upcoming_appointments = []
    recent_notifications = []
    stats = {}
    
    # Get recent notifications
    recent_notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    
    if hasattr(request.user, 'user_type') and request.user.user_type == 'patient':
        saved_assessments = SavedAssessment.objects.filter(user=request.user)[:5]
        prescriptions = Prescription.objects.filter(
            patient=request.user,
            status__in=['active', 'dispensed', 'completed']
        ).select_related('doctor')[:5]
        
        # Patient stats
        total_appointments = Appointment.objects.filter(patient=request.user).count()
        completed_appointments = Appointment.objects.filter(patient=request.user, status='completed').count()
        upcoming = Appointment.objects.filter(
            patient=request.user, 
            status__in=['confirmed', 'pending'],
            appointment_date__gte=timezone.now()
        ).order_by('appointment_date')[:3]
        total_paid = MpesaTransaction.objects.filter(user=request.user, status='success').aggregate(Sum('amount'))['amount__sum'] or 0
        
        stats = {
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'upcoming_count': upcoming.count(),
            'total_paid': total_paid,
            'prescription_count': Prescription.objects.filter(patient=request.user).count(),
        }
        upcoming_appointments = upcoming
        
    elif hasattr(request.user, 'user_type') and request.user.user_type == 'doctor':
        prescriptions = Prescription.objects.filter(
            doctor=request.user
        ).select_related('patient')[:5]
        
        # Doctor stats
        today = timezone.now().date()
        total_patients = Appointment.objects.filter(doctor=request.user).values('patient').distinct().count()
        today_appointments = Appointment.objects.filter(
            doctor=request.user,
            appointment_date__date=today
        ).count()
        upcoming = Appointment.objects.filter(
            doctor=request.user, 
            status__in=['confirmed', 'pending'],
            appointment_date__gte=timezone.now()
        ).order_by('appointment_date')[:3]
        total_prescriptions = Prescription.objects.filter(doctor=request.user).count()
        
        stats = {
            'total_patients': total_patients,
            'today_appointments': today_appointments,
            'upcoming_count': upcoming.count(),
            'total_prescriptions': total_prescriptions,
        }
        upcoming_appointments = upcoming
    
    # Get user's appointments - ALL appointments
    appointments = []
    if hasattr(request.user, 'user_type'):
        if request.user.user_type == 'patient':
            appointments = Appointment.objects.filter(patient=request.user).order_by('-appointment_date')
        elif request.user.user_type == 'doctor':
            appointments = Appointment.objects.filter(doctor=request.user).order_by('-appointment_date')
    
    return render(request, 'healthlink/users/dashboard.html', {
        'saved_assessments': saved_assessments,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'upcoming_appointments': upcoming_appointments,
        'recent_notifications': recent_notifications,
        'stats': stats,
    })

def logout_view(request):
    logout(request)
    return redirect('home')

def patient_register(request):
    # Use your actual patient registration template if it exists
    return render(request, 'healthlink/users/patient_register.html', {
        'title': 'Patient Registration'
    })

def doctor_register(request):
    if request.method == 'POST':
        return redirect('login')
    
    # Show the registration form for GET requests
    return render(request, 'healthlink/users/doctor_register.html', {
        'title': 'Doctor Registration'
    })

@login_required
def profile(request):
    # Use your actual profile template if it exists
    return render(request, 'healthlink/users/profile.html', {
        'title': 'User Profile'
    })

def doctor_list(request):
    doctors = DoctorProfile.objects.select_related('user').all()
    return render(request, 'healthlink/doctor_list.html', {'doctors': doctors})