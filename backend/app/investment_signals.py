"""
Investment Signals Dashboard
Real-time indicators and scoring for investment decisions
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics

class InvestmentSignalsAnalyzer:
    def __init__(self):
        self.signal_weights = {
            "product_market_fit": 0.20,
            "growth_momentum": 0.20,
            "team_quality": 0.15,
            "market_timing": 0.15,
            "competitive_moat": 0.15,
            "financial_health": 0.15
        }
    
    async def generate_investment_signals(self, all_data: Dict) -> Dict:
        """Generate comprehensive investment signals dashboard"""
        
        signals = {
            "overall_score": 0,
            "investment_grade": "HOLD",
            "signal_strength": "Medium",
            "key_signals": [],
            "red_flags": [],
            "green_flags": [],
            "momentum_indicators": {},
            "investment_readiness": {},
            "exit_potential": {},
            "risk_adjusted_score": 0
        }
        
        # Analyze each signal category
        product_signals = self._analyze_product_market_fit(all_data)
        growth_signals = self._analyze_growth_momentum(all_data)
        team_signals = self._analyze_team_quality(all_data)
        market_signals = self._analyze_market_timing(all_data)
        moat_signals = self._analyze_competitive_moat(all_data)
        financial_signals = self._analyze_financial_health(all_data)
        
        # Calculate weighted score
        scores = {
            "product_market_fit": product_signals["score"],
            "growth_momentum": growth_signals["score"],
            "team_quality": team_signals["score"],
            "market_timing": market_signals["score"],
            "competitive_moat": moat_signals["score"],
            "financial_health": financial_signals["score"]
        }
        
        # Overall score
        signals["overall_score"] = sum(
            scores[key] * self.signal_weights[key] 
            for key in scores
        )
        
        # Investment grade
        signals["investment_grade"] = self._determine_investment_grade(signals["overall_score"])
        signals["signal_strength"] = self._determine_signal_strength(scores)
        
        # Collect all signals
        all_signal_data = [
            product_signals, growth_signals, team_signals,
            market_signals, moat_signals, financial_signals
        ]
        
        for signal_data in all_signal_data:
            signals["key_signals"].extend(signal_data.get("positive_signals", []))
            signals["red_flags"].extend(signal_data.get("red_flags", []))
            signals["green_flags"].extend(signal_data.get("green_flags", []))
        
        # Momentum indicators
        signals["momentum_indicators"] = self._calculate_momentum_indicators(all_data)
        
        # Investment readiness
        signals["investment_readiness"] = self._assess_investment_readiness(all_data, scores)
        
        # Exit potential
        signals["exit_potential"] = self._analyze_exit_potential(all_data)
        
        # Risk-adjusted score
        signals["risk_adjusted_score"] = self._calculate_risk_adjusted_score(
            signals["overall_score"], 
            len(signals["red_flags"])
        )
        
        # Sort and limit signals
        signals["key_signals"] = signals["key_signals"][:10]
        signals["red_flags"] = signals["red_flags"][:5]
        signals["green_flags"] = signals["green_flags"][:5]
        
        return signals
    
    def _analyze_product_market_fit(self, data: Dict) -> Dict:
        """Analyze product-market fit signals"""
        score = 50
        positive_signals = []
        red_flags = []
        green_flags = []
        
        # Customer signals
        if data.get("intelligence", {}).get("customers", {}).get("found"):
            customers = data["intelligence"]["customers"]
            
            # Customer count
            if customers.get("estimated_customers"):
                count_str = customers["estimated_customers"]
                if "K" in count_str or "M" in count_str:
                    score += 15
                    green_flags.append(f"Strong customer base: {count_str}")
                elif any(char.isdigit() for char in count_str):
                    score += 5
            
            # Testimonials
            if customers.get("testimonials") and len(customers["testimonials"]) > 0:
                score += 10
                positive_signals.append("Customer testimonials validate product value")
            
            # Notable customers
            if customers.get("customer_logos") and len(customers["customer_logos"]) > 5:
                score += 10
                positive_signals.append(f"{len(customers['customer_logos'])} notable customers")
        
        # G2 Reviews
        if data.get("intelligence", {}).get("g2_reviews", {}).get("found"):
            g2 = data["intelligence"]["g2_reviews"]
            if g2.get("rating"):
                rating = float(g2["rating"])
                if rating >= 4.5:
                    score += 15
                    green_flags.append(f"Excellent G2 rating: {rating}/5")
                elif rating >= 4.0:
                    score += 10
                    positive_signals.append(f"Good G2 rating: {rating}/5")
                else:
                    red_flags.append(f"Low G2 rating: {rating}/5")
        
        # Product features
        if data.get("intelligence", {}).get("product", {}).get("features"):
            features = data["intelligence"]["product"]["features"]
            if len(features) > 10:
                score += 5
                positive_signals.append(f"Comprehensive feature set ({len(features)} features)")
        
        # Lack of validation
        if score == 50:  # No positive signals found
            red_flags.append("Limited product-market fit validation")
            score = 30
        
        return {
            "score": min(100, score),
            "positive_signals": positive_signals,
            "red_flags": red_flags,
            "green_flags": green_flags
        }
    
    def _analyze_growth_momentum(self, data: Dict) -> Dict:
        """Analyze growth momentum signals"""
        score = 40
        positive_signals = []
        red_flags = []
        green_flags = []
        
        # GitHub activity
        if data.get("github", {}).get("found"):
            github = data["github"]
            
            # Recent activity
            if github.get("recent_activity"):
                active_repos = [r for r in github["recent_activity"] if r.get("days_since_update", 999) < 7]
                if len(active_repos) >= 3:
                    score += 15
                    green_flags.append(f"{len(active_repos)} repos updated this week")
                elif len(active_repos) >= 1:
                    score += 10
                    positive_signals.append("Active development")
                else:
                    red_flags.append("No recent development activity")
            
            # Star growth
            total_stars = github.get("total_stars", 0)
            if total_stars > 10000:
                score += 20
                green_flags.append(f"Viral growth: {total_stars:,} GitHub stars")
            elif total_stars > 1000:
                score += 15
                positive_signals.append(f"Strong developer interest: {total_stars:,} stars")
            elif total_stars > 100:
                score += 5
        
        # News momentum
        if data.get("news", {}).get("found"):
            news = data["news"]
            if news.get("news_count", 0) >= 10:
                score += 10
                positive_signals.append(f"High media visibility: {news['news_count']} recent articles")
            
            if news.get("momentum") == "positive":
                score += 10
                positive_signals.append("Positive news momentum")
        
        # Hiring signals
        if data.get("intelligence", {}).get("team_indicators", {}).get("job_openings", 0) > 20:
            score += 15
            green_flags.append("Aggressive hiring indicates rapid growth")
        elif data.get("intelligence", {}).get("team_indicators", {}).get("job_openings", 0) > 5:
            score += 10
            positive_signals.append("Active hiring")
        
        # Traffic/engagement (from domain info)
        if data.get("domain", {}).get("has_blog") and data.get("domain", {}).get("has_careers"):
            score += 5
            positive_signals.append("Active content and hiring presence")
        
        return {
            "score": min(100, score),
            "positive_signals": positive_signals,
            "red_flags": red_flags,
            "green_flags": green_flags
        }
    
    def _analyze_team_quality(self, data: Dict) -> Dict:
        """Analyze team quality signals"""
        score = 60  # Base score
        positive_signals = []
        red_flags = []
        green_flags = []
        
        # GitHub contributors
        if data.get("github", {}).get("found"):
            github = data["github"]
            
            # Engineering team size
            if github.get("followers", 0) > 100:
                score += 10
                positive_signals.append(f"Large engineering presence: {github['followers']} followers")
            
            # Code quality (diverse tech stack)
            if github.get("tech_stack") and len(github["tech_stack"]) > 3:
                score += 5
                positive_signals.append("Diverse technical expertise")
        
        # Company age and maturity
        if data.get("github", {}).get("created_at"):
            created = data["github"]["created_at"]
            try:
                years = (datetime.now() - datetime.fromisoformat(created.replace("Z", "+00:00"))).days / 365
                if 2 <= years <= 7:
                    score += 10
                    positive_signals.append(f"Optimal company age: {int(years)} years")
                elif years > 10:
                    score += 5
                    positive_signals.append("Established company")
                elif years < 1:
                    red_flags.append("Very early stage (<1 year old)")
            except:
                pass
        
        # Leadership indicators
        if data.get("intelligence", {}).get("linkedin", {}).get("employees"):
            employees = data["intelligence"]["linkedin"]["employees"]
            try:
                emp_count = int(''.join(filter(str.isdigit, employees)))
                if emp_count > 500:
                    score += 15
                    green_flags.append(f"Strong team: {employees} employees")
                elif emp_count > 100:
                    score += 10
                    positive_signals.append(f"Growing team: {employees} employees")
                elif emp_count < 10:
                    red_flags.append(f"Very small team: {employees} employees")
            except:
                pass
        
        return {
            "score": min(100, score),
            "positive_signals": positive_signals,
            "red_flags": red_flags,
            "green_flags": green_flags
        }
    
    def _analyze_market_timing(self, data: Dict) -> Dict:
        """Analyze market timing signals"""
        score = 50
        positive_signals = []
        red_flags = []
        green_flags = []
        
        # Industry trends
        industry = data.get("company", {}).get("industry", "").lower()
        hot_markets = ["ai", "artificial intelligence", "machine learning", "climate", "fintech", "biotech", "quantum"]
        cooling_markets = ["crypto", "web3", "nft", "metaverse"]
        
        if any(hot in industry for hot in hot_markets):
            score += 20
            green_flags.append(f"Hot market: {industry}")
        elif any(cool in industry for cool in cooling_markets):
            score -= 10
            red_flags.append(f"Cooling market: {industry}")
        
        # Market maturity from competitive analysis
        if data.get("competitive_intelligence", {}).get("market_position", {}).get("market_maturity"):
            maturity = data["competitive_intelligence"]["market_position"]["market_maturity"]
            if "Emerging" in maturity:
                score += 15
                positive_signals.append("Early in emerging market")
            elif "Growth" in maturity:
                score += 10
                positive_signals.append("Growing market")
            elif "Mature" in maturity:
                red_flags.append("Mature market - limited growth")
        
        # Competitive landscape
        if data.get("competitive_intelligence", {}).get("competitors", {}).get("direct"):
            num_competitors = len(data["competitive_intelligence"]["competitors"]["direct"])
            if num_competitors < 3:
                score += 15
                green_flags.append("First-mover advantage")
            elif num_competitors > 10:
                score -= 10
                red_flags.append(f"Crowded market: {num_competitors}+ competitors")
        
        # Recent funding in the space (from news)
        if data.get("news", {}).get("recent_news"):
            funding_news = [n for n in data["news"]["recent_news"] if any(
                word in n.get("title", "").lower() for word in ["raises", "funding", "series"]
            )]
            if funding_news:
                score += 10
                positive_signals.append("Active investor interest in sector")
        
        return {
            "score": min(100, max(0, score)),
            "positive_signals": positive_signals,
            "red_flags": red_flags,
            "green_flags": green_flags
        }
    
    def _analyze_competitive_moat(self, data: Dict) -> Dict:
        """Analyze competitive moat and defensibility"""
        score = 40
        positive_signals = []
        red_flags = []
        green_flags = []
        
        # Technical moat
        if data.get("technical_dd", {}).get("technical_score", 0) > 80:
            score += 15
            green_flags.append("Strong technical infrastructure")
        
        # Patent moat
        if data.get("patent_data", {}).get("patents"):
            patent_count = len(data["patent_data"]["patents"])
            if patent_count > 10:
                score += 15
                green_flags.append(f"IP protection: {patent_count} patents")
            elif patent_count > 0:
                score += 10
                positive_signals.append(f"{patent_count} patents filed")
        
        # Network effects
        if data.get("intelligence", {}).get("customers", {}).get("customer_segments"):
            segments = data["intelligence"]["customers"]["customer_segments"]
            if "Enterprise" in segments and "SMB" in segments:
                score += 10
                positive_signals.append("Multi-segment penetration")
        
        # Brand moat
        if data.get("intelligence", {}).get("g2_reviews", {}).get("review_count"):
            reviews = int(data["intelligence"]["g2_reviews"]["review_count"])
            if reviews > 100:
                score += 10
                positive_signals.append(f"Strong brand presence: {reviews} reviews")
        
        # Platform lock-in
        if data.get("intelligence", {}).get("product", {}).get("integrations"):
            integrations = data["intelligence"]["product"]["integrations"]
            if len(integrations) > 5:
                score += 10
                positive_signals.append(f"Ecosystem lock-in: {len(integrations)} integrations")
        
        # Competitive advantages from analysis
        if data.get("competitive_intelligence", {}).get("competitive_advantages"):
            advantages = data["competitive_intelligence"]["competitive_advantages"]
            for adv in advantages:
                if adv.get("strength") == "High":
                    score += 5
                    positive_signals.append(f"{adv['type']} advantage")
        
        return {
            "score": min(100, score),
            "positive_signals": positive_signals,
            "red_flags": red_flags,
            "green_flags": green_flags
        }
    
    def _analyze_financial_health(self, data: Dict) -> Dict:
        """Analyze financial health signals"""
        score = 50
        positive_signals = []
        red_flags = []
        green_flags = []
        
        # Revenue indicators
        if data.get("intelligence", {}).get("revenue_indicators", {}).get("pricing_model"):
            pricing = data["intelligence"]["revenue_indicators"]["pricing_model"]
            if pricing in ["Subscription", "SaaS"]:
                score += 10
                positive_signals.append("Recurring revenue model")
            elif pricing == "Enterprise":
                score += 15
                positive_signals.append("Enterprise sales model")
        
        # Pricing transparency
        if data.get("intelligence", {}).get("product", {}).get("pricing"):
            score += 5
            positive_signals.append("Transparent pricing")
        
        # Business model
        if data.get("intelligence", {}).get("revenue_indicators", {}).get("business_model"):
            model = data["intelligence"]["revenue_indicators"]["business_model"]
            if "SaaS" in model:
                score += 10
                positive_signals.append("Scalable SaaS model")
            elif "Marketplace" in model:
                score += 5
                positive_signals.append("Network effects from marketplace")
        
        # Funding efficiency
        if data.get("intelligence", {}).get("revenue_indicators", {}).get("funding_stage"):
            stage = data["intelligence"]["revenue_indicators"]["funding_stage"]
            if "seed" in stage.lower():
                score += 5
                positive_signals.append("Early stage opportunity")
            elif "series" in stage.lower():
                score += 10
                positive_signals.append(f"Funded: {stage}")
        
        # Burn indicators
        if data.get("intelligence", {}).get("team_indicators", {}).get("estimated_size"):
            size = data["intelligence"]["team_indicators"]["estimated_size"]
            if "Seed" in size and "1-10" in size:
                score += 10
                positive_signals.append("Lean team structure")
            elif "500+" in size:
                red_flags.append("High burn rate likely")
                score -= 10
        
        return {
            "score": min(100, max(0, score)),
            "positive_signals": positive_signals,
            "red_flags": red_flags,
            "green_flags": green_flags
        }
    
    def _determine_investment_grade(self, score: float) -> str:
        """Determine investment grade based on score"""
        if score >= 85:
            return "STRONG BUY"
        elif score >= 75:
            return "BUY"
        elif score >= 65:
            return "MODERATE BUY"
        elif score >= 55:
            return "HOLD"
        elif score >= 45:
            return "WATCH"
        else:
            return "PASS"
    
    def _determine_signal_strength(self, scores: Dict[str, float]) -> str:
        """Determine overall signal strength"""
        avg_score = statistics.mean(scores.values())
        std_dev = statistics.stdev(scores.values()) if len(scores) > 1 else 0
        
        # High average with low variance = strong signal
        if avg_score >= 70 and std_dev < 15:
            return "Very Strong"
        elif avg_score >= 60:
            return "Strong"
        elif avg_score >= 50:
            return "Medium"
        else:
            return "Weak"
    
    def _calculate_momentum_indicators(self, data: Dict) -> Dict:
        """Calculate momentum indicators"""
        indicators = {
            "development_velocity": "Unknown",
            "hiring_velocity": "Unknown",
            "news_velocity": "Unknown",
            "customer_velocity": "Unknown",
            "overall_momentum": "Neutral"
        }
        
        momentum_scores = []
        
        # Development velocity
        if data.get("github", {}).get("recent_activity"):
            active_repos = len([r for r in data["github"]["recent_activity"] 
                              if r.get("days_since_update", 999) < 30])
            if active_repos >= 5:
                indicators["development_velocity"] = "High"
                momentum_scores.append(3)
            elif active_repos >= 2:
                indicators["development_velocity"] = "Medium"
                momentum_scores.append(2)
            else:
                indicators["development_velocity"] = "Low"
                momentum_scores.append(1)
        
        # Hiring velocity
        job_openings = data.get("intelligence", {}).get("team_indicators", {}).get("job_openings", 0)
        if job_openings > 20:
            indicators["hiring_velocity"] = "High"
            momentum_scores.append(3)
        elif job_openings > 5:
            indicators["hiring_velocity"] = "Medium"
            momentum_scores.append(2)
        else:
            indicators["hiring_velocity"] = "Low"
            momentum_scores.append(1)
        
        # News velocity
        news_count = data.get("news", {}).get("news_count", 0)
        if news_count >= 10:
            indicators["news_velocity"] = "High"
            momentum_scores.append(3)
        elif news_count >= 3:
            indicators["news_velocity"] = "Medium"
            momentum_scores.append(2)
        else:
            indicators["news_velocity"] = "Low"
            momentum_scores.append(1)
        
        # Overall momentum
        if momentum_scores:
            avg_momentum = statistics.mean(momentum_scores)
            if avg_momentum >= 2.5:
                indicators["overall_momentum"] = "Strong Positive"
            elif avg_momentum >= 2:
                indicators["overall_momentum"] = "Positive"
            elif avg_momentum >= 1.5:
                indicators["overall_momentum"] = "Neutral"
            else:
                indicators["overall_momentum"] = "Negative"
        
        return indicators
    
    def _assess_investment_readiness(self, data: Dict, scores: Dict[str, float]) -> Dict:
        """Assess readiness for different investment stages"""
        readiness = {
            "seed": {"ready": False, "score": 0, "missing": []},
            "series_a": {"ready": False, "score": 0, "missing": []},
            "series_b": {"ready": False, "score": 0, "missing": []},
            "growth": {"ready": False, "score": 0, "missing": []}
        }
        
        # Seed readiness
        seed_score = 0
        seed_missing = []
        
        if scores.get("product_market_fit", 0) > 40:
            seed_score += 25
        else:
            seed_missing.append("Product-market fit validation")
        
        if scores.get("team_quality", 0) > 50:
            seed_score += 25
        else:
            seed_missing.append("Strong founding team")
        
        if data.get("github", {}).get("found"):
            seed_score += 25
        else:
            seed_missing.append("Technical proof of concept")
        
        if scores.get("market_timing", 0) > 50:
            seed_score += 25
        else:
            seed_missing.append("Market opportunity")
        
        readiness["seed"] = {
            "ready": seed_score >= 75,
            "score": seed_score,
            "missing": seed_missing
        }
        
        # Series A readiness
        series_a_score = 0
        series_a_missing = []
        
        if data.get("intelligence", {}).get("customers", {}).get("estimated_customers"):
            series_a_score += 25
        else:
            series_a_missing.append("Customer traction")
        
        if scores.get("growth_momentum", 0) > 60:
            series_a_score += 25
        else:
            series_a_missing.append("Growth momentum")
        
        if scores.get("financial_health", 0) > 50:
            series_a_score += 25
        else:
            series_a_missing.append("Revenue model")
        
        if scores.get("competitive_moat", 0) > 50:
            series_a_score += 25
        else:
            series_a_missing.append("Competitive differentiation")
        
        readiness["series_a"] = {
            "ready": series_a_score >= 75,
            "score": series_a_score,
            "missing": series_a_missing
        }
        
        return readiness
    
    def _analyze_exit_potential(self, data: Dict) -> Dict:
        """Analyze potential exit strategies and valuation"""
        exit_potential = {
            "ipo_potential": "Low",
            "acquisition_potential": "Medium",
            "strategic_buyers": [],
            "exit_timeline": "3-5 years",
            "valuation_range": "Unknown"
        }
        
        # IPO potential
        ipo_score = 0
        
        # Large team indicates scale
        if data.get("intelligence", {}).get("linkedin", {}).get("employees"):
            try:
                emp_count = int(''.join(filter(str.isdigit, 
                    data["intelligence"]["linkedin"]["employees"])))
                if emp_count > 1000:
                    ipo_score += 40
                elif emp_count > 500:
                    ipo_score += 20
            except:
                pass
        
        # Strong brand presence
        if data.get("intelligence", {}).get("g2_reviews", {}).get("review_count"):
            try:
                reviews = int(data["intelligence"]["g2_reviews"]["review_count"])
                if reviews > 500:
                    ipo_score += 30
                elif reviews > 100:
                    ipo_score += 15
            except:
                pass
        
        # Market leadership
        if data.get("github", {}).get("total_stars", 0) > 10000:
            ipo_score += 30
        
        if ipo_score >= 70:
            exit_potential["ipo_potential"] = "High"
            exit_potential["exit_timeline"] = "5-7 years"
        elif ipo_score >= 40:
            exit_potential["ipo_potential"] = "Medium"
        
        # Acquisition potential
        acq_score = 0
        strategic_buyers = []
        
        # Technology fit
        if data.get("intelligence", {}).get("product", {}).get("integrations"):
            integrations = data["intelligence"]["product"]["integrations"]
            for integration in integrations[:5]:
                if any(bigco in integration.lower() for bigco in 
                      ["microsoft", "google", "amazon", "salesforce", "oracle"]):
                    strategic_buyers.append(integration)
                    acq_score += 20
        
        # Customer overlap
        if data.get("intelligence", {}).get("customers", {}).get("customer_segments"):
            if "Enterprise" in data["intelligence"]["customers"]["customer_segments"]:
                acq_score += 30
                strategic_buyers.extend(["Microsoft", "Salesforce", "Oracle"])
        
        # Technical assets
        if data.get("competitive_intelligence", {}).get("competitive_advantages"):
            for adv in data["competitive_intelligence"]["competitive_advantages"]:
                if adv.get("type") == "Technology" and adv.get("strength") == "High":
                    acq_score += 30
                    break
        
        if acq_score >= 60:
            exit_potential["acquisition_potential"] = "High"
            exit_potential["exit_timeline"] = "2-4 years"
        elif acq_score >= 30:
            exit_potential["acquisition_potential"] = "Medium"
        
        exit_potential["strategic_buyers"] = list(set(strategic_buyers))[:5]
        
        return exit_potential
    
    def _calculate_risk_adjusted_score(self, raw_score: float, red_flags_count: int) -> float:
        """Calculate risk-adjusted investment score"""
        # Penalty for red flags
        risk_penalty = red_flags_count * 5
        
        # Risk adjustment factor
        risk_factor = 1 - (risk_penalty / 100)
        risk_factor = max(0.5, risk_factor)  # Minimum 50% of original score
        
        return round(raw_score * risk_factor, 1)

# Singleton instance
investment_signals = InvestmentSignalsAnalyzer()