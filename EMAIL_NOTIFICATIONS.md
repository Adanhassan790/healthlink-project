# Email Notifications for HealthLink

This document covers the email notification system for appointments, messages, and video calls.

## Features

Email notifications are automatically sent for:

- **Appointments**: Created, confirmed, and cancelled
- **Messages**: New message in conversation
- **Video Calls**: Incoming call, answered, and ended
- **Appointment Reminders**: 1 hour before scheduled appointment

## Architecture

### Components

1. **Email Service** (`notifications/email_service.py`)
   - Core email sending utilities
   - HTML template rendering
   - Error handling and logging

2. **Signal Handlers** (`notifications/signals.py`)
   - Hooks into Django model signals
   - Automatically triggers email sending on model changes
   - Respects `SEND_EMAIL_NOTIFICATIONS` setting

3. **Templates** (`templates/emails/`)
   - HTML email templates for each event type
   - Context-aware rendering with appointment/user details

4. **Management Command** (`notifications/management/commands/send_appointment_reminders.py`)
   - Scheduled task to send appointment reminders
   - Runs periodically (e.g., via cron)

## Configuration

### Environment Variables

Add the relevant values to your `.env` file or Railway service variables:

```bash
# Email provider selection
EMAIL_PROVIDER=brevo

# Brevo
BREVO_API_KEY=xkeysib-your-brevo-api-key

# SendGrid (alternative provider)
SENDGRID_API_KEY=SG.your-sendgrid-api-key

# Shared settings
DEFAULT_FROM_EMAIL=qonqona@gmail.com
EMAIL_SEND_ASYNC=True
SEND_EMAIL_NOTIFICATIONS=True
SENDGRID_TIMEOUT=10
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

### Development Setup

For development, either use the **console backend** to print messages locally or keep Brevo enabled with a valid API key:

```bash
# .env
DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Emails will print to your Django development server console when the console backend is active.

### Production Setup

**Brevo**

Use Brevo's HTTPS API for transactional email:

```bash
EMAIL_PROVIDER=brevo
BREVO_API_KEY=xkeysib-your-brevo-api-key
DEFAULT_FROM_EMAIL=qonqona@gmail.com
EMAIL_SEND_ASYNC=True
SEND_EMAIL_NOTIFICATIONS=True
```

Brevo works without Gmail app passwords or 2-step verification. The sender email must be verified in Brevo.

**SendGrid**

Use SendGrid's HTTPS API as the alternative provider:

```bash
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@your-domain.com
EMAIL_SEND_ASYNC=True
SEND_EMAIL_NOTIFICATIONS=True
```

The app uses SendGrid's HTTPS API when `EMAIL_PROVIDER=sendgrid` and `SENDGRID_API_KEY` is set. That avoids SMTP reachability problems and keeps email work off the request thread when `EMAIL_SEND_ASYNC=True`.

**Fallback SMTP**

SMTP remains available for environments that explicitly rely on `EMAIL_BACKEND` and SMTP settings, but it is not the preferred path for Railway deployment.

## Automatic Notifications

These trigger automatically when events occur:

### Appointment Notifications

| Event | Recipients | Template |
|-------|-----------|----------|
| Appointment Created | Patient, Doctor | `appointment_created.html`, `appointment_created_doctor.html` |
| Appointment Confirmed | Patient, Doctor | `appointment_confirmed.html`, `appointment_confirmed_doctor.html` |
| Appointment Cancelled | Patient, Doctor | `appointment_cancelled.html`, `appointment_cancelled_doctor.html` |

### Message Notifications

| Event | Recipients | Template |
|-------|-----------|----------|
| New Message | Other participant in conversation | `new_message.html` |

### Video Call Notifications

| Event | Recipients | Template |
|-------|-----------|----------|
| Incoming Call | Call receiver | `incoming_call.html` |
| Call Answered | Both parties | `call_answered.html` |
| Call Ended | Both parties | `call_ended.html` |

## Appointment Reminders

Send reminder emails 1 hour before scheduled appointments.

### Running Manually

```bash
# Send reminders for appointments in next 1 hour
python manage.py send_appointment_reminders

# Dry run (show what would be sent without sending)
python manage.py send_appointment_reminders --dry-run

# Check wider window (last 2 hours)
python manage.py send_appointment_reminders --lookback=120
```

### End-to-End Notification Test

Use the dedicated management command to create test users, create an appointment, and send a direct test email:

```bash
python manage.py run_notification_test
```

This is the quickest way to verify appointment, doctor, and direct email delivery during local development or after a Railway deploy.

### Scheduling with Cron

Add to crontab to run every 15 minutes:

```bash
*/15 * * * * cd /path/to/healthlink && python manage.py send_appointment_reminders
```

### Scheduling with Celery (Optional)

If you add Celery to the project, create a periodic task:

