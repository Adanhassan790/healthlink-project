"""
Management command to send appointment reminders.
Run periodically (e.g., via cron: */15 * * * * python manage.py send_appointment_reminders)
to send reminder emails 1 hour before appointments.

Usage:
    python manage.py send_appointment_reminders
    python manage.py send_appointment_reminders --lookback=120  # Check last 2 hours
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string

from appointments.models import Appointment
from notifications.email_service import send_email
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send appointment reminders 1 hour before appointments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lookback',
            type=int,
            default=60,
            help='Minutes to lookback for upcoming appointments (default: 60 = 1 hour)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails'
        )

    def handle(self, *args, **options):
        lookback_minutes = options['lookback']
        dry_run = options['dry_run']

        # Calculate time window: now + 1 hour (reminder window)
        now = timezone.now()
        reminder_window_start = now
        reminder_window_end = now + timedelta(minutes=60 + lookback_minutes)

        # Find confirmed appointments in the reminder window that haven't been reminded
        appointments = Appointment.objects.filter(
            status='confirmed',
            appointment_date__gte=reminder_window_start,
            appointment_date__lte=reminder_window_end,
        ).exclude(
            # Exclude if reminder already sent (would need a field on model)
            # For now, we'll just send every time, but could add sent_reminder_at field
        )

        if not appointments.exists():
            self.stdout.write(self.style.WARNING('No appointments found in reminder window'))
            return

        count = 0
        for appointment in appointments:
            try:
                patient = appointment.patient
                doctor = appointment.doctor

                context = {
                    'appointment': appointment,
                    'patient': patient,
                    'doctor': doctor,
                }

                # Send reminder to patient
                subject = f"Appointment reminder: {appointment.appointment_date:%d/%m/%Y %I:%M %p}"
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f'[DRY RUN] Would send to {patient.email}: {subject}')
                    )
                else:
                    success, error = send_email(
                        subject=subject,
                        to_email=patient.email,
                        html_template='emails/appointment_reminder.html',
                        context=context
                    )
                    if success:
                        count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Reminder sent to {patient.email}')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to send to {patient.email}: {error}')
                        )

                # Optionally send to doctor too
                if not dry_run:
                    send_email(
                        subject=f"Appointment reminder: {appointment.appointment_date:%d/%m/%Y %I:%M %p}",
                        to_email=doctor.email,
                        html_template='emails/appointment_reminder_doctor.html',
                        context=context
                    )

            except Exception as e:
                logger.exception(f'Error sending reminder for appointment {appointment.id}: {e}')
                self.stdout.write(
                    self.style.ERROR(f'Error: {e}')
                )

        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] Would have sent {count} reminders'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent {count} appointment reminders')
            )
