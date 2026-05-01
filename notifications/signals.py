from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

from appointments.models import Appointment
from messaging.models import Message, VideoCall, Conversation
from users.models import CustomUser

from .email_service import send_appointment_email, send_message_email, send_call_email

logger = logging.getLogger(__name__)


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
    try:
        patient = instance.patient
        doctor = instance.doctor
        context = {
            'appointment': instance,
            'patient': patient,
            'doctor': doctor,
        }

        if created:
            subject = f"Appointment requested with Dr. {doctor.get_full_name()}"
            send_appointment_email(patient.email, subject, 'emails/appointment_created.html', context)
            # Notify doctor
            subject_doc = f"New appointment request from {patient.get_full_name()}"
            send_appointment_email(doctor.email, subject_doc, 'emails/appointment_created_doctor.html', context)
        else:
            prev = getattr(instance, '_previous_status', None)
            if prev != instance.status:
                # Status changed
                if instance.status == 'confirmed':
                    subject = f"Your appointment on {instance.appointment_date:%d/%m/%Y %I:%M %p} is confirmed"
                    send_appointment_email(patient.email, subject, 'emails/appointment_confirmed.html', context)
                    send_appointment_email(doctor.email, f"Appointment confirmed with {patient.get_full_name()}", 'emails/appointment_confirmed_doctor.html', context)
                elif instance.status == 'cancelled':
                    subj = f"Appointment cancelled: {instance.appointment_date:%d/%m/%Y %I:%M %p}"
                    send_appointment_email(patient.email, subj, 'emails/appointment_cancelled.html', context)
                    send_appointment_email(doctor.email, subj, 'emails/appointment_cancelled_doctor.html', context)
    except Exception as e:
        logger.exception('Error sending appointment emails: %s', e)


@receiver(post_save, sender=Message)
def message_post_save(sender, instance, created, **kwargs):
    # Send email when a new message is created to the other participant
    if not created:
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
        send_message_email(recipient.email, subject, 'emails/new_message.html', context)
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
    try:
        caller = instance.caller
        receiver = instance.receiver
        context = {'call': instance, 'caller': caller, 'receiver': receiver}

        if created:
            # New call initiated -> notify receiver
            subject = f"Incoming video consultation from {caller.get_full_name()}"
            send_call_email(receiver.email, subject, 'emails/incoming_call.html', context)
        else:
            prev = getattr(instance, '_previous_status', None)
            if prev != instance.status:
                if instance.status == 'ongoing':
                    # Call answered
                    send_call_email(caller.email, f"Call answered by {receiver.get_full_name()}", 'emails/call_answered.html', context)
                    send_call_email(receiver.email, f"You answered a call from {caller.get_full_name()}", 'emails/call_answered.html', context)
                elif instance.status in ('ended', 'missed', 'declined'):
                    send_call_email(caller.email, f"Call {instance.status}", 'emails/call_ended.html', context)
                    send_call_email(receiver.email, f"Call {instance.status}", 'emails/call_ended.html', context)
    except Exception:
        logger.exception('Failed to send video call emails')
