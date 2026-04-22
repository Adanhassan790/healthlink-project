# Railway Deployment Debugging Guide

## Current Configuration

### Logging Setup
- **Location**: `healthlink/settings.py`
- **Handler**: Console output (viewable in Railway logs)
- **Log Level**: DEBUG for appointments, DEBUG info is captured
- **Loggers Configured**: 
  - `django` - INFO level
  - `django.request` - ERROR level  
  - `healthlink` - DEBUG level
  - `users` - DEBUG level
  - `appointments` - DEBUG level ✅ (newly added)
  - `triage` - DEBUG level

### Error Handlers
- **500 Error**: `healthlink.views.error_500` - Logs request path, method, and user
- **404 Error**: `healthlink.views.error_404` - Logs requested path
- **403 Error**: `healthlink.views.error_403` - Logs path and user

## How to Debug the Doctor 500 Error

### Step 1: Check Railway Logs in Real-Time
```bash
# View live logs
railway logs --tail 100

# Or via web dashboard
# Open Railway dashboard → Select project → View live logs
```

### Step 2: What to Look For

**Doctor Detail Error Debugging** (for `doctors/:1` issue):
```
[DEBUG] appointmentments.views - Doctor detail request for doctor_id: 1
[DEBUG] appointments.views - Found doctor: Dr. John Doe
[DEBUG] appointments.views - Reviews for doctor 1: count=5, avg_rating=4.5
[DEBUG] appointments.views - Successfully rendered doctor_detail.html for doctor_id 1
```

**If you see errors like:**
```
[WARNING] appointments.views - DoctorProfile not found for user_id 1
[ERROR] appointments.views - Template rendering error in doctor_detail...
[ERROR] appointments.views - Unexpected error in doctor_detail...
```

### Step 3: Doctor List Debugging

**Success logs:**
```
[DEBUG] appointments.views - Fetching all doctors
[DEBUG] appointments.views - Found 25 doctors in database
[DEBUG] appointments.views - Final count: 25 doctors returned
```

**If there are issues:**
```
[DEBUG] appointments.views - Found 0 doctors in database
[WARNING] appointments.views - Invalid max_fee value: abc
[ERROR] appointments.views - Error in doctor_list view: ...
```

## Issue: DoctorProfile Not Found

If you see: `WARNING appointments.views - DoctorProfile not found for user_id 1`

**Cause**: User with ID 1 doesn't have a DoctorProfile

**Solution**:
1. Check database to verify doctor data exists:
```sql
-- Check if user exists
SELECT id, username, user_type FROM users_customuser WHERE id = 1;

-- Check if DoctorProfile exists
SELECT * FROM users_doctorprofile WHERE user_id = 1;
```

2. If DoctorProfile is missing but user exists, create one:
```python
# Django shell
python manage.py shell
from users.models import CustomUser, DoctorProfile
user = CustomUser.objects.get(id=1)
DoctorProfile.objects.create(
    user=user,
    license_number='LIC123456',
    specialization='General Practice',
    years_of_experience=5,
    consultation_fee=500
)
```

## Issue: Template Rendering Error

If you see: `ERROR appointments.views - Template rendering error in doctor_detail...`

**Causes**:
- Template file missing: `templates/appointments/doctor_detail.html`
- Template has syntax error
- Template tries to access undefined variable

**Solution**:
1. Check if template file exists
2. Check for syntax errors in template (unclosed tags, wrong variable names)
3. Look for AttributeError in logs - tells you which attribute doesn't exist

## Issue: CORS or Static Files

500 errors might also come from:
- Missing static files (CSS, JS)
- CORS configuration issues
- Database connection issues

**Check logs for**:
```
ERROR django.db - ...(database error)
WARNING django.security.csrf - ...
ERROR django.staticfiles - ...
```

## Step 4: Enable More Detailed Logging (if needed)

Edit `healthlink/settings.py` and change:
```python
'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),  # Change INFO to DEBUG
```

Then redeploy to Railway.

## Step 5: Monitor After Fix

After fixing the issue, monitor these logs:
1. Doctor list requests - ensure 200 status
2. Doctor detail requests - ensure rendering succeeds
3. No ERROR level logs for appointments

## Available Commands During Debugging

```bash
# View last 100 lines
railway logs --tail 100

# View last 500 lines  
railway logs --tail 500

# Stream live logs
railway logs -f

# Save logs to file for analysis
railway logs --tail 1000 > logs.txt
```

## What the Enhanced Error Handling Provides

1. **Better Logging**: All doctor view actions logged with DEBUG info
2. **Specific Error Messages**: User sees helpful message, not generic 500
3. **Error Templates**: Custom 404, 403, 500 pages with useful info
4. **Request Tracking**: Each request logged with path, method, user
5. **Template Error Isolation**: Template errors separately caught and logged

## Common Solutions

| Problem | Solution |
|---------|----------|
| No doctors show in list | Check DoctorProfile count in database |
| Doctor detail 500 error | Check if DoctorProfile exists for user_id |
| Reviews not loading | Check DoctorReview data exists |
| Availability not showing | Check DoctorAvailability records |
| Booking fails | Check Specialty and Appointment creation |

## Testing Locally Before Deployment

```bash
# Start server
python manage.py runserver

# Test doctor list
curl http://localhost:8000/appointments/doctors/

# Test doctor detail (adjust ID)
curl http://localhost:8000/appointments/doctors/1/

# Check logs in console output
```

## Next Steps

1. Deploy updated code to Railway
2. Monitor logs in real-time for errors
3. Test doctor pages on Railway URL
4. Verify all logs are being captured
5. Share any ERROR or WARNING logs if issues persist
