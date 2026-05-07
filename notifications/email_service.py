"""
Email service utilities for HealthLink.

Transactional email is sent through SendGrid when configured, with a Django
SMTP fallback for local development and tests. The public helpers can also queue
work on a background executor so request handlers do not wait on network calls.
"""
import logging
import socket
from concurrent.futures import ThreadPoolExecutor, Future
import threading

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)
_EMAIL_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix='healthlink-email')
_SENDGRID_API_URL = 'https://api.sendgrid.com/v3/mail/send'


def _default_from_email():
    return getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@healthlink.local')


def _email_provider():
    provider = getattr(settings, 'EMAIL_PROVIDER', 'django')
    return str(provider).strip().lower()


def _render_email_body(text_body=None, html_template=None, context=None):
    html_body = None
    if html_template:
        html_body = render_to_string(html_template, context or {})
        if text_body is None:
            text_body = strip_tags(html_body)
    return text_body or '', html_body


def _send_via_django(subject, recipients, text_body, html_body, from_email):
    msg = EmailMultiAlternatives(subject, text_body, from_email, recipients)
    if html_body:
        msg.attach_alternative(html_body, 'text/html')

    old_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(getattr(settings, 'EMAIL_SMTP_TIMEOUT', 10))
        msg.send(fail_silently=False)
    finally:
        socket.setdefaulttimeout(old_timeout)

    logger.info('Email sent via Django backend to %s subject=%s', recipients, subject)
    return True, None


def _send_via_sendgrid(subject, recipients, text_body, html_body, from_email):
    api_key = getattr(settings, 'SENDGRID_API_KEY', '')
    if not api_key:
        message = 'SENDGRID_API_KEY is missing; configure it in the runtime environment'
        logger.error(message)
        return False, message

    payload = {
        'personalizations': [{'to': [{'email': recipient} for recipient in recipients]}],
        'from': {'email': from_email},
        'subject': subject,
        'content': [],
    }

    if text_body:
        payload['content'].append({'type': 'text/plain', 'value': text_body})
    if html_body:
        payload['content'].append({'type': 'text/html', 'value': html_body})
    if not payload['content']:
        payload['content'].append({'type': 'text/plain', 'value': ''})

    response = requests.post(
        _SENDGRID_API_URL,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json=payload,
        timeout=getattr(settings, 'SENDGRID_TIMEOUT', 10),
    )

    if response.status_code not in (200, 201, 202):
        raise RuntimeError(f'SendGrid API error {response.status_code}: {response.text}')

    logger.info('Email sent via SendGrid to %s subject=%s', recipients, subject)
    return True, None


def _send_sync(subject, recipients, text_body, html_body, from_email):
    if _email_provider() == 'sendgrid':
        return _send_via_sendgrid(subject, recipients, text_body, html_body, from_email)
    return _send_via_django(subject, recipients, text_body, html_body, from_email)


def _queue_send(subject, recipients, text_body, html_body, from_email):
    try:
        try:
            future = _EMAIL_EXECUTOR.submit(
                _send_sync,
                subject,
                recipients,
                text_body,
                html_body,
                from_email,
            )
        except Exception as exc:
            # Fallback: in some server setups (pre-fork) the executor may be
            # unusable in the child process. Fall back to a daemon thread and
            # wrap the result in a Future so callers can use the same API.
            logger.warning('Email executor unavailable, falling back to thread: %s', exc)

            future = Future()

            def _run_and_set():
                try:
                    result = _send_sync(subject, recipients, text_body, html_body, from_email)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)

            t = threading.Thread(target=_run_and_set, daemon=True, name='healthlink-email-fallback')
            t.start()

        def _log_completion(done_future):
            try:
                success, error = done_future.result()
                if not success:
                    logger.warning('Async email failed for %s subject=%s: %s', recipients, subject, error)
            except Exception:
                logger.exception('Async email job crashed for %s subject=%s', recipients, subject)

        future.add_done_callback(_log_completion)
        return True, 'queued'
    except Exception as exc:
        logger.exception('Failed to queue async email to %s subject=%s: %s', recipients, subject, exc)
        return False, str(exc)


def send_email(subject, to_email, text_body=None, html_template=None, context=None, from_email=None, async_send=None):
    """Send an email.

    - `to_email` may be a single address string or list of addresses.
    - If `html_template` is provided, `context` will be used to render it.
    - When `async_send` is true, the send is queued on a background executor.
    """
    if isinstance(to_email, str):
        recipients = [to_email]
    else:
        recipients = list(to_email)

    from_email = from_email or _default_from_email()
    if async_send is None:
        async_send = getattr(settings, 'EMAIL_SEND_ASYNC', False)

    try:
        text_body, html_body = _render_email_body(text_body=text_body, html_template=html_template, context=context)
        if async_send:
            return _queue_send(subject, recipients, text_body, html_body, from_email)
        return _send_sync(subject, recipients, text_body, html_body, from_email)
    except socket.timeout:
        logger.warning('Email send timeout to %s subject=%s', recipients, subject)
        return False, 'Email send timeout (network issue)'
    except Exception as e:
        logger.exception('Failed to send email to %s: %s', recipients, e)
        return False, str(e)


# Convenience wrappers for common templates
def send_appointment_email(to_email, subject, template_html, context, async_send=None):
    return send_email(subject, to_email, html_template=template_html, context=context, async_send=async_send)


def send_message_email(to_email, subject, template_html, context, async_send=None):
    return send_email(subject, to_email, html_template=template_html, context=context, async_send=async_send)


def send_call_email(to_email, subject, template_html, context, async_send=None):
    return send_email(subject, to_email, html_template=template_html, context=context, async_send=async_send)
