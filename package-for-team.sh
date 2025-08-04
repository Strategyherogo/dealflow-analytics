#!/bin/bash

# DealFlow Analytics - Team Distribution Package Script
# Creates a clean, team-ready distribution package

set -e

echo "📦 Creating DealFlow Analytics Team Package"
echo "=========================================="

# Configuration
VERSION="1.0"
PACKAGE_NAME="dealflow-analytics-v${VERSION}"
TEMP_DIR="/tmp/${PACKAGE_NAME}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Clean up any existing temp directory
rm -rf "$TEMP_DIR"

print_step "Creating clean extension package..."

# Create temporary directory structure
mkdir -p "$TEMP_DIR/extension"
mkdir -p "$TEMP_DIR/docs"

# Copy extension files (excluding development files)
print_step "Copying extension files..."
cp -r extension/* "$TEMP_DIR/extension/"

# Remove development files
rm -rf "$TEMP_DIR/extension/node_modules" 2>/dev/null || true
rm -rf "$TEMP_DIR/extension/.git" 2>/dev/null || true
rm -rf "$TEMP_DIR/extension/*.log" 2>/dev/null || true
rm -rf "$TEMP_DIR/extension/.DS_Store" 2>/dev/null || true
find "$TEMP_DIR/extension" -name ".DS_Store" -delete 2>/dev/null || true

# Copy documentation
print_step "Adding team documentation..."
cp TEAM_DISTRIBUTION_GUIDE.md "$TEMP_DIR/docs/"
cp README.md "$TEMP_DIR/docs/" 2>/dev/null || echo "# DealFlow Analytics" > "$TEMP_DIR/docs/README.md"

# Create installation instructions
print_step "Creating installation guide..."
cat > "$TEMP_DIR/INSTALL.md" << 'EOF'
# 🚀 DealFlow Analytics - Installation Guide

## Quick Install (2 minutes)

### 1. Install Chrome Extension
1. **Extract** this zip file to a folder
2. **Open Chrome** → Settings → Extensions (or type `chrome://extensions/`)
3. **Enable** "Developer mode" (toggle in top right)
4. **Click** "Load unpacked" → Select the `extension` folder
5. **Pin** the extension icon to your toolbar

### 2. Configure API Endpoint
1. **Click** the DealFlow Analytics icon in Chrome
2. **Enter API URL** provided by your team admin
3. **Click** "Save Settings"

### 3. Test Installation
1. **Visit** any company website (LinkedIn profile, company homepage)
2. **Click** the DealFlow Analytics icon  
3. **Wait** 10 seconds for analysis
4. **Export** PDF report to verify everything works

## Troubleshooting

### Extension Not Loading
- Ensure "Developer mode" is enabled
- Try refreshing the extensions page
- Check that you selected the `extension` folder (not the parent folder)

### API Connection Issues  
- Verify the API URL with your team admin
- Check your internet connection
- Try refreshing the page and clicking the icon again

### No Company Detected
- Make sure you're on a company website or LinkedIn company page
- Try refreshing the page
- The extension works on any website - it extracts company info from page content

## Usage Tips

### Best Websites for Analysis
- ✅ LinkedIn company pages
- ✅ Company homepages
- ✅ Crunchbase profiles  
- ✅ AngelList profiles
- ✅ Any website mentioning a company

### Getting Better Results
- Use the extension on the company's main website
- LinkedIn company pages provide the richest data
- Wait 10-15 seconds for complete analysis
- Export PDF immediately after analysis completes

## Support
Contact your team admin for technical issues or questions.
EOF

# Create team configuration template
print_step "Creating configuration template..."
cat > "$TEMP_DIR/extension/config.template.js" << 'EOF'
// DealFlow Analytics - Team Configuration
// Copy this file to config.js and update with your team's API endpoint

const CONFIG = {
    API_BASE_URL: 'https://your-api-domain.com',  // Update this URL
    TEAM_NAME: 'Your VC Firm',                    // Optional: Your firm name
    VERSION: '1.0'
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
EOF

# Update popup.js to use config if available
print_step "Updating extension configuration..."
if [ -f "$TEMP_DIR/extension/js/popup.js" ]; then
    # Add config loading at the top of popup.js
    sed -i.bak '1i\
// Load team configuration if available\
try {\
    if (typeof CONFIG !== "undefined") {\
        var API_BASE_URL = CONFIG.API_BASE_URL;\
    } else {\
        var API_BASE_URL = "http://localhost:8000";\
    }\
} catch (e) {\
    var API_BASE_URL = "http://localhost:8000";\
}
' "$TEMP_DIR/extension/js/popup.js"
    
    # Remove backup file
    rm "$TEMP_DIR/extension/js/popup.js.bak" 2>/dev/null || true
fi

# Create package info
print_step "Creating package metadata..."
cat > "$TEMP_DIR/PACKAGE_INFO.txt" << EOF
DealFlow Analytics - Team Distribution Package
Version: ${VERSION}
Created: $(date)
Package Contents:
- Chrome Extension (Manifest V3)
- Installation Guide
- Team Configuration Template
- Documentation

This package is ready for distribution to your team members.
Each team member should follow the INSTALL.md instructions.
EOF

# Create the distribution zip
print_step "Creating distribution package..."
cd /tmp
zip -r "${PACKAGE_NAME}.zip" "${PACKAGE_NAME}" -q

# Move to project directory
mv "/tmp/${PACKAGE_NAME}.zip" "/Users/jenyago/Desktop/Apps Factory/dealflow-analytics/"

# Clean up
rm -rf "$TEMP_DIR"

print_step "Package created successfully!"
echo ""
echo "📦 Distribution Package: ${PACKAGE_NAME}.zip"
echo "📍 Location: /Users/jenyago/Desktop/Apps Factory/dealflow-analytics/${PACKAGE_NAME}.zip"
echo ""
echo "🎯 Next Steps:"
echo "1. Share ${PACKAGE_NAME}.zip with your team"
echo "2. Provide your API endpoint URL (from deployment)"
echo "3. Team members follow INSTALL.md instructions"
echo ""
echo "📊 Package Contents:"
echo "• Chrome Extension (production-ready)"
echo "• Installation guide for team members"
echo "• Configuration template"
echo "• Team distribution documentation"
echo ""
print_info "Your team package is ready for distribution!"