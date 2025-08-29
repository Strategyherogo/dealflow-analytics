/**
 * Enhanced DealFlow Analytics Chrome Extension
 * Advanced UI components and real-time features
 */

class DealFlowExtension {
    constructor() {
        this.apiUrl = this.getApiUrl();
        this.currentCompany = null;
        this.analysisData = null;
        this.wsConnection = null;
        this.userSettings = this.loadSettings();
        this.aiProviders = ['openai', 'anthropic', 'groq', 'perplexity'];
        this.selectedProviders = new Set(['groq']); // Default to fast provider
        
        this.init();
    }

    getApiUrl() {
        // Check if we're in development or production
        return chrome.runtime.getManifest().version.includes('dev') 
            ? 'http://localhost:8000'
            : 'https://monkfish-app-7otbm.ondigitalocean.app';
    }

    async init() {
        await this.loadUserPreferences();
        await this.detectCurrentCompany();
        this.setupEventListeners();
        this.initializeWebSocket();
        this.setupKeyboardShortcuts();
        this.checkSubscriptionStatus();
        
        // Initialize advanced features if premium user
        if (this.userSettings.tier !== 'free') {
            this.initializeAdvancedFeatures();
        }
    }

    async loadUserPreferences() {
        return new Promise((resolve) => {
            chrome.storage.sync.get(['preferences', 'tier', 'apiKeys'], (data) => {
                this.userSettings = {
                    ...this.userSettings,
                    ...data.preferences,
                    tier: data.tier || 'free',
                    apiKeys: data.apiKeys || {}
                };
                resolve();
            });
        });
    }

    async detectCurrentCompany() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        if (!tab || !tab.url) {
            this.showNoCompanyState();
            return;
        }

