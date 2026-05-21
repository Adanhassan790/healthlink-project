from django.core.management.base import BaseCommand
from django.conf import settings
import os


def _mask(val: str) -> str:
    if not val:
        return ''
    if len(val) <= 10:
        return val[:3] + '...' + val[-1:]
    return val[:6] + '...' + val[-4:]


class Command(BaseCommand):
    help = 'Check presence of BREVO_API_KEY and related email settings (masked output)'

    def handle(self, *args, **options):
        brevo = os.getenv('BREVO_API_KEY') or ''
        sendgrid = os.getenv('SENDGRID_API_KEY') or ''
        provider = getattr(settings, 'EMAIL_PROVIDER', None)
        async_send = getattr(settings, 'EMAIL_SEND_ASYNC', None)

        self.stdout.write('BREVO_API_KEY present: {}'.format(bool(brevo)))
        if brevo:
            self.stdout.write('BREVO_API_KEY (masked): {}'.format(_mask(brevo)))

        self.stdout.write('SENDGRID_API_KEY present: {}'.format(bool(sendgrid)))
        if sendgrid:
            self.stdout.write('SENDGRID_API_KEY (masked): {}'.format(_mask(sendgrid)))

        self.stdout.write('EMAIL_PROVIDER setting: {}'.format(provider))
        self.stdout.write('EMAIL_SEND_ASYNC setting: {}'.format(async_send))

        # Also show what the internal provider detection chooses
        try:
            from notifications.email_service import _email_provider
            detected = _email_provider()
            self.stdout.write('Detected provider via email_service: {}'.format(detected))
        except Exception as e:
            self.stdout.write('Failed to detect provider via email_service: {}'.format(e))
