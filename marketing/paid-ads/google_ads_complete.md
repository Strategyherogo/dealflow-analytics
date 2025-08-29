# Google Ads Campaign - Complete Implementation

## Campaign Structure

### Account Hierarchy
```
DealFlow Analytics (Account)
├── Search Campaigns
│   ├── Branded Search
│   ├── Competitor Targeting
│   ├── Problem/Solution Keywords
│   └── Industry Terms
├── Display Campaigns
│   ├── Remarketing
│   ├── Similar Audiences
│   └── Custom Intent
└── YouTube Campaigns
    ├── In-Stream Ads
    └── Discovery Ads
```

## Budget Allocation

**Total Monthly Budget: €10,000**

- Search: €6,000 (60%)
  - Branded: €500
  - Competitors: €2,000
  - Problem/Solution: €2,500
  - Industry: €1,000
- Display: €2,000 (20%)
  - Remarketing: €1,000
  - Similar: €500
  - Custom Intent: €500
- YouTube: €2,000 (20%)

**Target Metrics:**
- CPC: €2-5
- CTR: 3-5%
- Conversion Rate: 5-8%
- CAC: €50-100

## Search Campaigns

### Campaign 1: Branded Search

**Ad Groups:**
1. DealFlow Analytics
2. The Alternative VC Tool
3. Evgeny Goncharov Tool

**Keywords:**
```
[dealflow analytics]
[dealflow analytics chrome extension]
[dealflow ai]
[the alternative vc tool]
[evgeny goncharov ai]
"dealflow analytics"
"vc analysis tool"
```

**Ad Copy:**

```
Headline 1: DealFlow Analytics - Official
Headline 2: 74% Exit Prediction Accuracy
Headline 3: Built by VCs for VCs
Description 1: Chrome extension analyzing startups with 7 AI models. Used by 100+ VCs.
Description 2: Free trial. No credit card. See why The Alternative built this tool.
```

### Campaign 2: Competitor Targeting

**Ad Groups:**
1. PitchBook Alternatives
2. CB Insights Alternatives
3. Crunchbase Pro Alternatives
4. Signal AI Alternatives

**Keywords:**
```
+pitchbook +alternative
+pitchbook +pricing
+cb +insights +alternative
+crunchbase +pro +alternative
+signal +ai +vc
"pitchbook competitor"
"cb insights vs"
"crunchbase pro pricing"
"vc analysis tools"
```

**Ad Copy Variations:**

```
Ad 1: Better Than PitchBook
Headline 1: PitchBook Alternative - 74% Accurate
Headline 2: €149/mo vs €€€€ - See Why VCs Switch
Headline 3: 7 AI Models | Instant Analysis
Description 1: DealFlow Analytics costs 90% less than PitchBook. Better AI, faster analysis.
Description 2: Built by The Alternative VC firm. Try free - no credit card required.

Ad 2: Smarter Than CB Insights
Headline 1: CB Insights Alternative for VCs
Headline 2: Real AI Analysis - Not Just Data
Headline 3: €149/month | 100+ VCs Using It
Description 1: Why pay €1000s for data when AI can analyze better? 74% accuracy proven.
Description 2: Chrome extension works instantly on any startup. Free trial available.
```

### Campaign 3: Problem/Solution Keywords

**Ad Groups:**
1. Startup Analysis Problems
2. VC Efficiency Solutions
3. Due Diligence Automation
4. Deal Flow Management

**High-Intent Keywords:**
```
"how to analyze startups quickly"
"vc due diligence tools"
"automated startup analysis"
"ai for venture capital"
"deal flow management software"
"startup evaluation tool"
"vc productivity tools"
"investment analysis automation"
+analyze +startups +faster
+vc +tools +ai
+due +diligence +automation
+venture +capital +software
```

**Ad Copy Matrix:**

```
Problem-Focused Ad:
Headline 1: Drowning in Deal Flow?
Headline 2: Analyze 3x More Startups
Headline 3: 80% Less Time on Screening
Description 1: VCs save 20 hours/week with DealFlow Analytics. 7 AI models, instant analysis.
Description 2: Built by The Alternative VC firm. 74% accuracy. Try free today.

Solution-Focused Ad:
Headline 1: AI That Predicts Exits - 74% Accurate
Headline 2: Used by 100+ VCs Globally
Headline 3: Chrome Extension - Works Instantly
Description 1: One click on LinkedIn/Crunchbase = full analysis. 7 AI models working together.
Description 2: From the CTO of The Alternative. Free trial, no card required.

Urgency Ad:
Headline 1: Your Competitors Use AI for Deals
Headline 2: Don't Miss the Next Unicorn
Headline 3: Join 100+ VCs - Free Trial
Description 1: DealFlow Analytics found 3 unicorns others missed. 74% exit prediction accuracy.
Description 2: Limited time: 3 months free for new VCs. Install in 30 seconds.
```

