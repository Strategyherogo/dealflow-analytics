// DealFlow Analytics - Popup Script

const API_BASE_URL = 'https://monkfish-app-7otbm.ondigitalocean.app/api';

// Import monetization
const script = document.createElement('script');
script.src = 'js/monetization.js';
document.head.appendChild(script);

// DOM Elements
const elements = {
    status: document.getElementById('status'),
    loading: document.getElementById('loading'),
    error: document.getElementById('error'),
    errorMessage: document.getElementById('error-message'),
    mainContent: document.getElementById('main-content'),
    companyName: document.getElementById('company-name'),
    companyInfo: document.getElementById('company-info'),
    companyDetected: document.getElementById('company-detected'),
    noCompany: document.getElementById('no-company'),
    investmentScore: document.getElementById('investment-score'),
    fundingHistory: document.getElementById('funding-history'),
    growthSignals: document.getElementById('growth-signals'),
    marketAnalysis: document.getElementById('market-analysis'),
    aiThesis: document.getElementById('ai-thesis'),
    analyzeBtn: document.getElementById('analyze-btn'),
    exportPdfBtn: document.getElementById('export-pdf-btn'),
    exportCsvBtn: document.getElementById('export-csv-btn'),
    trackBtn: document.getElementById('track-btn'),
    retryBtn: document.getElementById('retry-btn')
};

// State
let currentCompany = null;
let analysisData = null;

// Initialize popup
document.addEventListener('DOMContentLoaded', initialize);

async function initialize() {
    // Check if we're on a supported page
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (isSupportedPage(tab.url)) {
        // Request company data from content script
        chrome.tabs.sendMessage(tab.id, { action: 'getCompanyData' }, (response) => {
            if (chrome.runtime.lastError) {
                console.error('Content script error:', chrome.runtime.lastError.message);
                // Try to inject content script manually
                chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    files: ['js/content_final.js']
                }, () => {
                    // Try again after injection
                    setTimeout(() => {
                        chrome.tabs.sendMessage(tab.id, { action: 'getCompanyData' }, (response2) => {
                            if (response2 && response2.success) {
                                displayCompanyData(response2.data);
                                currentCompany = response2.data;
                            } else {
                                showError('Unable to extract company data from this page');
                            }
                        });
                    }, 100);
                });
                return;
            }
            
            if (response && response.success) {
                displayCompanyData(response.data);
                currentCompany = response.data;
            } else {
                showNoCompany();
            }
        });
    } else {
        showNoCompany();
    }
    
    // Set up event listeners
    elements.analyzeBtn.addEventListener('click', analyzeCompany);
    elements.exportPdfBtn.addEventListener('click', exportPdf);
    elements.exportCsvBtn.addEventListener('click', exportCsv);
    elements.trackBtn.addEventListener('click', trackCompany);
    elements.retryBtn.addEventListener('click', () => location.reload());
}

function isSupportedPage(url) {
    // Support all http/https pages
    return url.startsWith('http://') || url.startsWith('https://');
}

function displayCompanyData(data) {
    elements.companyName.textContent = data.name || 'Unknown Company';
    elements.companyInfo.textContent = `${data.industry || 'Industry N/A'} • ${data.employeeCount || 'Size N/A'}`;
    
    elements.noCompany.classList.add('hidden');
    elements.companyDetected.classList.remove('hidden');
    elements.status.classList.add('active');
}

function showNoCompany() {
    elements.companyDetected.classList.add('hidden');
    elements.noCompany.classList.remove('hidden');
    elements.status.classList.remove('active');
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.error.classList.remove('hidden');
    elements.loading.classList.add('hidden');
}

function hideError() {
    elements.error.classList.add('hidden');
}

async function analyzeCompany() {
    if (!currentCompany) return;
    
    hideError();
    elements.loading.classList.remove('hidden');
    elements.analyzeBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: currentCompany.name,
                domain: currentCompany.domain || extractDomain(currentCompany.url),
                linkedinUrl: currentCompany.url,
                industry: currentCompany.industry || "Technology",
                employeeCount: currentCompany.employeeCount,
                description: currentCompany.description
            })
        });
        
        if (!response.ok) {
            throw new Error(`Analysis failed: ${response.statusText}`);
        }
        
        analysisData = await response.json();
        console.log('[DealFlow] Analysis data received:', analysisData);
        displayAnalysisResults(analysisData);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze company. Please try again.');
    } finally {
        elements.loading.classList.add('hidden');
        elements.analyzeBtn.disabled = false;
    }
}

