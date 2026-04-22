# HealthLink Environment Variables Guide

Complete reference for all environment variables used in the HealthLink Django project.

## Overview

Environment variables allow you to configure the application without hardcoding sensitive data or environment-specific settings. This is essential for security and managing different configurations (development, staging, production).

**⚠️ IMPORTANT:** Never commit the `.env` file to version control. It's already in `.gitignore`.

## Quick Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your actual values in `.env`

3. Never commit `.env` to git:
   ```bash
   git status  # Should NOT show .env
   ```

---

## Essential Variables (Required)

These variables MUST be set before the application can run in production.

### Django Core Settings

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `SECRET_KEY` | String | ✅ YES | Django's secret key for security | `abc123xyz...` |
| `DEBUG` | Boolean | ✅ YES | Debug mode (True=dev, False=prod) | `False` |
| `ALLOWED_HOSTS` | String (CSV) | ✅ YES | Comma-separated allowed domains | `example.com,www.example.com` |

**Where to get SECRET_KEY:**
- Generate at https://djecrety.ir/ (free, no registration needed)
- Must be unique and kept secret
- Change when key is compromised

### Database

| Variable | Type | Required | Description | Example/Format |
|----------|------|----------|-------------|-----------------|
| `DATABASE_URL` | String | ❌ NO* | Database connection string | `postgres://user:pass@host:5432/db` |

*Only required in production. Defaults to SQLite in development.

**Format:** `postgres://username:password@hostname:port/database`

**Railway:** Automatically sets this when you add PostgreSQL service

### M-Pesa Payment Integration

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `MPESA_ENVIRONMENT` | String | ✅ YES | `sandbox` or `production` | `sandbox` |
| `MPESA_CONSUMER_KEY` | String | ✅ YES | Business Consumer Key | `mWoFvuqkdkYEPhUr...` |
| `MPESA_CONSUMER_SECRET` | String | ✅ YES | Business Consumer Secret | `X2MktkC0zFhNyrZP...` |
| `MPESA_BUSINESS_SHORTCODE` | String | ✅ YES | Business Shortcode or Till Number | `174379` |
| `MPESA_PASSKEY` | String | ✅ YES | M-Pesa Passkey | `bfb279f9aa9bdbcf...` |
| `MPESA_CALLBACK_URL` | String | ✅ YES | URL where M-Pesa sends confirmations | `https://example.com/payments/mpesa/callback/` |

**Where to get M-Pesa credentials:**

1. Go to https://developer.safaricom.co.ke/
2. Create a free account (Sandbox environment)
3. Create a new application in the portal
4. Copy the generated credentials

**Callback URL Requirements:**
- Must be publicly accessible (not localhost)
- For local development, use ngrok: https://your-id.ngrok-free.dev/payments/mpesa/callback/
- For production: https://yourdomain.com/payments/mpesa/callback/
- Must be HTTPS (required by M-Pesa)

---

## Optional Variables

These variables are optional and have sensible defaults.

### CORS & Security

| Variable | Type | Default | Description | Example |
|----------|------|---------|-------------|---------|
| `CORS_ALLOWED_ORIGINS` | String (CSV) | `http://localhost:3000,http://127.0.0.1:3000` | Allowed cross-origin domains | `https://app.example.com,https://mobile.example.com` |
| `CSRF_TRUSTED_ORIGINS` | String (CSV) | `http://localhost:8000,http://127.0.0.1:8000` | Trusted origins for CSRF | `https://example.com,https://www.example.com` |

**Note:** In production (DEBUG=False), CORS is more restrictive. Set these to whitelist your frontend domains.

### Email Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EMAIL_BACKEND` | String | `django.core.mail.backends.console.EmailBackend` | How to send emails |
| `EMAIL_HOST` | String | `smtp.gmail.com` | SMTP server hostname |
| `EMAIL_PORT` | Integer | `587` | SMTP server port |
| `EMAIL_USE_TLS` | Boolean | `True` | Use TLS encryption |
| `EMAIL_HOST_USER` | String | (empty) | Email account username |
| `EMAIL_HOST_PASSWORD` | String | (empty) | Email account password or app password |
| `DEFAULT_FROM_EMAIL` | String | `noreply@healthlink.com` | Default sender email |

**Email Setup Examples:**

**Gmail:**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
```

Note: Use [app-specific password](https://support.google.com/accounts/answer/185833), not your regular Gmail password.

**Sendgrid:**
```
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=SG.xxxxx
```

**Mailgun:**
```
EMAIL_BACKEND=anymail.backends.mailgun.EmailBackend
MAILGUN_API_KEY=key-xxx
MAILGUN_SENDER_DOMAIN=mail.example.com
```

### SMS Configuration (Optional)

| Variable | Type | Description |
|----------|------|-------------|
| `SMS_PROVIDER` | String | SMS provider name (e.g., `twilio`, `nexmo`) |
| `SMS_API_KEY` | String | API key from SMS provider |
| `SMS_API_SECRET` | String | API secret from SMS provider |

### AI/OpenAI Features (Optional)

| Variable | Type | Description |
|----------|------|-------------|
| `OPENAI_API_KEY` | String | OpenAI API key for triage system |

Get it at: https://platform.openai.com/api-keys

### Logging & Debugging

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DJANGO_LOG_LEVEL` | String | `INFO` | Django logging level |
| `DEBUG_TOOLBAR_ENABLED` | Boolean | `False` | Enable Django Debug Toolbar (dev only) |

