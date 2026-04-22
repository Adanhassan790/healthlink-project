# HealthLink Django Project - Railway Deployment Guide

## Overview
This guide will walk you through deploying the HealthLink Django project to Railway.app.

## Prerequisites
- GitHub/GitLab account with your project repository
- Railway.app account (free tier available)
- Project already pushed to a git repository

## Files Created for Deployment

The following files have been created to support Railway deployment:

1. **requirements.txt** - Python dependencies for the project
2. **Procfile** - Process types for Railway (web and release)
3. **Dockerfile** - Container configuration for building the application
4. **railway.json** - Railway-specific configuration
5. **.railwayignore** - Files to exclude from deployment

## Step-by-Step Deployment Guide

### Step 1: Prepare Your Git Repository

Make sure all the deployment files are committed and pushed to your repository:

```bash
git add requirements.txt Procfile Dockerfile railway.json .railwayignore
git commit -m "Add Railway deployment configuration"
git push origin main
```

### Step 2: Create a Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with your GitHub account
3. Click on "New Project"
4. Select "Deploy from GitHub"
5. Authorize Railway to access your GitHub repos
6. Select your `healthlink-project` repository

### Step 3: Configure Environment Variables

Railway will automatically detect your Dockerfile and build the service. Once the build completes, you need to configure environment variables:

1. In the Railway dashboard, go to your project
2. Click on the service (healthlink-web or similar)
3. Go to the "Variables" tab
4. Add the following environment variables:

```
ALLOWED_HOSTS=<your-railway-domain>.up.railway.app,localhost,127.0.0.1
DATABASE_URL=<automatically-set-by-railway-if-you-add-postgres>
DEBUG=False
SECRET_KEY=<generate-a-secure-secret-key>
CSRF_TRUSTED_ORIGINS=https://<your-railway-domain>.up.railway.app
```

### Step 4: Add PostgreSQL Database

Railway recommends PostgreSQL for production:

1. In your Railway project dashboard, click "+ Add Service"
2. Select "PostgreSQL" from the available services
3. Railway will automatically set the `DATABASE_URL` environment variable
4. The Django ORM will automatically use PostgreSQL via the `DATABASE_URL`

### Step 5: Deploy

Once you've configured all environment variables:

1. Go to the "Deployments" tab in your service
2. Click "Create Deployment" or push a new commit to trigger a new deployment
3. Railway will automatically:
   - Build the Docker image
   - Run the Procfile release command (`python manage.py migrate`)
   - Start the web service with gunicorn

### Step 6: Verify Deployment

1. Once the deployment shows "Success", click on the service
2. Go to the "Networking" tab to get your Railway domain URL
3. Visit your deployed application: `https://<your-railway-domain>.up.railway.app`
4. Check the deployment logs for any errors

## Environment Variables Reference

### Required Variables
- **SECRET_KEY** - Django secret key for security. Generate one [here](https://djecrety.ir/)
- **DEBUG** - Set to `False` for production
- **ALLOWED_HOSTS** - Comma-separated list of domains that can access your app

### Optional Variables
- **CORS_ALLOWED_ORIGINS** - Comma-separated list of allowed CORS origins
- **CSRF_TRUSTED_ORIGINS** - Comma-separated list of trusted origins for CSRF protection

### Automatically Set by Railway
- **DATABASE_URL** - Connection string for PostgreSQL (auto-generated when you add Postgres service)
- **RAILWAY_STATIC_URL** - Your Railway domain URL

## Troubleshooting

### 1. Build Fails
- Check the build logs in Railway dashboard
- Ensure all dependencies in `requirements.txt` are correct
- Verify `python` and `pip` are available in your Dockerfile

### 2. Migrations Fail
- The `release` command in Procfile runs `python manage.py migrate`
- Check the Procfile definition is correct
- Verify DATABASE_URL is properly set
- Check logs: Railway → Service → Logs → Deployment logs

### 3. Static Files Not Loading
- WhiteNoise is configured in settings.py to serve static files
- Make sure static files are collected: `collectstatic --noinput`
- Check STATIC_ROOT and STATIC_URL in settings.py

### 4. Database Connection Issues
- Ensure PostgreSQL service is added to the project
- Verify DATABASE_URL environment variable is set
- Check that your IP is not being blocked (Railway allows all IPs)

### 5. Port Issues
- Railway assigns port 8000 by default
- The Dockerfile exposes port 8000
- gunicorn is bound to `0.0.0.0:8000`
- If port 8000 is not available, modify the Dockerfile CMD

## Additional Configuration

### Custom Domain
1. In Railway dashboard, go to "Networking" for your service
2. Click "Generate Railway Domain" or "Add Custom Domain"
3. Follow the instructions to add your custom domain

### Environment-Specific Settings
The `settings.py` has been configured to:
- Use SQLite in development (when DEBUG=True)
- Use PostgreSQL in production (when DATABASE_URL is set)
- Restrict CORS origins in production
- Handle debugging safely

### Monitoring and Logs
- View live logs: Railway dashboard → Service → Logs
- Check deployment history: Railway dashboard → Service → Deployments
- Monitor resource usage: Railway dashboard → Service → Runtime

## Production Checklist

Before deploying to production, ensure:

- [ ] SECRET_KEY is generated and securely stored in Railway environment variables
- [ ] DEBUG is set to `False`
- [ ] ALLOWED_HOSTS includes your production domain
- [ ] PostgreSQL database is added to the project
- [ ] CORS_ALLOWED_ORIGINS is properly configured
- [ ] Static files are being served correctly
- [ ] Database migrations run successfully
- [ ] Email configuration is set up (if using email features)
- [ ] M-Pesa credentials are updated for production (currently in sandbox mode)
- [ ] All sensitive data is in environment variables, not in code

## Security Notes

1. **Keep SECRET_KEY secret** - Never commit it to version control
2. **Use environment variables** - All secrets should be in Railway's environment variable section
3. **Enable HTTPS** - Railway automatically provides HTTPS with Let's Encrypt
4. **Database security** - PostgreSQL is protected within Railway's private network
5. **Disable DEBUG** - This prevents sensitive information leakage in error pages

## Updating Your Application

To update your application after initial deployment:

1. Commit your changes to your git repository
2. Push to your main branch: `git push origin main`
3. Railway will automatically detect the changes and create a new deployment
4. If you modified database models, migrations will run automatically

## Scaling and Advanced Configuration

### Worker Scaling
In the Dockerfile, the `--workers` parameter for gunicorn is set to 4. Adjust based on:
- Available Memory: 128 MB per railway container
- Recommended: 1-2 workers per 512 MB RAM
- Adjust in Dockerfile: `--workers N`

### Environment Variables in Railway
Railway provides a GUI for managing variables without modifying code. All sensitive data should be stored there.

### See Also
- [Railway Documentation](https://docs.railway.app/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/)
- [Gunicorn Settings](https://docs.gunicorn.org/en/stable/settings.html)

## Support

For issues with:
- **Railway deployment**: Check [Railway docs](https://docs.railway.app/) or [Discord community](https://discord.gg/railway)
- **Django configuration**: See [Django documentation](https://docs.djangoproject.com/)
- **Project-specific issues**: Review deployment logs in Railway dashboard

## Next Steps

After successful deployment:

1. Set up a custom domain
2. Configure email service for notifications
3. Update M-Pesa credentials for production (currently sandbox)
4. Set up monitoring and alerts
5. Configure backup strategy for PostgreSQL database
