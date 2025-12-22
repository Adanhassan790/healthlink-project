from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import DoctorProfile, Specialty, Appointment, DoctorAvailability, DoctorReview
from users.models import CustomUser
from django.http import JsonResponse
from django.db.models import Avg
from users.decorators import patient_required, doctor_required
from notifications.models import notify_appointment_booked  

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
        ) | doctors.filter(
            bio__icontains=search_query
        )
    
    # Filter by max fee
    max_fee = request.GET.get('max_fee')
    if max_fee:
        try:
            doctors = doctors.filter(consultation_fee__lte=int(max_fee))
        except ValueError:
            pass
    
    # Order by rating/experience
    doctors = doctors.order_by('-years_of_experience')
    
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
    
    # Get reviews and rating
    reviews = DoctorReview.objects.filter(doctor=doctor.user).order_by('-created_at')[:3]
    avg_rating = DoctorReview.objects.filter(doctor=doctor.user).aggregate(Avg('rating'))['rating__avg']
    review_count = DoctorReview.objects.filter(doctor=doctor.user).count()
    
    context = {
        'doctor': doctor,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count
    }
    return render(request, 'appointments/doctor_detail.html', context)

@login_required
@patient_required
def book_appointment(request, doctor_id):
    """Handle appointment booking - for patients only"""
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
        
        # Send notifications to patient and doctor
        notify_appointment_booked(request.user, doctor.user, appointment)

        messages.success(request, 'Appointment booked successfully! Please complete payment to confirm your appointment.')
        return redirect('payments:payment_page', appointment_id=appointment.id)  
    
    # GET request - show booking form
    available_slots = generate_available_slots(doctor)
    return render(request, 'appointments/book_appointment.html', {
        'doctor': doctor,
        'available_slots': available_slots
    })

@login_required
def my_appointments(request):
    """Display user's appointments with list and calendar views"""
    from calendar import monthcalendar
    import calendar as cal_module
    
    if request.user.user_type == 'patient':
        appointments = request.user.patient_appointments.all().order_by('-appointment_date')
    elif request.user.user_type == 'doctor':
        appointments = request.user.doctor_appointments.all().order_by('-appointment_date')
    else:
        appointments = Appointment.objects.none()
    
    # Get current month/year or from query params
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Build calendar data
    month_calendar = monthcalendar(year, month)
    month_name = cal_module.month_name[month]
    
    # Get appointments for this month
    month_start = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        month_end = timezone.make_aware(datetime(year + 1, 1, 1))
    else:
        month_end = timezone.make_aware(datetime(year, month + 1, 1))
    
    month_appointments = appointments.filter(
        appointment_date__gte=month_start,
        appointment_date__lt=month_end
    )
    
    # Group appointments by day
    appointments_by_day = {}
    for appt in month_appointments:
        day = appt.appointment_date.day
        if day not in appointments_by_day:
            appointments_by_day[day] = []
        appointments_by_day[day].append(appt)
    
    # Navigation
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1
    
    view_mode = request.GET.get('view', 'list')
    
    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments,
        'view_mode': view_mode,
        'calendar': month_calendar,
        'month_name': month_name,
        'year': year,
        'month': month,
        'today': today,
        'appointments_by_day': appointments_by_day,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    })

