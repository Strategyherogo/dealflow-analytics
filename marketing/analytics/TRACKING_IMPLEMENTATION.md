# Marketing Analytics & Tracking Implementation
## Complete Measurement Framework for DealFlow Analytics

### Analytics Architecture Overview

```
Data Flow:
Website → GA4 → BigQuery → Looker/Tableau → Decisions
Extension → Mixpanel → Segment → Warehouse → Insights
CRM → HubSpot → Zapier → PostgreSQL → Reports
Ads → Platform APIs → Supermetrics → Sheets → Analysis
```

---

## Google Analytics 4 Implementation

### Base Configuration

```javascript
// GA4 Global Site Tag Implementation
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  
  gtag('config', 'G-XXXXXXXXXX', {
    'user_properties': {
      'user_type': getUserType(), // free, trial, pro, enterprise
      'firm_size': getFirmSize(),
      'signup_date': getSignupDate(),
      'referral_source': getReferralSource()
    }
  });
</script>
```

### Enhanced Ecommerce Events

```javascript
// Track extension installation
gtag('event', 'begin_checkout', {
  'items': [{
    'item_id': 'dealflow-chrome-ext',
    'item_name': 'DealFlow Analytics Chrome Extension',
    'item_category': 'Software',
    'item_variant': 'Chrome',
    'price': 0,
    'currency': 'USD'
  }]
});

// Track trial start
gtag('event', 'begin_trial', {
  'value': 149, // Potential monthly value
  'currency': 'USD',
  'trial_type': 'free_trial',
  'trial_length': 14
});

// Track subscription
gtag('event', 'purchase', {
  'transaction_id': generateTransactionId(),
  'value': getPlanValue(),
  'currency': 'USD',
  'items': [{
    'item_id': getPlanId(),
    'item_name': getPlanName(),
    'item_category': 'Subscription',
    'price': getPlanPrice(),
    'quantity': 1
  }]
});

// Track feature usage
gtag('event', 'feature_use', {
  'feature_name': 'ai_analysis',
  'feature_category': 'core',
  'company_analyzed': getCompanyDomain(),
  'ai_models_used': getModelsUsed(),
  'analysis_time': getAnalysisTime()
});
```

### Custom Dimensions & Metrics

```javascript
// Custom Dimensions Setup
const customDimensions = {
  'subscription_status': 'dimension1',
  'firm_name': 'dimension2',
  'plan_type': 'dimension3',
  'install_date': 'dimension4',
  'last_analysis_date': 'dimension5',
  'total_analyses': 'metric1',
  'team_members': 'metric2',
  'monthly_revenue': 'metric3'
};

// Send custom data
gtag('event', 'page_view', {
  'custom_dimension_1': user.subscriptionStatus,
  'custom_dimension_2': user.firmName,
  'custom_metric_1': user.totalAnalyses
});
```

---

## Mixpanel Product Analytics

### Implementation Setup

```javascript
// Mixpanel Initialization
<script type="text/javascript">
(function(f,b){if(!b.__SV){var e,g,i,h;window.mixpanel=b;b._i=[];b.init=function(e,f,c){
// ... standard Mixpanel snippet
})(document,window.mixpanel||[]);

mixpanel.init('YOUR_PROJECT_TOKEN', {
  track_pageview: true,
  persistence: 'localStorage',
  api_host: 'https://api.mixpanel.com'
});
</script>
```

### User Identification & Properties

```javascript
// Identify user on signup/login
mixpanel.identify(user.id);

mixpanel.people.set({
  '$email': user.email,
  '$name': user.name,
  'Firm Name': user.firmName,
  'Plan Type': user.planType,
  'Signup Date': user.signupDate,
  'User Role': user.role,
  'Team Size': user.teamSize,
  'AUM Range': user.aumRange,
  'Investment Focus': user.investmentFocus,
  'Geographic Focus': user.geographicFocus
});

// Track super properties (sent with every event)
mixpanel.register({
  'Platform': 'Chrome Extension',
  'Version': extensionVersion,
  'Plan Type': user.planType
});
```

