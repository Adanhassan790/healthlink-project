# HealthLink - Credentials Migration to Environment Variables

## Summary of Changes

All hardcoded API credentials have been **removed** from the codebase and moved to environment variables. This improves security and follows the 12-factor app methodology.

---

## What Changed

### 1. ✅ settings.py Updated
**File:** `healthlink/settings.py`

**Before (UNSAFE - Hardcoded):**
```python
MPESA_CONSUMER_KEY = 'mWoFvuqkdkYEPhUr3e15qMv0axSOnZ4dRq8363nt8clYFWTZ'
MPESA_CONSUMER_SECRET = 'X2MktkC0zFhNyrZPZ6EWASPlhl3ZYbQHoE7MGerzJSmgtQhxFngJLD3XL09pFjsF'
MPESA_BUSINESS_SHORTCODE = '174379'
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
MPESA_CALLBACK_URL = 'https://untriumphantly-unlopped-kody.ngrok-free.dev/payments/mpesa/callback/'
```

**After (SAFE - Environment Variables):**
```python
MPESA_ENVIRONMENT = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', '')
MPESA_BUSINESS_SHORTCODE = os.getenv('MPESA_BUSINESS_SHORTCODE', '')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', '')
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL', 'http://localhost:8000/payments/mpesa/callback/')
```

### 2. ✅ .env.example Created
**File:** `.env.example`

- Template for all environment variables
- Comprehensive documentation for each variable
- Safe to commit to version control (no secrets)

### 3. ✅ .env in .gitignore
**File:** `.gitignore`

- Already includes `.env` pattern
- Ensures actual `.env` file is never committed
- Safe to store sensitive data

### 4. ✅ Complete Documentation
Created three documentation files:

| File | Purpose |
|------|---------|
| `ENVIRONMENT_VARIABLES.md` | Comprehensive guide to all env vars |
| `ENV_VARIABLES_QUICK_REFERENCE.md` | Quick lookup and checklist |
| This file | Migration guide and changes summary |

---

## List of Environment Variables

### Required for Operations

#### Django Core
```bash
SECRET_KEY                          # Django security key
DEBUG                               # Development/Production flag
ALLOWED_HOSTS                       # Comma-separated allowed domains
```

#### M-Pesa Payment Integration
```bash
MPESA_ENVIRONMENT                   # 'sandbox' or 'production'
MPESA_CONSUMER_KEY                  # Daraja API Consumer Key
MPESA_CONSUMER_SECRET               # Daraja API Consumer Secret
MPESA_BUSINESS_SHORTCODE            # M-Pesa Business Code
MPESA_PASSKEY                       # M-Pesa Passkey for tokens
MPESA_CALLBACK_URL                  # Payment confirmation webhook URL
```

#### Security (Production)
```bash
CSRF_TRUSTED_ORIGINS                # Trusted origins for CSRF (comma-separated)
CORS_ALLOWED_ORIGINS                # Allowed CORS origins (comma-separated)
```

#### Database (Production)
```bash
DATABASE_URL                        # PostgreSQL connection string
```

### Optional
```bash
EMAIL_BACKEND                       # Email sending backend
EMAIL_HOST                          # SMTP server address
EMAIL_PORT                          # SMTP port (usually 587)
EMAIL_USE_TLS                       # Use TLS encryption (True/False)
EMAIL_HOST_USER                     # Email account username
EMAIL_HOST_PASSWORD                 # Email account password/app-password
OPENAI_API_KEY                      # OpenAI API key for AI features
```

---

## How to Implement

### Step 1: Setup Local Development

```bash
# Copy the template
cp .env.example .env

# Edit .env and fill in values
nano .env          # or use your editor

# Verify it's in .gitignore
grep ".env" .gitignore
```

### Step 2: Fill in Required Variables

For development, at minimum:

```env
SECRET_KEY=generated-key-from-djecrety.ir
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your-sandbox-key
MPESA_CONSUMER_SECRET=your-sandbox-secret
MPESA_BUSINESS_SHORTCODE=174379
MPESA_PASSKEY=your-sandbox-passkey
MPESA_CALLBACK_URL=https://your-ngrok-domain.ngrok-free.dev/payments/mpesa/callback/
```

### Step 3: Test Local Application

```bash
# Run Django development server
python manage.py runserver

# Check if settings are loaded
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MPESA_CONSUMER_KEY)
# Should print your key (if set in .env)
```

### Step 4: Deploy to Railway

1. Remove old hardcoded credentials from settings.py ✅ (already done)
2. Commit changes:
   ```bash
   git add -A
   git commit -m "Move API credentials to environment variables"
   git push origin main
   ```

3. In Railway Dashboard → Service Variables → Add:
   ```
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   ALLOWED_HOSTS=yourapp.up.railway.app,yourdomain.com
   
   MPESA_ENVIRONMENT=production
   MPESA_CONSUMER_KEY=your-production-key
   MPESA_CONSUMER_SECRET=your-production-secret
   MPESA_BUSINESS_SHORTCODE=your-shortcode
   MPESA_PASSKEY=production-passkey
   MPESA_CALLBACK_URL=https://yourdomain.com/payments/mpesa/callback/
   
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com
   CORS_ALLOWED_ORIGINS=https://your-frontend.com
   ```

