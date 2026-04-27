# Vonage Video Call Integration - Deployment Guide

## 🎯 Summary

The HealthLink application has been successfully migrated from Jitsi to **Vonage Video API** (OpenTok). All code changes are complete and ready for deployment.

## ✅ What's Already Done

### Backend Integration (Complete)
- ✅ **vonage_service.py** - Session creation and token generation
- ✅ **models.py** - Added `vonage_session_id` field to VideoCall model
- ✅ **views.py** - Integrated Vonage session/token creation in conversation and video room views
- ✅ **messaging/urls.py** - All video call endpoints configured
- ✅ **requirements.txt** - Added `opentok==3.13.0` package

### Frontend Integration (Complete)
- ✅ **video_room.html** - Fully migrated to Vonage with:
  - OpenTok SDK integration
  - Session connection handling
  - Publisher initialization (local camera/mic)
  - Subscriber management (remote participant video)
  - Audio/video toggle controls
  - Call duration timer
  - Professional UI/UX

### Cleanup (Complete)
- ✅ Jitsi completely removed from codebase
- ✅ All references replaced with Vonage

---

## 🚀 Deployment Steps

### Step 1: Add Environment Variables to Railway

Your Railway project needs these environment variables (you've already added them):

```
VONAGE_API_KEY=your_actual_api_key_here
VONAGE_API_SECRET=your_actual_api_secret_here
```

**To verify they're set correctly:**
1. Go to Railway Dashboard → Your Project
2. Go to Settings → Environment
3. Confirm both variables are present

### Step 2: Push Code to GitHub

```bash
git add -A
git commit -m "Integrate Vonage video calls and remove Jitsi"
git push origin main
```

### Step 3: Railway Auto-Deployment

Railway will automatically:
1. Pull the latest code
2. Install dependencies (including opentok)
3. Run database migrations (if any)
4. Restart the application

Monitor the deployment in Railway Dashboard → Deployments

### Step 4: Test the Integration

#### From the Web UI:
1. Log in as a doctor and a patient (in separate browsers)
2. Start a conversation
3. Click "Start Video Call" button
4. Verify:
   - ✓ Your own video appears in the left panel
   - ✓ Other participant's video appears in the right panel
   - ✓ Audio/Video toggle buttons work
   - ✓ Call duration timer increments
   - ✓ "End Call" button ends the call properly

#### Using Test Script:
```bash
# Run the Vonage setup verification test
python test_vonage_setup.py
```

---

## 📋 Key Technical Details

### Vonage Session & Token Flow

```
1. Doctor initiates call
   ↓
2. Backend creates Vonage session (one per call)
   ↓
3. Backend generates token for doctor
   ↓
4. Doctor's browser connects to session with token
   ↓
5. Patient joins conversation
   ↓
6. Backend generates token for patient
   ↓
7. Patient's browser connects to session with token
   ↓
8. Both browsers can now see/hear each other
```

### Token Security
- Tokens are generated server-side with 24-hour expiration
- Each user gets a unique user_id in their token
- Tokens are not reusable after expiration
- Only doctor and patient in the conversation can access the call

### Data Storage
- **VideoCall.vonage_session_id** stores the Vonage session ID
- Used to retrieve the same session when both participants join
- Prevents session duplication

---

## 🔧 Troubleshooting

### Issue: "Vonage credentials not configured"

**Solution:** Check Railway environment variables
```bash
# In Railway Dashboard:
Settings → Environment → Verify VONAGE_API_KEY and VONAGE_API_SECRET are set
```

### Issue: Video shows but audio doesn't work

**Possible causes:**
1. Browser camera/microphone permissions not granted
2. User selected wrong device
3. Vonage token generation issue

**Solution:**
- Check browser console (F12) for permission errors
- Verify `get_api_key()` in vonage_service.py is working

### Issue: Connection fails

**Check:**
1. Railway logs for Vonage initialization errors
2. Network connectivity between participants
3. Vonage API credentials are correct
4. Opentok package is installed (`pip show opentok`)

---

## 📊 Vonage Features Implemented

### Call Controls
- 🔊 Audio toggle (mute/unmute)
- 📹 Video toggle (camera on/off)
- ⏱️ Call timer display
- 🔴 End call button

### Participant Management
- Maximum 2 participants (doctor + patient)
- Automatic cleanup on disconnect
- Session-based connection (not peer-to-peer)
- Server-managed session lifecycle

### Error Handling
- User-friendly error messages
- Automatic logging on backend
- Fallback UI when errors occur
- Graceful disconnection

---

## 📚 Code Structure

```
messaging/
├── vonage_service.py        # Vonage API integration
├── models.py                # VideoCall model with vonage_session_id
├── views.py                 # Video room & call management
├── urls.py                  # Video call routes
└── templates/
    └── messaging/
        └── video_room.html  # Vonage video UI

test_vonage_setup.py          # Verification script
```

---

## 🔒 Security Considerations

✅ **Implemented:**
- Server-side session creation (not exposed to client)
- Secure token generation with expiration
- User authentication required for all endpoints
- CSRF protection on all POST requests
- Authorization check (only conversation participants can join)

✅ **Already in code:**
- HTTPS enforced (via Railway HTTPS)
- Environment variables (never hardcoded)
- User-specific tokens per session

---

## 📞 Next Steps After Deployment

1. **Monitor logs** in Railway dashboard for any Vonage errors
2. **Test with multiple doctor-patient pairs** to ensure reliability
3. **Collect user feedback** on video quality and features
4. **Consider upgrades:**
   - Call recording (requires Vonage Archiving)
   - Screen sharing (requires Vonage Screen Sharing extension)
   - Group video (expand to 3+ participants)

---

## 📞 Support

For Vonage-related issues:
- **Vonage Docs:** https://tokbox.com/developer/
- **OpenTok Python SDK:** https://github.com/opentok/opentok-python
- **API Reference:** https://tokbox.com/developer/sdks/js/

For HealthLink-specific issues:
- Check Railway logs: `railway logs`
- Check Django logs for backend errors
- Check browser console (F12) for frontend errors

---

## Version Information

- **Vonage SDK:** OpenTok v2.20 (JavaScript)
- **opentok Python:** 3.13.0
- **Last Updated:** April 2026