### Core Event Tracking

```javascript
// Extension Events
const extensionEvents = {
  // Installation & Setup
  'Extension Installed': {
    source: installSource,
    referrer: document.referrer,
    campaign: getUTMParams()
  },
  
  'Account Created': {
    method: signupMethod,
    plan: selectedPlan,
    teamSize: teamSize
  },
  
  // Core Usage
  'Analysis Started': {
    companyURL: url,
    companyName: extractCompanyName(url),
    analysisType: 'full' | 'quick',
    modelsSelected: selectedModels,
    source: 'popup' | 'contextMenu' | 'hotkey'
  },
  
  'Analysis Completed': {
    companyURL: url,
    timeSpent: analysisTime,
    modelsUsed: modelsUsed,
    consensusScore: score,
    userAction: 'saved' | 'shared' | 'exported' | 'dismissed'
  },
  
  'Feature Used': {
    featureName: feature,
    featureCategory: category,
    usageContext: context,
    timeSpent: duration
  },
  
  // Collaboration
  'Team Member Invited': {
    inviteMethod: method,
    recipientDomain: domain,
    teamSize: currentTeamSize
  },
  
  'Analysis Shared': {
    shareMethod: 'link' | 'email' | 'slack',
    recipientCount: count,
    includesNotes: hasNotes
  },
  
  // Conversion Events
  'Trial Started': {
    planInterest: plan,
    triggeredBy: trigger,
    analysesCompleted: count
  },
  
  'Subscription Started': {
    plan: planType,
    price: monthlyPrice,
    billingPeriod: 'monthly' | 'annual',
    paymentMethod: method,
    couponUsed: coupon
  },
  
  'Subscription Cancelled': {
    reason: cancellationReason,
    daysSinceStart: days,
    totalAnalyses: analyses,
    suggestion: feedback
  }
};

// Track events
Object.entries(extensionEvents).forEach(([eventName, properties]) => {
  mixpanel.track(eventName, properties);
});
```

### Funnel Analysis Setup

```javascript
// Key Funnels to Track
const funnels = {
  'Activation Funnel': [
    'Extension Installed',
    'Account Created',
    'First Analysis Started',
    'First Analysis Completed',
    'Second Analysis Started'
  ],
  
  'Conversion Funnel': [
    'Extension Installed',
    'Trial Started',
    'Payment Method Added',
    'Subscription Started'
  ],
  
  'Team Adoption Funnel': [
    'Account Created',
    'Team Member Invited',
    'Invite Accepted',
    'Team Analysis Shared',
    'Team Collaboration'
  ],
  
  'Feature Adoption Funnel': [
    'Analysis Completed',
    'Advanced Feature Discovered',
    'Advanced Feature Used',
    'Feature Used Again'
  ]
};
```

---

## HubSpot CRM Integration

### Contact Properties Setup

```javascript
// Custom Properties for VC Contacts
const hubspotProperties = {
  // Firm Information
  'firm_name': 'text',
  'firm_size': 'dropdown', // 1-5, 6-10, 11-25, 26-50, 50+
  'aum_range': 'dropdown', // <$10M, $10-50M, $50-250M, $250M-1B, >$1B
  'investment_stage': 'multi-checkbox', // Pre-seed, Seed, Series A, B, C+
  'sector_focus': 'multi-checkbox', // B2B SaaS, Consumer, Fintech, etc.
  
  // Product Usage
  'extension_installed': 'boolean',
  'installation_date': 'date',
  'last_analysis_date': 'date',
  'total_analyses': 'number',
  'plan_type': 'dropdown', // Free, Trial, Pro, Enterprise
  'mrr_value': 'number',
  
  // Engagement Scoring
  'product_qualified_lead': 'boolean',
  'engagement_score': 'number', // 0-100
  'health_score': 'dropdown', // Green, Yellow, Red
  'churn_risk': 'dropdown', // Low, Medium, High
  
  // Attribution
  'original_source': 'text',
  'utm_campaign': 'text',
  'referral_source': 'text',
  'first_touch_content': 'text'
};
```

