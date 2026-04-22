# HealthLink - Required Environment Variables Checklist

Quick reference for environment variables needed to run HealthLink in development or production.

## Copy-Paste Setup

1. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Fill in these REQUIRED variables:**

```env
# Django Core
SECRET_KEY=<generate-at-https://djecrety.ir/>
DEBUG=False                          # For production
ALLOWED_HOSTS=localhost,127.0.0.1

# M-Pesa Payment Integration
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=<from-daraja-api>
MPESA_CONSUMER_SECRET=<from-daraja-api>
MPESA_BUSINESS_SHORTCODE=174379
MPESA_PASSKEY=<from-daraja-api>
MPESA_CALLBACK_URL=https://your-domain.com/payments/mpesa/callback/

# Security (Production)
CSRF_TRUSTED_ORIGINS=https://your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

---

## Complete Environment Variables Reference

### 🔴 REQUIRED Variables

| Variable | Purpose | Where to Get | Example |
|----------|---------|--------------|---------|
| **SECRET_KEY** | Django security | https://djecrety.ir/ | `abc123xyz...` |
| **DEBUG** | Development/Production mode | Set manually | `False` |
| **ALLOWED_HOSTS** | Allowed domains | Your domain | `example.com,app.example.com` |
| **MPESA_CONSUMER_KEY** | M-Pesa authentication | N/A Daraja API portal | `mWoFvuqkdkYE...` |
| **MPESA_CONSUMER_SECRET** | M-Pesa authentication | M-Pesa Daraja API portal | `X2MktkC0zFhNyrZPZ6E...` |
| **MPESA_BUSINESS_SHORTCODE** | M-Pesa account | M-Pesa Daraja API portal | `174379` |
| **MPESA_PASSKEY** | M-Pesa token generation | M-Pesa Daraja API portal | `bfb279f9aa9bd...` |
| **MPESA_ENVIRONMENT** | M-Pesa mode | Set manually | `sandbox` or `production` |
| **MPESA_CALLBACK_URL** | M-Pesa payment confirmation | Your domain | `https://example.com/payments/mpesa/callback/` |

### 🟡 OPTIONAL Variables (Production)

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| DATABASE_URL | PostgreSQL connection | SQLite (dev only) | `postgres://user:pass@host:5432/db` |
| CORS_ALLOWED_ORIGINS | Frontend cross-origin | localhost:3000 | `https://app.example.com` |
| CSRF_TRUSTED_ORIGINS | CSRF security | localhost:8000 | `https://example.com` |
| EMAIL_BACKEND | Email sending | Console (dev only) | `django.core.mail.backends.smtp.EmailBackend` |
| EMAIL_HOST | SMTP server | smtp.gmail.com | `smtp.gmail.com` |
| EMAIL_PORT | SMTP port | 587 | `587` |
| EMAIL_USE_TLS | SMTP encryption | True | `True` |
| EMAIL_HOST_USER | Email account | (empty) | `noreply@example.com` |
| EMAIL_HOST_PASSWORD | Email password | (empty) | `your-app-password` |

### 🟢 AUTO-SET by Railway

| Variable | Set By | Value |
|----------|--------|-------|
| DATABASE_URL | Railway PostgreSQL | Auto-generated |
| RAILWAY_STATIC_URL | Railway Platform | Your app domain |
| RAILWAY_ENVIRONMENT | Railway Platform | `production` |

---

## Step-by-Step Setup Guide

### Step 1: Local Development Setup

```bash
# Copy template
cp .env.example .env

# Edit and add only these:
SECRET_KEY=your-generated-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# For payments (sandbox mode):
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=<your-sandbox-key>
MPESA_CONSUMER_SECRET=<your-sandbox-secret>
MPESA_BUSINESS_SHORTCODE=174379
MPESA_PASSKEY=<your-sandbox-passkey>
MPESA_CALLBACK_URL=https://your-ngrok-domain.ngrok-free.dev/payments/mpesa/callback/
```

### Step 2: Railway Production Setup

1. Go to Railway dashboard
2. Select your project → service
3. Click "Variables" tab
4. Add each variable:

