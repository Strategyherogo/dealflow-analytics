// DealFlow Analytics - Enhanced LinkedIn Content Script
console.log('[DealFlow] LinkedIn content script loaded');

// Helper function to extract text safely
function safeText(element) {
    return element ? element.textContent.trim() : '';
}

// Extract LinkedIn company data
function extractLinkedInData() {
    console.log('[DealFlow] Extracting LinkedIn company data...');
    
    const data = {
        source: 'linkedin',
        url: window.location.href,
        extractedAt: new Date().toISOString()
    };
    
    // Check if we're on a company page
    if (!window.location.pathname.includes('/company/')) {
        console.log('[DealFlow] Not a company page');
        return null;
    }
    
    // Wait a bit for dynamic content to load
    setTimeout(() => {
        // Company name - multiple selectors for different LinkedIn layouts
        const nameSelectors = [
            'h1.org-top-card-summary__title',
            'h1.org-top-card__primary-content',
            'h1[data-test-org-top-card-summary-title]',
            '.org-top-card-summary__title span',
            '.org-page-details__definition-text',
            'h1 span.t-24'
        ];
        
        for (const selector of nameSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                data.name = safeText(element);
                console.log('[DealFlow] Found company name:', data.name);
                break;
            }
        }
        
        // Industry
        const industrySelectors = [
            '.org-top-card-summary-info-list__info-item:has(.org-top-card-summary-info-list__industries)',
            '.org-top-card-summary-info-list__info-item',
            '.org-page-details__definition-text',
            '[data-test-org-top-card-summary-industry]'
        ];
        
        for (const selector of industrySelectors) {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                const text = safeText(el);
                if (text && !text.includes('followers') && !text.includes('employees') && text.length < 100) {
                    data.industry = text;
                    console.log('[DealFlow] Found industry:', data.industry);
                }
            });
            if (data.industry) break;
        }
        
        // Employee count - look for various formats
        const employeeSelectors = [
            '.org-top-card-summary-info-list__info-item:has(.org-top-card-summary-info-list__employees)',
            '.org-top-card-summary-info-list__info-item',
            '.org-about-company-module__company-size-definition-text',
            '[data-test-org-about-company-module__employees]',
            '.text-body-small:has-text("employees")',
            '.org-page-details__employees-on-linkedin-count'
        ];
        
        // Try multiple approaches to find employee count
        const pageText = document.body.innerText;
        
        // Pattern 1: "X employees" or "X+ employees"
        const patterns = [
            /(\d{1,3}(?:,\d{3})*(?:\+)?)\s*employees\s*on\s*LinkedIn/i,
            /(\d{1,3}(?:,\d{3})*(?:\+)?)\s*employees/i,
            /(\d{1,3}(?:,\d{3})*)-(\d{1,3}(?:,\d{3})*)\s*employees/i,
            /Company size[:\s]*(\d{1,3}(?:,\d{3})*(?:\+)?)\s*employees/i
        ];
        
        for (const pattern of patterns) {
            const match = pageText.match(pattern);
            if (match) {
                if (match[2]) {
                    // Range format: "X-Y employees"
                    data.employeeCount = `${match[1]}-${match[2]} employees`;
                } else {
                    data.employeeCount = match[0].replace(/\s+/g, ' ').trim();
                }
                console.log('[DealFlow] Found employee count via regex:', data.employeeCount);
                break;
            }
        }
        
        // If not found via regex, try selectors
        if (!data.employeeCount) {
            for (const selector of employeeSelectors) {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    const text = safeText(el);
                    if (text && text.includes('employee')) {
                        data.employeeCount = text;
                        console.log('[DealFlow] Found employee count via selector:', data.employeeCount);
                    }
                });
                if (data.employeeCount) break;
            }
        }
        
        // Description/About
        const aboutSelectors = [
            '.org-top-card-summary__tagline',
            '.org-top-card__primary-content .break-words',
            '.org-about-us-organization-description',
            '[data-test-org-about-us-description]',
            '.org-page-details__definition-text'
        ];
        
        for (const selector of aboutSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                const text = safeText(element);
                if (text && text.length > 20) {
                    data.description = text.substring(0, 500);
                    console.log('[DealFlow] Found description');
                    break;
                }
            }
        }
        
        // Headquarters/Location
        const locationSelectors = [
            '.org-top-card-summary-info-list__info-item:has(.org-top-card-summary-info-list__headquarters)',
            '.org-locations-module__headquarters',
            '.org-page-details__definition-text'
        ];
        
        for (const selector of locationSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                const text = safeText(element);
                if (text && text.length < 100 && !text.includes('employees') && !text.includes('follower')) {
                    data.headquarters = text;
                    console.log('[DealFlow] Found headquarters:', data.headquarters);
                    break;
                }
            }
        }
        
        // Website
        const websiteSelectors = [
            '.org-top-card-primary-actions__action--website',
            'a[data-control-name="top_card_primary_button"]',
            '.org-about-company-module__company-page-url a'
        ];
        
        for (const selector of websiteSelectors) {
            const element = document.querySelector(selector);
            if (element && element.href) {
                data.website = element.href;
                console.log('[DealFlow] Found website:', data.website);
                break;
            }
        }
        
        // Extract domain from URL or website
        if (!data.domain) {
            if (data.website) {
                try {
                    const url = new URL(data.website);
                    data.domain = url.hostname.replace('www.', '');
                } catch (e) {
                    console.error('[DealFlow] Error parsing website URL:', e);
                }
            } else if (data.url.includes('/company/')) {
                // Extract from LinkedIn URL
                const companySlug = data.url.split('/company/')[1].split('/')[0];
                data.linkedinSlug = companySlug;
            }
        }
        
        console.log('[DealFlow] Final extracted data:', data);
        return data;
    }, 1000); // Wait for dynamic content
    
    return data;
}

// Message listener
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('[DealFlow] Received message:', request);
    
    if (request.action === 'getCompanyData') {
        // For LinkedIn, we need to wait for content to load
        if (window.location.hostname.includes('linkedin.com')) {
            setTimeout(() => {
                const data = extractLinkedInData();
                if (data && data.name) {
                    sendResponse({ success: true, data: data });
                } else {
                    // Fallback to basic extraction
                    const basicData = {
                        name: document.title.split(' | LinkedIn')[0].trim(),
                        source: 'linkedin',
                        url: window.location.href,
                        extractedAt: new Date().toISOString()
                    };
                    sendResponse({ success: true, data: basicData });
                }
            }, 1500); // Give LinkedIn time to load
            
            return true; // Keep message channel open for async response
        }
    }
});

// Auto-extract on page load for testing
if (window.location.hostname.includes('linkedin.com') && window.location.pathname.includes('/company/')) {
    setTimeout(() => {
        const data = extractLinkedInData();
        console.log('[DealFlow] Auto-extracted data:', data);
    }, 2000);
}