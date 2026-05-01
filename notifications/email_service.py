"""
Email service utilities for HealthLink

Provides simple helpers to send transactional emails (appointment, message, call)
using Django's EmailMultiAlternatives. Respects `DEFAULT_FROM_EMAIL` from settings
and falls back to console backend when DEBUG=True and SMTP not configured.
"""
import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def _default_from_email():
    return getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@healthlink.local')


def send_email(subject, to_email, text_body=None, html_template=None, context=None, from_email=None):
    """Send an email. Returns (success: bool, error_or_response).

    - `to_email` may be a single address string or list of addresses.
    - If `html_template` is provided, `context` will be used to render it.
    """
    if isinstance(to_email, str):
        recipients = [to_email]
    else:
        recipients = list(to_email)

    from_email = from_email or _default_from_email()

    try:
        if html_template:
            html_body = render_to_string(html_template, context or {})
            text_body = text_body or render_to_string(html_template, context or {})
        else:
            html_body = None

        msg = EmailMultiAlternatives(subject, text_body or '', from_email, recipients)
        if html_body:
            msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        logger.info('Email sent to %s subject=%s', recipients, subject)
        return True, None
    except Exception as e:
        logger.exception('Failed to send email to %s: %s', recipients, e)
        return False, str(e)


# Convenience wrappers for common templates
def send_appointment_email(to_email, subject, template_html, context):
    return send_email(subject, to_email, html_template=template_html, context=context)


def send_message_email(to_email, subject, template_html, context):
    return send_email(subject, to_email, html_template=template_html, context=context)


def send_call_email(to_email, subject, template_html, context):
    return send_email(subject, to_email, html_template=template_html, context=context)
