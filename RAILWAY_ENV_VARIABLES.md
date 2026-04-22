# HealthLink - Railway Environment Variables Checklist

Complete list of all environment variables needed to deploy HealthLink to Railway.

## 🚀 How to Add Variables in Railway

1. Go to **railway.app** dashboard
2. Select **healthlink-project**
3. Click on your **service** (healthlink-web or similar)
4. Go to **"Variables"** tab
5. Click **"Add Variable"** button
6. Enter the variable name and value
7. Click **"Deploy"** to apply changes

---

## 🔴 REQUIRED Variables (Must Set Before Deployment)

### Django Core Settings

```
SECRET_KEY = 3at9nyy231kdk1zvfuh%zs3o74_2z@*mhzo#n6w5j5^7*&tk@a
DEBUG = False
ALLOWED_HOSTS = yourapp.up.railway.app,yourdomain.com
```

**What Each Does:**
- `SECRET_KEY` - Django's security key (already generated for you)
- `DEBUG` - **Set to False for production** (security)
- `ALLOWED_HOSTS` - Your domain names (replace with your Railway domain)

---

## 🟡 M-PESA Variables (Sandbox - For Testing)

```
MPESA_ENVIRONMENT = sandbox
MPESA_CONSUMER_KEY = your-sandbox-consumer-key
MPESA_CONSUMER_SECRET = your-sandbox-consumer-secret
MPESA_BUSINESS_SHORTCODE = 174379
MPESA_PASSKEY = your-sandbox-passkey
MPESA_CALLBACK_URL = https://yourapp.up.railway.app/payments/mpesa/callback/
```

**Where to Get These:**
1. Visit: https://developer.safaricom.co.ke/
2. Create account (free)
3. Create new app in sandbox
4. Copy the credentials shown

**What Each Does:**
- `MPESA_ENVIRONMENT` - Set to "sandbox" for testing, "production" for live
- `MPESA_CONSUMER_KEY` - Your business API key from Daraja
- `MPESA_CONSUMER_SECRET` - Your API secret from Daraja
- `MPESA_BUSINESS_SHORTCODE` - For sandbox: always 174379
- `MPESA_PASSKEY` - Token generation key from Daraja portal
- `MPESA_CALLBACK_URL` - Where M-Pesa sends payment confirmations

---

## 🔵 Security Variables (Production)

```
CSRF_TRUSTED_ORIGINS = https://yourapp.up.railway.app,https://yourdomain.com
CORS_ALLOWED_ORIGINS = https://your-frontend-domain.com,https://yourdomain.com
```

**What Each Does:**
- `CSRF_TRUSTED_ORIGINS` - Domains that can make form submissions to your app
- `CORS_ALLOWED_ORIGINS` - Which frontend domains can call your API

---

## 🟢 Database (AUTO-SET BY RAILWAY)

When you add PostgreSQL service to Railway, this is automatically set:

```
DATABASE_URL = postgres://user:password@hostname:5432/database
```

**You don't need to set this manually - Railway creates it automatically!**

---

## 🟣 Optional Variables (Nice to Have)

```
# Email Configuration (Optional - for sending notifications)
EMAIL_BACKEND = django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST = smtp.gmail.com
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = your-email@gmail.com
EMAIL_HOST_PASSWORD = your-app-password

# AI Features (Optional - if using OpenAI)
OPENAI_API_KEY = sk-your-openai-api-key
```

---

## ✅ Quick Copy-Paste Setup

Copy and paste these into Railway Variables tab:

```
SECRET_KEY=3at9nyy231kdk1zvfuh%zs3o74_2z@*mhzo#n6w5j5^7*&tk@a
DEBUG=False
ALLOWED_HOSTS=yourapp.up.railway.app
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=<get-from-daraja>
MPESA_CONSUMER_SECRET=<get-from-daraja>
MPESA_BUSINESS_SHORTCODE=174379
MPESA_PASSKEY=<get-from-daraja>
MPESA_CALLBACK_URL=https://yourapp.up.railway.app/payments/mpesa/callback/
CSRF_TRUSTED_ORIGINS=https://yourapp.up.railway.app
CORS_ALLOWED_ORIGINS=https://yourapp.up.railway.app
```

---

## 🎯 Step-by-Step Setup Instructions

