# Quick Fix Steps for DealFlow Analytics

## Fixed Issues:
1. ✅ CORS configuration updated to allow Chrome extension
2. ✅ Service worker code fixed (removed unsupported APIs)
3. ✅ Content script updated with valid DOM selectors

## To Apply Fixes:

1. **Restart the Backend** (to apply CORS changes):
   ```bash
   # Stop the current server (Ctrl+C in the terminal)
   # Then restart:
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Reload the Chrome Extension**:
   - Go to `chrome://extensions/`
   - Find "DealFlow Analytics"
   - Click the refresh icon (↻)

3. **Test the Extension**:
   - Navigate to a LinkedIn company page (e.g., https://www.linkedin.com/company/stripe/)
   - Click the DealFlow Analytics extension icon
   - You should now see the company detected
   - Click "Analyze Company" to test the full flow

## What Was Fixed:

### 1. CORS Configuration (backend/app/main.py):
   - Added specific Chrome extension ID to allowed origins
   - Added wildcard support for development

### 2. Service Worker (extension/js/background.js):
   - Removed webRequest API (not supported in Manifest V3)
   - Fixed compatibility issues

### 3. Content Script (extension/js/content.js):
   - Fixed invalid CSS selector `:contains()` 
   - Updated to use proper DOM queries
   - Now uses the correct content.js file instead of test_inject.js

## If Issues Persist:

1. Check Chrome console for errors:
   - Right-click extension icon → "Inspect popup"
   - Check the Console tab

2. Verify backend is running:
   - Visit http://localhost:8000/health
   - Should show `{"status":"healthy",...}`

3. Clear extension storage:
   - In extension popup console: `chrome.storage.local.clear()`

The extension should now work properly! 🚀