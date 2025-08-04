#!/bin/bash

echo "🔍 DealFlow Analytics Diagnostic"
echo "================================"

# Check Python environment
echo -e "\n1. Python Environment:"
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "❌ Virtual environment missing"
fi

# Check backend server
echo -e "\n2. Backend Server:"
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on port 8000"
    curl -s http://localhost:8000/health | python3 -m json.tool
else
    echo "❌ Backend is not responding"
fi

# Check Chrome extension files
echo -e "\n3. Chrome Extension Files:"
if [ -f "extension/manifest.json" ]; then
    echo "✅ manifest.json exists"
else
    echo "❌ manifest.json missing"
fi

if [ -f "extension/popup.html" ]; then
    echo "✅ popup.html exists"
else
    echo "❌ popup.html missing"
fi

if [ -f "extension/js/popup.js" ]; then
    echo "✅ popup.js exists"
else
    echo "❌ popup.js missing"
fi

# Test API endpoint
echo -e "\n4. API Test:"
echo "Testing /api/analyze endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"name": "DiagnosticTest", "domain": "test.com", "industry": "Tech", "employeeCount": "50"}')

if [ $? -eq 0 ]; then
    echo "✅ API responded successfully"
    echo "Investment Score: $(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('investmentScore', 'N/A'))")/100"
else
    echo "❌ API request failed"
fi

echo -e "\n5. Common Issues & Solutions:"
echo "----------------------------"
echo "Issue: Extension not visible in Chrome"
echo "→ Solution: Go to chrome://extensions/ and ensure it's loaded and enabled"
echo ""
echo "Issue: 'Cannot read properties of undefined'"
echo "→ Solution: Make sure you're on a LinkedIn company page (not personal profile)"
echo ""
echo "Issue: CORS errors"
echo "→ Solution: Backend should be running on http://localhost:8000"
echo ""
echo "Issue: No data appearing"
echo "→ Solution: Check browser console (F12) for errors"

echo -e "\n6. Quick Start:"
echo "--------------"
echo "1. Open Chrome"
echo "2. Go to: chrome://extensions/"
echo "3. Enable 'Developer mode' (top right)"
echo "4. Click 'Load unpacked'"
echo "5. Select: $(pwd)/extension"
echo "6. Visit: https://www.linkedin.com/company/apple/"
echo "7. Click the DealFlow Analytics icon"

echo -e "\n✨ Demo page: file://$(pwd)/demo.html"