def generate_available_slots(doctor=None):
    """Generate available time slots for the next 7 days based on doctor's availability"""
    slots = []
    start_date = timezone.now().date()
    
    # Day of week mapping (Python weekday to our model's day_of_week)
    day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    # Get doctor's availability settings if doctor is provided
    doctor_availability = {}
    if doctor:
        availabilities = DoctorAvailability.objects.filter(doctor=doctor.user, is_available=True)
        for avail in availabilities:
            if avail.day_of_week not in doctor_availability:
                doctor_availability[avail.day_of_week] = []
            doctor_availability[avail.day_of_week].append({
                'start': avail.start_time,
                'end': avail.end_time
            })
    
    for i in range(1, 8):  # Next 7 days
        current_date = start_date + timedelta(days=i)
        day_name = day_names[current_date.weekday()]
        
        # Check if doctor has set availability for this day
        is_available = True
        time_slots = []
        
        if doctor and doctor_availability:
            # Doctor has set availability - only show days they're available
            if day_name in doctor_availability:
                is_available = True
                for slot in doctor_availability[day_name]:
                    time_slots.append({
                        'start': slot['start'].strftime('%H:%M'),
                        'end': slot['end'].strftime('%H:%M'),
                        'display': f"{slot['start'].strftime('%I:%M %p')} - {slot['end'].strftime('%I:%M %p')}"
                    })
            else:
                is_available = False
        else:
            # No doctor or no availability set - default hours (9 AM - 5 PM)
            default_times = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']
            for t in default_times:
                time_slots.append({
                    'start': t,
                    'end': '',
                    'display': datetime.strptime(t, '%H:%M').strftime('%I:%M %p')
                })
        
        if is_available:
            slots.append({
                'date': current_date,
                'display_date': current_date.strftime('%Y-%m-%d'),
                'display_text': current_date.strftime('%B %d, %Y'),
                'day_name': day_name.capitalize(),
                'time_slots': time_slots
            })
    
    return slots

@patient_required
def book_appointment_redirect(request):
    """Redirect to doctor list when book_appointment is called without doctor_id"""
    return redirect('appointments:doctor_list') 