### Campaign 4: Industry Terms

**Ad Groups:**
1. Venture Capital Software
2. Private Equity Tools
3. Investment Analysis
4. Startup Ecosystem

**Broader Keywords:**
```
"venture capital"
"vc firms"
"startup investing"
"seed investment"
"series a"
"startup valuation"
"investment thesis"
"portfolio management"
```

## Display Campaigns

### Remarketing Lists

**Audience Segments:**
1. Site visitors - didn't sign up (last 30 days)
2. Extension installed - not activated (last 14 days)
3. Free users - not upgraded (last 60 days)
4. Blog readers (last 90 days)

**Display Ad Sizes:**
- 300x250 (Medium Rectangle)
- 728x90 (Leaderboard)
- 160x600 (Wide Skyscraper)
- 320x50 (Mobile Banner)
- 300x600 (Half Page)

**Ad Creative Themes:**

```
Theme 1: Social Proof
Image: Screenshots with "100+ VCs" badge
Headline: "Join 100+ VCs Using DealFlow"
CTA: "Start Free Trial"

Theme 2: ROI Focus
Image: Graph showing 74% accuracy
Headline: "74% Exit Prediction Accuracy"
CTA: "See How It Works"

Theme 3: Competitor Comparison
Image: Price comparison chart
Headline: "90% Cheaper Than PitchBook"
CTA: "Try Free Today"
```

### Custom Intent Audiences

**Audience Definition:**
```javascript
// Target users researching these URLs/keywords
const customIntentAudience = {
  urls: [
    "pitchbook.com",
    "cbinsights.com", 
    "crunchbase.com/pro",
    "dealroom.co",
    "tracxn.com"
  ],
  keywords: [
    "vc tools",
    "startup analysis",
    "investment software",
    "due diligence automation"
  ]
};
```

## YouTube Campaigns

### Video Ad Scripts

**15-Second In-Stream Ad:**
```
[0-3s: Hook]
"VCs waste 20 hours a week on bad deals..."

[3-8s: Solution]
"DealFlow Analytics analyzes any startup in 1 second using 7 AI models"

[8-12s: Proof]
"74% accurate on exits. Used by 100+ VCs including The Alternative."

[12-15s: CTA]
"Free trial at dealflow-analytics.com"
```

**30-Second Story Ad:**
```
[0-5s: Problem]
"I'm Evgeny, CTO at The Alternative. We were drowning in deals, missing great opportunities."

[5-15s: Journey]
"So we built DealFlow Analytics. 7 AI models analyzing every startup instantly. The results? Incredible."

[15-25s: Results]
"80% less time screening. Found 3 unicorns in our reject pile. 74% accuracy on exit predictions."

[25-30s: CTA]
"Now 100+ VCs use it. Try free at dealflow-analytics.com"
```

### YouTube Targeting

**Audiences:**
1. Affinity: Venture Capital, Business Professionals
2. Custom Intent: Searching for VC tools
3. Remarketing: Website visitors
4. Similar: Based on converters

**Placements:**
- TechCrunch channel
- Y Combinator videos
- This Week in Startups
- All-In Podcast clips

## Landing Pages

### Landing Page Variants

**Variant A: Feature-Focused**
```
Headline: "Analyze Any Startup in 1 Second"
Subheadline: "7 AI Models. 74% Accuracy. Built by VCs."
CTA: "Start Free Trial"
Social Proof: Logo bar of VC firms
Features: Bullet points with icons
```

**Variant B: Problem-Solution**
```
Headline: "Stop Missing Great Deals"
Subheadline: "VCs using DealFlow find 3x more opportunities"
CTA: "Install Chrome Extension"
Case Study: Mini case with metrics
Demo: Embedded video
```

**Variant C: Competitor Comparison**
```
Headline: "Better Than PitchBook at 10% the Cost"
Subheadline: "See why 100+ VCs switched"
CTA: "See Comparison"
Table: Feature/price comparison
Testimonials: 3 VC quotes
```

