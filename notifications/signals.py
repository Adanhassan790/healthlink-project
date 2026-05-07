from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import sys

from appointments.models import Appointment
from messaging.models import Message, VideoCall, Conversation
from users.models import CustomUser

from .email_service import send_appointment_email, send_message_email, send_call_email

logger = logging.getLogger(__name__)


def should_send_email():
    """Check if email notifications are enabled"""
    return getattr(settings, 'SEND_EMAIL_NOTIFICATIONS', True)


def should_send_email_async():
    """Use async email delivery in production, but keep test runs synchronous."""
    if settings.DEBUG:
        return False

    return not any(arg == 'test' or arg.endswith(' test') or ' test ' in arg for arg in sys.argv)



@receiver(pre_save, sender=Appointment)
def appointment_pre_save(sender, instance, **kwargs):
    # Capture previous status for comparison in post_save
    if instance.pk:
        try:
            old = Appointment.objects.get(pk=instance.pk)
            instance._previous_status = old.status
        except Appointment.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Appointment)
def appointment_post_save(sender, instance, created, **kwargs):
    # Send emails on creation and status changes
    if not should_send_email():
        return
    
    # Don't block appointment creation with email sending - use try/except with fail_silently
    try:
        patient = instance.patient
        doctor = instance.doctor
        context = {
            'appointment': instance,
            'patient': patient,
            'doctor': doctor,
        }

        if created:
            try:
                subject = f"Appointment requested with Dr. {doctor.get_full_name()}"
                send_appointment_email(patient.email, subject, 'emails/appointment_created.html', context, async_send=should_send_email_async())
            except Exception as e:
                logger.warning('Failed to send patient appointment email: %s', e)
            
            try:
                # Notify doctor
                subject_doc = f"New appointment request from {patient.get_full_name()}"
                send_appointment_email(doctor.email, subject_doc, 'emails/appointment_created_doctor.html', context, async_send=should_send_email_async())
            except Exception as e:
                logger.warning('Failed to send doctor appointment email: %s', e)
        else:
            prev = getattr(instance, '_previous_status', None)
            if prev != instance.status:
                # Status changed
                if instance.status == 'confirmed':
                    try:
                        subject = f"Your appointment on {instance.appointment_date:%d/%m/%Y %I:%M %p} is confirmed"
                        send_appointment_email(patient.email, subject, 'emails/appointment_confirmed.html', context, async_send=should_send_email_async())
                    except Exception as e:
                        logger.warning('Failed to send patient confirmation email: %s', e)
                    
                    try:
                        send_appointment_email(doctor.email, f"Appointment confirmed with {patient.get_full_name()}", 'emails/appointment_confirmed_doctor.html', context, async_send=should_send_email_async())
                    except Exception as e:
                        logger.warning('Failed to send doctor confirmation email: %s', e)
                        
                elif instance.status == 'cancelled':
                    subj = f"Appointment cancelled: {instance.appointment_date:%d/%m/%Y %I:%M %p}"
                    try:
                        send_appointment_email(patient.email, subj, 'emails/appointment_cancelled.html', context, async_send=should_send_email_async())
                    except Exception as e:
                        logger.warning('Failed to send patient cancellation email: %s', e)
                    
                    try:
                        send_appointment_email(doctor.email, subj, 'emails/appointment_cancelled_doctor.html', context, async_send=should_send_email_async())
                    except Exception as e:
                        logger.warning('Failed to send doctor cancellation email: %s', e)
    except Exception as e:
        logger.exception('Unexpected error in appointment email signal: %s', e)


@receiver(post_save, sender=Message)
def message_post_save(sender, instance, created, **kwargs):
    # Send email when a new message is created to the other participant
    if not created or not should_send_email():
        return
    try:
        conv = instance.conversation
        # Determine recipient (other than sender)
        if conv.patient_id == instance.sender_id:
            recipient = conv.doctor
        else:
            recipient = conv.patient

        context = {
            'message': instance,
            'conversation': conv,
            'sender': instance.sender,
            'recipient': recipient,
        }
        subject = f"New message from {instance.sender.get_full_name()}"
        send_message_email(recipient.email, subject, 'emails/new_message.html', context, async_send=should_send_email_async())
    except Exception:
        logger.exception('Failed to send new message email')


@receiver(pre_save, sender=VideoCall)
def videocall_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = VideoCall.objects.get(pk=instance.pk)
            instance._previous_status = old.status
        except VideoCall.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=VideoCall)
def videocall_post_save(sender, instance, created, **kwargs):
    if not should_send_email():
        return
    
    try:
        caller = instance.caller
        receiver = instance.receiver
        context = {'call': instance, 'caller': caller, 'receiver': receiver}

        if created:
            # New call initiated -> notify receiver
            try:
                subject = f"Incoming video consultation from {caller.get_full_name()}"
                send_call_email(receiver.email, subject, 'emails/incoming_call.html', context, async_send=should_send_email_async())
            except Exception as e:
                logger.warning('Failed to send incoming call email: %s', e)
        else:
            prev = getattr(instance, '_previous_status', None)
            if prev != instance.status:
                if instance.status == 'ongoing':
                    # Call answered
                    try:
                        send_call_email(caller.email, f"Call answered by {receiver.get_full_name()}", 'emails/call_answered.html', context, async_send=should_send_email_async())
                    except Exception as e:
                        logger.warning('Failed to send call answered email to caller: %s', e)
                    
                    try:
                        send_call_email(receiver.email, f"You answered a call from {caller.get_full_name()}", 'emails/call_answered.html', context, async_send=should_send_email_async())
                    except Exception as e:
                        logger.warning('Failed to send call answered email to receiver: %s', e)
                        
                elif instance.status in ('ended', 'missed', 'declined'):
                    try:
                        send_call_email(caller.email, f"Call {instance.status}", 'emails/call_ended.html', context, async_send=should_send_email_async())
                    except Exception as e:
                        logger.warning('Failed to send call %s email to caller: %s', instance.status, e)
                    
                    try:
                        send_call_email(receiver.email, f"Call {instance.status}", 'emails/call_ended.html', context, async_send=should_send_email_async())
                    except Exception as e:
                        logger.warning('Failed to send call %s email to receiver: %s', instance.status, e)
    except Exception as e:
        logger.exception('Unexpected error in video call email signal: %s', e)
