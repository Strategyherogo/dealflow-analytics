#!/bin/bash

# DealFlow Analytics - Extension Packager
# Creates a distribution-ready ZIP file for Chrome Web Store

echo "📦 Packaging DealFlow Analytics Extension..."

# Create the final ZIP - Chrome Web Store format (only extension directory contents)
OUTPUT_FILE="dealflow-analytics-extension-$(date +%Y%m%d).zip"
echo "Creating $OUTPUT_FILE..."

# Navigate to extension directory and create ZIP from contents
cd extension
zip -r ../$OUTPUT_FILE * -x "*.DS_Store" "*/.DS_Store" "*/node_modules/*" "*/.git/*"
cd ..

# Cleanup
rm -rf $TEMP_DIR

# Create a shareable link instruction file
cat > SHARE_INSTRUCTIONS.md << EOF
# How to Share DealFlow Analytics

## Option 1: Direct File Sharing
Share the file: $OUTPUT_FILE
- Via email
- Via Slack/Discord
- Via Google Drive/Dropbox

## Option 2: GitHub Release
1. Go to: https://github.com/Strategyherogo/dealflow-analytics/releases
2. Click "Create a new release"
3. Upload $OUTPUT_FILE
4. Share the release link

## Option 3: Quick Testing Link
Share this repository link with instructions:
https://github.com/Strategyherogo/dealflow-analytics

Testers can:
1. Click "Code" → "Download ZIP"
2. Extract and load the extension folder

## Testing Group Message Template

Subject: Test DealFlow Analytics - VC Investment Analysis Tool

Hi everyone!

I've built a Chrome extension that analyzes companies for investment potential. Would love your feedback!

**What it does:**
- Instant analysis on any LinkedIn company page
- Investment score (0-100) based on real data
- Growth signals, market analysis, AI insights
- Export to PDF/CSV

**To install:**
1. Download attached file and extract
2. Open chrome://extensions/
3. Enable Developer Mode
4. Load unpacked → select 'extension' folder

**Please test:**
- LinkedIn pages (best results)
- Different company sizes
- Export features
- Report any bugs!

Thanks for your help! 🙏

EOF

echo ""
echo "✅ Package created successfully!"
echo ""
echo "📦 File: $OUTPUT_FILE"
echo "📏 Size: $(du -h $OUTPUT_FILE | cut -f1)"
echo "📄 Instructions: SHARE_INSTRUCTIONS.md"
echo ""
echo "Ready to share with testers!"