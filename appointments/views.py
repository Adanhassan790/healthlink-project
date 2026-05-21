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
import logging

logger = logging.getLogger(__name__)  

def doctor_list(request):
    """Display list of doctors with search and filter functionality"""
    try:
        logger.debug("Fetching all doctors")
        doctors = DoctorProfile.objects.select_related('user').all()
        logger.debug(f"Found {doctors.count()} doctors in database")
        
        specialties = Specialty.objects.all()
        logger.debug(f"Found {specialties.count()} specialties")
        
        # Filter by specialty if provided
        specialty_filter = request.GET.get('specialty')
        if specialty_filter:
            logger.debug(f"Filtering by specialty: {specialty_filter}")
            doctors = doctors.filter(specialization=specialty_filter)
            logger.debug(f"After specialty filter: {doctors.count()} doctors")
        
        # Filter by search query
        search_query = request.GET.get('search')
        if search_query:
            logger.debug(f"Searching for: {search_query}")
            doctors = doctors.filter(
                user__first_name__icontains=search_query
            ) | doctors.filter(
                user__last_name__icontains=search_query
            ) | doctors.filter(
                specialization__icontains=search_query
            ) | doctors.filter(
                bio__icontains=search_query
            )
            logger.debug(f"After search filter: {doctors.count()} doctors")
        
        # Filter by max fee
        max_fee = request.GET.get('max_fee')
        if max_fee:
            try:
                logger.debug(f"Filtering by max_fee: {max_fee}")
                doctors = doctors.filter(consultation_fee__lte=int(max_fee))
                logger.debug(f"After fee filter: {doctors.count()} doctors")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid max_fee value: {max_fee} - {str(e)}")
                pass
        
        # Order by rating/experience
        doctors = doctors.order_by('-years_of_experience')
        logger.debug(f"Final count: {doctors.count()} doctors returned")
        
        context = {
            'doctors': doctors,
            'specialties': specialties,
            'selected_specialty': specialty_filter,
            'search_query': search_query or ''
        }
        return render(request, 'appointments/doctor_list.html', context)
        
    except DoctorProfile.DoesNotExist:
        logger.error("No doctors found in database")
        messages.warning(request, 'No doctors available at the moment. Please try again later.')
        return render(request, 'appointments/doctor_list.html', {
            'doctors': [],
            'specialties': [],
            'error': 'No doctors available'
        })
    except Exception as e:
        logger.exception(f"Error in doctor_list view: {str(e)}")
        messages.error(request, 'An error occurred while fetching doctors. Please try again.')
        return render(request, 'appointments/doctor_list.html', {
            'doctors': [],
            'specialties': [],
            'error': 'Error loading doctors'
        })

def doctor_detail(request, doctor_id):
    """Display detailed doctor profile"""
    try:
        logger.debug(f"Doctor detail request for doctor_id: {doctor_id}")
        
        # Verify doctor exists
        try:
            doctor = DoctorProfile.objects.select_related('user').get(user_id=doctor_id)
            logger.debug(f"Found doctor: {doctor.user.get_full_name()}")
        except DoctorProfile.DoesNotExist:
            logger.warning(f"DoctorProfile not found for user_id {doctor_id}")
            messages.error(request, f'Doctor with ID {doctor_id} not found.')
            return redirect('appointments:doctor_list')
        
        # Get reviews and rating with error handling
        reviews = []
        avg_rating = None
        review_count = 0
        
        try:
            reviews = DoctorReview.objects.filter(doctor=doctor.user).order_by('-created_at')[:3]
            rating_data = DoctorReview.objects.filter(doctor=doctor.user).aggregate(Avg('rating'))
            avg_rating = rating_data.get('rating__avg') if rating_data else None
            review_count = DoctorReview.objects.filter(doctor=doctor.user).count()
            logger.debug(f"Reviews for doctor {doctor_id}: count={review_count}, avg_rating={avg_rating}")
        except Exception as e:
            logger.warning(f"Error fetching reviews for doctor {doctor_id}: {str(e)}", exc_info=True)
            reviews = []
            avg_rating = None
            review_count = 0
        
        context = {
            'doctor': doctor,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_count': review_count
        }
        
        try:
            response = render(request, 'appointments/doctor_detail.html', context)
            logger.debug(f"Successfully rendered doctor_detail.html for doctor_id {doctor_id}")
            return response
        except Exception as template_error:
            logger.exception(f"Template rendering error in doctor_detail for doctor_id {doctor_id}: {str(template_error)}")
            messages.error(request, 'Error displaying doctor profile. Please try again.')
            return redirect('appointments:doctor_list')
        
    except Exception as e:
        logger.exception(f"Unexpected error in doctor_detail view for doctor_id {doctor_id}: {str(e)}")
        messages.error(request, 'An unexpected error occurred. Please try again.')
        return redirect('appointments:doctor_list')