```
SECRET_KEY = <generate-at-djecrety.ir>
DEBUG = False
ALLOWED_HOSTS = yourapp.up.railway.app,yourdomain.com

MPESA_ENVIRONMENT = production        (change from sandbox)
MPESA_CONSUMER_KEY = <production-key>
MPESA_CONSUMER_SECRET = <production-secret>
MPESA_BUSINESS_SHORTCODE = <your-code>
MPESA_PASSKEY = <production-passkey>
MPESA_CALLBACK_URL = https://yourdomain.com/payments/mpesa/callback/

CSRF_TRUSTED_ORIGINS = https://yourdomain.com
CORS_ALLOWED_ORIGINS = https://your-frontend.com

# Optional (Railway auto-sets this if you add PostgreSQL):
DATABASE_URL = [auto-set by Railway PostgreSQL]
```

5. Click "Deploy" to apply

### Step 3: Verify Setup

```bash
# Check .env exists and is in .gitignore
ls -la .env
grep ".env" .gitignore  # Should show: .env

# Check settings.py reads variables correctly
python manage.py shell
>>> import os
>>> os.getenv('SECRET_KEY')  # Should return your key
```

---

## Where to Get Credentials

### 🔐 SECRET_KEY
- **Where:** https://djecrety.ir/
- **Steps:** Visit link → Generate → Copy → Paste in .env
- **Security:** Keep secret, change if exposed

### 💳 M-Pesa Credentials (Sandbox)
1. Visit: https://developer.safaricom.co.ke/
2. Sign up (free)
3. Create new app in sandbox
4. Copy:
   - Consumer Key → `MPESA_CONSUMER_KEY`
   - Consumer Secret → `MPESA_CONSUMER_SECRET`
   - Shortcode (provided) → `MPESA_BUSINESS_SHORTCODE` (174379 for sandbox)
   - Passkey (generated) → `MPESA_PASSKEY`

### 💳 M-Pesa Credentials (Production)
- Contact Safaricom M-Pesa for production credentials
- Requires registered business account
- Different from sandbox credentials

### 📧 Email SMTP Credentials
**Gmail:**
1. Go to account.google.com
2. Security → App passwords
3. Generate app password
4. Use as EMAIL_HOST_PASSWORD

**Other providers:** Refer to their SMTP documentation

---

## Environment Variable Best Practices

✅ **DO:**
- [ ] Generate unique SECRET_KEY for each environment
- [ ] Keep .env in .gitignore (already done)
- [ ] Use production M-Pesa credentials in production
- [ ] Use environment-specific values for each deployment
- [ ] Document where each credential comes from
- [ ] Rotate credentials periodically

❌ **DON'T:**
- [ ] Hardcode credentials in code
- [ ] Commit .env to version control
- [ ] Reuse same credentials across environments
- [ ] Share .env files in email/chat
- [ ] Use test credentials in production
- [ ] Leave default examples in production

---

## Troubleshooting

### ❌ "SECRET_KEY not set"
```bash
# Fix: Add to .env
SECRET_KEY=your-generated-key
```

### ❌ M-Pesa payments failing
```bash
# Check: Are credentials correct?
python manage.py shell

>>> from django.conf import settings
>>> print(settings.MPESA_CONSUMER_KEY)  # Should show your key
>>> print(settings.MPESA_ENVIRONMENT)   # Should be 'sandbox' or 'production'
```

### ❌ Email not sending
```bash
# Check: Is EMAIL_BACKEND set?
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_BACKEND)  # Should not be empty

# Test: Send test email
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
```

### ❌ CORS errors in browser
```bash
# Add frontend domain to CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

---

## Quick Commands

```bash
# Show all loaded environment variables
python -c "from dotenv import dotenv_values; import json; print(json.dumps(dotenv_values('.env'), indent=2))"

# Validate .env syntax
python -c "from dotenv import load_dotenv; load_dotenv(); print('✓ .env loaded successfully')"

# Check if variable is set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('SECRET_KEY', 'NOT SET'))"

# List all Django settings
python manage.py diffsettings --default=django.conf.global_settings
```

---

## Related Documentation

- Detailed guide: [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)
- Deployment guide: [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)
- Setup checklist: [RAILWAY_CHECKLIST.md](RAILWAY_CHECKLIST.md)
- Settings code: [healthlink/settings.py](healthlink/settings.py)

---

## Summary

| Environment | SECRET_KEY ⚠️ | DEBUG | DATABASE | M-Pesa Mode | HTTPS Required |
|-------------|————————————|——————|—————————|—————————————|————————————————|
| **Local Dev** | Generate | `True` | SQLite | `sandbox` | ❌ No |
| **Railway** | Generate | `False` | PostgreSQL | `production` | ✅ Yes |
| **Testing** | Generate | `False` | Postgres | `sandbox` | ❌ No |

**Remember:** Always use unique `SECRET_KEY` and change `DEBUG=False` in production! 🔒