## Conversion Tracking Setup

### Google Tag Manager Implementation

```javascript
// GTM Custom Events
dataLayer.push({
  'event': 'extension_installed',
  'value': 0,
  'currency': 'EUR'
});

dataLayer.push({
  'event': 'free_trial_started',
  'value': 0,
  'currency': 'EUR'
});

dataLayer.push({
  'event': 'pro_subscription',
  'value': 149,
  'currency': 'EUR'
});

dataLayer.push({
  'event': 'enterprise_lead',
  'value': 499,
  'currency': 'EUR'
});
```

### Conversion Actions

1. **Primary Conversions:**
   - Pro Subscription (€149 value)
   - Enterprise Lead (€499 value)

2. **Secondary Conversions:**
   - Extension Install (€10 value)
   - Free Trial Start (€20 value)
   - Demo Request (€50 value)

## Bidding Strategies

### Strategy by Campaign Type

**Branded Search:** Manual CPC
- Max CPC: €1
- Position target: 1-2

**Competitor Search:** Target CPA
- Target CPA: €75
- Learning period: 2 weeks

**Problem/Solution:** Maximize Conversions
- Daily budget: €100
- Conversion window: 30 days

**Display:** Target ROAS
- Target: 300%
- Bid cap: €5

**YouTube:** Maximum CPV
- Max CPV: €0.10
- View definition: 30s or completion

## Ad Extensions

### Sitelink Extensions
1. "Free Trial" → /free-trial
2. "See Pricing" → /pricing
3. "How It Works" → /demo
4. "VC Testimonials" → /testimonials
5. "vs PitchBook" → /compare

### Callout Extensions
- "74% Accuracy on Exits"
- "Built by VCs for VCs"
- "No Credit Card Required"
- "100+ VCs Using It"
- "7 AI Models"

### Structured Snippets
- **Types:** Software features
- **Values:** AI Analysis, Chrome Extension, Exit Predictions, Competitive Intelligence, Team Assessment

## Negative Keywords List

```
-free
-torrent
-crack
-tutorial
-how to build
-open source
-job
-jobs
-career
-salary
-intern
-internship
-course
-training
-certification
```

## A/B Testing Calendar

### Month 1: Baseline
- Test ad copy variations
- Landing page variants
- Bidding strategies

### Month 2: Optimization
- Audience expansion
- New ad formats
- Conversion path testing

### Month 3: Scale
- Budget reallocation
- Geographic expansion
- Video ad testing

## Reporting Dashboard

```python
# Weekly KPIs to Track
kpis = {
    "spend": {"target": 2500, "actual": 0},
    "impressions": {"target": 500000, "actual": 0},
    "clicks": {"target": 15000, "actual": 0},
    "ctr": {"target": 0.03, "actual": 0},
    "conversions": {"target": 100, "actual": 0},
    "cpa": {"target": 25, "actual": 0},
    "roas": {"target": 4.0, "actual": 0}
}

# Performance by Campaign Type
performance = {
    "search": {"spend": 0, "conversions": 0, "cpa": 0},
    "display": {"spend": 0, "conversions": 0, "cpa": 0},
    "youtube": {"spend": 0, "conversions": 0, "cpa": 0}
}
```

## Optimization Rules

### Automated Rules

1. **Pause Poor Performers**
   - If CPA > €150 after 50 clicks → Pause
   - If CTR < 1% after 1000 impressions → Pause

2. **Increase Winning Bids**
   - If Conv Rate > 10% → Increase bid 20%
   - If Quality Score = 10 → Increase bid 15%

3. **Budget Reallocation**
   - If ROAS > 5 → Increase budget 25%
   - If ROAS < 2 → Decrease budget 50%

## Scripts for Automation

```javascript
// Google Ads Script: Daily Performance Alert
function main() {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  
  const stats = AdWordsApp.currentAccount().getStatsFor(
    Utilities.formatDate(yesterday, 'PST', 'yyyyMMdd'),
    Utilities.formatDate(yesterday, 'PST', 'yyyyMMdd')
  );
  
  if (stats.getCost() > 500 && stats.getConversions() < 5) {
    MailApp.sendEmail(
      'evgeny@thealternative.vc',
      'ALERT: Low Conversion Day',
      `Yesterday's performance:
       Spend: €${stats.getCost()}
       Conversions: ${stats.getConversions()}
       CPA: €${stats.getCost() / stats.getConversions()}`
    );
  }
}
```