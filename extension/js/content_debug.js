// Debug version of content script
console.log('[DealFlow Analytics] Content script loaded on:', window.location.href);

// Test if we're on a supported page
const url = window.location.href;
const isLinkedIn = url.includes('linkedin.com/company/');
const isCrunchbase = url.includes('crunchbase.com/organization/');

console.log('[DealFlow Analytics] Is LinkedIn company page:', isLinkedIn);
console.log('[DealFlow Analytics] Is Crunchbase page:', isCrunchbase);

// Try to find company name with various selectors
const selectors = [
    // LinkedIn selectors
    'h1.org-top-card-summary__title',
    'h1.top-card-layout__title', 
    'h1[data-test-org-page-name]',
    '.org-top-card__primary-content h1',
    'h1.text-heading-xlarge',
    'h1 span[dir="ltr"]',
    // Generic h1
    'h1',
    // Crunchbase selectors
    'h1[data-test="profile-name"]'
];

console.log('[DealFlow Analytics] Testing selectors...');

selectors.forEach(selector => {
    const element = document.querySelector(selector);
    if (element) {
        console.log(`[DealFlow Analytics] Found with selector "${selector}":`, element.textContent.trim());
    }
});

// Also log the page structure
console.log('[DealFlow Analytics] Page title:', document.title);
console.log('[DealFlow Analytics] First h1 on page:', document.querySelector('h1')?.textContent);

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('[DealFlow Analytics] Received message:', request);
    
    if (request.action === 'getCompanyData') {
        // Simple test response
        const testData = {
            name: document.title.split('|')[0].trim() || 'Unknown Company',
            url: window.location.href,
            source: 'debug',
            extractedAt: new Date().toISOString()
        };
        
        console.log('[DealFlow Analytics] Sending test data:', testData);
        sendResponse({ success: true, data: testData });
    }
    
    return true;
});