        // Send message to content script
        chrome.tabs.sendMessage(tab.id, { action: 'detectCompany' }, (response) => {
            if (chrome.runtime.lastError) {
                console.error('Error detecting company:', chrome.runtime.lastError);
                this.showNoCompanyState();
                return;
            }

            if (response && response.company) {
                this.currentCompany = response.company;
                this.displayCompanyInfo();
                
                // Auto-analyze if enabled
                if (this.userSettings.autoAnalyze) {
                    this.analyzeCompany();
                }
            } else {
                this.showNoCompanyState();
            }
        });
    }

    displayCompanyInfo() {
        const companyHeader = document.getElementById('company-header');
        const companyName = document.getElementById('company-name');
        const companyInfo = document.getElementById('company-info');
        
        companyName.textContent = this.currentCompany.name;
        companyInfo.textContent = `${this.currentCompany.industry || 'Unknown Industry'} • ${this.currentCompany.employeeCount || 'Unknown'} employees`;
        
        document.getElementById('company-detected').classList.remove('hidden');
        document.getElementById('no-company').classList.add('hidden');
        
        // Add company logo if available
        if (this.currentCompany.logoUrl) {
            const logo = document.createElement('img');
            logo.src = this.currentCompany.logoUrl;
            logo.className = 'company-logo';
            companyHeader.prepend(logo);
        }
    }

    async analyzeCompany() {
        if (!this.currentCompany) return;

        this.showLoadingState();
        
        try {
            // Determine analysis type based on user tier
            const analysisType = this.getAnalysisType();
            
            const response = await fetch(`${this.apiUrl}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Extension-Version': chrome.runtime.getManifest().version,
                    'X-User-Tier': this.userSettings.tier
                },
                body: JSON.stringify({
                    ...this.currentCompany,
                    analysisType,
                    aiProviders: Array.from(this.selectedProviders),
                    userApiKeys: this.userSettings.apiKeys
                })
            });

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }

            this.analysisData = await response.json();
            this.displayAnalysisResults();
            this.saveToHistory();
            
            // Track usage for billing
            this.trackUsage('analysis', analysisType);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Failed to analyze company. Please try again.');
        } finally {
            this.hideLoadingState();
        }
    }

    getAnalysisType() {
        const tier = this.userSettings.tier;
        
        if (tier === 'enterprise') {
            return 'comprehensive';
        } else if (tier === 'pro') {
            return 'deep_dive';
        } else {
            return 'quick';
        }
    }

    displayAnalysisResults() {
        if (!this.analysisData) return;

        // Update investment score with animation
        this.animateScore(this.analysisData.investmentScore);
        
        // Display funding history
        this.displayFundingHistory(this.analysisData.fundingHistory);
        
        // Display growth signals
        this.displayGrowthSignals(this.analysisData.growthSignals);
        
        // Display market analysis
        this.displayMarketAnalysis(this.analysisData.marketAnalysis);
        
        // Display AI insights
        this.displayAIInsights(this.analysisData.aiThesis);
        
        // Display advanced analytics if available
        if (this.analysisData.predictiveAnalytics) {
            this.displayPredictiveAnalytics(this.analysisData.predictiveAnalytics);
        }
        
        // Enable export buttons
        document.getElementById('export-pdf-btn').disabled = false;
        document.getElementById('export-csv-btn').disabled = false;
        document.getElementById('track-btn').disabled = false;
        
        // Show collaboration features for team users
        if (this.userSettings.tier !== 'free') {
            this.showCollaborationFeatures();
        }
    }

    animateScore(score) {
        const scoreElement = document.querySelector('.score-value');
        const circle = document.getElementById('investment-score');
        
        // Animate number
        let currentScore = 0;
        const increment = score / 50; // 50 frames
        const interval = setInterval(() => {
            currentScore += increment;
            if (currentScore >= score) {
                currentScore = score;
                clearInterval(interval);
            }
            scoreElement.textContent = Math.round(currentScore);
        }, 20);
        
        // Color based on score
        let color = '#ff4444'; // Red for low scores
        if (score >= 70) {
            color = '#44ff44'; // Green for high scores
        } else if (score >= 50) {
            color = '#ffaa44'; // Orange for medium scores
        }
        
        circle.style.background = `conic-gradient(${color} ${score * 3.6}deg, #e0e0e0 0deg)`;
    }

    displayFundingHistory(fundingHistory) {
        const container = document.getElementById('funding-history');
        
        if (!fundingHistory || fundingHistory.length === 0) {
            container.innerHTML = '<p class="no-data">No funding data available</p>';
            return;
        }
        
        const html = fundingHistory.map(round => `
            <div class="funding-round">
                <div class="round-header">
                    <span class="round-type">${round.type}</span>
                    <span class="round-amount">$${this.formatAmount(round.amount)}</span>
                </div>
                <div class="round-details">
                    <span class="round-date">${this.formatDate(round.date)}</span>
                    ${round.investors ? `<span class="round-investors">${round.investors.join(', ')}</span>` : ''}
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }

    displayGrowthSignals(growthSignals) {
        const container = document.getElementById('growth-signals');
        
        if (!growthSignals) {
            container.innerHTML = '<p class="no-data">Analyzing growth signals...</p>';
            return;
        }
        
        const signals = [
            { label: '👥 Team Growth', value: growthSignals.employeeGrowth, trend: 'up' },
            { label: '🌐 Web Traffic', value: growthSignals.webTraffic, trend: 'up' },
            { label: '💻 Tech Stack', value: growthSignals.techStack, trend: 'stable' },
            { label: '📰 Media Buzz', value: growthSignals.mediaSentiment, trend: 'up' },
            { label: '💼 Hiring Velocity', value: growthSignals.hiringSignal, trend: 'up' }
        ];
        
        const html = signals.map(signal => `
            <div class="signal-item">
                <span class="signal-label">${signal.label}</span>
                <div class="signal-value">
                    <span>${signal.value || 'N/A'}</span>
                    ${this.getTrendIcon(signal.trend)}
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }

    displayMarketAnalysis(marketAnalysis) {
        const container = document.getElementById('market-analysis');
        
        if (!marketAnalysis) {
            container.innerHTML = '<p class="no-data">Loading market data...</p>';
            return;
        }
        
        const html = `
            <div class="market-stats">
                <div class="stat-item">
                    <label>TAM</label>
                    <value>$${this.formatAmount(marketAnalysis.tam)}B</value>
                </div>
                <div class="stat-item">
                    <label>Growth Rate</label>
                    <value>${(marketAnalysis.growthRate * 100).toFixed(1)}%</value>
                </div>
                <div class="stat-item">
                    <label>Competition</label>
                    <value>${marketAnalysis.competitors?.length || 0} players</value>
                </div>
            </div>
            ${marketAnalysis.competitors ? `
                <div class="competitors-list">
                    <label>Key Competitors:</label>
                    <div class="competitor-chips">
                        ${marketAnalysis.competitors.slice(0, 5).map(c => 
                            `<span class="chip">${c}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
        `;
        
        container.innerHTML = html;
    }

    displayAIInsights(aiThesis) {
        const container = document.getElementById('ai-thesis');
        
        if (!aiThesis) {
            container.innerHTML = '<p class="placeholder">Generating AI insights...</p>';
            return;
        }
        
        const html = `
            <div class="ai-summary">
                <h4>Investment Thesis</h4>
                <p>${aiThesis.summary}</p>
            </div>
            
            <div class="ai-analysis-grid">
                <div class="ai-section strengths">
                    <h5>✅ Strengths</h5>
                    <ul>
                        ${aiThesis.strengths.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="ai-section risks">
                    <h5>⚠️ Risks</h5>
                    <ul>
                        ${aiThesis.risks.map(r => `<li>${r}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="ai-recommendation">
                <strong>Recommendation:</strong> 
                <span class="recommendation-badge ${this.getRecommendationClass(aiThesis.recommendation)}">
                    ${aiThesis.recommendation}
                </span>
            </div>
            
            ${aiThesis.similarCompanies ? `
                <div class="similar-companies">
                    <h5>Similar Successful Companies</h5>
                    <div class="company-cards">
                        ${aiThesis.similarCompanies.map(c => `
                            <div class="similar-company-card">
                                <span class="company-name">${c.name}</span>
                                <span class="exit-value">${c.exitValue}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;
        
        container.innerHTML = html;
    }

    displayPredictiveAnalytics(predictiveAnalytics) {
        // Create a new section for predictive analytics
        const predictiveSection = document.createElement('div');
        predictiveSection.className = 'predictive-analytics-section';
        predictiveSection.innerHTML = `
            <h3>🔮 Predictive Analytics</h3>
            
            <div class="prediction-cards">
                <div class="prediction-card">
                    <h4>Exit Prediction</h4>
                    <div class="prediction-value">${predictiveAnalytics.exitPrediction.likely_exit_type}</div>
                    <div class="prediction-details">
                        <span>Expected Value: $${this.formatAmount(predictiveAnalytics.exitPrediction.expected_exit_value)}</span>
                        <span>Timeline: ${predictiveAnalytics.exitPrediction.expected_time_to_exit_years} years</span>
                        <span>Confidence: ${(predictiveAnalytics.exitPrediction.confidence_score * 100).toFixed(0)}%</span>
                    </div>
                </div>
                
                <div class="prediction-card">
                    <h4>Success Probability</h4>
                    <div class="probability-meter">
                        <div class="probability-fill" style="width: ${predictiveAnalytics.exitPrediction.exit_probability * 100}%"></div>
                        <span class="probability-text">${(predictiveAnalytics.exitPrediction.exit_probability * 100).toFixed(0)}%</span>
                    </div>
                </div>
                
                <div class="prediction-card">
                    <h4>Key Value Drivers</h4>
                    <ul class="value-drivers">
                        ${predictiveAnalytics.exitPrediction.key_drivers.map(driver => 
                            `<li class="driver-item">${driver}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        // Insert after AI thesis section
        document.querySelector('.ai-insights').appendChild(predictiveSection);
    }

    showCollaborationFeatures() {
        // Add collaboration toolbar
        const toolbar = document.createElement('div');
        toolbar.className = 'collaboration-toolbar';
        toolbar.innerHTML = `
            <button class="collab-btn" id="share-btn">
                <svg class="icon"><!-- Share icon --></svg>
                Share
            </button>
            <button class="collab-btn" id="annotate-btn">
                <svg class="icon"><!-- Annotate icon --></svg>
                Annotate
            </button>
            <button class="collab-btn" id="vote-btn">
                <svg class="icon"><!-- Vote icon --></svg>
                Vote
            </button>
            <button class="collab-btn" id="compare-btn">
                <svg class="icon"><!-- Compare icon --></svg>
                Compare
            </button>
        `;
        
        document.querySelector('.action-buttons').before(toolbar);
        
        // Add event listeners for collaboration features
        document.getElementById('share-btn').addEventListener('click', () => this.shareAnalysis());
        document.getElementById('annotate-btn').addEventListener('click', () => this.openAnnotationMode());
        document.getElementById('vote-btn').addEventListener('click', () => this.openVotingPanel());
        document.getElementById('compare-btn').addEventListener('click', () => this.openComparisonTool());
    }

    async shareAnalysis() {
        const shareModal = this.createModal('Share Analysis', `
            <div class="share-modal">
                <div class="share-options">
                    <h4>Share with Team</h4>
                    <input type="email" id="share-emails" placeholder="Enter email addresses (comma separated)">
                    
                    <h4>Permissions</h4>
                    <label class="checkbox-label">
                        <input type="checkbox" id="perm-view" checked> Can View
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="perm-comment" checked> Can Comment
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="perm-edit"> Can Edit
                    </label>
                    
                    <h4>Add Note</h4>
                    <textarea id="share-note" placeholder="Add a note for recipients..."></textarea>
                </div>
                
                <div class="share-link-section">
                    <h4>Or Share via Link</h4>
                    <div class="share-link-container">
                        <input type="text" id="share-link" readonly>
                        <button id="copy-link-btn">Copy</button>
                    </div>
                </div>
            </div>
        `);
        
        // Generate share link
        const shareData = {
            company: this.currentCompany,
            analysis: this.analysisData,
            sharedBy: this.userSettings.email,
            timestamp: Date.now()
        };
        
        try {
            const response = await fetch(`${this.apiUrl}/api/share`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(shareData)
            });
            
            const { shareUrl } = await response.json();
            document.getElementById('share-link').value = shareUrl;
            
            document.getElementById('copy-link-btn').addEventListener('click', () => {
                navigator.clipboard.writeText(shareUrl);
                this.showNotification('Link copied to clipboard!');
            });
            
        } catch (error) {
            console.error('Share error:', error);
        }
    }

    openAnnotationMode() {
        // Add annotation layer over the analysis
        const annotationLayer = document.createElement('div');
        annotationLayer.className = 'annotation-layer';
        annotationLayer.innerHTML = `
            <div class="annotation-toolbar">
                <button class="annotation-tool" data-type="highlight">🖍 Highlight</button>
                <button class="annotation-tool" data-type="note">📝 Note</button>
                <button class="annotation-tool" data-type="flag">🚩 Flag</button>
                <button class="annotation-tool" data-type="question">❓ Question</button>
                <button id="exit-annotation">✕ Exit</button>
            </div>
        `;
        
        document.body.appendChild(annotationLayer);
        
        // Make analysis sections selectable
        document.querySelectorAll('.metric-card, .ai-section').forEach(section => {
            section.classList.add('annotatable');
            section.addEventListener('click', (e) => this.addAnnotation(e.target));
        });
        
        document.getElementById('exit-annotation').addEventListener('click', () => {
            annotationLayer.remove();
            document.querySelectorAll('.annotatable').forEach(section => {
                section.classList.remove('annotatable');
            });
        });
    }

    async addAnnotation(element) {
        const annotationType = document.querySelector('.annotation-tool.active')?.dataset.type || 'note';
        
        const annotation = {
            type: annotationType,
            content: prompt('Enter your annotation:'),
            section: element.id || element.className,
            timestamp: Date.now(),
            user: this.userSettings.email
        };
        
        if (!annotation.content) return;
        
        // Send to server
        try {
            await fetch(`${this.apiUrl}/api/annotations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    companyId: this.currentCompany.id,
                    annotation
                })
            });
            
            // Add visual indicator
            const indicator = document.createElement('span');
            indicator.className = `annotation-indicator annotation-${annotationType}`;
            indicator.title = annotation.content;
            element.appendChild(indicator);
            
            this.showNotification('Annotation added');
            
        } catch (error) {
            console.error('Annotation error:', error);
        }
    }

    openVotingPanel() {
        const votingModal = this.createModal('Investment Committee Vote', `
            <div class="voting-panel">
                <h4>Cast Your Vote</h4>
                
                <div class="vote-options">
                    <label class="vote-option">
                        <input type="radio" name="vote" value="strong_yes">
                        <span class="vote-label strong-yes">Strong Yes</span>
                    </label>
                    <label class="vote-option">
                        <input type="radio" name="vote" value="yes">
                        <span class="vote-label yes">Yes</span>
                    </label>
                    <label class="vote-option">
                        <input type="radio" name="vote" value="neutral">
                        <span class="vote-label neutral">Neutral</span>
                    </label>
                    <label class="vote-option">
                        <input type="radio" name="vote" value="no">
                        <span class="vote-label no">No</span>
                    </label>
                    <label class="vote-option">
                        <input type="radio" name="vote" value="strong_no">
                        <span class="vote-label strong-no">Strong No</span>
                    </label>
                </div>
                
                <div class="vote-comment">
                    <h4>Comments</h4>
                    <textarea id="vote-comment" placeholder="Explain your decision..."></textarea>
                </div>
                
                <div class="current-votes">
                    <h4>Current Votes</h4>
                    <div id="vote-summary">Loading...</div>
                </div>
                
                <button id="submit-vote" class="btn-primary">Submit Vote</button>
            </div>
        `);
        
        // Load current votes
        this.loadVotes();
        
        document.getElementById('submit-vote').addEventListener('click', () => this.submitVote());
    }

    async submitVote() {
        const vote = document.querySelector('input[name="vote"]:checked')?.value;
        const comment = document.getElementById('vote-comment').value;
        
        if (!vote) {
            alert('Please select a vote');
            return;
        }
        
        try {
            await fetch(`${this.apiUrl}/api/votes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    companyId: this.currentCompany.id,
                    vote,
                    comment,
                    user: this.userSettings.email
                })
            });
            
            this.showNotification('Vote submitted successfully');
            this.closeModal();
            
        } catch (error) {
            console.error('Vote submission error:', error);
        }
    }

    openComparisonTool() {
        const comparisonModal = this.createModal('Company Comparison', `
            <div class="comparison-tool">
                <div class="comparison-search">
                    <input type="text" id="comparison-search" placeholder="Search for companies to compare...">
                    <div id="comparison-suggestions"></div>
                </div>
                
                <div class="comparison-selected">
                    <h4>Selected Companies</h4>
                    <div id="selected-companies">
                        <div class="selected-company">${this.currentCompany.name}</div>
                    </div>
                </div>
                
                <button id="run-comparison" class="btn-primary">Compare</button>
                
                <div id="comparison-results"></div>
            </div>
        `);
        
        // Setup search
        document.getElementById('comparison-search').addEventListener('input', (e) => {
            this.searchCompanies(e.target.value);
        });
        
        document.getElementById('run-comparison').addEventListener('click', () => {
            this.runComparison();
        });
    }

    async searchCompanies(query) {
        if (query.length < 3) return;
        
        try {
            const response = await fetch(`${this.apiUrl}/api/search?q=${encodeURIComponent(query)}`);
            const companies = await response.json();
            
            const suggestions = document.getElementById('comparison-suggestions');
            suggestions.innerHTML = companies.map(company => `
                <div class="suggestion" data-company='${JSON.stringify(company)}'>
                    ${company.name} - ${company.industry}
                </div>
            `).join('');
            
            suggestions.querySelectorAll('.suggestion').forEach(s => {
                s.addEventListener('click', (e) => {
                    const company = JSON.parse(e.target.dataset.company);
                    this.addToComparison(company);
                });
            });
            
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    initializeWebSocket() {
        if (this.userSettings.tier === 'free') return;
        
        const wsUrl = this.apiUrl.replace('http', 'ws') + '/ws';
        this.wsConnection = new WebSocket(wsUrl);
        
        this.wsConnection.onopen = () => {
            console.log('WebSocket connected');
            
            // Join workspace
            this.wsConnection.send(JSON.stringify({
                type: 'join',
                workspace: this.userSettings.workspace,
                user: this.userSettings.email
            }));
        };
        
        this.wsConnection.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleRealtimeUpdate(message);
        };
        
        this.wsConnection.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleRealtimeUpdate(message) {
        switch (message.type) {
            case 'annotation_created':
                this.showRealtimeAnnotation(message.annotation);
                break;
                
            case 'vote_update':
                this.updateVoteDisplay(message.vote_summary);
                break;
                
            case 'user_joined':
                this.showNotification(`${message.user_id} joined the workspace`);
                break;
                
            case 'analysis_update':
                this.updateAnalysisData(message.updates);
                break;
                
            default:
                console.log('Unknown message type:', message.type);
        }
    }

    showRealtimeAnnotation(annotation) {
        // Find the annotated section
        const section = document.getElementById(annotation.section) || 
                       document.querySelector(`.${annotation.section}`);
        
        if (section) {
            const bubble = document.createElement('div');
            bubble.className = 'realtime-annotation';
            bubble.innerHTML = `
                <div class="annotation-user">${annotation.user}</div>
                <div class="annotation-content">${annotation.content}</div>
            `;
            
            section.appendChild(bubble);
            
            // Fade out after 5 seconds
            setTimeout(() => {
                bubble.classList.add('fade-out');
                setTimeout(() => bubble.remove(), 500);
            }, 5000);
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to analyze
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.analyzeCompany();
            }
            
            // Ctrl/Cmd + S to share
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.shareAnalysis();
            }
            
            // Ctrl/Cmd + E to export
            if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
                e.preventDefault();
                this.exportPDF();
            }
            
            // ESC to close modals
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    async checkSubscriptionStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/api/subscription/status`, {
                headers: {
                    'Authorization': `Bearer ${this.userSettings.apiToken}`
                }
            });
            
            if (response.ok) {
                const status = await response.json();
                this.userSettings.tier = status.tier;
                this.userSettings.usage = status.usage;
                
                // Update UI based on tier
                this.updateTierUI();
            }
        } catch (error) {
            console.error('Subscription check error:', error);
        }
    }

    updateTierUI() {
        // Add tier badge
        const tierBadge = document.createElement('div');
        tierBadge.className = `tier-badge tier-${this.userSettings.tier}`;
        tierBadge.textContent = this.userSettings.tier.toUpperCase();
        document.querySelector('header').appendChild(tierBadge);
        
        // Show usage if applicable
        if (this.userSettings.usage) {
            const usageBar = document.createElement('div');
            usageBar.className = 'usage-bar';
            usageBar.innerHTML = `
                <div class="usage-progress" style="width: ${this.userSettings.usage.percentage}%"></div>
                <span class="usage-text">${this.userSettings.usage.used}/${this.userSettings.usage.limit} analyses</span>
            `;
            document.querySelector('footer').before(usageBar);
        }
    }

    initializeAdvancedFeatures() {
        // Add AI provider selector
        this.addAIProviderSelector();
        
        // Add natural language query
        this.addNaturalLanguageQuery();
        
        // Add bulk analysis option
        this.addBulkAnalysisOption();
        
        // Add export options
        this.enhanceExportOptions();
    }

    addAIProviderSelector() {
        const selector = document.createElement('div');
        selector.className = 'ai-provider-selector';
        selector.innerHTML = `
            <h4>AI Providers</h4>
            <div class="provider-chips">
                ${this.aiProviders.map(provider => `
                    <label class="provider-chip">
                        <input type="checkbox" value="${provider}" ${this.selectedProviders.has(provider) ? 'checked' : ''}>
                        <span>${provider.charAt(0).toUpperCase() + provider.slice(1)}</span>
                    </label>
                `).join('')}
            </div>
        `;
        
        document.querySelector('.main-content').prepend(selector);
        
        selector.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.selectedProviders.add(e.target.value);
                } else {
                    this.selectedProviders.delete(e.target.value);
                }
            });
        });
    }

    addNaturalLanguageQuery() {
        const querySection = document.createElement('div');
        querySection.className = 'nl-query-section';
        querySection.innerHTML = `
            <div class="nl-query-container">
                <input type="text" id="nl-query" placeholder="Ask anything... e.g., 'Is this company likely to exit in 3 years?'">
                <button id="nl-query-btn">Ask AI</button>
            </div>
            <div id="nl-query-result"></div>
        `;
        
        document.querySelector('.ai-insights').after(querySection);
        
        document.getElementById('nl-query-btn').addEventListener('click', () => {
            this.processNaturalLanguageQuery();
        });
        
        document.getElementById('nl-query').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.processNaturalLanguageQuery();
            }
        });
    }

    async processNaturalLanguageQuery() {
        const query = document.getElementById('nl-query').value;
        if (!query) return;
        
        const resultDiv = document.getElementById('nl-query-result');
        resultDiv.innerHTML = '<div class="loading">Processing query...</div>';
        
        try {
            const response = await fetch(`${this.apiUrl}/api/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    context: this.analysisData,
                    company: this.currentCompany
                })
            });
            
            const result = await response.json();
            
            resultDiv.innerHTML = `
                <div class="query-answer">
                    <h5>Answer:</h5>
                    <p>${result.answer}</p>
                    ${result.confidence ? `<span class="confidence">Confidence: ${(result.confidence * 100).toFixed(0)}%</span>` : ''}
                    ${result.sources ? `
                        <div class="sources">
                            <h6>Sources:</h6>
                            ${result.sources.map(s => `<a href="${s.url}" target="_blank">${s.title}</a>`).join(', ')}
                        </div>
                    ` : ''}
                </div>
            `;
            
        } catch (error) {
            console.error('Query error:', error);
            resultDiv.innerHTML = '<div class="error">Failed to process query</div>';
        }
    }

    // Utility functions
    formatAmount(amount) {
        if (!amount) return 'N/A';
        
        if (amount >= 1e9) {
            return (amount / 1e9).toFixed(1) + 'B';
        } else if (amount >= 1e6) {
            return (amount / 1e6).toFixed(1) + 'M';
        } else if (amount >= 1e3) {
            return (amount / 1e3).toFixed(1) + 'K';
        }
        
        return amount.toFixed(0);
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        const date = new Date(dateString);
        const options = { year: 'numeric', month: 'short' };
        return date.toLocaleDateString('en-US', options);
    }

    getTrendIcon(trend) {
        const icons = {
            up: '📈',
            down: '📉',
            stable: '➡️'
        };
        return icons[trend] || '';
    }

    getRecommendationClass(recommendation) {
        if (recommendation.includes('STRONG') || recommendation.includes('BUY')) {
            return 'strong-positive';
        } else if (recommendation.includes('CONSIDER')) {
            return 'positive';
        } else if (recommendation.includes('WATCH')) {
            return 'neutral';
        } else {
            return 'negative';
        }
    }

    createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close">✕</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.remove();
        });
        
        return modal;
    }

    closeModal() {
        const modal = document.querySelector('.modal');
        if (modal) {
            modal.remove();
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }

    showLoadingState() {
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('main-content').classList.add('blur');
    }

    hideLoadingState() {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('main-content').classList.remove('blur');
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error').classList.remove('hidden');
    }

    showNoCompanyState() {
        document.getElementById('company-detected').classList.add('hidden');
        document.getElementById('no-company').classList.remove('hidden');
    }

    saveToHistory() {
        if (!this.analysisData || !this.currentCompany) return;
        
        chrome.storage.local.get(['analysisHistory'], (data) => {
            const history = data.analysisHistory || [];
            
            history.unshift({
                company: this.currentCompany,
                analysis: this.analysisData,
                timestamp: Date.now()
            });
            
            // Keep only last 50 analyses
            if (history.length > 50) {
                history.pop();
            }
            
            chrome.storage.local.set({ analysisHistory: history });
        });
    }

    trackUsage(action, type) {
        // Track usage for billing and analytics
        fetch(`${this.apiUrl}/api/track`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.userSettings.apiToken}`
            },
            body: JSON.stringify({
                action,
                type,
                company: this.currentCompany?.name,
                timestamp: Date.now()
            })
        }).catch(error => console.error('Tracking error:', error));
    }

    loadSettings() {
        return {
            autoAnalyze: false,
            theme: 'light',
            tier: 'free',
            apiKeys: {},
            workspace: null,
            email: null,
            apiToken: null
        };
    }

    setupEventListeners() {
        // Main analyze button
        document.getElementById('analyze-btn')?.addEventListener('click', () => {
            this.analyzeCompany();
        });
        
        // Export buttons
        document.getElementById('export-pdf-btn')?.addEventListener('click', () => {
            this.exportPDF();
        });
        
        document.getElementById('export-csv-btn')?.addEventListener('click', () => {
            this.exportCSV();
        });
        
        // Track button
        document.getElementById('track-btn')?.addEventListener('click', () => {
            this.trackCompany();
        });
        
        // Retry button
        document.getElementById('retry-btn')?.addEventListener('click', () => {
            this.detectCurrentCompany();
        });
    }

    async exportPDF() {
        if (!this.analysisData) return;
        
        try {
            const response = await fetch(`${this.apiUrl}/api/export/pdf`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    company: this.currentCompany,
                    analysis: this.analysisData
                })
            });
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            
            chrome.downloads.download({
                url,
                filename: `${this.currentCompany.name.replace(/\s+/g, '_')}_analysis.pdf`,
                saveAs: true
            });
            
            this.trackUsage('export', 'pdf');
            
        } catch (error) {
            console.error('PDF export error:', error);
            this.showError('Failed to export PDF');
        }
    }

    async exportCSV() {
        if (!this.analysisData) return;
        
        try {
            const response = await fetch(`${this.apiUrl}/api/export/csv`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    company: this.currentCompany,
                    analysis: this.analysisData
                })
            });
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            
            chrome.downloads.download({
                url,
                filename: `${this.currentCompany.name.replace(/\s+/g, '_')}_data.csv`,
                saveAs: true
            });
            
            this.trackUsage('export', 'csv');
            
        } catch (error) {
            console.error('CSV export error:', error);
            this.showError('Failed to export CSV');
        }
    }

    async trackCompany() {
        if (!this.currentCompany) return;
        
        try {
            const response = await fetch(`${this.apiUrl}/api/track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    company: this.currentCompany,
                    user: this.userSettings.email
                })
            });
            
            if (response.ok) {
                this.showNotification('Company added to tracking list');
                document.getElementById('track-btn').textContent = 'Tracking';
                document.getElementById('track-btn').disabled = true;
            }
            
        } catch (error) {
            console.error('Tracking error:', error);
            this.showError('Failed to track company');
        }
    }
}

// Initialize extension when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new DealFlowExtension();
});