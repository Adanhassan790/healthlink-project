from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from appointments.models import Specialty, Appointment
from notifications.email_service import send_email

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users and appointment to trigger notification emails (patient + doctor).'

    def handle(self, *args, **options):
        try:
            # Create or get patient
            patient, created_p = User.objects.get_or_create(
                username='test_patient',
                defaults={
                    'email': 'patient@example.com',
                }
            )
            if created_p:
                patient.set_password('testpass123')
                patient.save()
                self.stdout.write(self.style.SUCCESS('Created test patient'))
            else:
                self.stdout.write('Using existing test patient')

            # Create or get doctor
            doctor, created_d = User.objects.get_or_create(
                username='test_doctor',
                defaults={
                    'email': 'doctor@example.com',
                    'user_type': 'doctor'
                }
            )
            if created_d:
                doctor.set_password('testpass123')
                doctor.save()
                self.stdout.write(self.style.SUCCESS('Created test doctor'))
            else:
                self.stdout.write('Using existing test doctor')

            # Ensure specialty exists
            spec, _ = Specialty.objects.get_or_create(name='Testing', defaults={'description': 'Auto-created for tests'})

            # Create appointment (this should trigger signals that send two emails)
            appt = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                specialty=spec,
                appointment_date=timezone.now() + timezone.timedelta(days=1),
                symptoms='Notification test',
                status='pending'
            )

            self.stdout.write(self.style.SUCCESS(f'Created appointment id={appt.id}'))

            # Direct single test email
            self.stdout.write('Sending direct test email to patient@example.com...')
            success, error = send_email('HealthLink Test', 'patient@example.com', text_body='This is a test email from HealthLink')
            self.stdout.write(f'send_email returned: success={success}, error={error}')

            self.stdout.write(self.style.SUCCESS('Notification test completed. Check logs and inboxes (patient@example.com / doctor@example.com).'))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.stderr.write(self.style.ERROR(f'Error running notification test: {e}'))
