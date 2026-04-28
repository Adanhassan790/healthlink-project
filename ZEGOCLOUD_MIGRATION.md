# Vonage to Zegocloud Migration Guide

## Overview
Successfully migrated from Vonage OpenTok video conferencing to Zegocloud. Zegocloud is easier to set up and doesn't require complex API management.

## What Changed

### Backend Changes
1. **Removed**: `opentok==3.13.0` from requirements.txt
2. **Replaced**: `messaging/vonage_service.py` → `messaging/zegocloud_service.py`
3. **Updated**: `messaging/views.py` to use Zegocloud token generation
4. **Key Differences**:
   - Vonage required creating a session first, then generating tokens
   - Zegocloud generates tokens directly without session creation
   - Zegocloud uses App ID + Server Secret instead of API Key + Secret

### Files Changed
- `messaging/zegocloud_service.py` (NEW)
- `messaging/views.py` (UPDATED)
- `requirements.txt` (UPDATED - removed opentok)
- `.env` (UPDATED - Zegocloud credentials)
- `.env.zegocloud` (NEW - template file)

## Setup Instructions

### Step 1: Get Zegocloud Credentials

1. **Sign up at**: https://zegocloud.com/
2. **Create an account** (Free tier available)
3. **Go to Console**: https://console.zegocloud.com/
4. **Get your credentials**:
   - **AppID**: Navigate to Project Management → Select/Create Project → Get AppID
   - **ServerSecret**: Navigate to Project Management → Auth → Get ServerSecret

### Step 2: Add Credentials to .env

Update your `.env` file with your Zegocloud credentials:

```env
ZEGOCLOUD_APP_ID=your_actual_app_id_here
ZEGOCLOUD_SERVER_SECRET=your_actual_server_secret_here
```

**Example** (your actual values will be different):
```env
ZEGOCLOUD_APP_ID=1234567890
ZEGOCLOUD_SERVER_SECRET=abcdefghijklmnopqrstuvwxyz
```

### Step 3: Update Frontend (if applicable)

If you have custom JavaScript for video conferencing, update it to use:
- `zegocloud_app_id` (instead of `vonage_api_key`)
- `zegocloud_room_id` (instead of `vonage_session_id`)
- `zegocloud_access_token` (instead of `vonage_token`)
- `zegocloud_user_id` (for user identification)

### Step 4: Reinstall Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate

# Reinstall requirements (removes opentok, adds nothing new)
pip install -r requirements.txt
```

### Step 5: Test the Integration

1. Start the development server:
```bash
python manage.py runserver
```

2. Log in as both doctor and patient
3. Try starting a video call
4. Check Django logs for any Zegocloud errors

If you see "Zegocloud not configured" error, verify that:
- `.env` file has correct `ZEGOCLOUD_APP_ID` and `ZEGOCLOUD_SERVER_SECRET`
- Django has reloaded (server needs restart after .env changes)
- Credentials from Zegocloud console are copied exactly (no extra spaces)

## Zegocloud Documentation

- **Official Docs**: https://docs.zegocloud.com/
- **Console**: https://console.zegocloud.com/
- **Pricing**: https://zegocloud.com/pricing (Free tier: up to 10,000 minutes/month)

## Benefits of Zegocloud

✅ **Easier Setup**: No complex API key management
✅ **Free Tier**: Up to 10,000 minutes per month
✅ **Better Support**: More responsive support team
✅ **Lower Cost**: Competitive pricing compared to Vonage
✅ **Modern Architecture**: WebRTC-based, no proprietary protocols
✅ **Scalable**: Handles up to 10,000+ concurrent users

## Migration Notes

### Model Changes
The `VideoCall` model still has the `vonage_session_id` field for backward compatibility. This field is no longer populated by the new code, but leaving it prevents database migration issues. Can be safely removed in a future update.

### Token Generation
- **Vonage**: Required server-side session creation
- **Zegocloud**: Token generated on-the-fly, no pre-creation needed
- This improves scalability and reduces server overhead

### API Key Security
- Store `ZEGOCLOUD_SERVER_SECRET` in `.env` (never commit to git)
- The `.env` file is in `.gitignore` for security
- On production (Railway), set these as environment variables

## Troubleshooting

### Error: "Zegocloud not configured"
**Solution**: Verify `ZEGOCLOUD_APP_ID` and `ZEGOCLOUD_SERVER_SECRET` are set in `.env`

### Token Generation Fails
**Solution**: Check that:
- App ID is numeric (not a string)
- Server Secret is correctly copied from console
- No extra spaces in credentials

### Video Call Not Working in Browser
**Solution**: Ensure:
- Browser has permission to access camera/microphone
- Zegocloud credentials are passed correctly to frontend
- Check browser console for JavaScript errors

## Rolling Back to Vonage (if needed)

If you need to revert to Vonage:

1. Replace `messaging/zegocloud_service.py` with `messaging/vonage_service.py`
2. Update imports in `messaging/views.py`
3. Add `opentok==3.13.0` back to `requirements.txt`
4. Set `VONAGE_API_KEY` and `VONAGE_API_SECRET` in `.env`

## Questions?

Refer to Zegocloud documentation or contact their support at: https://zegocloud.com/contact
