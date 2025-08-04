// DealFlow Analytics - Final Content Script
console.log('[DealFlow] Content script loaded on:', window.location.href);

// Message listener
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('[DealFlow] Received message:', request);
    
    if (request.action === 'getCompanyData') {
        // Simple extraction from page title
        let companyName = 'Unknown Company';
        let companyData = {
            source: 'unknown',
            url: window.location.href,
            extractedAt: new Date().toISOString()
        };
        
        // Extract from title
        const title = document.title;
        if (title.includes(' | LinkedIn')) {
            companyName = title.split(' | LinkedIn')[0].trim();
            companyData.source = 'linkedin';
        } else if (title.includes(' | Crunchbase')) {
            companyName = title.split(' | Crunchbase')[0].trim();
            companyData.source = 'crunchbase';
        } else {
            // For other websites, try common patterns
            // Remove common suffixes
            const suffixes = [
                ' - Home', ' | Home', ' - Official Website', ' | Official Site', 
                ' - About', ' | About', ' – Home', ' — Home', ' · Home',
                ': Home', ' Home', ' - Welcome', ' | Welcome'
            ];
            let cleanTitle = title;
            for (const suffix of suffixes) {
                if (cleanTitle.includes(suffix)) {
                    cleanTitle = cleanTitle.split(suffix)[0].trim();
                    break;
                }
            }
            
            // Remove common prefixes
            const prefixes = ['Welcome to ', 'Home - ', 'Home | '];
            for (const prefix of prefixes) {
                if (cleanTitle.startsWith(prefix)) {
                    cleanTitle = cleanTitle.substring(prefix.length).trim();
                    break;
                }
            }
            
            // Clean up the title
            cleanTitle = cleanTitle.replace(/\.(com|io|ai|co|org|net|app|dev)$/i, '');
            cleanTitle = cleanTitle.replace(/^\W+|\W+$/g, ''); // Remove leading/trailing non-word chars
            
            // If it's a reasonable company name, use it
            if (cleanTitle.length < 50 && cleanTitle.length > 1 && !cleanTitle.includes('<')) {
                companyName = cleanTitle;
                companyData.source = 'website';
            }
            
            // Try to get company name from domain
            if (companyName === 'Unknown Company' || companyName.length <= 1) {
                const domain = window.location.hostname.replace('www.', '');
                const domainParts = domain.split('.');
                if (domainParts.length > 0) {
                    let domainName = domainParts[0];
                    // Handle special cases
                    if (domainName === 'github' && window.location.pathname.length > 1) {
                        // For GitHub, use org name from URL
                        const pathParts = window.location.pathname.split('/');
                        if (pathParts[1]) {
                            domainName = pathParts[1];
                        }
                    }
                    // Capitalize properly (handle names like "cohere", "openai")
                    if (domainName.toLowerCase() === 'openai') {
                        companyName = 'OpenAI';
                    } else {
                        companyName = domainName.charAt(0).toUpperCase() + domainName.slice(1);
                    }
                    companyData.source = 'domain';
                }
            }
            
            // Try to extract from meta tags as last resort
            if (companyName === 'Unknown Company') {
                const metaOgSite = document.querySelector('meta[property="og:site_name"]');
                if (metaOgSite && metaOgSite.content) {
                    companyName = metaOgSite.content;
                    companyData.source = 'meta';
                }
            }
        }
        
        // Set company name
        companyData.name = companyName;
        
        // Extract domain
        if (companyData.source === 'website' || companyData.source === 'domain') {
            companyData.domain = window.location.hostname.replace('www.', '');
        }
        
        // Try to get more data if on LinkedIn company page
        if (window.location.href.includes('linkedin.com/company/')) {
            // Simple industry detection from page text
            const pageText = document.body.innerText;
            
            // Common industries to look for
            const industries = ['Technology', 'Software', 'Financial Services', 'Healthcare', 'E-commerce'];
            for (const industry of industries) {
                if (pageText.includes(industry)) {
                    companyData.industry = industry;
                    break;
                }
            }
            
            // Employee count
            const employeeMatch = pageText.match(/(\d{1,3}(?:,\d{3})*(?:\+)?)\s*employees/i);
            if (employeeMatch) {
                companyData.employeeCount = employeeMatch[0];
            }
        }
        
        console.log('[DealFlow] Sending data:', companyData);
        sendResponse({ success: true, data: companyData });
    }
    
    return true; // Keep channel open
});

// Notify that we're ready
console.log('[DealFlow] Content script ready!');

// Optional: Send a message to background script that we're loaded
if (window.location.href.includes('linkedin.com/company/') || window.location.href.includes('crunchbase.com/organization/')) {
    chrome.runtime.sendMessage({
        action: 'contentScriptReady',
        url: window.location.href
    }, response => {
        if (chrome.runtime.lastError) {
            console.log('[DealFlow] Background script not responding');
        }
    });
}