### Workflow Automation

```javascript
// HubSpot Workflow Triggers
const workflows = {
  'Trial Nurture Sequence': {
    trigger: 'Trial Started',
    enrollment: 'automatic',
    actions: [
      { delay: '1 hour', action: 'Send Welcome Email' },
      { delay: '1 day', action: 'Send Quick Win Tutorial' },
      { delay: '3 days', action: 'Send Feature Discovery' },
      { delay: '7 days', action: 'Send Success Story' },
      { delay: '10 days', action: 'Check Usage', 
        branch: {
          if: 'analyses > 5',
          then: 'Send Upgrade Offer',
          else: 'Send Activation Help'
        }
      },
      { delay: '13 days', action: 'Send Trial Ending Warning' },
      { delay: '14 days', action: 'Send Last Chance Offer' }
    ]
  },
  
  'High-Value Lead Alert': {
    trigger: 'Lead Score > 80',
    enrollment: 'automatic',
    actions: [
      { immediate: 'Notify Sales Team' },
      { immediate: 'Assign to Account Executive' },
      { immediate: 'Send Calendly Link' },
      { immediate: 'Add to High-Priority List' }
    ]
  },
  
  'Churn Prevention': {
    trigger: 'Health Score = Red',
    enrollment: 'automatic',
    actions: [
      { immediate: 'Alert Customer Success' },
      { immediate: 'Send Re-engagement Email' },
      { delay: '3 days', action: 'Offer Success Call' },
      { delay: '7 days', action: 'Send Feature Tutorial' },
      { delay: '14 days', action: 'Offer Discount' }
    ]
  }
};
```

### Lead Scoring Model

```javascript
// Progressive Lead Scoring
const leadScoringRules = {
  // Demographic Scoring (0-40 points)
  firmographics: {
    'AUM > $100M': 10,
    'Team Size > 5': 8,
    'Target Investment Stage Match': 7,
    'Geographic Match': 5,
    'Sector Focus Match': 5,
    'Decision Maker Title': 5
  },
  
  // Behavioral Scoring (0-60 points)
  behaviors: {
    'Extension Installed': 15,
    'Completed 5+ Analyses': 10,
    'Invited Team Members': 10,
    'Used Advanced Features': 8,
    'Viewed Pricing Page': 7,
    'Downloaded Case Study': 5,
    'Attended Webinar': 5
  },
  
  // Negative Scoring
  negativeSignals: {
    'Unsubscribed from Emails': -20,
    'No Activity 30+ Days': -10,
    'Support Ticket Unresolved': -5,
    'Competitor Employee': -50
  }
};

// Calculate MQL Threshold
const MQL_THRESHOLD = 65;
const SQL_THRESHOLD = 80;
```

---

## Attribution Modeling

### Multi-Touch Attribution Setup

```javascript
// Attribution Model Configuration
const attributionModels = {
  'First Touch': {
    credit: { first: 100 },
    useCase: 'Top of funnel optimization'
  },
  
  'Last Touch': {
    credit: { last: 100 },
    useCase: 'Conversion optimization'
  },
  
  'Linear': {
    credit: 'equal distribution',
    useCase: 'Full journey understanding'
  },
  
  'Time Decay': {
    halfLife: 7, // days
    useCase: 'Recent influence weighting'
  },
  
  'U-Shaped': {
    credit: { first: 40, last: 40, middle: 20 },
    useCase: 'Balanced attribution'
  },
  
  'Custom Data-Driven': {
    algorithm: 'Shapley Value',
    useCase: 'ML-based attribution'
  }
};

// Track touchpoints
const trackTouchpoint = (user, source, medium, campaign, content) => {
  const touchpoint = {
    userId: user.id,
    timestamp: Date.now(),
    source: source,
    medium: medium,
    campaign: campaign,
    content: content,
    sessionId: getSessionId(),
    deviceId: getDeviceId()
  };
  
  // Store in attribution database
  saveToAttributionDB(touchpoint);
  
  // Send to analytics platforms
  gtag('event', 'touchpoint', touchpoint);
  mixpanel.track('Marketing Touchpoint', touchpoint);
};
```

