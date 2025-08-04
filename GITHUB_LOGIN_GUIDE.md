# 🔐 GitHub Login Guide - Step by Step

## Method 1: Interactive Browser Login (Easiest)

### Step 1: Start the login process
Open Terminal and run:
```bash
gh auth login
```

### Step 2: Follow these prompts:

1. **What account do you want to log into?**
   - Press Enter to select: `GitHub.com`

2. **What is your preferred protocol for Git operations?**
   - Press Enter to select: `HTTPS`

3. **Authenticate Git with your GitHub credentials?**
   - Press Enter to select: `Yes`

4. **How would you like to authenticate GitHub CLI?**
   - Press Enter to select: `Login with a web browser`

5. **First copy your one-time code:**
   - You'll see something like: `XXXX-XXXX`
   - Copy this code (select and Cmd+C)
   - Press Enter to open browser

6. **In your browser:**
   - Paste the code in the box
   - Click "Continue"
   - Click "Authorize github"
   - You'll see "Congratulations, you're all set!"

7. **Back in Terminal:**
   - You'll see: ✓ Authenticated to GitHub as YOUR_USERNAME

## Method 2: Personal Access Token (If browser doesn't work)

### Step 1: Create a token on GitHub
1. Go to: https://github.com/settings/tokens/new
2. Sign in to GitHub if needed
3. Fill in:
   - **Note**: `DealFlow Analytics CLI`
   - **Expiration**: 90 days (or your preference)
   - **Select scopes**: Check these boxes:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
     - ✅ `read:org` (Read org and team membership)
4. Click green "Generate token" button at bottom
5. **IMPORTANT**: Copy the token NOW (starts with `ghp_`)
   - You won't be able to see it again!

### Step 2: Use the token to login
```bash
gh auth login
```

Follow prompts:
1. Choose: `GitHub.com`
2. Choose: `HTTPS`
3. Choose: `Yes` (authenticate Git)
4. Choose: `Paste an authentication token`
5. Paste your token (it won't show on screen)
6. Press Enter

## Method 3: Quick Token Login (One Command)

If you already have a token:
```bash
echo "YOUR_TOKEN_HERE" | gh auth login --with-token
```

## Verify You're Logged In

Run this to check:
```bash
gh auth status
```

You should see:
```
✓ Logged in to github.com as YOUR_USERNAME
✓ Git operations for github.com configured to use https protocol
✓ Token: ghp_****
```

## Troubleshooting

### "Command not found: gh"
Install GitHub CLI first:
```bash
brew install gh
```

### "Error: could not prompt"
Use the token method instead of browser method.

### "Permission denied"
Make sure your token has the `repo` scope selected.

### Browser didn't open
1. Copy the URL shown in terminal
2. Open it manually in your browser
3. Enter the code

## Quick Test

Once logged in, test with:
```bash
gh repo list --limit 5
```

This shows your recent repositories.

---

## Ready to Continue?

Once you see "✓ Logged in", run:
```bash
cd /Users/jenyago/Desktop/Apps\ Factory/dealflow-analytics
./create-github-repo.sh
```

This will create your repository and push the code!