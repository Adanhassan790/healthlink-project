"""
Unit tests for email notification signals and email service.
Tests appointment, message, and video call notifications.
"""
from django.test import TestCase, override_settings
from django.core import mail
from django.utils import timezone
from datetime import timedelta

from users.models import CustomUser
from appointments.models import Appointment, Specialty
from messaging.models import Conversation, Message, VideoCall
from notifications.email_service import send_email


class EmailServiceTestCase(TestCase):
    """Test basic email sending functionality"""

    def test_send_email_basic(self):
        """Test sending a simple email"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            success, error = send_email(
                subject='Test Subject',
                to_email='recipient@example.com',
                text_body='This is a test email.'
            )
            self.assertTrue(success)
            self.assertIsNone(error)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'Test Subject')
            self.assertIn('recipient@example.com', mail.outbox[0].to)

    def test_send_email_html_template(self):
        """Test sending email with HTML template"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            success, error = send_email(
                subject='HTML Test',
                to_email='user@example.com',
                html_template='emails/new_message.html',
                context={'message': type('obj', (object,), {'content': 'Hello'})}
            )
            self.assertTrue(success)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'HTML Test')

    def test_send_email_multiple_recipients(self):
        """Test sending to multiple recipients"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            recipients = ['user1@example.com', 'user2@example.com']
            success, error = send_email(
                subject='Bulk Email',
                to_email=recipients,
                text_body='Message for all'
            )
            self.assertTrue(success)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(set(mail.outbox[0].to), set(recipients))




class AppointmentEmailSignalsTestCase(TestCase):
    """Test appointment creation and status change signals"""

    def setUp(self):
        """Create test users and specialty"""
        self.specialty = Specialty.objects.create(
            name='General',
            description='General Practice'
        )
        self.patient = CustomUser.objects.create_user(
            username='patient1',
            email='patient@example.com',
            password='testpass123'
        )
        self.doctor = CustomUser.objects.create_user(
            username='doctor1',
            email='doctor@example.com',
            password='testpass123',
            user_type='doctor'
        )

    def test_appointment_created_signal(self):
        """Test emails sent when appointment is created"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            appointment = Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                specialty=self.specialty,
                appointment_date=timezone.now() + timedelta(days=1),
                symptoms='Headache',
                status='pending'
            )

            # Should have 2 emails: patient + doctor
            self.assertEqual(len(mail.outbox), 2)
            subjects = {email.subject for email in mail.outbox}
            self.assertTrue(any('appointment' in s.lower() for s in subjects))

    def test_appointment_status_confirmed_signal(self):
        """Test emails sent when appointment is confirmed"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            appointment = Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                specialty=self.specialty,
                appointment_date=timezone.now() + timedelta(days=1),
                symptoms='Fever',
                status='pending'
            )
            mail.outbox.clear()

            # Change status to confirmed
            appointment.status = 'confirmed'
            appointment.save()

            # Should have 2 emails: patient + doctor
            self.assertEqual(len(mail.outbox), 2)
            subjects = {email.subject for email in mail.outbox}
            self.assertTrue(any('confirm' in s.lower() for s in subjects))

    def test_appointment_status_cancelled_signal(self):
        """Test emails sent when appointment is cancelled"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            appointment = Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                specialty=self.specialty,
                appointment_date=timezone.now() + timedelta(days=1),
                symptoms='Cough',
                status='confirmed'
            )
            mail.outbox.clear()

            # Cancel the appointment
            appointment.status = 'cancelled'
            appointment.save()

            # Should have 2 emails: patient + doctor
            self.assertEqual(len(mail.outbox), 2)
            subjects = {email.subject for email in mail.outbox}
            self.assertTrue(any('cancel' in s.lower() for s in subjects))


class MessageEmailSignalsTestCase(TestCase):
    """Test message creation signals"""

    def setUp(self):
        """Create test users and conversation"""
        self.patient = CustomUser.objects.create_user(
            username='patient1',
            email='patient@example.com',
            password='testpass123'
        )
        self.doctor = CustomUser.objects.create_user(
            username='doctor1',
            email='doctor@example.com',
            password='testpass123',
            user_type='doctor'
        )
        self.conversation = Conversation.objects.create(
            patient=self.patient,
            doctor=self.doctor
        )