function displayAnalysisResults(data) {
    console.log('[DealFlow] Displaying results for:', data);
    
    // Investment Score
    const scoreElement = elements.investmentScore.querySelector('.score-value');
    if (scoreElement) {
        scoreElement.textContent = data.investmentScore || '--';
        
        // Color code the score
        const score = parseInt(data.investmentScore);
        const scoreCircle = elements.investmentScore;
        if (score >= 80) {
            scoreCircle.style.background = 'linear-gradient(135deg, #42c767 0%, #3aa856 100%)';
        } else if (score >= 60) {
            scoreCircle.style.background = 'linear-gradient(135deg, #f7b731 0%, #e6a023 100%)';
        } else {
            scoreCircle.style.background = 'linear-gradient(135deg, #ee5a6f 0%, #d64759 100%)';
        }
    } else {
        console.error('[DealFlow] Score element not found');
    }
    
    // Funding History
    if (data.fundingHistory && data.fundingHistory.length > 0) {
        elements.fundingHistory.innerHTML = data.fundingHistory.map(round => `
            <div class="funding-round">
                <strong>${round.type}</strong>: $${formatMoney(round.amount)} 
                <span class="date">(${round.date})</span>
            </div>
        `).join('');
    } else {
        elements.fundingHistory.innerHTML = '<p class="placeholder">No funding data available</p>';
    }
    
    // Growth Signals
    if (data.growthSignals) {
        console.log('[DealFlow] Growth signals:', data.growthSignals);
        const growthHTML = `
            <div class="signal">Employee Growth: <strong>${data.growthSignals.employeeGrowth || 'N/A'}</strong></div>
            <div class="signal">Web Traffic: <strong>${data.growthSignals.webTraffic || 'N/A'}</strong></div>
            <div class="signal">Tech Stack: <strong>${data.growthSignals.techStack || 'N/A'}</strong></div>
            <div class="signal">News Velocity: <strong>${data.growthSignals.newsVelocity || 'N/A'}</strong></div>
            <div class="signal">Media Sentiment: <strong>${data.growthSignals.mediaSentiment || 'N/A'}</strong></div>
        `;
        elements.growthSignals.innerHTML = growthHTML;
        console.log('[DealFlow] Growth signals element:', elements.growthSignals);
    } else {
        elements.growthSignals.innerHTML = '<p class="placeholder">No growth data available</p>';
    }
    
    // Market Analysis
    if (data.marketAnalysis) {
        console.log('[DealFlow] Market analysis:', data.marketAnalysis);
        const marketHTML = `
            <div class="market-stat">TAM: <strong>${data.marketAnalysis.tam ? '$' + formatMoney(data.marketAnalysis.tam) : 'N/A'}</strong></div>
            <div class="market-stat">Growth Rate: <strong>${data.marketAnalysis.growthRate ? data.marketAnalysis.growthRate + '%' : 'N/A'}</strong></div>
        `;
        elements.marketAnalysis.innerHTML = marketHTML;
    } else {
        elements.marketAnalysis.innerHTML = '<p class="placeholder">No market data available</p>';
    }
    
    // AI Thesis
    if (data.aiThesis) {
        elements.aiThesis.innerHTML = `
            <div class="thesis-section">
                <h4>Executive Summary</h4>
                <p>${data.aiThesis.summary}</p>
            </div>
            <div class="thesis-section">
                <h4>Strengths</h4>
                <ul>${data.aiThesis.strengths.map(s => `<li>${s}</li>`).join('')}</ul>
            </div>
            <div class="thesis-section">
                <h4>Risks</h4>
                <ul>${data.aiThesis.risks.map(r => `<li>${r}</li>`).join('')}</ul>
            </div>
            <div class="thesis-section">
                <h4>Recommendation</h4>
                <p><strong>${data.aiThesis.recommendation}</strong></p>
            </div>
        `;
    }
    
    // Display Product Intelligence if available
    if (data.intelligence && data.intelligence.executive_summary) {
        displayProductIntelligence(data.intelligence);
    }
    
    // Display Competitive Intelligence if available
    if (data.competitiveIntelligence && data.competitiveIntelligence.competitors) {
        displayCompetitiveIntelligence(data.competitiveIntelligence);
    }
    
    // Display Technical Due Diligence if available
    if (data.technicalDueDiligence && data.technicalDueDiligence.technical_score) {
        displayTechnicalDueDiligence(data.technicalDueDiligence);
    }
    
    // Display Investment Signals if available
    if (data.investmentSignals && data.investmentSignals.overall_score) {
        displayInvestmentSignals(data.investmentSignals);
    }
    
    // Display Social Sentiment if available
    if (data.socialSentiment && data.socialSentiment.overall_sentiment) {
        displaySocialSentiment(data.socialSentiment);
    }
    
    // Display Data Metrics if available
    if (data.dataMetrics && data.dataMetrics.quantitative_score) {
        displayDataMetrics(data.dataMetrics);
    }
    
    // Enable action buttons
    elements.exportPdfBtn.disabled = false;
    elements.exportCsvBtn.disabled = false;
    elements.trackBtn.disabled = false;
    
    // Save to storage
    chrome.storage.local.set({
        [`analysis_${currentCompany.name}`]: {
            company: currentCompany,
            analysis: data,
            timestamp: new Date().toISOString()
        }
    });
}

async function exportPdf() {
    if (!analysisData || !currentCompany) return;
    
    elements.exportPdfBtn.disabled = true;
    elements.exportPdfBtn.textContent = 'Generating PDF...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/export-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                company: currentCompany,
                analysis: analysisData
            })
        });
        
        if (!response.ok) {
            throw new Error('PDF generation failed');
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        // Download the PDF
        chrome.downloads.download({
            url: url,
            filename: `DealFlow_${currentCompany.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`,
            saveAs: true
        });
        
    } catch (error) {
        console.error('PDF export error:', error);
        showError('Failed to generate PDF. Please try again.');
    } finally {
        elements.exportPdfBtn.disabled = false;
        elements.exportPdfBtn.textContent = 'Export PDF Report';
    }
}

async function exportCsv() {
    if (!analysisData || !currentCompany) return;
    
    elements.exportCsvBtn.disabled = true;
    elements.exportCsvBtn.textContent = 'Generating CSV...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/export-csv`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                company: currentCompany,
                analysis: analysisData
            })
        });
        
        if (!response.ok) {
            throw new Error('CSV generation failed');
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        
        // Download the CSV
        chrome.downloads.download({
            url: url,
            filename: `DealFlow_${currentCompany.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.csv`,
            saveAs: true
        });
        
    } catch (error) {
        console.error('CSV export error:', error);
        showError('Failed to generate CSV. Please try again.');
    } finally {
        elements.exportCsvBtn.disabled = false;
        elements.exportCsvBtn.textContent = 'Export CSV Data';
    }
}

async function trackCompany() {
    if (!currentCompany) return;
    
    // Save to tracked companies
    chrome.storage.sync.get(['trackedCompanies'], (result) => {
        const tracked = result.trackedCompanies || [];
        
        // Check if already tracked
        if (tracked.find(c => c.name === currentCompany.name)) {
            elements.trackBtn.textContent = 'Already Tracked';
            return;
        }
        
        // Add to tracked list
        tracked.push({
            ...currentCompany,
            trackedAt: new Date().toISOString()
        });
        
        chrome.storage.sync.set({ trackedCompanies: tracked }, () => {
            elements.trackBtn.textContent = 'Tracked!';
            elements.trackBtn.disabled = true;
            
            // Show notification
            chrome.notifications.create({
                type: 'basic',
                iconUrl: '../icons/icon128.png',
                title: 'Company Tracked',
                message: `${currentCompany.name} has been added to your watchlist`
            });
        });
    });
}

