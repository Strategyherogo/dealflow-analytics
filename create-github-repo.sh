#!/bin/bash

# Quick GitHub Repository Creation Script
echo "🚀 Creating GitHub Repository for DealFlow Analytics"
echo "===================================================="

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "Run: gh auth login"
    echo "Then run this script again"
    exit 1
fi

# Get GitHub username
GITHUB_USER=$(gh api user --jq .login)
echo "✅ Authenticated as: $GITHUB_USER"

# Create the repository
echo "Creating repository..."
gh repo create dealflow-analytics \
    --public \
    --source=. \
    --description="VC investment analysis Chrome extension with AI insights" \
    --remote=origin \
    --push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Repository created successfully!"
    echo "📍 URL: https://github.com/$GITHUB_USER/dealflow-analytics"
    echo ""
    echo "Next steps:"
    echo "1. Go to: https://cloud.digitalocean.com/apps"
    echo "2. Click 'Create App'"
    echo "3. Select GitHub and choose 'dealflow-analytics' repository"
    echo "4. Follow the deployment guide in DIGITALOCEAN_SETUP_GUIDE.md"
else
    echo "❌ Failed to create repository"
    echo "You can create it manually at: https://github.com/new"
fi