### Channel Attribution Tracking

```javascript
// UTM Parameter Processing
const processUTMParams = () => {
  const params = new URLSearchParams(window.location.search);
  
  const utm = {
    source: params.get('utm_source') || 'direct',
    medium: params.get('utm_medium') || 'none',
    campaign: params.get('utm_campaign') || 'none',
    term: params.get('utm_term') || '',
    content: params.get('utm_content') || ''
  };
  
  // Store in cookie for 30 days
  setCookie('utm_params', JSON.stringify(utm), 30);
  
  // Store first touch (if new user)
  if (!getCookie('first_touch')) {
    setCookie('first_touch', JSON.stringify({
      ...utm,
      timestamp: Date.now(),
      landingPage: window.location.pathname
    }), 365);
  }
  
  // Store last touch (always update)
  setCookie('last_touch', JSON.stringify({
    ...utm,
    timestamp: Date.now()
  }), 30);
  
  return utm;
};
```

---

## Custom Dashboard Creation

### Executive Dashboard Metrics

```sql
-- Daily Executive Dashboard Query
WITH daily_metrics AS (
  SELECT 
    DATE(timestamp) as date,
    COUNT(DISTINCT user_id) as dau,
    COUNT(CASE WHEN event = 'Extension Installed' THEN 1 END) as new_installs,
    COUNT(CASE WHEN event = 'Trial Started' THEN 1 END) as trials_started,
    COUNT(CASE WHEN event = 'Subscription Started' THEN 1 END) as new_paid,
    SUM(CASE WHEN event = 'Subscription Started' THEN revenue END) as new_mrr,
    COUNT(CASE WHEN event = 'Analysis Completed' THEN 1 END) as analyses_completed
  FROM events
  WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY DATE(timestamp)
),
cohort_metrics AS (
  SELECT 
    DATE_TRUNC('week', first_seen) as cohort_week,
    COUNT(DISTINCT user_id) as cohort_size,
    AVG(CASE WHEN converted THEN 1 ELSE 0 END) as conversion_rate,
    AVG(days_to_convert) as avg_conversion_time
  FROM users
  WHERE first_seen >= CURRENT_DATE - INTERVAL '90 days'
  GROUP BY DATE_TRUNC('week', first_seen)
)
SELECT 
  d.*,
  c.conversion_rate as weekly_conversion_rate,
  c.avg_conversion_time
FROM daily_metrics d
LEFT JOIN cohort_metrics c ON DATE_TRUNC('week', d.date) = c.cohort_week
ORDER BY d.date DESC;
```

### Marketing Channel Performance

```sql
-- Channel Attribution Performance
WITH channel_performance AS (
  SELECT 
    utm_source,
    utm_medium,
    utm_campaign,
    COUNT(DISTINCT user_id) as users,
    COUNT(CASE WHEN trial_started THEN 1 END) as trials,
    COUNT(CASE WHEN converted THEN 1 END) as customers,
    SUM(revenue) as total_revenue,
    AVG(cost) as avg_cac
  FROM marketing_attribution
  WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY utm_source, utm_medium, utm_campaign
)
SELECT 
  *,
  ROUND(trials::DECIMAL / NULLIF(users, 0) * 100, 2) as trial_rate,
  ROUND(customers::DECIMAL / NULLIF(trials, 0) * 100, 2) as conversion_rate,
  ROUND(total_revenue / NULLIF(customers, 0), 2) as avg_revenue_per_customer,
  ROUND(total_revenue / NULLIF(avg_cac, 0), 2) as roas
FROM channel_performance
ORDER BY total_revenue DESC;
```