### Step 1: Get Your Railway Domain
1. Go to railway.app dashboard
2. Click your service
3. Look for "Networking" tab or service URL
4. You'll see something like: `healthlink-project-production.up.railway.app`
5. **Copy this domain** - you'll use it below

### Step 2: Get M-Pesa Sandbox Credentials
1. Visit: https://developer.safaricom.co.ke/
2. Click "Sign Up" → Create account
3. Go to applications → Create new app
4. In sandbox environment
5. You'll see:
   - Consumer Key
   - Consumer Secret
   - Passkey (generate if not shown)
6. **Copy all three values**

### Step 3: Add Variables to Railway
1. Login to railway.app
2. Go to your project
3. Click the web service
4. Go to "Variables" tab
5. **Add each variable:**

| Variable Name | Value |
|---------------|-------|
| SECRET_KEY | 3at9nyy231kdk1zvfuh%zs3o74_2z@*mhzo#n6w5j5^7*&tk@a |
| DEBUG | False |
| ALLOWED_HOSTS | yourapp.up.railway.app |
| MPESA_ENVIRONMENT | sandbox |
| MPESA_CONSUMER_KEY | (from Daraja) |
| MPESA_CONSUMER_SECRET | (from Daraja) |
| MPESA_BUSINESS_SHORTCODE | 174379 |
| MPESA_PASSKEY | (from Daraja) |
| MPESA_CALLBACK_URL | https://yourapp.up.railway.app/payments/mpesa/callback/ |
| CSRF_TRUSTED_ORIGINS | https://yourapp.up.railway.app |
| CORS_ALLOWED_ORIGINS | https://yourapp.up.railway.app |

### Step 4: Add PostgreSQL Database
1. In Railway dashboard
2. Click "+ Add Service"
3. Select "PostgreSQL"
4. Railway automatically adds `DATABASE_URL` variable
5. **Important:** This must be added before deploying!

### Step 5: Deploy
1. Click the "Deploy" button
2. Wait for build to complete
3. Check logs for any errors
4. Visit your URL when green ✅

---

## 📋 Pre-Deployment Checklist

Before clicking Deploy, verify you have:

- [ ] Railway account created
- [ ] Project created and connected to GitHub
- [ ] SECRET_KEY set (already provided)
- [ ] DEBUG set to False
- [ ] ALLOWED_HOSTS includes your Railway domain
- [ ] M-Pesa sandbox credentials obtained
- [ ] All 11 required variables added to Railway
- [ ] PostgreSQL service added
- [ ] DATABASE_URL automatically set (can verify in Variables)

---

## 🚀 Deployment Status

✅ **Dockerfile fixed** - Now uses Python 3.12
✅ **Requirements optimized** - Lightweight dependencies
✅ **Code pushed to GitHub** - Ready to build
⏳ **Waiting for:** Environment variables to be set in Railway

---

## ❓ Troubleshooting

### "SECRET_KEY not set" error
→ Add `SECRET_KEY` variable to Railway Variables tab

### M-Pesa not working
→ Check that all M-Pesa variables are correct
→ Verify MPESA_CALLBACK_URL has your actual Railway domain

### "No module found" errors
→ Check requirements.txt is correct (already fixed)
→ Check Python 3.12 is being used (already fixed)

### CORS errors from frontend
→ Add your frontend domain to `CORS_ALLOWED_ORIGINS`

### Build keeps failing
→ Check Railway logs for specific error
→ Make sure all required variables are set

---

## 🎯 What Happens After You Add Variables

1. **Click Deploy** in Railway
2. Railway detects code change (or you manually trigger)
3. Builds Docker image with Python 3.12
4. Installs dependencies from requirements.txt
5. Runs migrations from Procfile:
   ```
   python manage.py migrate
   ```
6. Starts gunicorn web server
7. Your app is live at `https://yourapp.up.railway.app`

---

## 📞 Support Resources

- **M-Pesa Daraja Portal:** https://developer.safaricom.co.ke/
- **Railway Docs:** https://docs.railway.app/
- **Django Docs:** https://docs.djangoproject.com/
- **HealthLink Environment Docs:** See ENVIRONMENT_VARIABLES.md

---

## 🎉 You're Almost There!

The hard part is done! Now just:

1. ✅ Fix deployed (Python 3.12)
2. ✅ Code pushed to GitHub
3. ⏳ Set environment variables in Railway
4. ⏳ Click Deploy
5. ✅ App live!

**Next action: Go to Railway and add the 11 variables listed above!** 🚀