class MessageEmailSignalsTestCase(TestCase):
    """Test message creation signals"""

    def setUp(self):
        """Create test users and conversation"""
        self.patient = CustomUser.objects.create_user(
            username='patient1',
            email='patient@example.com',
            password='testpass123'
        )
        self.doctor = CustomUser.objects.create_user(
            username='doctor1',
            email='doctor@example.com',
            password='testpass123',
            user_type='doctor'
        )
        self.conversation = Conversation.objects.create(
            patient=self.patient,
            doctor=self.doctor
        )

    def test_new_message_signal(self):
        """Test email sent when new message is created"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            message = Message.objects.create(
                conversation=self.conversation,
                sender=self.patient,
                content='Hello Doctor, I have a question.'
            )

            # Should have 1 email to the doctor
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn(self.doctor.email, mail.outbox[0].to)
            self.assertIn('message', mail.outbox[0].subject.lower())

    def test_message_from_doctor(self):
        """Test email sent when doctor sends message"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            message = Message.objects.create(
                conversation=self.conversation,
                sender=self.doctor,
                content='Hello Patient, here is my response.'
            )

            # Should have 1 email to the patient
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn(self.patient.email, mail.outbox[0].to)




class VideoCallEmailSignalsTestCase(TestCase):
    """Test video call creation and status change signals"""

    def setUp(self):
        """Create test users and conversation"""
        self.patient = CustomUser.objects.create_user(
            username='patient1',
            email='patient@example.com',
            password='testpass123'
        )
        self.doctor = CustomUser.objects.create_user(
            username='doctor1',
            email='doctor@example.com',
            password='testpass123',
            user_type='doctor'
        )
        self.conversation = Conversation.objects.create(
            patient=self.patient,
            doctor=self.doctor
        )

    def test_incoming_call_signal(self):
        """Test email sent when video call is initiated"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            call = VideoCall.objects.create(
                conversation=self.conversation,
                caller=self.patient,
                receiver=self.doctor,
                status='initiated'
            )

            # Should have 1 email to receiver (doctor)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn(self.doctor.email, mail.outbox[0].to)
            self.assertIn('consultation', mail.outbox[0].subject.lower())

    def test_call_status_ongoing_signal(self):
        """Test emails sent when call status changes to ongoing"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            call = VideoCall.objects.create(
                conversation=self.conversation,
                caller=self.patient,
                receiver=self.doctor,
                status='initiated'
            )
            mail.outbox.clear()

            # Change status to ongoing (answered)
            call.status = 'ongoing'
            call.save()

            # Should have 2 emails: caller + receiver
            self.assertEqual(len(mail.outbox), 2)
            emails_to = {email.to[0] for email in mail.outbox}
            self.assertIn(self.patient.email, emails_to)
            self.assertIn(self.doctor.email, emails_to)

    def test_call_status_ended_signal(self):
        """Test emails sent when call ends"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            call = VideoCall.objects.create(
                conversation=self.conversation,
                caller=self.patient,
                receiver=self.doctor,
                status='ongoing'
            )
            call.answered_at = timezone.now()
            call.save()
            mail.outbox.clear()

            # End the call
            call.status = 'ended'
            call.ended_at = timezone.now()
            call.duration = 300  # 5 minutes
            call.save()

            # Should have 2 emails: caller + receiver
            self.assertEqual(len(mail.outbox), 2)

    def test_call_status_missed_signal(self):
        """Test emails sent when call is missed"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            call = VideoCall.objects.create(
                conversation=self.conversation,
                caller=self.patient,
                receiver=self.doctor,
                status='initiated'
            )
            mail.outbox.clear()

            # Mark as missed
            call.status = 'missed'
            call.save()

            # Should have 2 emails
            self.assertEqual(len(mail.outbox), 2)

    def test_call_status_declined_signal(self):
        """Test emails sent when call is declined"""
        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_EMAIL_NOTIFICATIONS=True,
            DEFAULT_FROM_EMAIL='test@healthlink.local'
        ):
            call = VideoCall.objects.create(
                conversation=self.conversation,
                caller=self.patient,
                receiver=self.doctor,
                status='initiated'
            )
            mail.outbox.clear()

            # Mark as declined
            call.status = 'declined'
            call.save()

            # Should have 2 emails
            self.assertEqual(len(mail.outbox), 2)