@login_required
@patient_required
def reschedule_appointment(request, appointment_id):
    """Handle appointment rescheduling - for patients only"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if request.method == 'POST':
        # Get new date and time from form
        new_date_str = request.POST.get('appointment_date')
        new_time_str = request.POST.get('appointment_time')
        
        try:
            # Combine date and time
            datetime_str = f"{new_date_str} {new_time_str}"
            new_appointment_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            new_appointment_datetime = timezone.make_aware(new_appointment_datetime)
            
            # Update appointment
            appointment.appointment_date = new_appointment_datetime
            appointment.status = 'confirmed'  # Keep it confirmed if it was already paid
            appointment.save()
            
            messages.success(request, 'Appointment rescheduled successfully!')
            return redirect('appointments:my_appointments')
            
        except ValueError:
            messages.error(request, 'Invalid date or time format.')
            return render(request, 'appointments/reschedule_appointment.html', {
                'appointment': appointment,
                'available_slots': generate_available_slots()
            })
    
    # GET request - show rescheduling form
    return render(request, 'appointments/reschedule_appointment.html', {
        'appointment': appointment,
        'available_slots': generate_available_slots()
    })

@login_required
def cancel_appointment(request, appointment_id):
    """Handle appointment cancellation"""
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
        
        # Update appointment status to cancelled
        appointment.status = 'cancelled'
        appointment.save()
        
        messages.success(request, 'Appointment cancelled successfully.')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# ==================== DOCTOR AVAILABILITY VIEWS ====================

@login_required
@doctor_required
def manage_availability(request):
    """Doctor view to manage their weekly availability"""
    availability = DoctorAvailability.objects.filter(doctor=request.user).order_by('day_of_week', 'start_time')
    
    days = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    # Group availability by day
    availability_by_day = {day[0]: [] for day in days}
    for slot in availability:
        availability_by_day[slot.day_of_week].append(slot)
    
    context = {
        'days': days,
        'availability_by_day': availability_by_day,
    }
    return render(request, 'appointments/manage_availability.html', context)


@login_required
@doctor_required
def add_availability(request):
    """Add a new availability slot"""
    if request.method == 'POST':
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        slot_duration = request.POST.get('slot_duration', 30)
        
        if not all([day_of_week, start_time, end_time]):
            messages.error(request, 'Please fill in all fields.')
            return redirect('appointments:manage_availability')
        
        # Check for overlapping slots
        existing = DoctorAvailability.objects.filter(
            doctor=request.user,
            day_of_week=day_of_week,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
        
        if existing:
            messages.error(request, 'This time slot overlaps with an existing slot.')
            return redirect('appointments:manage_availability')
        
        DoctorAvailability.objects.create(
            doctor=request.user,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            slot_duration=slot_duration
        )
        
        messages.success(request, 'Availability slot added successfully.')
        return redirect('appointments:manage_availability')
    
    return redirect('appointments:manage_availability')


@login_required
@doctor_required
def delete_availability(request, slot_id):
    """Delete an availability slot"""
    slot = get_object_or_404(DoctorAvailability, id=slot_id, doctor=request.user)
    slot.delete()
    messages.success(request, 'Availability slot removed.')
    return redirect('appointments:manage_availability')


@login_required
@doctor_required  
def toggle_availability(request, slot_id):
    """Toggle availability slot on/off"""
    slot = get_object_or_404(DoctorAvailability, id=slot_id, doctor=request.user)
    slot.is_available = not slot.is_available
    slot.save()
    return JsonResponse({'success': True, 'is_available': slot.is_available})


def get_doctor_available_slots(request, doctor_id):
    """API to get available slots for a doctor on a specific date"""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date required'}, status=400)
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    doctor = get_object_or_404(CustomUser, id=doctor_id, user_type='doctor')
    day_of_week = selected_date.weekday()
    
    # Get doctor's availability for this day
    availability = DoctorAvailability.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week,
        is_available=True
    )
    
    if not availability.exists():
        return JsonResponse({'slots': [], 'message': 'Doctor not available on this day'})
    
    # Get existing appointments for this date
    existing_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date=selected_date,
        status__in=['pending', 'confirmed']
    ).values_list('appointment_date', flat=True)
    
    booked_times = [apt.time() for apt in existing_appointments]
    
    # Generate available slots
    slots = []
    for avail in availability:
        current_time = datetime.combine(selected_date, avail.start_time)
        end_time = datetime.combine(selected_date, avail.end_time)
        
        while current_time + timedelta(minutes=avail.slot_duration) <= end_time:
            slot_time = current_time.time()
            
            # Check if slot is not booked and not in the past
            if slot_time not in booked_times:
                if selected_date > timezone.now().date() or (
                    selected_date == timezone.now().date() and 
                    current_time > timezone.now()
                ):
                    slots.append({
                        'time': slot_time.strftime('%H:%M'),
                        'display': slot_time.strftime('%I:%M %p')
                    })
            
            current_time += timedelta(minutes=avail.slot_duration)
    
    return JsonResponse({'slots': slots})


# ==================== REVIEWS ====================

@login_required
@patient_required
def submit_review(request, appointment_id):
    """Submit a review for a completed appointment"""
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        patient=request.user,
        status='completed'
    )
    
    # Check if review already exists
    if hasattr(appointment, 'review'):
        messages.warning(request, 'You have already reviewed this appointment.')
        return redirect('appointments:my_appointments')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if not rating:
            messages.error(request, 'Please select a rating.')
            return render(request, 'appointments/submit_review.html', {
                'appointment': appointment
            })
        
        DoctorReview.objects.create(
            appointment=appointment,
            patient=request.user,
            doctor=appointment.doctor,
            rating=int(rating),
            comment=comment
        )
        
        messages.success(request, 'Thank you for your review!')
        return redirect('appointments:my_appointments')
    
    return render(request, 'appointments/submit_review.html', {
        'appointment': appointment
    })


def doctor_reviews(request, doctor_id):
    """View all reviews for a doctor"""
    doctor = get_object_or_404(DoctorProfile, user_id=doctor_id)
    reviews = DoctorReview.objects.filter(doctor=doctor.user).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    return render(request, 'appointments/doctor_reviews.html', {
        'doctor': doctor,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count()
    })