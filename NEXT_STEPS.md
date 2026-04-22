# HealthLink - Next Steps: Railway Deployment

## ✅ Completed So Far

1. **✓ Local Development Setup**
   - Django app running at http://127.0.0.1:8000/
   - Environment variables configured in .env
   - M-Pesa sandbox credentials configured
   - All dependencies installed

2. **✓ Production Configuration**
   - Created Dockerfile for containerization
   - Created Procfile with web/release processes
   - Updated settings.py for production
   - Configured environment variable handling

3. **✓ Security & Documentation**
   - Moved all credentials to environment variables
   - Created .env.example template
   - Written 5 comprehensive deployment guides
   - All changes committed to GitHub

---

## 🚀 NEXT STEP: Deploy to Railway

### Step 1: Create Railway Account (If you don't have one)
- Go to: https://railway.app
- Sign up with GitHub (recommended)
- Authorize Railway to access your GitHub account

### Step 2: Create Railway Project
1. Login to railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub"**
4. Authorize Railway
5. Select **`healthlink-project`** repository
6. Click **"Deploy"**

Railway will automatically:
- Detect the Dockerfile
- Build the Docker image
- Deploy the application
- Assign you a unique domain (e.g., `yourapp.up.railway.app`)

### Step 3: Configure Environment Variables in Railway
1. Go to **Railway Dashboard → Your Project**
2. Click on the **service** (healthlink-web)
3. Go to **"Variables"** tab
4. Click **"Add Variable"** for each:

**REQUIRED:**
```
SECRET_KEY = 3at9nyy231kdk1zvfuh%zs3o74_2z@*mhzo#n6w5j5^7*&tk@a
DEBUG = False
ALLOWED_HOSTS = yourapp.up.railway.app,yourdomain.com
MPESA_ENVIRONMENT = sandbox
MPESA_CONSUMER_KEY = <from-daraja-api>
MPESA_CONSUMER_SECRET = <from-daraja-api>
MPESA_BUSINESS_SHORTCODE = 174379
MPESA_PASSKEY = <from-daraja-api>
MPESA_CALLBACK_URL = https://yourapp.up.railway.app/payments/mpesa/callback/
CSRF_TRUSTED_ORIGINS = https://yourapp.up.railway.app
CORS_ALLOWED_ORIGINS = https://your-frontend.com
```

### Step 4: Add PostgreSQL Database (Recommended)
1. In Railway dashboard, click **"+ Add Service"**
2. Select **"PostgreSQL"**
3. Railway will:
   - Create PostgreSQL database
   - Automatically set `DATABASE_URL` variable
   - Connect it to your service

### Step 5: Run Database Migrations
1. Go to **Railway Dashboard → Your Project**
2. Click on your **service**
3. Click **"Deploy"** or **"Redeploy"** button
4. Railway will run the `release` command from Procfile:
   ```
   python manage.py migrate
   ```

### Step 6: Verify Deployment
1. Check **"Logs"** tab for any errors
2. Visit your Railway domain: `https://yourapp.up.railway.app`
3. Check admin panel: `https://yourapp.up.railway.app/admin/`

---

## 📋 Quick Checklist for Railway Deployment

- [ ] Have Railway account created
- [ ] Repository pushed to GitHub (✓ Done)
- [ ] Have M-Pesa sandbox credentials ready
- [ ] SECRET_KEY ready (already generated)
- [ ] Domain name ready (optional, use Railway domain for now)
- [ ] Understand environment variables needed

---

## ⚠️ Important Reminders

1. **Never commit .env to GitHub** (it's in .gitignore ✓)
2. **Use Railway dashboard** to set sensitive variables
3. **Keep M-Pesa keys secret** - only in Railway
4. **Use HTTPS** for all production URLs
5. **Update MPESA_CALLBACK_URL** with your actual Railway domain

---

## 🤔 Do You Want To:

1. **Proceed with Railway Deployment?** - I'll help you through each step
2. **Need Help with M-Pesa Credentials?** - I'll guide you where to get them
3. **Setup Custom Domain?** - Instructions for pointing domain to Railway
4. **Review Documentation?** - Check RAILWAY_DEPLOYMENT.md or RAILWAY_CHECKLIST.md
5. **Something Else?** - Let me know!

---

## 📞 What You Need Before Deploying

### From M-Pesa Daraja Portal:
```
MPESA_CONSUMER_KEY = Your Business Consumer Key
MPESA_CONSUMER_SECRET = Your Business Consumer Secret
MPESA_PASSKEY = Your M-Pesa Passkey
MPESA_BUSINESS_SHORTCODE = Your Business Shortcode (174379 for sandbox)
```

**Get these from:** https://developer.safaricom.co.ke/

### From Railway:
```
Railway will automatically provide:
- Your unique domain (e.g., yourapp.up.railway.app)
- DATABASE_URL (when you add PostgreSQL)
```

---

## 🎯 Recommended Deployment Flow

```
1. Railway Account Created
   ↓
2. New Project from GitHub
   ↓
3. Set Environment Variables
   ↓
4. Add PostgreSQL Database
   ↓
5. Verify Deployment
   ↓
6. Test Application
   ↓
7. Configure Custom Domain (Optional)
   ↓
8. Monitor Logs & Performance
```

---

## 💡 Tips

- Start with **Railway's provided domain** (free, no DNS setup)
- Test in **sandbox mode first** (M-Pesa)
- Keep **logs open** during first deployment
- Make sure **all env variables** are set before deploying
- **Monitor the deployment** in Railway dashboard

---

**Ready to deploy?** Tell me which step you want to start with! 🚀
