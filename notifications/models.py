from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Model to store user notifications"""
    
    NOTIFICATION_TYPES = [
        ('appointment_booked', 'Appointment Booked'),
        ('appointment_confirmed', 'Appointment Confirmed'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('new_message', 'New Message'),
        ('prescription_created', 'Prescription Created'),
        ('payment_received', 'Payment Received'),
        ('video_call', 'Video Call'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True)  # Optional link to related page
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type}: {self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()


# Helper functions to create notifications easily
def create_notification(user, notification_type, title, message, link=None):
    """Helper function to create a notification"""
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )


def notify_appointment_booked(patient, doctor, appointment):
    """Notify both patient and doctor when an appointment is booked"""
    from django.urls import reverse
    
    # Notify patient
    create_notification(
        user=patient,
        notification_type='appointment_booked',
        title='Appointment Booked',
        message=f'Your appointment with Dr. {doctor.get_full_name()} has been booked for {appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p")}.',
        link=reverse('appointments:my_appointments')
    )
    
    # Notify doctor
    create_notification(
        user=doctor,
        notification_type='appointment_booked',
        title='New Appointment',
        message=f'New appointment with {patient.get_full_name()} on {appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p")}.',
        link=reverse('appointments:my_appointments')
    )


def notify_appointment_confirmed(patient, doctor, appointment):
    """Notify patient when appointment is confirmed"""
    from django.urls import reverse
    
    create_notification(
        user=patient,
        notification_type='appointment_confirmed',
        title='Appointment Confirmed',
        message=f'Your appointment with Dr. {doctor.get_full_name()} on {appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p")} has been confirmed.',
        link=reverse('appointments:my_appointments')
    )


def notify_new_message(sender, receiver, conversation):
    """Notify user of a new message"""
    from django.urls import reverse
    
    create_notification(
        user=receiver,
        notification_type='new_message',
        title='New Message',
        message=f'You have a new message from {sender.get_full_name()}.',
        link=reverse('messaging:conversation', kwargs={'conversation_id': conversation.id})
    )


def notify_prescription_created(patient, doctor, prescription):
    """Notify patient when a prescription is created"""
    from django.urls import reverse
    
    create_notification(
        user=patient,
        notification_type='prescription_created',
        title='New Prescription',
        message=f'Dr. {doctor.get_full_name()} has written a prescription for you.',
        link=reverse('prescriptions:my_prescriptions')
    )


def notify_payment_received(patient, appointment):
    """Notify about successful payment"""
    from django.urls import reverse
    
    create_notification(
        user=patient,
        notification_type='payment_received',
        title='Payment Received',
        message=f'Payment for your appointment has been received. Your appointment is now confirmed.',
        link=reverse('appointments:my_appointments')
    )
