# Local Zegocloud SDK Setup Guide

## Problem
All external CDNs (jsDelivr, unpkg, Skypack, Zegocloud official) are failing to load the Zegocloud SDK due to DNS resolution and dependency issues. This appears to be a network/firewall restriction in your environment.

## Solution: Host SDK Locally

### Step 1: Download the Zegocloud SDK

1. Visit: https://www.npmjs.com/package/zego-express-web-sdk
2. Download version 2.9.9 (or latest stable)
3. Extract the bundle

### Step 2: Copy to Static Directory

Copy the SDK files to: `/static/js/zegocloud/`

```
static/js/zegocloud/
├── zego-express-web.min.js
├── zego-express-web.js
├── package.json
└── README.md
```

### Step 3: Verify Installation

The HTML template will automatically load from the local path:
```html
<script src="/static/js/zegocloud/zego-express-web.min.js"></script>
```

### Step 4: Update Django Settings (if needed)

Ensure WhiteNoise is configured in `healthlink/settings.py`:
```python
MIDDLEWARE = [
    # ...
    'whitenoise.middleware.WhiteNoiseMiddleware',
]
```

This is already configured in your project.

### Step 5: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 6: Deploy to Railway

```bash
git add static/js/zegocloud/
git commit -m "feat: Add local Zegocloud SDK files"
git push
```

Railway will automatically serve static files via WhiteNoise.

## Alternative: Use Different Video Provider

If you continue having issues with Zegocloud, consider:

1. **Whereby** - Simple WebRTC video (no complex dependencies)
2. **Agora.io** - Better CDN distribution
3. **TokBox (Vonage)** - If you can get the API key working
4. **SimpleWebRTC** - Lightweight, no external services

## Troubleshooting

| Issue | Solution |
|-------|----------|
| SDK still not loading | Check DevTools Network tab for `/static/js/zegocloud/zego-express-web.min.js` |
| 404 errors | Run `python manage.py collectstatic --noinput` |
| Railway not serving static files | Ensure `STATIC_URL=/static/` in settings.py |
| Zegocloud room join fails | Verify App ID (1922185230) and token generation |

## Testing

After setup, try a video call:
1. Login as patient
2. Start a conversation with a doctor
3. Click "Start Video Call"
4. Check browser console for: `✓ Zegocloud SDK loaded successfully`
