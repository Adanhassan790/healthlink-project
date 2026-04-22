# Railway Deployment Checklist

This checklist ensures your HealthLink project is properly configured for deployment to Railway.

## Pre-Deployment Checklist

### Code Preparation
- [ ] All changes are committed to git
- [ ] `.gitignore` includes `db.sqlite3`, `.env`, `.venv`, `__pycache__/`
- [ ] `requirements.txt` contains all project dependencies
- [ ] No hardcoded secrets in the codebase

### Configuration Files
- [ ] `Dockerfile` exists and is properly configured
- [ ] `Procfile` specifies the web and release processes
- [ ] `railway.json` is configured
- [ ] `.railwayignore` excludes unnecessary files
- [ ] `.env.example` provides template for environment variables

### Django Settings
- [ ] `DEBUG = os.getenv('DEBUG', 'False') == 'True'` (not hardcoded to True)
- [ ] `ALLOWED_HOSTS` includes your Railway domain
- [ ] Database configuration supports both SQLite and PostgreSQL via `DATABASE_URL`
- [ ] Static files configured with WhiteNoise middleware
- [ ] `STATIC_ROOT` is set to `BASE_DIR / 'staticfiles'`
- [ ] CORS and CSRF settings are environment-aware

### Database
- [ ] All database migrations are created and tested locally
- [ ] Models are reviewed for production readiness
- [ ] Indexes are created for frequently queried fields

### Security
- [ ] `SECRET_KEY` is generated and will be set as environment variable
- [ ] `DEBUG=False` is set for production
- [ ] HTTPS will be enforced (Railway provides this)
- [ ] Sensitive data (M-Pesa keys) are in `.env.example` with placeholder values
- [ ] `.env` file is in `.gitignore`

## Deployment Steps

### Step 1: Generate Secret Key
- [ ] Generate a secure SECRET_KEY at [djecrety.ir](https://djecrety.ir/)
- [ ] Save it securely (you'll need it in Step 4)

### Step 2: Push Code to Repository
```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

### Step 3: Create Railway Project
- [ ] Log in to [railway.app](https://railway.app)
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub"
- [ ] Choose your healthlink-project repository
- [ ] Railway will auto-detect and start building

### Step 4: Configure Environment Variables
Go to **Railway Dashboard → your-service → Variables** and add:

```
ALLOWED_HOSTS=<your-railway-domain>.up.railway.app,localhost
DEBUG=False
SECRET_KEY=<generated-secret-key>
CSRF_TRUSTED_ORIGINS=https://<your-railway-domain>.up.railway.app
MPESA_CALLBACK_URL=https://<your-railway-domain>.up.railway.app/payments/mpesa/callback/
```

### Step 5: Add PostgreSQL Database
- [ ] Click "+ Add Service" in Railway project
- [ ] Select PostgreSQL
- [ ] Railway automatically sets `DATABASE_URL` environment variable
- [ ] Trigger a redeploy to apply database changes

### Step 6: Monitor Deployment
- [ ] Watch the deployment progress in Railway Dashboard
- [ ] Check build logs for any errors
- [ ] Verify the `release` command (migrations) completes successfully
- [ ] Check application logs for runtime errors

### Step 7: Verify Application
- [ ] Visit your Railway domain URL
- [ ] Check that static files (CSS, JS) are loading
- [ ] Test authentication (login page should appear)
- [ ] Verify database operations work (e.g., create an account if possible)

## Post-Deployment Tasks

### Immediate
- [ ] Test all critical user flows
- [ ] Check email functionality (if applicable)
- [ ] Verify M-Pesa integration in sandbox mode
- [ ] Review application logs for errors

### Within 24 Hours
- [ ] Set up custom domain (if applicable)
- [ ] Configure domain SSL certificate (Railway auto-provisions)
- [ ] Test with mobile devices
- [ ] Review performance metrics

### Before Going Live
- [ ] Update M-Pesa to production credentials
- [ ] Configure email service
- [ ] Set up database backups
- [ ] Create admin user account
- [ ] Document deployment procedures for team
- [ ] Create rollback plan

## Troubleshooting Guide

### Build Fails
```
Solution: Check Railway build logs
- Ensure requirements.txt is complete
- Verify Dockerfile syntax
- Check for missing dependencies
```

### Migrations Fail
```
Solution: Check deployment logs for migration errors
- Ensure all models are properly defined
- Check for circular imports
- Verify DATABASE_URL is set correctly
```

### Static Files Not Loading
```
Solution: Verify static file configuration
- Ensure WhiteNoise middleware is installed and in MIDDLEWARE
- Check STATIC_ROOT and STATIC_URL settings
- Verify Dockerfile runs collectstatic
```

### Database Connection Issues
```
Solution: Verify database configuration
- Confirm DATABASE_URL environment variable is set
- Check PostgreSQL service is added to project
- Verify connection string format: postgres://user:pass@host:port/db
```

## Environment Variables Reference

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `SECRET_KEY` | Yes | None | Generate at djecrety.ir |
| `DEBUG` | Yes | False | Always False in production |
| `ALLOWED_HOSTS` | Yes | localhost | Include your Railway domain |
| `DATABASE_URL` | No* | None | Auto-set when PostgreSQL added |
| `CSRF_TRUSTED_ORIGINS` | Yes | Empty | Include your domain with https |
| `CORS_ALLOWED_ORIGINS` | No | Empty | Comma-separated list |
| `MPESA_CALLBACK_URL` | Optional | None | Your Railway domain URL |

*DATABASE_URL is automatically set by Railway when PostgreSQL service is added.

## Quick Links

- [Railway Documentation](https://docs.railway.app/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [Secret Key Generator](https://djecrety.ir/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

## Still Need Help?

1. Check the [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for detailed guide
2. Review Railway logs: Dashboard → Service → Logs
3. Check Django logs for application errors
4. Join Railway Discord community for support
