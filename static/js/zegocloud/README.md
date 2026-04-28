# Zegocloud SDK - Manual Setup Required

## Issue
Your network environment is blocking downloads from all CDNs:
- jsDelivr CDN (blocked)
- unpkg CDN (blocked)
- Skypack CDN (blocked)
- Zegocloud official CDNs (blocked)

This is likely a firewall/ISP restriction on your network or hosting provider.

## Solution: Manual SDK Installation

### For Local Development (Windows)

#### Option 1: Download from Browser (Easiest)

1. Visit: https://www.jsdelivr.net/npm/zego-express-web-sdk@2.9.9/
2. Look for `index.min.js` file
3. Right-click → "Save As"
4. Save to: `c:\Users\Ibnuhassan\Desktop\projects\healthlink-project\static\js\zegocloud\zego-express-web.min.js`

#### Option 2: Use Python on Different Network

If you can access the internet from a different machine/network:

```python
import urllib.request
import os

url = 'https://cdn.jsdelivr.net/npm/zego-express-web-sdk@2.9.9/index.min.js'
output_file = 'zego-express-web.min.js'

urllib.request.urlretrieve(url, output_file)
print(f'Downloaded {os.path.getsize(output_file)} bytes')
```

Then transfer the file to this directory.

### For Railway Deployment

**Important:** Railway's build environment also appears to be blocking Zegocloud CDNs, so you MUST include the SDK in your repository.

#### Steps:

1. **Download the SDK file** locally (using one of the methods above)

2. **Place in:** `static/js/zegocloud/zego-express-web.min.js`

3. **Verify file exists:**
   ```bash
   ls -la static/js/zegocloud/
   ```
   Should show: `zego-express-web.min.js` (typically ~500KB+)

4. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Commit to Git:**
   ```bash
   git add static/js/zegocloud/zego-express-web.min.js
   git commit -m "Add Zegocloud SDK file for offline/restricted network support"
   ```

6. **Deploy to Railway:**
   ```bash
   git push
   ```
   Railway will:
   - Include the SDK file in deployment
   - Serve it via WhiteNoise middleware
   - Available at: `/static/js/zegocloud/zego-express-web.min.js`

### Verify Installation

After deploying:

1. Open DevTools (F12)
2. Go to video call page
3. Check Network tab for: `/static/js/zegocloud/zego-express-web.min.js`
4. Should show status 200 (not 404)
5. Console should show: `✓ Zegocloud SDK loaded successfully`

## Alternative Solutions

If you continue having SDK issues, consider:

1. **Use WhatsApp/Google Meet Links** - Simpler, no SDK
2. **Switch to Whereby.com** - Simpler WebRTC (single script tag)
3. **Use Agora.io** - Better global CDN distribution
4. **Host SDK on your own S3/server** - Full control

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 404 Not Found for SDK | File not in `/static/js/zegocloud/` or collectstatic not run |
| SDK loads but breaks | File corrupted in transfer, re-download |
| File exists but not served | Run `python manage.py collectstatic --noinput` |
| Railway still shows 404 | Push code, wait for Railway redeploy |

## File Size Reference

The Zegocloud SDK should be approximately:
- `zego-express-web.min.js`: 500KB - 1.5MB (minified)
- `zego-express-web.js`: 2MB - 3MB (unminified)

If your file is much smaller (<100KB), it may be corrupted.
