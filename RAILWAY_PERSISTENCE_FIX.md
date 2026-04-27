# User Data Loss on Railway - Root Cause & Solution

## Problem
After every deployment on Railway, old user credentials don't work because the database is being deleted.

## Root Cause
**DATABASE_URL is not being set in Railway environment variables**, so Django falls back to SQLite. Railway uses ephemeral storage, which means:
1. Container filesystem is deleted on each deployment
2. SQLite database file (`db.sqlite3`) is stored in ephemeral storage
3. **All data is lost during deployment**

## Solution

### Step 1: Set up PostgreSQL on Railway
Railway provides PostgreSQL as a plugin:

1. Go to your Railway project dashboard
2. Click "Create New" → "Database" → "PostgreSQL"
3. This creates a PostgreSQL instance and **automatically sets DATABASE_URL**

### Step 2: Verify DATABASE_URL is Set
In Railway dashboard:
1. Go to your **project settings**
2. Click **"Variables"**
3. Look for `DATABASE_URL` - it should look like:
   ```
   postgresql://user:password@host:5432/dbname
   ```

### Step 3: Deploy & Migrate
After Railway auto-configures PostgreSQL:
```bash
git push origin main
# Railway will redeploy and run migrations against PostgreSQL
```

### Step 4: Verify It's Working
- Create a new user after deployment
- Try logging in after another deployment
- **Old users should still exist!**

## How to Check Which Database You're Using

Run this on production:
```python
from django.conf import settings
print(settings.DATABASES['default']['ENGINE'])
# Should print: django.db.backends.postgresql
# NOT: django.db.backends.sqlite3
```

## Testing Locally (Before Deploying)
To test with PostgreSQL locally:
```bash
# Set DATABASE_URL locally
export DATABASE_URL="postgresql://postgres:password@localhost:5432/healthlink"
python manage.py migrate
python manage.py runserver
```

## Why Migrations Work But Users Don't
- Migrations run successfully because they're part of the startup sequence
- But the database connection resets each deployment
- **With SQLite**: New empty database each time
- **With PostgreSQL**: Same persistent database each time

## Key Difference
| Aspect | SQLite | PostgreSQL on Railway |
|--------|--------|----------------------|
| Storage | Local filesystem | Railway-managed persistent DB |
| Survives deployment | ❌ No | ✅ Yes |
| Multi-instance | ❌ No | ✅ Yes |
| Recommended for | Development only | Production |

## Next Steps
1. Go to Railway dashboard
2. Add PostgreSQL plugin
3. Redeploy
4. Test with old user credentials - they should work now!

---
**This is a common issue with Railway + Django. PostgreSQL should be configured for production.**