function displayProductIntelligence(intelligence) {
    // Create intelligence section if it doesn't exist
    let intelligenceSection = document.getElementById('product-intelligence');
    if (!intelligenceSection) {
        intelligenceSection = document.createElement('div');
        intelligenceSection.id = 'product-intelligence';
        intelligenceSection.className = 'ai-insights';
        intelligenceSection.innerHTML = `
            <h3>Product & Customer Intelligence</h3>
            <div class="intelligence-content"></div>
        `;
        // Insert after AI thesis
        elements.aiThesis.parentElement.after(intelligenceSection);
    }
    
    const content = intelligenceSection.querySelector('.intelligence-content');
    
    // Executive Summary
    const execSummary = intelligence.executive_summary;
    if (execSummary) {
        let summaryHtml = '<div class="intel-section">';
        
        if (execSummary.product_summary) {
            summaryHtml += `<p><strong>Product:</strong> ${execSummary.product_summary}</p>`;
        }
        if (execSummary.customer_summary) {
            summaryHtml += `<p><strong>Customers:</strong> ${execSummary.customer_summary}</p>`;
        }
        if (execSummary.market_position) {
            summaryHtml += `<p><strong>Market:</strong> ${execSummary.market_position}</p>`;
        }
        
        summaryHtml += '</div>';
        content.innerHTML = summaryHtml;
    }
    
    // Product Details
    if (intelligence.product && intelligence.product.found) {
        const product = intelligence.product;
        let productHtml = '<div class="intel-section"><h4>Product Details</h4>';
        
        if (product.features && product.features.length > 0) {
            productHtml += '<p><strong>Key Features:</strong></p><ul class="feature-list">';
            product.features.slice(0, 5).forEach(feature => {
                productHtml += `<li>${feature}</li>`;
            });
            productHtml += '</ul>';
        }
        
        if (product.pricing) {
            productHtml += `<p><strong>Pricing:</strong> ${product.pricing.slice(0, 3).join(' | ')}</p>`;
        }
        
        productHtml += '</div>';
        content.innerHTML += productHtml;
    }
    
    // Customer Intelligence
    if (intelligence.customers && intelligence.customers.found) {
        const customers = intelligence.customers;
        let customerHtml = '<div class="intel-section"><h4>Customer Intelligence</h4>';
        
        if (customers.estimated_customers) {
            customerHtml += `<p><strong>Customer Base:</strong> ${customers.estimated_customers}</p>`;
        }
        
        if (customers.customer_logos && customers.customer_logos.length > 0) {
            customerHtml += `<p><strong>Notable Customers:</strong> ${customers.customer_logos.slice(0, 5).join(', ')}</p>`;
        }
        
        if (customers.customer_segments && customers.customer_segments.length > 0) {
            customerHtml += `<p><strong>Segments:</strong> ${customers.customer_segments.join(', ')}</p>`;
        }
        
        customerHtml += '</div>';
        content.innerHTML += customerHtml;
    }
    
    // Market Validation
    let validationHtml = '<div class="intel-section"><h4>Market Validation</h4><ul class="validation-list">';
    
    if (intelligence.g2_reviews && intelligence.g2_reviews.found) {
        const g2 = intelligence.g2_reviews;
        validationHtml += `<li>G2 Reviews: ${g2.rating}/5 (${g2.review_count} reviews)</li>`;
    }
    
    if (intelligence.producthunt && intelligence.producthunt.found) {
        validationHtml += '<li>Featured on ProductHunt</li>';
    }
    
    if (intelligence.app_presence) {
        const apps = [];
        if (intelligence.app_presence.ios) apps.push('iOS');
        if (intelligence.app_presence.android) apps.push('Android');
        if (apps.length > 0) {
            validationHtml += `<li>Mobile Apps: ${apps.join(' & ')}</li>`;
        }
    }
    
    if (intelligence.revenue_indicators) {
        const rev = intelligence.revenue_indicators;
        if (rev.business_model) {
            validationHtml += `<li>Business Model: ${rev.business_model}</li>`;
        }
        if (rev.funding_stage) {
            validationHtml += `<li>Funding: ${rev.funding_stage}</li>`;
        }
    }
    
    validationHtml += '</ul></div>';
    content.innerHTML += validationHtml;
}

function displayCompetitiveIntelligence(competitiveData) {
    // Create competitive section
    let competitiveSection = document.getElementById('competitive-intelligence');
    if (!competitiveSection) {
        competitiveSection = document.createElement('div');
        competitiveSection.id = 'competitive-intelligence';
        competitiveSection.className = 'ai-insights';
        competitiveSection.innerHTML = `
            <h3>Competitive Intelligence</h3>
            <div class="competitive-content"></div>
        `;
        // Insert after product intelligence
        const productIntel = document.getElementById('product-intelligence');
        if (productIntel) {
            productIntel.after(competitiveSection);
        } else {
            elements.aiThesis.parentElement.after(competitiveSection);
        }
    }
    
    const content = competitiveSection.querySelector('.competitive-content');
    let html = '';
    
    // Market Opportunity Score
    if (competitiveData.market_opportunity_score !== undefined) {
        html += `<div class="competitive-metric">
            <strong>Market Opportunity Score:</strong>
            <span class="score-badge ${competitiveData.market_opportunity_score >= 70 ? 'high' : competitiveData.market_opportunity_score >= 50 ? 'medium' : 'low'}">
                ${competitiveData.market_opportunity_score}/100
            </span>
        </div>`;
    }
    
    // Direct Competitors
    if (competitiveData.competitors && competitiveData.competitors.direct) {
        html += '<div class="competitor-section"><h4>Direct Competitors</h4><ul class="competitor-list">';
        competitiveData.competitors.direct.slice(0, 5).forEach(comp => {
            html += `<li>
                <strong>${comp.name}</strong>
                ${comp.analysis && comp.analysis.estimated_size ? ` - ${comp.analysis.estimated_size}` : ''}
            </li>`;
        });
        html += '</ul></div>';
    }
    
    // Market Position
    if (competitiveData.market_position) {
        const pos = competitiveData.market_position;
        html += '<div class="market-position"><h4>Market Position</h4>';
        if (pos.market_segment) {
            html += `<p><strong>Segment:</strong> ${pos.market_segment}</p>`;
        }
        if (pos.market_maturity) {
            html += `<p><strong>Market Maturity:</strong> ${pos.market_maturity}</p>`;
        }
        html += '</div>';
    }
    
    // Strategic Insights
    if (competitiveData.strategic_insights && competitiveData.strategic_insights.length > 0) {
        html += '<div class="strategic-insights"><h4>Strategic Insights</h4><ul>';
        competitiveData.strategic_insights.forEach(insight => {
            html += `<li>${insight}</li>`;
        });
        html += '</ul></div>';
    }
    
    content.innerHTML = html;
}