4. Deploy → Done! ✅

---

## Security Improvements

### Before (UNSAFE) 🔴
- Credentials hardcoded in `settings.py`
- Visible in version control history
- Same credentials across all environments
- Difficult to rotate or update

### After (SECURE) 🟢
- Credentials in `.env` (not committed)
- Never visible in version control
- Different credentials per environment
- Easy to rotate or update
- Follows industry best practices (12-factor app)

---

## Where to Get Credentials

### 🔐 SECRET_KEY
- **URL:** https://djecrety.ir/
- **Action:** Click "Generate" → Copy → Paste in .env
- **Cost:** Free, no signup required

### 💳 M-Pesa Sandbox (Testing)
1. Visit: https://developer.safaricom.co.ke/
2. Sign up (free account)
3. Create new application
4. Copy credentials:
   - Consumer Key → `MPESA_CONSUMER_KEY`
   - Consumer Secret → `MPESA_CONSUMER_SECRET`
   - Shortcode: `174379` (given)
   - Passkey: Generated → `MPESA_PASSKEY`

### 💳 M-Pesa Production (Live)
- Contact Safaricom M-Pesa team
- Requires business account registration
- Different credentials than sandbox
- Higher costs and transaction limits

### 📧 Email (Gmail)
1. Go to: https://myaccount.google.com/
2. Security tab → App passwords
3. Generate app-specific password
4. Use as `EMAIL_HOST_PASSWORD`

---

## Verification Checklist

- [ ] `settings.py` reads all credentials from environment variables ✅
- [ ] `.env` file is in `.gitignore` ✅
- [ ] `.env.example` has all required variable templates ✅
- [ ] Hardcoded credentials removed from codebase ✅
- [ ] Local `.env` file created with test values
- [ ] Application runs locally with environment variables
- [ ] No secrets visible in `git log`
- [ ] Railway variables configured in dashboard
- [ ] Production deployment successful

---

## Commands for Verification

```bash
# Check hardcoded secrets are removed
grep -r "174379\|bfb279f9aa9bdbcf" --include="*.py" healthlink/

# This should return NOTHING if credentials are fully migrated

# Check .env is properly ignored
git status | grep ".env"

# Should NOT show .env file

# Verify environment variables are loaded
python manage.py shell
>>> import os
>>> print(os.getenv('SECRET_KEY'))  # Should show key
>>> print(os.getenv('MPESA_CONSUMER_KEY'))  # Should show key

# Test Django settings
python manage.py diffsettings | grep MPESA

# Should show environment-based values, not hardcoded
```

---

## Troubleshooting

### Issue: Settings still shows old values
```
Solution: 
1. Stop Django development server (Ctrl+C)
2. Verify .env file exists in project root
3. Verify variables are spelled correctly
4. Restart Django: python manage.py runserver
```

### Issue: .env file not being loaded
```
Solution:
1. Check python-dotenv is installed: pip install python-dotenv
2. Verify import in settings.py: from dotenv import load_dotenv
3. Check load is called: load_dotenv()
4. Verify .env is in project root (same folder as manage.py)
```

### Issue: Empty credentials in settings
```
Solution:
1. Check variable name spelling exactly matches .env
2. Check no quotes around value in .env:
   ✅ CORRECT:    MPESA_CONSUMER_KEY=abc123
   ❌ WRONG:      MPESA_CONSUMER_KEY="abc123"
3. Reload: killall -9 python && python manage.py runserver
```

---

## Best Practices Going Forward

✅ **DO:**
- [ ] Always use environment variables for secrets
- [ ] Generate new SECRET_KEY for each deployment
- [ ] Use different credentials per environment
- [ ] Document where each credential comes from
- [ ] Delete old versions of credentials
- [ ] Use `.env.example` for templates only

❌ **DON'T:**
- [ ] Commit `.env` to git (ever!)
- [ ] Share `.env` content in messages/email
- [ ] Reuse credentials across projects
- [ ] Hardcode any credentials in code
- [ ] Leave default test values in production
- [ ] Store credentials in comments

---

## Related Files

- **For detailed information:** `ENVIRONMENT_VARIABLES.md`
- **For quick reference:** `ENV_VARIABLES_QUICK_REFERENCE.md`
- **For deployment:** `RAILWAY_DEPLOYMENT.md`
- **For checklist:** `RAILWAY_CHECKLIST.md`
- **Settings file:** `healthlink/settings.py`

---

## Summary

✅ **All credentials have been moved to environment variables**
✅ **settings.py updated to read from .env**
✅ **Comprehensive documentation provided**
✅ **Security best practices implemented**
✅ **Ready for production deployment**

Next step: Fill in `.env` file with your actual credentials and deploy! 🚀
