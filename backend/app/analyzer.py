"""
Company Analyzer
Combines data from multiple sources and generates investment scores
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

class CompanyAnalyzer:
    def __init__(self):
        self.weights = {
            "financial": 0.25,
            "growth": 0.20,
            "innovation": 0.15,
            "market": 0.15,
            "team": 0.15,
            "momentum": 0.10
        }
    
    async def analyze(self, combined_data: Dict) -> Dict:
        """Analyze combined data from all sources"""
        # Extract company info
        company_info = combined_data.get("company", {})
        
        # Calculate individual scores
        scores = {
            "financial_score": self._calculate_financial_score(combined_data),
            "growth_score": self._calculate_growth_score(combined_data),
            "innovation_score": self._calculate_innovation_score(combined_data),
            "market_score": self._calculate_market_score(combined_data),
            "team_score": self._calculate_team_score(combined_data),
            "momentum_score": self._calculate_momentum_score(combined_data)
        }
        
        # Calculate weighted investment score
        investment_score = self._calculate_investment_score(scores)
        
        # Extract funding history
        funding_history = self._extract_funding_history(combined_data)
        
        # Growth signals
        growth_signals = self._extract_growth_signals(combined_data)
        
        # Market analysis
        market_analysis = self._perform_market_analysis(combined_data)
        
        # Determine data sources used
        data_sources = self._get_data_sources(combined_data)
        
        return {
            "investment_score": investment_score,
            "score_breakdown": scores,
            "funding_history": funding_history,
            "growth_signals": growth_signals,
            "market_analysis": market_analysis,
            "data_sources": data_sources,
            "data_quality": self._assess_overall_data_quality(combined_data)
        }
    
    def _calculate_financial_score(self, data: Dict) -> int:
        """Calculate financial health score"""
        score = 50  # Base score
        
        # SEC data
        sec_data = data.get("sec_data", {})
        if not isinstance(sec_data, dict) or "error" in sec_data:
            return score
        
        financial_metrics = sec_data.get("financial_metrics", {})
        
        # Adjust based on filing recency
        data_quality = sec_data.get("data_quality", {})
        if data_quality.get("score", 0) > 0.7:
            score += 20
        
        # Revenue growth (placeholder - would parse from filings)
        if financial_metrics.get("has_financial_data"):
            score += 10
        
        # Funding from Wikipedia/Crunchbase data
        wiki_data = data.get("wikipedia_data", {})
        if isinstance(wiki_data, dict) and not "error" in wiki_data:
            if wiki_data.get("structured_data", {}).get("revenue"):
                score += 10
        
        return min(100, score)
    
    def _calculate_growth_score(self, data: Dict) -> int:
        """Calculate growth trajectory score"""
        score = 40  # Base score
        
        # GitHub growth indicators
        github_data = data.get("github_data", {})
        if isinstance(github_data, dict) and not "error" in github_data:
            growth_metrics = github_data.get("growth_metrics", {})
            score += growth_metrics.get("activity_score", 0) * 0.3
            score += growth_metrics.get("popularity_score", 0) * 0.2
        
        # Patent velocity
        patent_data = data.get("patent_data", {})
        if isinstance(patent_data, dict) and not "error" in patent_data:
            innovation_metrics = patent_data.get("innovation_metrics", {})
            velocity = innovation_metrics.get("patent_velocity", 0)
            if velocity > 5:
                score += 20
            elif velocity > 2:
                score += 10
        
        # Employee growth from LinkedIn data
        company_info = data.get("company", {})
        if company_info.get("employeeCount"):
            try:
                employees = int(company_info["employeeCount"])
                if employees > 1000:
                    score += 15
                elif employees > 100:
                    score += 10
                elif employees > 50:
                    score += 5
            except:
                pass
        
        return min(100, int(score))
    
    def _calculate_innovation_score(self, data: Dict) -> int:
        """Calculate innovation and technology score"""
        score = 30  # Base score
        
        # Patent portfolio
        patent_data = data.get("patent_data", {})
        if isinstance(patent_data, dict) and not "error" in patent_data:
            score += patent_data.get("innovation_metrics", {}).get("innovation_score", 0) * 0.5
        
        # GitHub tech diversity
        github_data = data.get("github_data", {})
        if isinstance(github_data, dict) and not "error" in github_data:
            tech_diversity = github_data.get("growth_metrics", {}).get("tech_diversity", 0)
            score += min(20, tech_diversity * 4)
            
            # Open source contribution
            if github_data.get("repository_stats", {}).get("total_stars", 0) > 1000:
                score += 10
        
        return min(100, int(score))
    
    def _calculate_market_score(self, data: Dict) -> int:
        """Calculate market opportunity score"""
        score = 50  # Base score
        
        # Industry from company info
        company_info = data.get("company", {})
        hot_industries = ["artificial intelligence", "ai", "machine learning", "biotech", 
                         "fintech", "saas", "cybersecurity", "clean energy", "quantum"]
        
        industry = (company_info.get("industry") or "").lower()
        if any(hot in industry for hot in hot_industries):
            score += 20
        
        # News coverage as market validation
        news_data = data.get("news_data", {})
        if isinstance(news_data, dict) and not "error" in news_data:
            attention_score = news_data.get("metrics", {}).get("media_attention_score", 0)
            score += attention_score * 0.3
        
        return min(100, int(score))
    
    def _calculate_team_score(self, data: Dict) -> int:
        """Calculate team and leadership score"""
        score = 60  # Base score
        
        # GitHub contributors as proxy for team size
        github_data = data.get("github_data", {})
        if isinstance(github_data, dict) and not "error" in github_data:
            contributors = github_data.get("contributor_stats", {}).get("estimated_contributors", 0)
            if contributors > 100:
                score += 20
            elif contributors > 50:
                score += 15
            elif contributors > 20:
                score += 10
        
        # Company age from Wikipedia
        wiki_data = data.get("wikipedia_data", {})
        if isinstance(wiki_data, dict) and not "error" in wiki_data:
            founded = wiki_data.get("structured_data", {}).get("founded")
            if founded:
                try:
                    age = datetime.now().year - int(founded)
                    if 3 <= age <= 10:  # Sweet spot for growth
                        score += 10
                except:
                    pass
        
        return min(100, int(score))
    
    def _calculate_momentum_score(self, data: Dict) -> int:
        """Calculate recent momentum score"""
        score = 40  # Base score
        
        # News sentiment
        news_data = data.get("news_data", {})
        if isinstance(news_data, dict) and not "error" in news_data:
            sentiment = news_data.get("metrics", {}).get("sentiment_score", 50)
            if sentiment > 70:
                score += 30
            elif sentiment > 60:
                score += 20
            elif sentiment > 50:
                score += 10
            
            # News velocity
            velocity = news_data.get("metrics", {}).get("news_velocity", 0)
            if velocity > 5:
                score += 20
            elif velocity > 2:
                score += 10
        
        # Recent patent activity
        patent_data = data.get("patent_data", {})
        if isinstance(patent_data, dict) and not "error" in patent_data:
            recent_patents = patent_data.get("recent_patents", 0)
            if recent_patents > 10:
                score += 10
            elif recent_patents > 5:
                score += 5
        
        return min(100, int(score))
    
    def _calculate_investment_score(self, scores: Dict[str, int]) -> int:
        """Calculate weighted investment score"""
        total_score = 0
        
        total_score += scores["financial_score"] * self.weights["financial"]
        total_score += scores["growth_score"] * self.weights["growth"]
        total_score += scores["innovation_score"] * self.weights["innovation"]
        total_score += scores["market_score"] * self.weights["market"]
        total_score += scores["team_score"] * self.weights["team"]
        total_score += scores["momentum_score"] * self.weights["momentum"]
        
        return min(100, int(total_score))
    
    def _extract_funding_history(self, data: Dict) -> List[Dict]:
        """Extract funding history from available data"""
        funding_rounds = []
        
        # From Wikipedia data
        wiki_data = data.get("wikipedia_data", {})
        if isinstance(wiki_data, dict) and not "error" in wiki_data:
            # Placeholder - would parse from page content
            pass
        
        # From SEC data (IPO, etc.)
        sec_data = data.get("sec_data", {})
        if isinstance(sec_data, dict) and not "error" in sec_data:
            filings = sec_data.get("filings", [])
            for filing in filings:
                if filing.get("form") == "S-1":
                    funding_rounds.append({
                        "type": "IPO Filing",
                        "date": filing.get("filing_date"),
                        "amount": None,  # Would parse from filing
                        "investors": []
                    })
        
        return funding_rounds
    
    def _extract_growth_signals(self, data: Dict) -> Dict:
        """Extract growth signals from data"""
        signals = {}
        
        # Employee growth
        company_info = data.get("company", {})
        if company_info.get("employeeCount"):
            signals["employeeGrowth"] = f"{company_info['employeeCount']} employees"
        
        # Web traffic (placeholder - would use SimilarWeb API)
        signals["webTraffic"] = "Data not available"
        
        # Tech stack from GitHub
        github_data = data.get("github_data", {})
        if isinstance(github_data, dict) and not "error" in github_data:
            tech_stack = github_data.get("tech_stack", [])
            if tech_stack:
                signals["techStack"] = ", ".join(tech_stack[:3])
        
        # Patent activity
        patent_data = data.get("patent_data", {})
        if isinstance(patent_data, dict) and not "error" in patent_data:
            recent = patent_data.get("recent_patents", 0)
            if recent > 0:
                signals["patentActivity"] = f"{recent} patents in last 3 years"
        
        # News velocity
        news_data = data.get("news_data", {})
        if isinstance(news_data, dict) and not "error" in news_data:
            velocity = news_data.get("metrics", {}).get("news_velocity", 0)
            signals["newsVelocity"] = f"{velocity:.1f} articles/week"
        
        return signals
    
    def _perform_market_analysis(self, data: Dict) -> Dict:
        """Perform market analysis"""
        analysis = {
            "tam": None,  # Would calculate from industry data
            "growthRate": None,
            "competitors": []
        }
        
        # Industry growth rate estimation
        company_info = data.get("company", {})
        industry = (company_info.get("industry") or "").lower()
        
        # Simplified TAM estimation based on industry
        tam_estimates = {
            "software": 500_000_000_000,
            "saas": 200_000_000_000,
            "fintech": 150_000_000_000,
            "healthcare": 300_000_000_000,
            "ai": 100_000_000_000
        }
        
        for key, tam in tam_estimates.items():
            if key in industry:
                analysis["tam"] = tam
                analysis["growthRate"] = 15.0  # Placeholder growth rate
                break
        
        return analysis
    
    def _get_data_sources(self, data: Dict) -> List[str]:
        """List data sources that provided valid data"""
        sources = []
        
        if data.get("sec_data") and not "error" in data.get("sec_data", {}):
            sources.append("SEC EDGAR")
        if data.get("github_data") and not "error" in data.get("github_data", {}):
            sources.append("GitHub")
        if data.get("wikipedia_data") and not "error" in data.get("wikipedia_data", {}):
            sources.append("Wikipedia")
        if data.get("patent_data") and not "error" in data.get("patent_data", {}):
            sources.append("USPTO")
        if data.get("news_data") and not "error" in data.get("news_data", {}):
            sources.append("News API")
        
        return sources
    
    def _assess_overall_data_quality(self, data: Dict) -> Dict:
        """Assess overall data quality"""
        quality_scores = []
        
        # Check each data source
        for source in ["sec_data", "github_data", "wikipedia_data", "patent_data", "news_data"]:
            source_data = data.get(source, {})
            if isinstance(source_data, dict) and not "error" in source_data:
                dq = source_data.get("data_quality", {})
                if dq.get("score") is not None:
                    quality_scores.append(dq["score"])
        
        if quality_scores:
            avg_quality = statistics.mean(quality_scores)
            if avg_quality > 0.7:
                return {"score": avg_quality, "status": "high_quality"}
            elif avg_quality > 0.4:
                return {"score": avg_quality, "status": "moderate_quality"}
            else:
                return {"score": avg_quality, "status": "low_quality"}
        
        return {"score": 0, "status": "insufficient_data"}
    
    async def get_latest_data(self, company_name: str, domain: Optional[str], last_checked: Optional[str]) -> Dict:
        """Get latest data for update checks"""
        # Simplified - would re-fetch key metrics
        return {
            "company_name": company_name,
            "domain": domain,
            "last_updated": datetime.utcnow().isoformat(),
            "changes": []
        }
    
    async def detect_significant_changes(self, old_data: Dict, new_data: Dict) -> bool:
        """Detect if there are significant changes"""
        # Simplified - would compare key metrics
        return False
    
    def summarize_changes(self, old_data: Dict, new_data: Dict) -> str:
        """Summarize changes between data points"""
        return "No significant changes detected"