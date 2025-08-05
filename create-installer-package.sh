#!/bin/bash

# Create a complete package with extension + instructions

echo "📦 Creating Complete Installer Package..."

# Create distribution directory
DIST_DIR="DealFlow-Analytics-Package"
rm -rf $DIST_DIR
mkdir -p $DIST_DIR

# Copy extension ZIP
cp dealflow-analytics-extension-*.zip $DIST_DIR/extension.zip

# Copy instructions
cp INSTALLATION_GUIDE.md $DIST_DIR/
cp SHARE_INSTRUCTIONS.md $DIST_DIR/

# Create simple README
cat > $DIST_DIR/README.txt << EOF
DealFlow Analytics - Installation Package
=========================================

This package contains:
1. extension.zip - The Chrome extension (upload this to Chrome)
2. INSTALLATION_GUIDE.md - Detailed installation instructions
3. SHARE_INSTRUCTIONS.md - How to share with others

Quick Install:
1. Extract extension.zip
2. Open Chrome → chrome://extensions/
3. Enable "Developer mode"
4. Click "Load unpacked" and select the extracted folder

For detailed help, see INSTALLATION_GUIDE.md

Questions? See troubleshooting in the guide.
EOF

# Create final package
FINAL_PACKAGE="DealFlow-Analytics-Complete-$(date +%Y%m%d).zip"
zip -r $FINAL_PACKAGE $DIST_DIR

# Cleanup
rm -rf $DIST_DIR

echo ""
echo "✅ Complete package created!"
echo "📦 Extension only: dealflow-analytics-extension-$(date +%Y%m%d).zip (for Chrome Web Store)"
echo "📦 Complete package: $FINAL_PACKAGE (for manual sharing)"
echo ""
echo "Use the extension-only ZIP for Chrome Web Store upload."
echo "Use the complete package for sharing with testers."