@login_required
@patient_required
def book_appointment(request, doctor_id):
    """Handle appointment booking - for patients only"""
    try:
        doctor = get_object_or_404(DoctorProfile, user_id=doctor_id)
        
        if request.method == 'POST':
            try:
                # Get form data
                symptoms = request.POST.get('symptoms', '').strip()
                appointment_date_str = request.POST.get('appointment_date', '').strip()
                appointment_time_str = request.POST.get('appointment_time', '').strip()
                
                # Validate required fields
                if not symptoms or not appointment_date_str or not appointment_time_str:
                    messages.error(request, 'Please fill in all required fields.')
                    return render(request, 'appointments/book_appointment.html', {
                        'doctor': doctor,
                        'symptoms': symptoms,
                        'appointment_date': appointment_date_str,
                        'appointment_time': appointment_time_str,
                        'from_triage': request.GET.get('from_triage') == 'true',
                        'triage_symptoms': request.GET.get('symptoms', '').strip() or symptoms,
                    })
                
                # Combine date and time and validate format
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
                    
                except ValueError as e:
                    logger.warning(f"Invalid date/time format: {appointment_date_str} {appointment_time_str}")
                    messages.error(request, 'Invalid date or time format. Please use YYYY-MM-DD and HH:MM.')
                    return render(request, 'appointments/book_appointment.html', {
                        'doctor': doctor,
                        'symptoms': symptoms,
                        'appointment_date': appointment_date_str,
                        'appointment_time': appointment_time_str,
                        'from_triage': request.GET.get('from_triage') == 'true',
                        'triage_symptoms': request.GET.get('symptoms', '').strip() or symptoms,
                    })
                
                # Get or create specialty
                try:
                    specialty, created = Specialty.objects.get_or_create(
                        name=doctor.specialization,
                        defaults={'description': f'Specialty: {doctor.specialization}'}
                    )
                except Exception as e:
                    logger.error(f"Error creating specialty: {str(e)}")
                    messages.error(request, 'Error processing specialization. Please try again.')
                    return redirect('appointments:doctor_detail', doctor_id=doctor_id)
                
                # Create appointment with error handling
                try:
                    appointment = Appointment.objects.create(
                        patient=request.user,
                        doctor=doctor.user,
                        specialty=specialty,
                        appointment_date=appointment_datetime,
                        symptoms=symptoms,
                        status='pending'
                    )
                    
                    # Send notifications - wrap in try-catch to prevent booking failure
                    try:
                        notify_appointment_booked(request.user, doctor.user, appointment)
                    except Exception as notify_error:
                        logger.error(f"Error sending notification: {str(notify_error)}")
                        # Don't fail the booking, just log the error
                    
                    messages.success(request, 'Appointment booked successfully! Please complete payment to confirm.')
                    return redirect('payments:payment_page', appointment_id=appointment.id)
                    
                except Exception as appt_error:
                    logger.exception(f"Error creating appointment: {str(appt_error)}")
                    messages.error(request, 'Error creating appointment. Please try again.')
                    return render(request, 'appointments/book_appointment.html', {
                        'doctor': doctor,
                        'available_slots': generate_available_slots(doctor),
                        'from_triage': request.GET.get('from_triage') == 'true',
                        'triage_symptoms': request.GET.get('symptoms', '').strip() or symptoms,
                    })
            
            except Exception as post_error:
                logger.exception(f"Error processing booking request: {str(post_error)}")
                messages.error(request, 'An error occurred while processing your booking. Please try again.')
                return render(request, 'appointments/book_appointment.html', {
                    'doctor': doctor,
                    'available_slots': generate_available_slots(doctor)
                })
        
        # GET request - show booking form
        try:
            available_slots = generate_available_slots(doctor)
        except Exception as slot_error:
            logger.warning(f"Error generating slots for doctor {doctor_id}: {str(slot_error)}")
            available_slots = []

        from_triage = request.GET.get('from_triage') == 'true'
        symptoms = request.GET.get('symptoms', '').strip()
        
        return render(request, 'appointments/book_appointment.html', {
            'doctor': doctor,
            'available_slots': available_slots,
            'from_triage': from_triage,
            'triage_symptoms': symptoms,
        })
        
    except Exception as e:
        logger.exception(f"Error in book_appointment view for doctor_id {doctor_id}: {str(e)}")
        messages.error(request, 'Doctor not found or an error occurred. Please try again.')
        return redirect('appointments:doctor_list')

