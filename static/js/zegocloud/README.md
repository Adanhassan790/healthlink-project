# Zegocloud SDK - Local File Required

## Summary

The video call page now loads the Zegocloud SDK from a local static file only:

`static/js/zegocloud/zego-express-web.min.js`

This avoids all CDN and DNS issues, but it means the real SDK bundle must be present in the repository or deployed static files.

## What You Need To Do

1. Obtain the real Zegocloud Web SDK bundle from a machine or network that can access it.
2. Save it as `static/js/zegocloud/zego-express-web.min.js`.
3. Make sure the file is not the placeholder stub.
4. Run `python manage.py collectstatic --noinput`.
5. Deploy the updated files to Railway.

## Verification

After deployment:

1. Open DevTools.
2. Load the video call page.
3. Confirm `/static/js/zegocloud/zego-express-web.min.js` returns `200`.
4. Confirm the console shows `✓ Zegocloud SDK loaded successfully`.

## Troubleshooting

| Issue | Likely Cause |
|-------|--------------|
| 404 Not Found for SDK | File missing from `static/js/zegocloud/` |
| Placeholder error in console | Real SDK bundle was not copied over |
| File exists but not served | `collectstatic` was not run or deploy did not include it |
| SDK loads but call still fails | SDK bundle version mismatch or invalid token/App ID |

## File Size Reference

The real Zegocloud SDK should be much larger than the placeholder file, typically several hundred KB or more. If the file is tiny, it is probably not the real bundle.
