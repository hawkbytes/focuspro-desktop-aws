# Debug Guide: Screenshot Preview Not Working

## Quick Troubleshooting Checklist

### 1. Check Browser Console
Open browser DevTools (F12) and check Console tab for errors:
```
Expected messages:
✅ Screenshot preview updated successfully
OR
❌ No user email found in localStorage
❌ No screenshot available
❌ Network error
```

### 2. Verify User Email is Stored
In browser console, run:
```javascript
console.log('Email:', localStorage.getItem('user_email'));
console.log('Alt Email:', sessionStorage.getItem('userEmail'));
```

**Expected:** Your email address  
**If null:** You need to log in properly

### 3. Check Screenshot Files Exist
Navigate to:
```
C:\Users\micro\OneDrive\Desktop\Git-Projects\Client-Side-DDS-Focus\Screen-Recordings\
```

Look for folders with your email (e.g., `user_at_example_com`)

### 4. Test API Endpoint Directly
In browser, navigate to:
```
http://127.0.0.1:5000/api/latest-screenshot?email=YOUR_EMAIL_HERE
```

Replace YOUR_EMAIL_HERE with your actual email.

**Expected Response:**
```json
{
  "success": true,
  "image_data": "data:image/webp;base64,...",
  "metadata": {...}
}
```

**If 404:** No screenshots captured yet  
**If 400:** Email not provided  
**If 500:** Server error (check server logs)

### 5. Start a Work Session
If no screenshots exist:
1. Go to main dashboard
2. Select a project and task
3. Click "Start Work"
4. Wait 1-2 minutes for first screenshot
5. Refresh Settings page

### 6. Check Server Logs
Look at terminal running Flask server for:
```
📸 [Cache] Updated for user@example.com
📸 [API] Latest screenshot retrieved for user@example.com
```

### 7. Manual Test Steps

**Step 1:** Open browser console (F12)

**Step 2:** Run this command:
```javascript
fetch('/api/latest-screenshot?email=' + localStorage.getItem('user_email'))
  .then(r => r.json())
  .then(d => console.log('API Response:', d))
  .catch(e => console.error('API Error:', e));
```

**Step 3:** Check response

### Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "User not logged in" | Email not in localStorage | Log in through /client page |
| "No screenshot available" | No screenshots captured yet | Start a work session and wait |
| "Network error" | Flask server not running | Start server with `python app.py` |
| "Failed to decrypt screenshot" | Encryption key mismatch | Check ENCRYPTION_KEY in .env |
| Preview shows but image broken | Base64 encoding issue | Check server logs for errors |

### Manual Email Setup (Temporary)

If email is not being stored, manually set it in console:
```javascript
localStorage.setItem('user_email', 'your.email@example.com');
localStorage.setItem('user_name', 'Your Name');
```

Then reload the Settings page.

### Server-Side Debug

Check if cache is working:
```python
from moduller.screenshot_cache_manager import screenshot_cache
print(screenshot_cache._cache)
```

### Force Screenshot Capture

If you need to test immediately, manually trigger screenshot:
1. Start a work session
2. Wait for first capture (check server console)
3. You should see: `✅ [CACHE] Updated screenshot cache for user@example.com`
4. Refresh Settings page

### Full Reset

If nothing works:
1. Stop Flask server
2. Clear browser cache (Ctrl+Shift+Delete)
3. Clear localStorage: `localStorage.clear()`
4. Restart Flask server
5. Log in again through /client
6. Start work session
7. Wait for screenshot
8. Open Settings page

### Contact Points

- Check `app.py` line ~2420 for API endpoint
- Check `moduller/screenshot_cache_manager.py` for cache logic
- Check browser Network tab for API calls
- Check Flask terminal for server errors