@login_required
def my_appointments(request):
    """Display user's appointments with list and calendar views"""
    try:
        from calendar import monthcalendar
        import calendar as cal_module
        
        # Get user's appointments with error handling
        try:
            if request.user.user_type == 'patient':
                appointments = request.user.patient_appointments.all().order_by('-appointment_date')
            elif request.user.user_type == 'doctor':
                appointments = request.user.doctor_appointments.all().order_by('-appointment_date')
            else:
                logger.warning(f"User {request.user.id} has invalid user_type: {request.user.user_type}")
                appointments = Appointment.objects.none()
        except AttributeError as e:
            logger.error(f"Error accessing user_type for user {request.user.id}: {str(e)}")
            appointments = Appointment.objects.none()
        
        # Get current month/year or from query params with validation
        today = timezone.now().date()
        try:
            year = int(request.GET.get('year', today.year))
            month = int(request.GET.get('month', today.month))
            
            # Validate month and year
            if month < 1 or month > 12:
                month = today.month
            if year < 2000 or year > 2100:
                year = today.year
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid month/year parameters: {request.GET}")
            year = today.year
            month = today.month
        
        # Build calendar data with error handling
        try:
            month_calendar = monthcalendar(year, month)
            month_name = cal_module.month_name[month]
        except Exception as e:
            logger.error(f"Error building calendar for {year}-{month}: {str(e)}")
            month_calendar = []
            month_name = 'Unknown'
        
        # Get appointments for this month
        try:
            month_start = timezone.make_aware(datetime(year, month, 1))
            if month == 12:
                month_end = timezone.make_aware(datetime(year + 1, 1, 1))
            else:
                month_end = timezone.make_aware(datetime(year, month + 1, 1))
            
            month_appointments = appointments.filter(
                appointment_date__gte=month_start,
                appointment_date__lt=month_end
            )
        except Exception as e:
            logger.error(f"Error filtering monthly appointments: {str(e)}")
            month_appointments = []
        
        # Group appointments by day with error handling
        appointments_by_day = {}
        try:
            for appt in month_appointments:
                try:
                    day = appt.appointment_date.day
                    if day not in appointments_by_day:
                        appointments_by_day[day] = []
                    appointments_by_day[day].append(appt)
                except AttributeError as e:
                    logger.warning(f"Error processing appointment {appt.id}: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"Error grouping appointments: {str(e)}")
            appointments_by_day = {}
        
        # Calculate navigation
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
        
    except Exception as e:
        logger.exception(f"Error in my_appointments view: {str(e)}")
        messages.error(request, 'An error occurred while loading your appointments. Please try again.')
        return render(request, 'appointments/my_appointments.html', {
            'appointments': [],
            'calendar': [],
            'appointments_by_day': {},
            'error': 'Error loading appointments'
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
@patient_required
def book_appointment_redirect(request):
    """Redirect to doctor list when book_appointment is called without doctor_id"""
    return redirect('appointments:doctor_list') 

@login_required
@patient_required
def reschedule_appointment(request, appointment_id):
    """Handle appointment rescheduling - for patients only"""
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
        
        if request.method == 'POST':
            try:
                # Get new date and time from form
                new_date_str = request.POST.get('appointment_date', '').strip()
                new_time_str = request.POST.get('appointment_time', '').strip()
                
                if not new_date_str or not new_time_str:
                    messages.error(request, 'Please provide a new date and time.')
                    return render(request, 'appointments/reschedule_appointment.html', {
                        'appointment': appointment,
                        'available_slots': generate_available_slots()
                    })
                
                try:
                    # Combine date and time
                    datetime_str = f"{new_date_str} {new_time_str}"
                    new_appointment_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                    new_appointment_datetime = timezone.make_aware(new_appointment_datetime)
                    
                    # Validate future date
                    if new_appointment_datetime <= timezone.now():
                        messages.error(request, 'Please select a future date and time.')
                        return render(request, 'appointments/reschedule_appointment.html', {
                            'appointment': appointment,
                            'available_slots': generate_available_slots()
                        })
                    
                    # Update appointment
                    appointment.appointment_date = new_appointment_datetime
                    appointment.status = 'confirmed'
                    appointment.save()
                    
                    messages.success(request, 'Appointment rescheduled successfully!')
                    return redirect('appointments:my_appointments')
                    
                except ValueError as e:
                    logger.warning(f"Invalid date/time for reschedule: {new_date_str} {new_time_str}")
                    messages.error(request, 'Invalid date or time format. Use YYYY-MM-DD and HH:MM.')
                    return render(request, 'appointments/reschedule_appointment.html', {
                        'appointment': appointment,
                        'available_slots': generate_available_slots()
                    })
                    
            except Exception as e:
                logger.error(f"Error processing reschedule request: {str(e)}")
                messages.error(request, 'Error processing your reschedule request. Please try again.')
                return render(request, 'appointments/reschedule_appointment.html', {
                    'appointment': appointment,
                    'available_slots': generate_available_slots()
                })
        
        # GET request - show rescheduling form
        try:
            available_slots = generate_available_slots()
        except Exception as e:
            logger.warning(f"Error generating slots: {str(e)}")
            available_slots = []
        
        return render(request, 'appointments/reschedule_appointment.html', {
            'appointment': appointment,
            'available_slots': available_slots
        })
        
    except Exception as e:
        logger.exception(f"Error in reschedule_appointment for appointment_id {appointment_id}: {str(e)}")
        messages.error(request, 'Appointment not found or an error occurred.')
        return redirect('appointments:my_appointments')

@login_required
def cancel_appointment(request, appointment_id):
    """Handle appointment cancellation"""
    try:
        if request.method == 'POST':
            try:
                appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
                
                # Validate appointment can be cancelled
                if appointment.status == 'cancelled':
                    return JsonResponse({'success': False, 'error': 'Appointment is already cancelled.'})
                if appointment.status == 'completed':
                    return JsonResponse({'success': False, 'error': 'Cannot cancel a completed appointment.'})
                
                # Update appointment status
                appointment.status = 'cancelled'
                appointment.save()
                
                logger.info(f"Appointment {appointment_id} cancelled by user {request.user.id}")
                messages.success(request, 'Appointment cancelled successfully.')
                return JsonResponse({'success': True})
                
            except Exception as e:
                logger.error(f"Error cancelling appointment: {str(e)}")
                return JsonResponse({'success': False, 'error': 'Error cancelling appointment.'}, status=500)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
            
    except Exception as e:
        logger.exception(f"Error in cancel_appointment for appointment_id {appointment_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An error occurred.'}, status=500)


# ==================== DOCTOR AVAILABILITY VIEWS ====================

@login_required
@doctor_required
@login_required
@doctor_required
def manage_availability(request):
    """Doctor view to manage their weekly availability"""
    try:
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
        try:
            for slot in availability:
                availability_by_day[slot.day_of_week].append(slot)
        except Exception as e:
            logger.error(f"Error grouping availability slots: {str(e)}")
        
        context = {
            'days': days,
            'availability_by_day': availability_by_day,
        }
        return render(request, 'appointments/manage_availability.html', context)
        
    except Exception as e:
        logger.exception(f"Error in manage_availability view for doctor {request.user.id}: {str(e)}")
        messages.error(request, 'Error loading availability management. Please try again.')
        return redirect('dashboard')


@login_required
@doctor_required
def add_availability(request):
    """Add a new availability slot"""
    try:
        if request.method == 'POST':
            try:
                day_of_week = request.POST.get('day_of_week')
                start_time = request.POST.get('start_time')
                end_time = request.POST.get('end_time')
                slot_duration = request.POST.get('slot_duration', 30)
                
                # Validate required fields
                if not all([day_of_week, start_time, end_time]):
                    messages.error(request, 'Please fill in all required fields.')
                    return redirect('appointments:manage_availability')
                
                # Validate day of week
                try:
                    day_of_week = int(day_of_week)
                    if day_of_week < 0 or day_of_week > 6:
                        messages.error(request, 'Invalid day of week.')
                        return redirect('appointments:manage_availability')
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid day of week format.')
                    return redirect('appointments:manage_availability')
                
                # Validate slot duration
                try:
                    slot_duration = int(slot_duration) if slot_duration else 30
                    if slot_duration < 5 or slot_duration > 480:  # 5 mins to 8 hours
                        slot_duration = 30
                except (ValueError, TypeError):
                    slot_duration = 30
                
                # Check for overlapping slots
                try:
                    existing = DoctorAvailability.objects.filter(
                        doctor=request.user,
                        day_of_week=day_of_week,
                        start_time__lt=end_time,
                        end_time__gt=start_time
                    ).exists()
                    
                    if existing:
                        messages.error(request, 'This time slot overlaps with an existing slot.')
                        return redirect('appointments:manage_availability')
                except Exception as e:
                    logger.error(f"Error checking slot overlap: {str(e)}")
                    messages.error(request, 'Error validating time slot. Please try again.')
                    return redirect('appointments:manage_availability')
                
                # Create the availability slot
                try:
                    DoctorAvailability.objects.create(
                        doctor=request.user,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time,
                        slot_duration=slot_duration
                    )
                    messages.success(request, 'Availability slot added successfully.')
                except Exception as e:
                    logger.error(f"Error creating availability slot: {str(e)}")
                    messages.error(request, 'Error creating availability slot. Please try again.')
                
                return redirect('appointments:manage_availability')
                
            except Exception as e:
                logger.exception(f"Error processing availability form: {str(e)}")
                messages.error(request, 'Error processing your request. Please try again.')
                return redirect('appointments:manage_availability')
        
        return redirect('appointments:manage_availability')
        
    except Exception as e:
        logger.exception(f"Error in add_availability view: {str(e)}")
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('appointments:manage_availability')


@login_required
@doctor_required
def delete_availability(request, slot_id):
    """Delete an availability slot"""
    try:
        slot = get_object_or_404(DoctorAvailability, id=slot_id, doctor=request.user)
        try:
            slot.delete()
            messages.success(request, 'Availability slot removed.')
        except Exception as e:
            logger.error(f"Error deleting availability slot {slot_id}: {str(e)}")
            messages.error(request, 'Error deleting availability slot. Please try again.')
    except Exception as e:
        logger.exception(f"Error in delete_availability view: {str(e)}")
        messages.error(request, 'Availability slot not found or error occurred.')
    
    return redirect('appointments:manage_availability')


@login_required
@doctor_required  
def toggle_availability(request, slot_id):
    """Toggle availability slot on/off"""
    try:
        slot = get_object_or_404(DoctorAvailability, id=slot_id, doctor=request.user)
        try:
            slot.is_available = not slot.is_available
            slot.save()
            return JsonResponse({'success': True, 'is_available': slot.is_available})
        except Exception as e:
            logger.error(f"Error toggling availability slot {slot_id}: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Error updating slot'}, status=500)
    except Exception as e:
        logger.exception(f"Error in toggle_availability view: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Slot not found'}, status=404)


def get_doctor_available_slots(request, doctor_id):
    """API to get available slots for a doctor on a specific date"""
    try:
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': 'Date required'}, status=400)
        
        # Validate and parse date
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid date format provided: {date_str}")
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Validate doctor exists
        try:
            doctor = get_object_or_404(CustomUser, id=doctor_id, user_type='doctor')
        except Exception as e:
            logger.warning(f"Doctor not found: {doctor_id}")
            return JsonResponse({'error': 'Doctor not found'}, status=404)
        
        day_of_week = selected_date.weekday()
        
        # Get doctor's availability for this day with error handling
        try:
            availability = DoctorAvailability.objects.filter(
                doctor=doctor,
                day_of_week=day_of_week,
                is_available=True
            )
        except Exception as e:
            logger.error(f"Error fetching availability for doctor {doctor_id}: {str(e)}")
            return JsonResponse({'slots': [], 'message': 'Error retrieving availability'}, status=500)
        
        if not availability.exists():
            return JsonResponse({'slots': [], 'message': 'Doctor not available on this day'})
        
        # Get existing appointments with error handling
        try:
            existing_appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date__date=selected_date,
                status__in=['pending', 'confirmed']
            ).values_list('appointment_date', flat=True)
            booked_times = [apt.time() for apt in existing_appointments]
        except Exception as e:
            logger.error(f"Error fetching appointments: {str(e)}")
            booked_times = []
        
        # Generate available slots
        slots = []
        try:
            for avail in availability:
                try:
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
                except Exception as e:
                    logger.error(f"Error generating slots for availability {avail.id}: {str(e)}")
                    continue
        except Exception as e:
            logger.exception(f"Error in slot generation loop: {str(e)}")
        
        return JsonResponse({'slots': slots})
        
    except Exception as e:
        logger.exception(f"Error in get_doctor_available_slots: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ==================== REVIEWS ====================

@login_required
@patient_required
def submit_review(request, appointment_id):
    """Submit a review for a completed appointment"""
    try:
        appointment = get_object_or_404(
            Appointment, 
            id=appointment_id, 
            patient=request.user,
            status='completed'
        )
        
        # Check if review already exists
        try:
            if hasattr(appointment, 'review'):
                messages.warning(request, 'You have already reviewed this appointment.')
                return redirect('appointments:my_appointments')
        except Exception as e:
            logger.warning(f"Error checking review status: {str(e)}")
        
        if request.method == 'POST':
            try:
                rating = request.POST.get('rating', '').strip()
                comment = request.POST.get('comment', '').strip()
                
                if not rating:
                    messages.error(request, 'Please select a rating.')
                    return render(request, 'appointments/submit_review.html', {
                        'appointment': appointment
                    })
                
                # Validate rating value
                try:
                    rating_int = int(rating)
                    if rating_int < 1 or rating_int > 5:
                        messages.error(request, 'Rating must be between 1 and 5.')
                        return render(request, 'appointments/submit_review.html', {
                            'appointment': appointment
                        })
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid rating value.')
                    return render(request, 'appointments/submit_review.html', {
                        'appointment': appointment
                    })
                
                # Create review
                try:
                    DoctorReview.objects.create(
                        appointment=appointment,
                        patient=request.user,
                        doctor=appointment.doctor,
                        rating=rating_int,
                        comment=comment
                    )
                    logger.info(f"Review created for appointment {appointment_id} by user {request.user.id}")
                    messages.success(request, 'Thank you for your review!')
                    return redirect('appointments:my_appointments')
                    
                except Exception as e:
                    logger.error(f"Error creating review: {str(e)}")
                    messages.error(request, 'Error submitting your review. Please try again.')
                    return render(request, 'appointments/submit_review.html', {
                        'appointment': appointment
                    })
                    
            except Exception as e:
                logger.exception(f"Error processing review submission: {str(e)}")
                messages.error(request, 'An error occurred while submitting your review. Please try again.')
                return render(request, 'appointments/submit_review.html', {
                    'appointment': appointment
                })
        
        return render(request, 'appointments/submit_review.html', {
            'appointment': appointment
        })
        
    except Exception as e:
        logger.exception(f"Error in submit_review for appointment_id {appointment_id}: {str(e)}")
        messages.error(request, 'Appointment not found or an error occurred.')
        return redirect('appointments:my_appointments')


def doctor_reviews(request, doctor_id):
    """View all reviews for a doctor"""
    try:
        doctor = get_object_or_404(DoctorProfile, user_id=doctor_id)
        
        try:
            reviews = DoctorReview.objects.filter(doctor=doctor.user).order_by('-created_at')
            # Calculate average rating safely
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        except Exception as e:
            logger.error(f"Error fetching reviews for doctor {doctor_id}: {str(e)}")
            reviews = []
            avg_rating = None
        
        return render(request, 'appointments/doctor_reviews.html', {
            'doctor': doctor,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'review_count': reviews.count() if reviews else 0
        })
        
    except Exception as e:
        logger.exception(f"Error in doctor_reviews view for doctor_id {doctor_id}: {str(e)}")
        messages.error(request, 'Doctor not found or an error occurred.')
        return redirect('appointments:doctor_list')