---

## Railway-Specific Variables

These are automatically set by Railway and should NOT be manually set.

| Variable | Description |
|----------|-------------|
| `RAILWAY_STATIC_URL` | Your Railway domain (e.g., `myapp.up.railway.app`) |
| `RAILWAY_ENVIRONMENT` | `production` or `staging` |
| `DATABASE_URL` | Automatically set when PostgreSQL service is added |

---

## Environment Configuration Examples

### Development (Local)

```bash
# .env (development)
DEBUG=True
SECRET_KEY=development-key-not-secure-change-for-production
ALLOWED_HOSTS=localhost,127.0.0.1
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=sandbox-key
MPESA_CONSUMER_SECRET=sandbox-secret
MPESA_BUSINESS_SHORTCODE=174379
MPESA_PASSKEY=sandbox-passkey
MPESA_CALLBACK_URL=https://your-ngrok-id.ngrok-free.dev/payments/mpesa/callback/
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production (Railway)

```
# Set in Railway Dashboard → Variables

DEBUG=False
SECRET_KEY=your-generated-secure-key
ALLOWED_HOSTS=yourapp.up.railway.app,yourdomain.com
DATABASE_URL=postgres://user:password@host:5432/db  # Auto-set by Railway
MPESA_ENVIRONMENT=production
MPESA_CONSUMER_KEY=production-key
MPESA_CONSUMER_SECRET=production-secret
MPESA_BUSINESS_SHORTCODE=your-shortcode
MPESA_PASSKEY=production-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/payments/mpesa/callback/
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-app-password
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## Security Best Practices

1. **Never Commit .env**
   - `.env` is in `.gitignore` for a reason
   - Check with `git status` before committing

2. **Unique Secret Key**
   - Generate at https://djecrety.ir/
   - Change if ever exposed
   - Keep it secret!

3. **Use Strong Passwords**
   - For email/database credentials
   - Consider using password manager

4. **Rotate Credentials**
   - Change M-Pesa keys if compromised
   - Update email passwords periodically
   - Regenerate API keys regularly

5. **Environment-Specific Values**
   - Never use production credentials in development
   - Keep separate .env files for different environments
   - Use Railway Variables tab for production secrets

6. **HTTPS in Production**
   - Railway provides HTTPS automatically
   - Update CSRF_TRUSTED_ORIGINS with https:// URLs
   - M-Pesa requires HTTPS callbacks

---

## Troubleshooting

### "SECRET_KEY not set" Error
```
Solution: Set SECRET_KEY in .env
SECRET_KEY=your-generated-key
```

### M-Pesa Payments Failing
```
Solution: Check credentials and callback URL
1. Verify MPESA_ENVIRONMENT matches (sandbox vs production)
2. Check MPESA_CALLBACK_URL is publicly accessible
3. Ensure callback URL uses HTTPS
4. Verify credentials are correct in M-Pesa portal
```

### Email Not Sending
```
Solution: Configure EMAIL_BACKEND and SMTP
1. Check EMAIL_BACKEND is correctly set
2. Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
3. For Gmail, use app-specific password, not regular password
4. Check firewall/network allows outbound SMTP
```

### CORS Errors in Frontend
```
Solution: Add frontend domain to CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS=https://frontend.example.com,https://app.example.com
```

---

## .env File Template

Use `.env.example` as a template. Copy and fill in your values:

```bash
cp .env.example .env
# Edit .env with your values
echo ".env" >> .gitignore  # Ensure it's ignored (already done)
```

---

## Railway Dashboard Configuration

1. Go to Railway.app dashboard
2. Select your project
3. Click on your service
4. Go to "Variables" tab
5. Add variables using the "Add Variable" button
6. Click "Deploy" to apply changes

Rail way automatically redeploys when variables change.

---

## See Also

- [Django Environment Settings](https://12factor.net/config)
- [M-Pesa Developer Portal](https://developer.safaricom.co.ke/)
- [Railway Documentation](https://docs.railway.app/)
- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)

---

## Tips & Tricks

### Testing Different Environments
```bash
# Run with production settings
DEBUG=False python manage.py runserver

# Run with different database
DATABASE_URL=sqlite:///test.db python manage.py runserver
```

### Viewing Current Values
```bash
# Don't print secrets!
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('DEBUG:', os.getenv('DEBUG'))"
```

### Validating .env Format
```bash
# Check for syntax errors
python -c "from dotenv import load_dotenv; load_dotenv()"
```
