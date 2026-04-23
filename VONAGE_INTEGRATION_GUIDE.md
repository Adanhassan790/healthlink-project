# VONAGE VIDEO CALL INTEGRATION - SETUP INSTRUCTIONS

## What's Been Done

✅ **Created vonage_service.py** - Service module for session creation and token generation  
✅ **Updated requirements.txt** - Added `opentok==3.14.0` package  
✅ **Updated messaging/models.py** - Added `vonage_session_id` field to VideoCall model  
✅ **Updated messaging/views.py** - Integrated Vonage session/token creation  
✅ **Created migration** - Database migration for vonage_session_id field  
✅ **Committed to GitHub** - All changes pushed to repository  

## What Still Needs To Be Done

### 1. Set Vonage Environment Variables

Add these to your Railway project's environment variables:

```
VONAGE_API_KEY=your_api_key_here
VONAGE_API_SECRET=your_api_secret_here
```

To get credentials:
1. Go to https://tokbox.com/account/
2. Sign up or log in
3. Get your **API Key** and **API Secret** from the dashboard
4. Add them to Railway environment variables

### 2. Replace video_room.html Template

The current `templates/messaging/video_room.html` uses Jitsi. Replace it with Vonage version:

**Template location:** `templates/messaging/video_room.html`

**Include these scripts:**
```html
<!-- Vonage Video API SDK -->
<script src="https://static.opentok.com/v2.20/js/opentok.min.js"></script>
```

**Key variables needed from Django context:**
- `vonage_api_key` - API Key for Vonage
- `vonage_session_id` - Session ID created for this call
- `vonage_token` - Authentication token for user
- `user_display_name` - Name to display in call
- `request.user.user_type` - 'doctor' or 'patient'
- `conversation.id` - Conversation ID
- `video_call.id` - Call ID

**JavaScript implementation:**
```javascript
// Initialize Vonage session
session = OT.initSession(VONAGE_API_KEY, SESSION_ID);

// Handle when other participant joins
session.on('streamCreated', (event) => {
    subscriber = session.subscribe(event.stream, 'vonage-subscriber-container');
});

// Connect and publish own video
session.connect(TOKEN, (error) => {
    if (error) return;
    publisher = OT.initPublisher('vonage-container');
    session.publish(publisher);
});
```

### 3. Optional: Update Call Features

The Vonage implementation supports:
- ✅ Audio toggle (mute/unmute)
- ✅ Video toggle (camera on/off)
- ✅ Call duration timer
- ✅ Proper disconnect handling
- ✅ Error handling with user messages

## Database Migration

The migration file has been created:
```
messaging/migrations/0002_videocall_vonage_session_id.py
```

When you push to Railway, it will automatically run migrations on startup.

## Testing

1. **Add Vonage credentials to Railway environment**
2. **Push code to GitHub** (if not already done)
3. **Wait for Railway deployment**
4. **Test video call functionality:**
   - Start a conversation between doctor and patient
   - Click "Start Video Call"
   - Both users should see their own video + other participant's video
   - Test mute/unmute audio
   - Test turn camera off/on
   - End call should redirect to conversation

## Troubleshooting

If video call fails:

1. **Check Railway logs:**
   - Look for Vonage initialization errors
   - Check if API key is being read correctly

2. **Common errors:**
   - `ModuleNotFoundError: opentok` - Wait for Railway to install requirements
   - `Missing Vonage configuration` - Add environment variables to Railway
   - `Could not connect to session` - Check Vonage credentials are correct

3. **Enable browser console logging:**
   - Open browser DevTools (F12)
   - Go to Console tab
   - Check for any JavaScript errors

## Files Modified

- `messaging/vonage_service.py` - NEW
- `messaging/models.py` - Added vonage_session_id field
- `messaging/views.py` - Integrated Vonage  
- `requirements.txt` - Added opentok
- `messaging/migrations/0002_videocall_vonage_session_id.py` - NEW

## Next Steps After Setup

1. Test video calls work end-to-end
2. Consider adding:
   - Call recording (Vonage supports this)
   - Screen sharing
   - Call quality settings
   - Participant list/indicators

## Documentation References

- **Vonage Video API Docs:** https://tokbox.com/developer/guides/
- **OpenTok Python SDK:** https://github.com/opentok/OpenTok-Python-SDK
- **Sample App:** https://github.com/opentok/opentok-python-sdk/tree/master/samples

## Cost Note

Vonage Video API is free for development and has generous free tier:
- First 300 minutes/month FREE
- $0.05/minute after that for SD calls
- Perfect for healthcare applications
