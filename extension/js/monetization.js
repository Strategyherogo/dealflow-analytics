// DealFlow Analytics - Monetization System
// Handles pricing, usage tracking, and payment integration

const PRICING = {
    free: {
        name: 'Free',
        price: 0,
        analyses: 10,
        features: [
            '10 analyses per month',
            'Basic AI scoring',
            'CSV export',
            'LinkedIn & Crunchbase'
        ]
    },
    pro: {
        name: 'Pro',
        price: 49,
        analyses: 100,
        features: [
            '100 analyses per month',
            '3 AI models (GPT-4, Claude, Groq)',
            'PDF & CSV export',
            'All websites',
            'Priority support'
        ]
    },
    premium: {
        name: 'Premium',
        price: 149,
        analyses: -1, // Unlimited
        features: [
            'Unlimited analyses',
            'All 7 AI models',
            'Advanced predictions',
            'Team collaboration',
            'API access',
            'White-glove support'
        ]
    },
    enterprise: {
        name: 'Enterprise',
        price: 499,
        analyses: -1,
        features: [
            'Everything in Premium',
            'Custom AI models',
            'SSO integration',
            'Dedicated account manager',
            'SLA guarantee',
            'Training & onboarding'
        ]
    }
};

class MonetizationManager {
    constructor() {
        this.currentPlan = 'free';
        this.usageCount = 0;
        this.usageLimit = PRICING.free.analyses;
        this.billingCycle = null;
        this.init();
    }

    async init() {
        // Load stored data
        const stored = await chrome.storage.sync.get(['plan', 'usage', 'billingCycle', 'customerId']);
        
        this.currentPlan = stored.plan || 'free';
        this.usageCount = stored.usage || 0;
        this.billingCycle = stored.billingCycle || this.getCurrentCycle();
        this.customerId = stored.customerId || null;
        
        // Reset usage if new billing cycle
        if (this.billingCycle !== this.getCurrentCycle()) {
            this.resetUsage();
        }
        
        this.usageLimit = PRICING[this.currentPlan].analyses;
    }

    getCurrentCycle() {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    }

    async resetUsage() {
        this.usageCount = 0;
        this.billingCycle = this.getCurrentCycle();
        await this.saveData();
    }

    async saveData() {
        await chrome.storage.sync.set({
            plan: this.currentPlan,
            usage: this.usageCount,
            billingCycle: this.billingCycle,
            customerId: this.customerId
        });
    }

    canAnalyze() {
        if (this.usageLimit === -1) return true; // Unlimited
        return this.usageCount < this.usageLimit;
    }

    async trackUsage() {
        this.usageCount++;
        await this.saveData();
        
        // Check if approaching limit
        if (this.usageLimit !== -1) {
            const remaining = this.usageLimit - this.usageCount;
            
            if (remaining === 0) {
                this.showUpgradePrompt('limit_reached');
            } else if (remaining === 3) {
                this.showUpgradePrompt('approaching_limit');
            }
        }
        
        return {
            used: this.usageCount,
            limit: this.usageLimit,
            remaining: this.usageLimit === -1 ? 'Unlimited' : this.usageLimit - this.usageCount
        };
    }

    showUpgradePrompt(reason) {
        const messages = {
            limit_reached: {
                title: '🚀 Monthly Limit Reached',
                message: 'You\'ve used all 10 free analyses this month. Upgrade to Pro for 100 analyses/month!',
                cta: 'Upgrade to Pro ($49/mo)'
            },
            approaching_limit: {
                title: '⚠️ Only 3 Analyses Left',
                message: 'You\'re almost at your monthly limit. Upgrade now for unlimited access!',
                cta: 'View Pricing'
            },
            feature_locked: {
                title: '🔒 Premium Feature',
                message: 'This feature requires a Pro or Premium subscription.',
                cta: 'Unlock Features'
            }
        };

        const prompt = messages[reason];
        
        // Create notification
        chrome.notifications.create({
            type: 'basic',
            iconUrl: chrome.runtime.getURL('icons/icon128.png'),
            title: prompt.title,
            message: prompt.message,
            buttons: [
                { title: prompt.cta },
                { title: 'Maybe Later' }
            ],
            priority: 2
        });
    }

