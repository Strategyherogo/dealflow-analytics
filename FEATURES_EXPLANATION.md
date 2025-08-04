# DealFlow Analytics Features

## 1. PDF Export Report
When you click "Export PDF Report" after analyzing a company, it generates a professional investment memo that includes:

- **Executive Summary** - AI-generated investment thesis
- **Investment Score** - 0-100 score with visual indicators
- **Company Overview** - Basic company information
- **Financial Metrics & Growth** - Growth signals and indicators
- **Market Analysis** - TAM and growth rates
- **Investment Thesis** - Detailed strengths and weaknesses
- **Risk Analysis** - Key risks identified
- **Comparable Companies** - Similar companies and their outcomes
- **Data Sources** - Transparency on where data came from

The PDF is professionally formatted like a Sequoia Capital investment memo.

## 2. Track Companies Feature
The "Track Companies" feature allows you to:

- **Save companies to a watchlist** - Click "Track Company" to save it
- **Monitor multiple companies** - Build a portfolio of companies you're interested in
- **Get updates** - (In background service) Periodic checks for changes
- **Quick access** - Tracked companies are saved in Chrome storage

### How it works:
1. Analyze any company
2. Click "Track Company" button
3. The company is saved to your watchlist
4. Access tracked companies from extension storage
5. Get notifications when significant changes occur (if implemented)

### Use Cases:
- **VCs**: Track portfolio companies or potential investments
- **Investors**: Monitor companies before investing
- **Job Seekers**: Track companies you want to work for
- **Competitors**: Keep tabs on competitor companies

## Current Status:
- ✅ Company detection on any website
- ✅ Instant analysis with AI insights
- ✅ PDF export (needs matplotlib installed)
- ✅ Company tracking (saves to Chrome storage)
- ✅ Works on LinkedIn, Crunchbase, and any company website

## To Test PDF Export:
1. Go to any company website (e.g., stripe.com)
2. Click the extension icon
3. Click "Analyze Company"
4. After analysis completes, click "Export PDF Report"
5. Chrome will download the investment memo PDF

## To Test Tracking:
1. After analyzing a company
2. Click "Track Company"
3. The button will change to "Tracked!"
4. Company is now saved in your watchlist