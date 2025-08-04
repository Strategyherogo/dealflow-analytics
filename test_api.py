#!/usr/bin/env python3
"""
Test script for DealFlow Analytics API
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_analyze_company():
    """Test company analysis"""
    print("2. Testing company analysis...")
    
    # Test with a well-known company
    test_company = {
        "name": "Stripe",
        "domain": "stripe.com",
        "industry": "Financial Services",
        "employeeCount": "8000",
        "description": "Online payment processing for internet businesses"
    }
    
    print(f"   Analyzing: {test_company['name']}")
    response = requests.post(
        f"{BASE_URL}/api/analyze",
        json=test_company
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Investment Score: {data.get('investmentScore')}/100")
        print(f"   Data Sources: {', '.join(data.get('dataSources', []))}")
        
        # Show AI thesis if available
        ai_thesis = data.get('aiThesis')
        if ai_thesis:
            print(f"   AI Summary: {ai_thesis.get('summary', 'N/A')}")
            print(f"   Recommendation: {ai_thesis.get('recommendation', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
    print()

def test_manual_browser():
    """Instructions for manual browser testing"""
    print("3. Manual Browser Testing:")
    print("   a) Open Chrome and go to: chrome://extensions/")
    print("   b) Enable 'Developer mode' (top right)")
    print("   c) Click 'Load unpacked'")
    print(f"   d) Select: /Users/jenyago/Desktop/Apps Factory/dealflow-analytics/extension")
    print("   e) Visit: https://www.linkedin.com/company/stripe/")
    print("   f) Click the DealFlow Analytics extension icon")
    print("   g) Click 'Analyze Company' button")
    print()

def main():
    print("=" * 60)
    print("DealFlow Analytics - API Test Suite")
    print("=" * 60)
    print()
    
    # Run tests
    test_health()
    test_analyze_company()
    test_manual_browser()
    
    print("=" * 60)
    print(f"Tests completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()