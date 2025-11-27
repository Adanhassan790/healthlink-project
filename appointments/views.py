from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import DoctorProfile, Specialty, Appointment
from users.models import CustomUser

def doctor_list(request):
    """Display list of doctors with search and filter functionality"""
    doctors = DoctorProfile.objects.all()
    specialties = Specialty.objects.all()
    
    # Filter by specialty if provided
    specialty_filter = request.GET.get('specialty')
    if specialty_filter:
        doctors = doctors.filter(specialization=specialty_filter)
    
    # Filter by search query
    search_query = request.GET.get('search')
    if search_query:
        doctors = doctors.filter(
            user__first_name__icontains=search_query
        ) | doctors.filter(
            user__last_name__icontains=search_query
        ) | doctors.filter(
            specialization__icontains=search_query
        )
    
    context = {
        'doctors': doctors,
        'specialties': specialties,
        'selected_specialty': specialty_filter,
        'search_query': search_query or ''
    }
    return render(request, 'appointments/doctor_list.html', context)

def doctor_detail(request, doctor_id):
    """Display detailed doctor profile"""
    doctor = get_object_or_404(DoctorProfile, user_id=doctor_id)
    context = {'doctor': doctor}
    return render(request, 'appointments/doctor_detail.html', context)

@login_required
def book_appointment(request, doctor_id):
    """Handle appointment booking"""
    doctor = get_object_or_404(DoctorProfile, user_id=doctor_id)
    
    if request.method == 'POST':
        # Get form data
        symptoms = request.POST.get('symptoms', '')
        appointment_date_str = request.POST.get('appointment_date')
        appointment_time_str = request.POST.get('appointment_time')
        
        # Validate required fields
        if not symptoms or not appointment_date_str or not appointment_time_str:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'appointments/book_appointment.html', {
                'doctor': doctor,
                'symptoms': symptoms,
                'appointment_date': appointment_date_str,
                'appointment_time': appointment_time_str
            })
        
        # Combine date and time
        try:
            datetime_str = f"{appointment_date_str} {appointment_time_str}"
            appointment_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            
            # Make the datetime timezone-aware
            appointment_datetime = timezone.make_aware(appointment_datetime)
            
            # Check if the datetime is in the future
            if appointment_datetime <= timezone.now():
                messages.error(request, 'Please select a future date and time.')
                return render(request, 'appointments/book_appointment.html', {
                    'doctor': doctor,
                    'symptoms': symptoms,
                    'appointment_date': appointment_date_str,
                    'appointment_time': appointment_time_str
                })
            
        except ValueError:
            messages.error(request, 'Invalid date or time format.')
            return render(request, 'appointments/book_appointment.html', {
                'doctor': doctor,
                'symptoms': symptoms,
                'appointment_date': appointment_date_str,
                'appointment_time': appointment_time_str
            })
        
        # Get or create specialty
        specialty, created = Specialty.objects.get_or_create(name=doctor.specialization)
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor.user,
            specialty=specialty,
            appointment_date=appointment_datetime,
            symptoms=symptoms,
            status='pending'
        )
        

        messages.success(request, 'Appointment booked successfully! Please complete payment to confirm your appointment.')
        return redirect('payment_page', appointment_id=appointment.id)  
    
    # GET request - show booking form
    available_slots = generate_available_slots()
    return render(request, 'appointments/book_appointment.html', {
        'doctor': doctor,
        'available_slots': available_slots
    })

@login_required
def my_appointments(request):
    """Display user's appointments"""
    if request.user.user_type == 'patient':
        appointments = request.user.patient_appointments.all().order_by('-appointment_date')
    elif request.user.user_type == 'doctor':
        appointments = request.user.doctor_appointments.all().order_by('-appointment_date')
    else:
        appointments = Appointment.objects.none()
    
    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments
    })

def generate_available_slots():
    """Generate available time slots for the next 7 days"""
    slots = []
    start_date = timezone.now().date()
    
    for i in range(1, 8):  # Next 7 days
        current_date = start_date + timedelta(days=i)
        slots.append({
            'date': current_date,
            'display_date': current_date.strftime('%Y-%m-%d'),
            'display_text': current_date.strftime('%B %d, %Y')
        })
    
    return slots

def book_appointment_redirect(request):
    """Redirect to doctor list when book_appointment is called without doctor_id"""
    return redirect('appointments:doctor_list') 