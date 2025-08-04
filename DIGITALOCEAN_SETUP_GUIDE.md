# 🚀 Step-by-Step DigitalOcean App Platform Deployment

## Prerequisites Checklist
- [ ] GitHub account (free)
- [ ] DigitalOcean account ([Sign up here](https://www.digitalocean.com/) - get $200 credit)
- [ ] Anthropic API key (optional but recommended - [Get it here](https://console.anthropic.com/))

## Step 1: Create GitHub Repository

### Option A: Using GitHub CLI (if installed)
```bash
gh repo create dealflow-analytics --public --source=. --remote=origin --push
```

### Option B: Manual GitHub Setup
1. Go to [GitHub.com](https://github.com/new)
2. Create a new repository:
   - Repository name: `dealflow-analytics`
   - Description: `VC investment analysis Chrome extension with AI insights`
   - Public repository
   - **DON'T** initialize with README (we already have one)
3. Click "Create repository"
4. Run these commands in your terminal:

```bash
cd /Users/jenyago/Desktop/Apps\ Factory/dealflow-analytics

# Add your GitHub repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/dealflow-analytics.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 2: Deploy to DigitalOcean App Platform

### 2.1 Connect to DigitalOcean
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click the blue **"Create App"** button
3. Choose **"GitHub"** as your source
4. Authorize DigitalOcean to access your GitHub (if first time)
5. Select your `dealflow-analytics` repository
6. Choose branch: `main`
7. Click **"Next"**

### 2.2 Configure Resources
DigitalOcean will auto-detect your Dockerfile. You'll see:
- **Type**: Web Service
- **Source Directory**: `/backend`
- **Dockerfile Path**: `/backend/Dockerfile`

Click **"Edit"** next to the resource and configure:
- **HTTP Port**: 8000
- **HTTP Route**: /
- **Instance Size**: Basic ($12/month) - Select "1 GB RAM | 1 vCPU"
- **Instance Count**: 1

Click **"Back"** then **"Next"**

### 2.3 Set Environment Variables
Click **"Edit"** next to Environment Variables and add:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
REDIS_HOST=localhost
REDIS_PORT=6379
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

**Important**: 
- Mark `ANTHROPIC_API_KEY` as **encrypted** (click the lock icon)
- If you don't have an Anthropic key, the app still works but without AI features

Click **"Save"** then **"Next"**

### 2.4 Name Your App
- **App name**: `dealflow-analytics` (or your preferred name)
- **Region**: Choose closest to your users (NYC recommended)

Click **"Next"**

### 2.5 Review and Launch
- Review the configuration
- Your cost should be **~$12/month**
- Click **"Create Resources"**

## Step 3: Wait for Deployment (5-10 minutes)

DigitalOcean will:
1. Build your Docker container
2. Deploy it
3. Set up HTTPS/SSL automatically
4. Provide you with a URL

You can watch the progress in the **"Activity"** tab.

## Step 4: Get Your App URL

Once deployed, you'll get a URL like:
```
https://dealflow-analytics-xxxxx.ondigitalocean.app
```

Test it by visiting:
```
https://dealflow-analytics-xxxxx.ondigitalocean.app/health
```

You should see:
```json
{"status":"healthy","redis":"disconnected","timestamp":"..."}
```

## Step 5: Update Chrome Extension

1. Open the file:
```bash
open /Users/jenyago/Desktop/Apps\ Factory/dealflow-analytics/extension/js/popup.js
```

2. Change line 3 from:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```
To:
```javascript
const API_BASE_URL = 'https://dealflow-analytics-xxxxx.ondigitalocean.app/api';
```

3. Reload the extension in Chrome:
   - Go to `chrome://extensions/`
   - Find DealFlow Analytics
   - Click the refresh icon

## Step 6: Test Everything

1. **Test the API**:
```bash
curl https://your-app-url.ondigitalocean.app/health
```

2. **Test the Extension**:
   - Go to any LinkedIn company page
   - Click the DealFlow Analytics extension
   - Click "Analyze Company"
   - You should see the analysis!

## Troubleshooting

### If deployment fails:
1. Check the **"Activity"** tab for error messages
2. Common issues:
   - Missing environment variables
   - Port mismatch (should be 8000)
   - Dockerfile issues

### View logs:
In DigitalOcean dashboard:
- Go to your app
- Click **"Runtime Logs"** tab
- Check for errors

### If extension doesn't work:
1. Check browser console (right-click extension → Inspect)
2. Verify API URL is correct in popup.js
3. Check CORS is allowing your extension

## Optional: Custom Domain

To use your own domain (e.g., api.yourdomain.com):
1. In App Platform, go to **Settings** → **Domains**
2. Click **"Add Domain"**
3. Follow the DNS instructions
4. Update your extension with the new URL

## Costs Summary
- **App Platform Basic**: $12/month
- **Optional upgrades**:
  - Add database: +$7/month
  - Scale to 2GB RAM: +$12/month
  - Custom domain: Free (you own the domain)

## Next Steps
1. ✅ Monitor usage in DigitalOcean dashboard
2. ✅ Set up alerts for errors/downtime
3. ✅ Share extension with beta users
4. ✅ Collect feedback and iterate

## Support
- [DigitalOcean Support](https://www.digitalocean.com/support/)
- [App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- Check logs: Dashboard → Your App → Runtime Logs

---

**Ready to deploy?** Follow the steps above and you'll be live in 15 minutes! 🚀