function displayTechnicalDueDiligence(techData) {
    // Create technical section
    let techSection = document.getElementById('technical-dd');
    if (!techSection) {
        techSection = document.createElement('div');
        techSection.id = 'technical-dd';
        techSection.className = 'ai-insights';
        techSection.innerHTML = `
            <h3>Technical Due Diligence</h3>
            <div class="technical-content"></div>
        `;
        // Insert at the end
        const lastSection = document.getElementById('competitive-intelligence') || 
                          document.getElementById('product-intelligence') || 
                          elements.aiThesis.parentElement;
        lastSection.after(techSection);
    }
    
    const content = techSection.querySelector('.technical-content');
    let html = '';
    
    // Technical Score
    html += `<div class="tech-score">
        <strong>Technical Score:</strong>
        <div class="score-bar">
            <div class="score-fill ${techData.technical_score >= 70 ? 'high' : techData.technical_score >= 50 ? 'medium' : 'low'}" 
                 style="width: ${techData.technical_score}%">
                ${techData.technical_score}/100
            </div>
        </div>
    </div>`;
    
    // Website Technology
    if (techData.website_tech && techData.website_tech.found) {
        const tech = techData.website_tech;
        html += '<div class="tech-section"><h4>Technology Stack</h4>';
        
        if (tech.frontend && tech.frontend.length > 0) {
            html += `<p><strong>Frontend:</strong> ${tech.frontend.join(', ')}</p>`;
        }
        if (tech.infrastructure && tech.infrastructure.length > 0) {
            html += `<p><strong>Infrastructure:</strong> ${tech.infrastructure.join(', ')}</p>`;
        }
        if (tech.cdn) {
            html += `<p><strong>CDN:</strong> ${tech.cdn}</p>`;
        }
        html += '</div>';
    }
    
    // Security Score
    if (techData.security && techData.security.found) {
        html += `<div class="security-section">
            <h4>Security Analysis</h4>
            <p><strong>Security Score:</strong> ${techData.security.score}/100</p>`;
        
        if (techData.security.vulnerabilities && techData.security.vulnerabilities.length > 0) {
            html += '<p class="warning"><strong>⚠️ Vulnerabilities:</strong></p><ul>';
            techData.security.vulnerabilities.slice(0, 3).forEach(vuln => {
                html += `<li class="vulnerability">${vuln}</li>`;
            });
            html += '</ul>';
        }
        html += '</div>';
    }
    
    // Performance
    if (techData.performance && techData.performance.found) {
        const perf = techData.performance;
        html += '<div class="performance-section"><h4>Performance Metrics</h4>';
        html += `<p><strong>Load Time:</strong> ${perf.load_time}s</p>`;
        
        const optimizations = perf.optimization || {};
        const optCount = Object.values(optimizations).filter(v => v).length;
        html += `<p><strong>Optimizations:</strong> ${optCount}/4 
            (${Object.entries(optimizations).filter(([k,v]) => v).map(([k,v]) => k).join(', ') || 'None'})</p>`;
        html += '</div>';
    }
    
    // Technical Strengths & Risks
    if (techData.technical_strengths && techData.technical_strengths.length > 0) {
        html += '<div class="tech-strengths"><h4>Technical Strengths</h4><ul>';
        techData.technical_strengths.slice(0, 3).forEach(strength => {
            html += `<li class="strength">✓ ${strength}</li>`;
        });
        html += '</ul></div>';
    }
    
    if (techData.technical_risks && techData.technical_risks.length > 0) {
        html += '<div class="tech-risks"><h4>Technical Risks</h4><ul>';
        techData.technical_risks.slice(0, 3).forEach(risk => {
            html += `<li class="risk">⚠️ ${risk}</li>`;
        });
        html += '</ul></div>';
    }
    
    content.innerHTML = html;
}

// Utility functions
function extractDomain(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname.replace('www.', '');
    } catch {
        return null;
    }
}

function formatMoney(amount) {
    if (!amount || amount === null || amount === undefined) return '0';
    const num = parseFloat(amount);
    if (isNaN(num)) return '0';
    if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
    return num.toString();
}

function displayInvestmentSignals(signalsData) {
    // Create investment signals section
    let signalsSection = document.getElementById('investment-signals');
    if (!signalsSection) {
        signalsSection = document.createElement('div');
        signalsSection.id = 'investment-signals';
        signalsSection.className = 'ai-insights';
        signalsSection.innerHTML = `
            <h3>Investment Signals Dashboard</h3>
            <div class="signals-content"></div>
        `;
        // Insert after technical DD
        const lastSection = document.getElementById('technical-dd') || 
                          document.getElementById('competitive-intelligence') || 
                          document.getElementById('product-intelligence') || 
                          elements.aiThesis.parentElement;
        lastSection.after(signalsSection);
    }
    
    const content = signalsSection.querySelector('.signals-content');
    let html = '';
    
    // Overall Investment Grade
    const gradeColors = {
        'STRONG BUY': 'high',
        'BUY': 'high',
        'MODERATE BUY': 'medium',
        'HOLD': 'medium',
        'WATCH': 'low',
        'PASS': 'low'
    };
    
    html += `<div class="investment-grade">
        <strong>Investment Grade:</strong>
        <span class="grade-badge ${gradeColors[signalsData.investment_grade] || 'medium'}">
            ${signalsData.investment_grade}
        </span>
        <span class="signal-strength">(${signalsData.signal_strength} signals)</span>
    </div>`;
    
    // Risk-Adjusted Score
    html += `<div class="risk-adjusted-score">
        <strong>Risk-Adjusted Score:</strong>
        <span class="score-value">${signalsData.risk_adjusted_score}/100</span>
    </div>`;
    
    // Key Signals
    if (signalsData.key_signals && signalsData.key_signals.length > 0) {
        html += '<div class="key-signals"><h4>Key Investment Signals</h4><ul>';
        signalsData.key_signals.slice(0, 5).forEach(signal => {
            html += `<li class="signal-item positive">✓ ${signal}</li>`;
        });
        html += '</ul></div>';
    }
    
    // Green Flags
    if (signalsData.green_flags && signalsData.green_flags.length > 0) {
        html += '<div class="green-flags"><h4>Green Flags</h4><ul>';
        signalsData.green_flags.forEach(flag => {
            html += `<li class="flag-item green">✓ ${flag}</li>`;
        });
        html += '</ul></div>';
    }
    
    // Red Flags
    if (signalsData.red_flags && signalsData.red_flags.length > 0) {
        html += '<div class="red-flags"><h4>Red Flags</h4><ul>';
        signalsData.red_flags.forEach(flag => {
            html += `<li class="flag-item red">⚠️ ${flag}</li>`;
        });
        html += '</ul></div>';
    }
    
    // Momentum Indicators
    if (signalsData.momentum_indicators) {
        const momentum = signalsData.momentum_indicators;
        html += '<div class="momentum-indicators"><h4>Momentum Indicators</h4>';
        html += `<div class="momentum-grid">`;
        
        const momentumColors = {
            'High': 'high',
            'Medium': 'medium',
            'Low': 'low',
            'Strong Positive': 'high',
            'Positive': 'medium',
            'Neutral': 'low',
            'Negative': 'low'
        };
        
        Object.entries(momentum).forEach(([key, value]) => {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            html += `<div class="momentum-item">
                <span class="momentum-label">${label}:</span>
                <span class="momentum-value ${momentumColors[value] || ''}">${value}</span>
            </div>`;
        });
        
        html += '</div></div>';
    }
    
    // Exit Potential
    if (signalsData.exit_potential) {
        const exit = signalsData.exit_potential;
        html += '<div class="exit-potential"><h4>Exit Potential</h4>';
        html += `<p><strong>IPO Potential:</strong> ${exit.ipo_potential}</p>`;
        html += `<p><strong>Acquisition Potential:</strong> ${exit.acquisition_potential}</p>`;
        if (exit.strategic_buyers && exit.strategic_buyers.length > 0) {
            html += `<p><strong>Potential Buyers:</strong> ${exit.strategic_buyers.join(', ')}</p>`;
        }
        html += `<p><strong>Timeline:</strong> ${exit.exit_timeline}</p>`;
        html += '</div>';
    }
    
    content.innerHTML = html;
}