```python
# Add to celery tasks
@periodic_task(run_every=crontab(minute='*/15'))
def send_appointment_reminders():
    from django.core.management import call_command
    call_command('send_appointment_reminders')
```

## Testing

### Run Unit Tests

```bash
python manage.py test notifications.test_email_notifications
```

Tests use the in-memory email backend and verify:
- Email sending functionality
- Signal handlers trigger correctly
- Correct recipients are notified
- Status changes are handled properly

### Manual Testing

1. Set `EMAIL_BACKEND` to console backend in `.env` if you want printed output
2. Restart Django development server
3. Run `python manage.py run_notification_test`
4. Check Django console output for email content or verify delivery in the provider dashboard

### Example Test Scenario

```bash
# In Django shell
python manage.py shell

# Create test users
from users.models import CustomUser
from appointments.models import Appointment, Specialty

patient = CustomUser.objects.create_user(username='patient', email='patient@test.com')
doctor = CustomUser.objects.create_user(username='doctor', email='doctor@test.com', user_type='doctor')
spec = Specialty.objects.create(name='General')

# Create appointment (should trigger emails)
from datetime import timedelta
from django.utils import timezone

appt = Appointment.objects.create(
    patient=patient,
    doctor=doctor,
    specialty=spec,
    appointment_date=timezone.now() + timedelta(days=1),
    symptoms='Test',
    status='pending'
)

# Check emails in console output
```

## Disabling Notifications

### Globally

Set in `.env`:
```bash
SEND_EMAIL_NOTIFICATIONS=False
```

### Per-Environment

The setting is automatically:
- **Enabled** in production (`DEBUG=False`)
- **Disabled** by default in development (uses console backend instead)

You can override by explicitly setting `SEND_EMAIL_NOTIFICATIONS`.

## Email Templates

Located in `templates/emails/`:

- `appointment_created.html` - Patient notified of new appointment
- `appointment_created_doctor.html` - Doctor notified of new appointment
- `appointment_confirmed.html` - Patient appointment confirmed
- `appointment_confirmed_doctor.html` - Doctor appointment confirmed
- `appointment_cancelled.html` - Patient appointment cancelled
- `appointment_cancelled_doctor.html` - Doctor appointment cancelled
- `appointment_reminder.html` - Patient 1-hour reminder
- `appointment_reminder_doctor.html` - Doctor 1-hour reminder
- `new_message.html` - New message in conversation
- `incoming_call.html` - Incoming video call
- `call_answered.html` - Call answered notification
- `call_ended.html` - Call ended with duration

### Customizing Templates

Edit templates in `templates/emails/` to customize email content, styling, and messaging.

Available context variables in templates:

| Variable | Type | Usage |
|----------|------|-------|
| `appointment` | Appointment | Appointment details, date, status |
| `patient` | CustomUser | Patient name, email |
| `doctor` | CustomUser | Doctor name, email |
| `message` | Message | Message content, timestamp |
| `conversation` | Conversation | Conversation between participants |
| `sender` | CustomUser | Message/call sender |
| `recipient` | CustomUser | Message/call recipient |
| `call` | VideoCall | Call details, duration, status |
| `caller` | CustomUser | Video call caller |
| `receiver` | CustomUser | Video call receiver |

## Troubleshooting

### Emails Not Sending

1. Check `EMAIL_BACKEND` in `.env` (should be SMTP for production)
2. Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` credentials
3. Check `DEFAULT_FROM_EMAIL` matches your sender email
4. Review Django logs for SMTP errors:
   ```bash
   tail -f logs/django.log | grep -i email
   ```

### Test Email Sending

```bash
# In Django shell
from django.core.mail import send_mail

send_mail(
    'Test Subject',
    'This is a test email body',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

### SMTP Authentication Errors

- **Gmail**: Make sure 2-step verification is enabled and use app-specific password
- **SendGrid**: Username must be `apikey` (lowercase), not your account email
- **AWS SES**: Verify sender email in SES console first

### Reminder Command Issues

```bash
# Check what reminders would be sent
python manage.py send_appointment_reminders --dry-run

# Increase lookback window if missing reminders
python manage.py send_appointment_reminders --lookback=180
```

## Security Notes

1. **Never commit** `.env` file with credentials (already in `.gitignore`)
2. **Use environment variables** for all sensitive data
3. **Rotate credentials** if exposed
4. **Use TLS/SSL** for SMTP connections (recommended)
5. **Verify sender email** in production email services
6. **Limit email rate** to avoid spam detection

## Future Enhancements

- [ ] Add email templates to admin interface for easy customization
- [ ] Implement email preference management (user opt-in/opt-out)
- [ ] Add attachment support (e.g., prescriptions, receipts)
- [ ] Implement email unsubscribe links
- [ ] Add email delivery tracking and bounce handling
- [ ] Support for SMS fallback if email unavailable
- [ ] Add personalization features (user preferences, notification frequency)
- [ ] Implement email queue/async sending with Celery
