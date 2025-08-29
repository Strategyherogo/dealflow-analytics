# Chrome Web Store Permission Justifications

## Single Purpose Description
This extension analyzes companies for investment opportunities by extracting publicly available business data and generating investment insights with scoring, AI analysis, and professional reports.

## Detailed Description (Full Version)
DealFlow Analytics is a powerful Chrome extension designed for venture capitalists, investors, and business analysts who need quick, comprehensive company analysis.

**Key Features:**
✓ One-Click Analysis - Analyze any company directly from LinkedIn, Crunchbase, or any website
✓ Investment Score (0-100) - Data-driven scoring based on growth signals, market position, and innovation metrics
✓ AI-Powered Investment Thesis - Get Claude AI's investment recommendation with strengths, risks, and similar companies
✓ Real-Time Data - Pulls from GitHub, SEC filings, patents, news, and more
✓ Professional PDF Reports - Export Sequoia-style investment memos
✓ Company Tracking - Save and monitor companies for updates
✓ Dark Mode UI - Professional interface optimized for extended use

**How It Works:**
1. Navigate to any company's LinkedIn page, Crunchbase profile, or website
2. Click the DealFlow Analytics extension icon
3. Click "Analyze Company" to get instant insights
4. Export reports or save companies to your watchlist

**Perfect For:**
- Venture Capitalists doing quick due diligence
- Angel Investors evaluating opportunities
- Business Development professionals
- Market researchers
- Startup founders analyzing competitors

## Permission Justifications

### 1. activeTab
**Justification**: This permission is essential for extracting company information from the current webpage when the user clicks "Analyze Company". We only access the active tab's content when explicitly triggered by the user, ensuring privacy and security. The extension reads company names, descriptions, employee counts, and other publicly visible business data from LinkedIn, Crunchbase, and company websites.

### 2. downloads
**Justification**: This permission enables users to export their analysis results as PDF investment memos and CSV data files. Users can download professional reports for offline viewing, sharing with team members, or archiving for future reference. The download functionality is only triggered when users explicitly click the "Export PDF" or "Export CSV" buttons.

### 3. host_permissions
**Justification**: Host permissions for specific domains are required to:
- **linkedin.com**: Extract company data from LinkedIn company pages (name, employee count, industry)
- **crunchbase.com**: Extract startup information from Crunchbase profiles
- **localhost:8000**: Enable local development and testing of the extension
- **monkfish-app-7otbm.ondigitalocean.app**: Communicate with our secure API server to process analysis requests and generate reports

These permissions are limited to only the domains necessary for the extension's core functionality.

### 4. scripting
**Justification**: The scripting API is used to inject content scripts that extract company information from web pages. This is necessary to read publicly available data like company names, descriptions, and employee counts from LinkedIn and Crunchbase pages. Scripts only run when the user actively requests an analysis, ensuring minimal performance impact.

### 5. storage
**Justification**: Local storage is used to:
- Save user preferences (dark/light theme)
- Store the list of tracked companies for monitoring
- Cache recent analysis results for quick access
- Remember user settings between sessions

No sensitive data is stored, and all storage is local to the user's browser.

### 6. tabs
**Justification**: The tabs permission is required to:
- Detect when users navigate to supported websites (LinkedIn, Crunchbase)
- Extract the current page URL to identify which company is being viewed
- Ensure the extension icon shows the correct state based on the current page

We only access tab information, never modify or redirect tabs without user action.

### 7. Remote Code Use
**Justification**: The extension does not execute any remote code. All JavaScript files are bundled within the extension package and undergo Chrome Web Store review. The extension only makes HTTPS API calls to our server for data processing, receiving JSON responses. No code is dynamically loaded or executed from external sources.

## Data Use Practices

### Data Collection
- We only collect company names and publicly available business information
- Data is extracted locally in the browser
- Information is sent to our servers only when users click "Analyze Company"

### Data Usage
- Company data is used solely to generate investment analysis
- We do not store user queries or analysis results on our servers
- No personal user data is collected or transmitted

### Data Sharing
- We do not sell or share any data with third parties
- Analysis results are only visible to the user who requested them
- We do not track browsing history or user behavior

## Privacy Practices Certification
We certify that DealFlow Analytics:
- Complies with Chrome Web Store Developer Program Policies
- Does not collect or transmit personal user data
- Only processes publicly available business information
- Implements secure HTTPS communication
- Respects user privacy and data protection regulations (GDPR/CCPA)

## Contact Information
**Developer Email**: support@dealflowanalytics.com
**Privacy Policy**: https://monkfish-app-7otbm.ondigitalocean.app/privacy-policy
**Support**: https://github.com/Strategyherogo/dealflow-analytics/issues