function displaySocialSentiment(sentimentData) {
    // Create social sentiment section
    let sentimentSection = document.getElementById('social-sentiment');
    if (!sentimentSection) {
        sentimentSection = document.createElement('div');
        sentimentSection.id = 'social-sentiment';
        sentimentSection.className = 'ai-insights';
        sentimentSection.innerHTML = `
            <h3>Social Sentiment Analysis</h3>
            <div class="sentiment-content"></div>
        `;
        // Insert after investment signals
        const lastSection = document.getElementById('investment-signals') ||
                          document.getElementById('technical-dd') || 
                          document.getElementById('competitive-intelligence') || 
                          elements.aiThesis.parentElement;
        lastSection.after(sentimentSection);
    }
    
    const content = sentimentSection.querySelector('.sentiment-content');
    let html = '';
    
    // Overall Sentiment
    if (sentimentData.overall_sentiment) {
        const sentiment = sentimentData.overall_sentiment;
        const sentimentColors = {
            'Positive': 'high',
            'Mixed': 'medium',
            'Negative': 'low',
            'Unknown': 'unknown'
        };
        
        html += `<div class="overall-sentiment">
            <strong>Overall Sentiment:</strong>
            <span class="sentiment-badge ${sentimentColors[sentiment.sentiment] || 'unknown'}">
                ${sentiment.sentiment}
            </span>
            <span class="confidence">(${sentiment.confidence}% confidence)</span>
        </div>`;
    }
    
    // Platform breakdown
    const platforms = ['twitter', 'reddit', 'hackernews', 'youtube', 'glassdoor'];
    const platformNames = {
        'twitter': 'Twitter/X',
        'reddit': 'Reddit',
        'hackernews': 'Hacker News',
        'youtube': 'YouTube',
        'glassdoor': 'Glassdoor'
    };
    
    html += '<div class="platform-sentiments"><h4>Platform Analysis</h4>';
    
    platforms.forEach(platform => {
        if (sentimentData[platform] && sentimentData[platform].found) {
            const data = sentimentData[platform];
            html += `<div class="platform-item">
                <strong>${platformNames[platform]}:</strong>`;
            
            // Platform-specific details
            if (platform === 'twitter') {
                html += ` ${data.sentiment} sentiment, ${data.engagement_level} engagement`;
            } else if (platform === 'reddit') {
                html += ` ${data.posts_count} posts, ${data.community_size} community`;
                if (data.subreddits && data.subreddits.length > 0) {
                    html += ` (r/${data.subreddits[0]})`;
                }
            } else if (platform === 'hackernews') {
                html += ` ${data.posts_count} stories`;
                if (data.technical_validation) {
                    html += ' ✓ Technical validation';
                }
            } else if (platform === 'youtube') {
                html += ` ${data.video_count_estimate} videos`;
                if (data.channel_exists) {
                    html += ' ✓ Official channel';
                }
            } else if (platform === 'glassdoor') {
                if (data.rating) {
                    html += ` ${data.rating}/5 rating, ${data.employee_sentiment} sentiment`;
                }
            }
            
            html += '</div>';
        }
    });
    
    html += '</div>';
    
    // Social Signals
    if (sentimentData.social_signals && sentimentData.social_signals.length > 0) {
        html += '<div class="social-signals"><h4>Key Social Signals</h4><ul>';
        sentimentData.social_signals.forEach(signal => {
            html += `<li class="social-signal-item">• ${signal}</li>`;
        });
        html += '</ul></div>';
    }
    
    // Viral Indicators
    if (sentimentData.viral_indicators) {
        const viral = sentimentData.viral_indicators;
        html += '<div class="viral-indicators"><h4>Viral Potential</h4>';
        html += `<p><strong>Viral Potential:</strong> 
            <span class="viral-badge ${viral.viral_potential.toLowerCase()}">${viral.viral_potential}</span>
            (Score: ${viral.viral_score}/100)</p>`;
        
        if (viral.indicators && viral.indicators.length > 0) {
            html += '<ul>';
            viral.indicators.forEach(indicator => {
                html += `<li>• ${indicator}</li>`;
            });
            html += '</ul>';
        }
        html += '</div>';
    }
    
    // Community Health
    if (sentimentData.community_health) {
        const health = sentimentData.community_health;
        const healthColors = {
            'Healthy': 'high',
            'Moderate': 'medium',
            'Unhealthy': 'low'
        };
        
        html += '<div class="community-health"><h4>Community Health</h4>';
        html += `<p><strong>Status:</strong> 
            <span class="health-badge ${healthColors[health.status] || 'medium'}">${health.status}</span>
            (Score: ${health.health_score}/100)</p>`;
        
        if (health.positive_indicators && health.positive_indicators.length > 0) {
            html += '<p class="health-positive"><strong>Strengths:</strong></p><ul>';
            health.positive_indicators.forEach(indicator => {
                html += `<li class="positive">✓ ${indicator}</li>`;
            });
            html += '</ul>';
        }
        
        if (health.issues && health.issues.length > 0) {
            html += '<p class="health-issues"><strong>Issues:</strong></p><ul>';
            health.issues.forEach(issue => {
                html += `<li class="negative">⚠️ ${issue}</li>`;
            });
            html += '</ul>';
        }
        html += '</div>';
    }
    
    content.innerHTML = html;
}