    async initializePayment(plan) {
        // Open Stripe Checkout
        const checkoutUrl = await this.createCheckoutSession(plan);
        chrome.tabs.create({ url: checkoutUrl });
    }

    async createCheckoutSession(plan) {
        try {
            const response = await fetch('https://monkfish-app-7otbm.ondigitalocean.app/api/create-checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    plan: plan,
                    customerId: this.customerId,
                    extensionId: chrome.runtime.id
                })
            });

            const data = await response.json();
            return data.checkoutUrl;
        } catch (error) {
            console.error('Failed to create checkout session:', error);
            // Fallback to direct pricing page
            return 'https://dealflowanalytics.com/pricing';
        }
    }

    async verifySubscription() {
        if (!this.customerId) return false;
        
        try {
            const response = await fetch('https://monkfish-app-7otbm.ondigitalocean.app/api/verify-subscription', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    customerId: this.customerId
                })
            });

            const data = await response.json();
            
            if (data.active) {
                this.currentPlan = data.plan;
                this.usageLimit = PRICING[data.plan].analyses;
                await this.saveData();
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Failed to verify subscription:', error);
            return false;
        }
    }

    getUsageDisplay() {
        if (this.usageLimit === -1) {
            return `Unlimited analyses`;
        }
        
        const remaining = this.usageLimit - this.usageCount;
        const percentage = (this.usageCount / this.usageLimit) * 100;
        
        return {
            text: `${remaining} of ${this.usageLimit} analyses left`,
            percentage: percentage,
            color: percentage > 80 ? '#ef4444' : percentage > 60 ? '#f59e0b' : '#10b981'
        };
    }

    isPremiumFeature(feature) {
        const premiumFeatures = [
            'pdf_export',
            'team_sharing',
            'api_access',
            'advanced_ai',
            'exit_prediction',
            'pattern_recognition'
        ];
        
        const featureRequirements = {
            pdf_export: ['pro', 'premium', 'enterprise'],
            team_sharing: ['premium', 'enterprise'],
            api_access: ['premium', 'enterprise'],
            advanced_ai: ['premium', 'enterprise'],
            exit_prediction: ['premium', 'enterprise'],
            pattern_recognition: ['enterprise']
        };
        
        if (!premiumFeatures.includes(feature)) return false;
        
        const requiredPlans = featureRequirements[feature];
        return !requiredPlans.includes(this.currentPlan);
    }

    async handleFeatureRequest(feature) {
        if (this.isPremiumFeature(feature)) {
            this.showUpgradePrompt('feature_locked');
            return false;
        }
        return true;
    }
}

// Export for use in other scripts
window.MonetizationManager = MonetizationManager;

// Initialize on load
const monetization = new MonetizationManager();

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'check_usage') {
        sendResponse({
            canAnalyze: monetization.canAnalyze(),
            usage: monetization.getUsageDisplay(),
            plan: monetization.currentPlan
        });
    } else if (request.action === 'track_usage') {
        monetization.trackUsage().then(sendResponse);
        return true; // Keep channel open for async response
    } else if (request.action === 'upgrade') {
        monetization.initializePayment(request.plan);
    } else if (request.action === 'verify_subscription') {
        monetization.verifySubscription().then(sendResponse);
        return true;
    }
});

// Check subscription status on startup
chrome.runtime.onStartup.addListener(() => {
    monetization.verifySubscription();
});

// Handle notification button clicks
chrome.notifications.onButtonClicked.addListener((notificationId, buttonIndex) => {
    if (buttonIndex === 0) {
        // Open pricing page
        chrome.tabs.create({ url: 'https://dealflowanalytics.com/pricing' });
    }
});