---

## Real-Time Monitoring & Alerts

### Alert Configuration

```javascript
// Critical Business Metrics Alerts
const alertRules = {
  'Conversion Rate Drop': {
    metric: 'trial_to_paid_rate',
    threshold: 0.15, // Alert if drops below 15%
    lookback: '7 days',
    comparison: 'previous_period',
    severity: 'high',
    notify: ['founder@dealflow.ai', 'growth@dealflow.ai']
  },
  
  'Extension Errors Spike': {
    metric: 'error_rate',
    threshold: 0.05, // Alert if exceeds 5%
    lookback: '1 hour',
    comparison: 'absolute',
    severity: 'critical',
    notify: ['eng@dealflow.ai', 'support@dealflow.ai']
  },
  
  'CAC Increase': {
    metric: 'customer_acquisition_cost',
    threshold: 1.3, // Alert if 30% increase
    lookback: '30 days',
    comparison: 'previous_month',
    severity: 'medium',
    notify: ['marketing@dealflow.ai']
  },
  
  'Churn Spike': {
    metric: 'monthly_churn_rate',
    threshold: 0.10, // Alert if exceeds 10%
    lookback: '30 days',
    comparison: 'absolute',
    severity: 'high',
    notify: ['founder@dealflow.ai', 'cs@dealflow.ai']
  }
};

// Alert monitoring function
const monitorMetrics = async () => {
  for (const [alertName, rule] of Object.entries(alertRules)) {
    const currentValue = await getMetricValue(rule.metric, rule.lookback);
    const shouldAlert = evaluateThreshold(currentValue, rule);
    
    if (shouldAlert) {
      await sendAlert({
        name: alertName,
        severity: rule.severity,
        currentValue: currentValue,
        threshold: rule.threshold,
        recipients: rule.notify,
        dashboard: `https://analytics.dealflow.ai/alerts/${alertName}`
      });
    }
  }
};

// Run monitoring every 5 minutes
setInterval(monitorMetrics, 5 * 60 * 1000);
```

---

## Privacy & Compliance

### GDPR/CCPA Compliance

```javascript
// Cookie Consent Implementation
const cookieConsent = {
  init: () => {
    if (!getCookie('cookie_consent')) {
      showConsentBanner();
    }
  },
  
  categories: {
    necessary: true, // Always enabled
    analytics: false,
    marketing: false,
    preferences: false
  },
  
  handleConsent: (categories) => {
    // Store consent
    setCookie('cookie_consent', JSON.stringify(categories), 365);
    
    // Initialize based on consent
    if (categories.analytics) {
      initializeGA4();
      initializeMixpanel();
    }
    
    if (categories.marketing) {
      initializeAdPixels();
      initializeRetargeting();
    }
    
    // Log consent for compliance
    logConsent({
      userId: getUserId(),
      timestamp: Date.now(),
      categories: categories,
      ipAddress: getIPAddress(),
      userAgent: navigator.userAgent
    });
  },
  
  updateConsent: (categories) => {
    // Handle consent updates
    cookieConsent.handleConsent(categories);
    
    // Remove non-consented cookies
    if (!categories.analytics) {
      deleteCookie('_ga');
      deleteCookie('_gid');
      deleteCookie('mp_');
    }
  }
};
```

### Data Retention Policies

```javascript
// Automated Data Retention
const dataRetention = {
  policies: {
    'raw_events': 90, // days
    'user_profiles': 730, // 2 years
    'aggregated_data': 1095, // 3 years
    'financial_records': 2555 // 7 years
  },
  
  cleanup: async () => {
    for (const [dataType, retentionDays] of Object.entries(dataRetention.policies)) {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - retentionDays);
      
      await deleteDataOlderThan(dataType, cutoffDate);
    }
  }
};

// Run cleanup daily
schedule.daily(dataRetention.cleanup);
```