function displayDataMetrics(metricsData) {
    // Create data metrics section
    let metricsSection = document.getElementById('data-metrics');
    if (!metricsSection) {
        metricsSection = document.createElement('div');
        metricsSection.id = 'data-metrics';
        metricsSection.className = 'ai-insights';
        metricsSection.innerHTML = `
            <h3>📊 Quantitative Metrics</h3>
            <div class="metrics-content"></div>
        `;
        // Insert after social sentiment
        const lastSection = document.getElementById('social-sentiment') ||
                          document.getElementById('investment-signals') ||
                          document.getElementById('technical-dd') || 
                          elements.aiThesis.parentElement;
        lastSection.after(metricsSection);
    }
    
    const content = metricsSection.querySelector('.metrics-content');
    let html = '';
    
    // Overall Score
    html += `<div class="quantitative-score">
        <strong>Quantitative Score:</strong>
        <span class="score-value-large">${metricsData.quantitative_score}/100</span>
        <span class="data-quality">(${metricsData.data_quality_score}% data quality)</span>
    </div>`;
    
    // Key Performance Indicators
    if (metricsData.key_performance_indicators) {
        const kpis = metricsData.key_performance_indicators;
        html += '<div class="kpis-grid">';
        
        // Revenue metrics
        if (kpis.revenue_estimate > 0) {
            html += `<div class="kpi-card">
                <div class="kpi-label">Est. Revenue</div>
                <div class="kpi-value">$${formatMoney(kpis.revenue_estimate)}</div>
            </div>`;
        }
        
        // Customer count
        if (kpis.customer_count > 0) {
            html += `<div class="kpi-card">
                <div class="kpi-label">Customers</div>
                <div class="kpi-value">${formatMoney(kpis.customer_count)}</div>
            </div>`;
        }
        
        // Growth rate
        if (kpis.growth_rate > 0) {
            html += `<div class="kpi-card">
                <div class="kpi-label">Growth Rate</div>
                <div class="kpi-value">${kpis.growth_rate}%</div>
            </div>`;
        }
        
        // Employee count
        if (kpis.employee_count > 0) {
            html += `<div class="kpi-card">
                <div class="kpi-label">Employees</div>
                <div class="kpi-value">${kpis.employee_count}</div>
            </div>`;
        }
        
        // Burn rate
        if (kpis.burn_rate > 0) {
            html += `<div class="kpi-card">
                <div class="kpi-label">Monthly Burn</div>
                <div class="kpi-value">$${formatMoney(kpis.burn_rate)}</div>
            </div>`;
        }
        
        // Runway
        if (kpis.runway > 0) {
            html += `<div class="kpi-card">
                <div class="kpi-label">Runway</div>
                <div class="kpi-value">${kpis.runway}mo</div>
            </div>`;
        }
        
        html += '</div>';
    }
    
    // Valuation Estimate
    if (metricsData.valuation_estimate && metricsData.valuation_estimate.valuation_estimate > 0) {
        const val = metricsData.valuation_estimate;
        html += '<div class="valuation-section">';
        html += '<h4>💰 Valuation Estimate</h4>';
        html += `<div class="valuation-main">
            <span class="valuation-amount">$${formatMoney(val.valuation_estimate)}</span>
            <span class="valuation-multiple">${val.revenue_multiple}x revenue</span>
        </div>`;
        html += `<div class="valuation-range">
            Range: $${formatMoney(val.valuation_range_min)} - $${formatMoney(val.valuation_range_max)}
            <span class="confidence">(${val.confidence_score}% confidence)</span>
        </div>`;
        html += '</div>';
    }
    
    // Growth Metrics
    if (metricsData.growth_metrics) {
        const growth = metricsData.growth_metrics;
        html += '<div class="growth-section">';
        html += '<h4>📈 Growth Metrics</h4>';
        html += '<div class="metrics-list">';
        
        if (growth.employee_growth_rate > 0) {
            html += `<div class="metric-item">
                <span class="metric-label">Employee Growth:</span>
                <span class="metric-value positive">${growth.employee_growth_rate}%</span>
            </div>`;
        }
        
        if (growth.github_star_velocity > 0) {
            html += `<div class="metric-item">
                <span class="metric-label">Star Velocity:</span>
                <span class="metric-value">${growth.github_star_velocity}/month</span>
            </div>`;
        }
        
        if (growth.customer_growth_rate > 0) {
            html += `<div class="metric-item">
                <span class="metric-label">Customer Growth:</span>
                <span class="metric-value positive">${growth.customer_growth_rate}%</span>
            </div>`;
        }
        
        html += '</div></div>';
    }
    
    // Efficiency Metrics
    if (metricsData.efficiency_metrics) {
        const eff = metricsData.efficiency_metrics;
        html += '<div class="efficiency-section">';
        html += '<h4>⚡ Efficiency Metrics</h4>';
        html += '<div class="metrics-list">';
        
        if (eff.revenue_per_employee > 0) {
            html += `<div class="metric-item">
                <span class="metric-label">Revenue/Employee:</span>
                <span class="metric-value">$${formatMoney(eff.revenue_per_employee)}</span>
            </div>`;
        }
        
        if (eff.efficiency_ratio > 0) {
            const effClass = eff.efficiency_ratio > 0.5 ? 'positive' : eff.efficiency_ratio > 0.3 ? 'neutral' : 'negative';
            html += `<div class="metric-item">
                <span class="metric-label">Efficiency Ratio:</span>
                <span class="metric-value ${effClass}">${eff.efficiency_ratio}</span>
            </div>`;
        }
        
        if (eff.capital_efficiency > 0) {
            html += `<div class="metric-item">
                <span class="metric-label">Capital Efficiency:</span>
                <span class="metric-value">${eff.capital_efficiency}</span>
            </div>`;
        }
        
        html += '</div></div>';
    }
    
    // Market Position
    if (metricsData.market_metrics) {
        const market = metricsData.market_metrics;
        html += '<div class="market-section">';
        html += '<h4>🎯 Market Position</h4>';
        html += '<div class="metrics-list">';
        
        if (market.market_share > 0) {
            html += `<div class="metric-item">
                <span class="metric-label">Market Share:</span>
                <span class="metric-value">${market.market_share}%</span>
            </div>`;
        }
        
        if (market.tam_size > 0) {
            html += `<div class="metric-item">
                <span class="metric-label">TAM:</span>
                <span class="metric-value">$${formatMoney(market.tam_size)}</span>
            </div>`;
        }
        
        if (market.competitor_count > 0) {
            html += `<div class="metric-item">
                <span class="metric-label">Competitors:</span>
                <span class="metric-value">${market.competitor_count}</span>
            </div>`;
        }
        
        html += '</div></div>';
    }
    
    // Data Completeness
    if (metricsData.data_completeness) {
        const completeness = metricsData.data_completeness;
        html += '<div class="data-completeness">';
        html += '<h4>📋 Data Coverage</h4>';
        html += '<div class="completeness-grid">';
        
        Object.entries(completeness).forEach(([key, value]) => {
            if (key !== 'overall') {
                const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                const colorClass = value >= 80 ? 'high' : value >= 50 ? 'medium' : 'low';
                html += `<div class="completeness-item">
                    <span class="completeness-label">${label}:</span>
                    <span class="completeness-value ${colorClass}">${value}%</span>
                </div>`;
            }
        });
        
        html += '</div></div>';
    }
    
    content.innerHTML = html;
}

// Add CSS for additional styling
const style = document.createElement('style');
style.textContent = `
    .funding-round {
        padding: 5px 0;
        border-bottom: 1px solid var(--border);
    }
    .funding-round:last-child {
        border-bottom: none;
    }
    .date {
        color: var(--text-tertiary);
        font-size: 12px;
    }
    .signal, .market-stat {
        padding: 5px 0;
    }
    .thesis-section {
        margin-bottom: 15px;
    }
    .thesis-section:last-child {
        margin-bottom: 0;
    }
    .thesis-section h4 {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
        color: var(--accent-primary);
    }
    .thesis-section ul {
        list-style: none;
        padding-left: 0;
    }
    .thesis-section li {
        position: relative;
        padding-left: 20px;
        margin-bottom: 5px;
    }
    .thesis-section li:before {
        content: "→";
        position: absolute;
        left: 0;
        color: var(--accent-primary);
    }
    
    /* Product Intelligence Styles */
    #product-intelligence {
        margin-top: 20px;
        padding: 20px;
        background: var(--card-bg);
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    .intel-section {
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid var(--border);
    }
    .intel-section:last-child {
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: none;
    }
    .intel-section h4 {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 10px;
        color: var(--accent-primary);
    }
    .intel-section p {
        margin: 8px 0;
        line-height: 1.5;
    }
    .feature-list, .validation-list {
        list-style: none;
        padding-left: 0;
        margin: 10px 0;
    }
    .feature-list li, .validation-list li {
        position: relative;
        padding-left: 20px;
        margin-bottom: 8px;
        font-size: 13px;
    }
    .feature-list li:before, .validation-list li:before {
        content: "•";
        position: absolute;
        left: 5px;
        color: var(--accent-primary);
    }
    
    /* Competitive Intelligence Styles */
    #competitive-intelligence, #technical-dd {
        margin-top: 20px;
        padding: 20px;
        background: var(--card-bg);
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    .competitive-metric {
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .score-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }
    .score-badge.high {
        background: rgba(66, 199, 103, 0.1);
        color: #42c767;
    }
    .score-badge.medium {
        background: rgba(247, 183, 49, 0.1);
        color: #f7b731;
    }
    .score-badge.low {
        background: rgba(238, 90, 111, 0.1);
        color: #ee5a6f;
    }
    .competitor-list {
        list-style: none;
        padding: 0;
    }
    .competitor-list li {
        padding: 8px 0;
        border-bottom: 1px solid var(--border);
        font-size: 13px;
    }
    .competitor-list li:last-child {
        border-bottom: none;
    }
    .strategic-insights ul {
        list-style: none;
        padding: 0;
    }
    .strategic-insights li {
        padding: 8px 0;
        padding-left: 20px;
        position: relative;
        font-size: 13px;
    }
    .strategic-insights li:before {
        content: "→";
        position: absolute;
        left: 0;
        color: var(--accent-primary);
    }
    
    /* Technical DD Styles */
    .tech-score {
        margin-bottom: 20px;
    }
    .score-bar {
        background: var(--border);
        height: 24px;
        border-radius: 12px;
        overflow: hidden;
        margin-top: 8px;
    }
    .score-fill {
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 12px;
        font-weight: 600;
        transition: width 0.3s ease;
    }
    .score-fill.high {
        background: linear-gradient(135deg, #42c767 0%, #3aa856 100%);
    }
    .score-fill.medium {
        background: linear-gradient(135deg, #f7b731 0%, #e6a023 100%);
    }
    .score-fill.low {
        background: linear-gradient(135deg, #ee5a6f 0%, #d64759 100%);
    }
    .tech-section, .security-section, .performance-section {
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 1px solid var(--border);
    }
    .tech-section:last-child, .security-section:last-child, .performance-section:last-child {
        border-bottom: none;
    }
    .vulnerability {
        color: #e74c3c;
        font-size: 12px;
    }
    .strength {
        color: #27ae60;
        font-size: 13px;
    }
    .risk {
        color: #e74c3c;
        font-size: 13px;
    }
    .warning {
        color: #f39c12;
    }
    
    /* Investment Signals Styles */
    #investment-signals {
        margin-top: 20px;
        padding: 20px;
        background: var(--bg-secondary);
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    .investment-grade {
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 16px;
    }
    .grade-badge {
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }
    .grade-badge.high {
        background: rgba(66, 199, 103, 0.2);
        color: #42c767;
    }
    .grade-badge.medium {
        background: rgba(247, 183, 49, 0.2);
        color: #f7b731;
    }
    .grade-badge.low {
        background: rgba(238, 90, 111, 0.2);
        color: #ee5a6f;
    }
    .signal-strength {
        color: var(--text-tertiary);
        font-size: 13px;
    }
    .risk-adjusted-score {
        margin-bottom: 20px;
        font-size: 14px;
    }
    .risk-adjusted-score .score-value {
        font-weight: 600;
        color: var(--accent-primary);
    }
    .key-signals, .green-flags, .red-flags {
        margin-bottom: 15px;
    }
    .signal-item, .flag-item {
        list-style: none;
        padding: 6px 0;
        font-size: 13px;
    }
    .signal-item.positive, .flag-item.green {
        color: #42c767;
    }
    .flag-item.red {
        color: #ee5a6f;
    }
    .momentum-indicators {
        margin-top: 20px;
    }
    .momentum-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 10px;
    }
    .momentum-item {
        display: flex;
        justify-content: space-between;
        padding: 8px;
        background: var(--bg-tertiary);
        border-radius: 8px;
        font-size: 12px;
    }
    .momentum-label {
        color: var(--text-secondary);
    }
    .momentum-value {
        font-weight: 600;
    }
    .momentum-value.high {
        color: #42c767;
    }
    .momentum-value.medium {
        color: #f7b731;
    }
    .momentum-value.low {
        color: #ee5a6f;
    }
    .exit-potential {
        margin-top: 20px;
        padding: 15px;
        background: var(--bg-tertiary);
        border-radius: 8px;
    }
    .exit-potential p {
        margin: 8px 0;
        font-size: 13px;
    }
    
    /* Social Sentiment Styles */
    #social-sentiment {
        margin-top: 20px;
        padding: 20px;
        background: var(--bg-secondary);
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    .overall-sentiment {
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 16px;
    }
    .sentiment-badge {
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }
    .sentiment-badge.high {
        background: rgba(66, 199, 103, 0.2);
        color: #42c767;
    }
    .sentiment-badge.medium {
        background: rgba(247, 183, 49, 0.2);
        color: #f7b731;
    }
    .sentiment-badge.low {
        background: rgba(238, 90, 111, 0.2);
        color: #ee5a6f;
    }
    .sentiment-badge.unknown {
        background: rgba(138, 141, 145, 0.2);
        color: var(--text-tertiary);
    }
    .confidence {
        color: var(--text-tertiary);
        font-size: 13px;
    }
    .platform-sentiments {
        margin-bottom: 20px;
    }
    .platform-item {
        padding: 8px 0;
        border-bottom: 1px solid var(--border);
        font-size: 13px;
    }
    .platform-item:last-child {
        border-bottom: none;
    }
    .social-signals, .viral-indicators, .community-health {
        margin-bottom: 15px;
    }
    .social-signal-item {
        list-style: none;
        padding: 6px 0;
        font-size: 13px;
        color: var(--text-secondary);
    }
    .viral-badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .viral-badge.high {
        background: rgba(66, 199, 103, 0.2);
        color: #42c767;
    }
    .viral-badge.medium {
        background: rgba(247, 183, 49, 0.2);
        color: #f7b731;
    }
    .viral-badge.low {
        background: rgba(238, 90, 111, 0.2);
        color: #ee5a6f;
    }
    .health-badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    .health-badge.high {
        background: rgba(66, 199, 103, 0.2);
        color: #42c767;
    }
    .health-badge.medium {
        background: rgba(247, 183, 49, 0.2);
        color: #f7b731;
    }
    .health-badge.low {
        background: rgba(238, 90, 111, 0.2);
        color: #ee5a6f;
    }
    .health-positive {
        color: #42c767;
        margin-top: 10px;
    }
    .health-issues {
        color: #ee5a6f;
        margin-top: 10px;
    }
    .positive {
        color: #42c767;
    }
    .negative {
        color: #ee5a6f;
    }
    
    /* Data Metrics Styles */
    #data-metrics {
        margin-top: 20px;
        padding: 20px;
        background: var(--bg-secondary);
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    .quantitative-score {
        text-align: center;
        margin-bottom: 20px;
        padding: 15px;
        background: var(--bg-tertiary);
        border-radius: 8px;
    }
    .score-value-large {
        font-size: 24px;
        font-weight: 700;
        color: var(--accent-primary);
        margin: 0 10px;
    }
    .data-quality {
        color: var(--text-tertiary);
        font-size: 12px;
    }
    .kpis-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 10px;
        margin-bottom: 20px;
    }
    .kpi-card {
        padding: 12px;
        background: var(--bg-tertiary);
        border-radius: 8px;
        text-align: center;
    }
    .kpi-label {
        font-size: 11px;
        color: var(--text-secondary);
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
    }
    .valuation-section {
        margin-bottom: 20px;
        padding: 15px;
        background: var(--bg-tertiary);
        border-radius: 8px;
    }
    .valuation-main {
        text-align: center;
        margin-bottom: 10px;
    }
    .valuation-amount {
        font-size: 20px;
        font-weight: 700;
        color: var(--success);
        margin-right: 10px;
    }
    .valuation-multiple {
        font-size: 12px;
        color: var(--text-secondary);
    }
    .valuation-range {
        text-align: center;
        font-size: 12px;
        color: var(--text-tertiary);
    }
    .growth-section, .efficiency-section, .market-section, .data-completeness {
        margin-bottom: 15px;
    }
    .metrics-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .metric-item {
        display: flex;
        justify-content: space-between;
        padding: 8px;
        background: var(--bg-tertiary);
        border-radius: 6px;
        font-size: 13px;
    }
    .metric-label {
        color: var(--text-secondary);
    }
    .metric-value {
        font-weight: 600;
    }
    .metric-value.positive {
        color: #42c767;
    }
    .metric-value.neutral {
        color: #f7b731;
    }
    .metric-value.negative {
        color: #ee5a6f;
    }
    .completeness-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
    }
    .completeness-item {
        display: flex;
        justify-content: space-between;
        padding: 6px;
        background: var(--bg-tertiary);
        border-radius: 4px;
        font-size: 11px;
    }
    .completeness-label {
        color: var(--text-secondary);
    }
    .completeness-value {
        font-weight: 600;
    }
    .completeness-value.high {
        color: #42c767;
    }
    .completeness-value.medium {
        color: #f7b731;
    }
    .completeness-value.low {
        color: #ee5a6f;
    }
`;
document.head.appendChild(style);