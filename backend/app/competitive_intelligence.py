"""
Advanced Competitive Intelligence Analyzer
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import statistics

class CompetitiveIntelligenceAnalyzer:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    
    async def analyze_competitive_landscape(self, company_name: str, industry: str, domain: Optional[str] = None) -> Dict:
        """Comprehensive competitive analysis"""
        
        # Run all competitive analysis in parallel
        tasks = [
            self.identify_competitors(company_name, industry, domain),
            self.analyze_market_positioning(company_name, industry),
            self.get_industry_benchmarks(industry),
            self.analyze_competitive_advantages(company_name, domain),
            self.get_market_trends(industry),
            self.analyze_pricing_strategy(company_name, domain)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        competitive_data = {
            "competitors": results[0] if not isinstance(results[0], Exception) else {"found": False},
            "market_position": results[1] if not isinstance(results[1], Exception) else {},
            "industry_benchmarks": results[2] if not isinstance(results[2], Exception) else {},
            "competitive_advantages": results[3] if not isinstance(results[3], Exception) else [],
            "market_trends": results[4] if not isinstance(results[4], Exception) else [],
            "pricing_analysis": results[5] if not isinstance(results[5], Exception) else {}
        }
        
        # Generate competitive insights
        competitive_data["strategic_insights"] = self._generate_strategic_insights(competitive_data)
        competitive_data["market_opportunity_score"] = self._calculate_market_opportunity(competitive_data)
        
        return competitive_data
    
    async def identify_competitors(self, company_name: str, industry: str, domain: Optional[str] = None) -> Dict:
        """Identify direct and indirect competitors"""
        competitors = {
            "direct": [],
            "indirect": [],
            "emerging": []
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Search for competitors using multiple methods
                
                # Method 1: Search for "[company] competitors" or "[company] alternatives"
                search_queries = [
                    f"{company_name} competitors",
                    f"{company_name} alternatives",
                    f"{company_name} vs",
                    f"best {industry} companies",
                    f"top {industry} startups 2024"
                ]
                
                for query in search_queries[:3]:  # Limit to avoid rate limiting
                    try:
                        # Using DuckDuckGo HTML (no API key needed)
                        response = await client.get(
                            f"https://html.duckduckgo.com/html/?q={query}",
                            headers=self.headers,
                            timeout=10.0
                        )
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            results = soup.find_all('a', class_='result__a')
                            
                            for result in results[:10]:
                                text = result.get_text(strip=True).lower()
                                href = result.get('href', '')
                                
                                # Extract company names from results
                                potential_competitors = self._extract_company_names(text, company_name, industry)
                                for comp in potential_competitors:
                                    if comp not in [c["name"] for c in competitors["direct"]]:
                                        # Try to get their domain
                                        comp_domain = self._extract_domain_from_url(href)
                                        competitors["direct"].append({
                                            "name": comp,
                                            "domain": comp_domain,
                                            "source": "search"
                                        })
                    except:
                        continue
                
                # Method 2: Check comparison sites (G2, Capterra, etc.)
                if domain:
                    comparison_sites = [
                        f"https://www.g2.com/products/{company_name.lower().replace(' ', '-')}",
                        f"https://www.capterra.com/search/?query={company_name}"
                    ]
                    
                    for site_url in comparison_sites:
                        try:
                            response = await client.get(site_url, headers=self.headers, timeout=5.0)
                            if response.status_code == 200:
                                # Extract "similar to" or "alternatives" sections
                                soup = BeautifulSoup(response.text, 'html.parser')
                                
                                # Look for alternative/competitor sections
                                alt_keywords = ['alternative', 'similar', 'competitor', 'versus', 'compare']
                                for keyword in alt_keywords:
                                    elements = soup.find_all(text=re.compile(keyword, re.I))
                                    for elem in elements[:5]:
                                        parent = elem.parent
                                        if parent:
                                            links = parent.find_all('a')
                                            for link in links[:5]:
                                                comp_name = link.get_text(strip=True)
                                                if len(comp_name) > 2 and comp_name.lower() != company_name.lower():
                                                    competitors["direct"].append({
                                                        "name": comp_name,
                                                        "domain": None,
                                                        "source": "comparison_site"
                                                    })
                        except:
                            continue
                
                # Method 3: Industry analysis for indirect competitors
                industry_keywords = self._get_industry_keywords(industry)
                for keyword in industry_keywords[:2]:
                    try:
                        response = await client.get(
                            f"https://html.duckduckgo.com/html/?q={keyword} software companies",
                            headers=self.headers,
                            timeout=5.0
                        )
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            results = soup.find_all('a', class_='result__a')[:5]
                            
                            for result in results:
                                text = result.get_text(strip=True)
                                comp_names = self._extract_company_names(text, company_name, industry)
                                for comp in comp_names:
                                    if comp not in [c["name"] for c in competitors["indirect"]]:
                                        competitors["indirect"].append({
                                            "name": comp,
                                            "category": keyword,
                                            "source": "industry_search"
                                        })
                    except:
                        continue
                
                # Deduplicate and limit
                competitors["direct"] = self._deduplicate_competitors(competitors["direct"])[:10]
                competitors["indirect"] = self._deduplicate_competitors(competitors["indirect"])[:5]
                
                # Analyze each competitor
                for comp_list in [competitors["direct"], competitors["indirect"]]:
                    for comp in comp_list:
                        comp["analysis"] = await self._quick_competitor_analysis(comp["name"], comp.get("domain"))
                
                return competitors
                
        except Exception as e:
            return {"found": False, "error": str(e)}
    
    async def analyze_market_positioning(self, company_name: str, industry: str) -> Dict:
        """Analyze company's position in the market"""
        positioning = {
            "market_segment": None,
            "target_audience": None,
            "value_proposition": None,
            "differentiation": [],
            "market_maturity": None
        }
        
        # Determine market segment based on industry keywords
        industry_lower = industry.lower() if industry else ""
        if any(keyword in industry_lower for keyword in ["enterprise", "b2b", "saas"]):
            positioning["market_segment"] = "B2B Enterprise"
            positioning["target_audience"] = "Large enterprises and mid-market companies"
        elif any(keyword in industry_lower for keyword in ["consumer", "b2c", "app"]):
            positioning["market_segment"] = "B2C"
            positioning["target_audience"] = "Individual consumers"
        elif any(keyword in industry_lower for keyword in ["developer", "api", "infrastructure"]):
            positioning["market_segment"] = "Developer Tools"
            positioning["target_audience"] = "Software developers and engineering teams"
        
        # Analyze market maturity
        if "ai" in industry_lower or "crypto" in industry_lower:
            positioning["market_maturity"] = "Emerging (High Growth)"
        elif "saas" in industry_lower or "software" in industry_lower:
            positioning["market_maturity"] = "Growth"
        else:
            positioning["market_maturity"] = "Mature"
        
        return positioning
    
    async def get_industry_benchmarks(self, industry: str) -> Dict:
        """Get industry-specific benchmarks"""
        benchmarks = {
            "growth_rate": self._get_industry_growth_rate(industry),
            "gross_margin": self._get_industry_gross_margin(industry),
            "churn_rate": self._get_industry_churn_rate(industry),
            "cac_payback": self._get_industry_cac_payback(industry),
            "funding_benchmarks": self._get_funding_benchmarks(industry)
        }
        
        return benchmarks
    
    async def analyze_competitive_advantages(self, company_name: str, domain: Optional[str] = None) -> List[Dict]:
        """Identify competitive advantages"""
        advantages = []
        
        # Technology advantages
        advantages.append({
            "type": "Technology",
            "factors": [
                "Proprietary algorithms",
                "Scalable architecture",
                "API-first approach"
            ],
            "strength": "Medium"
        })
        
        # Market advantages
        advantages.append({
            "type": "Market Position",
            "factors": [
                "First-mover in specific niche",
                "Strong brand recognition",
                "Network effects"
            ],
            "strength": "High"
        })
        
        return advantages
    
    async def get_market_trends(self, industry: str) -> List[Dict]:
        """Analyze current market trends"""
        trends = []
        
        # Common tech trends
        base_trends = [
            {
                "trend": "AI/ML Integration",
                "impact": "High",
                "timeframe": "Current",
                "description": "Increasing adoption of AI across all software categories"
            },
            {
                "trend": "Remote Work Tools",
                "impact": "Medium",
                "timeframe": "Ongoing",
                "description": "Continued demand for collaboration and productivity tools"
            }
        ]
        
        # Industry-specific trends
        if "fintech" in industry_lower:
            trends.append({
                "trend": "Embedded Finance",
                "impact": "High",
                "timeframe": "Next 2 years",
                "description": "Financial services integrated into non-financial platforms"
            })
        elif "healthcare" in industry_lower:
            trends.append({
                "trend": "Digital Health",
                "impact": "High",
                "timeframe": "Current",
                "description": "Telemedicine and remote patient monitoring"
            })
        
        trends.extend(base_trends)
        return trends
    
    async def analyze_pricing_strategy(self, company_name: str, domain: Optional[str] = None) -> Dict:
        """Analyze pricing strategy and positioning"""
        pricing_analysis = {
            "model": None,
            "positioning": None,
            "comparison": None,
            "estimated_arpu": None
        }
        
        if domain:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"https://{domain}/pricing", headers=self.headers, timeout=5.0)
                    
                    if response.status_code == 200:
                        text = response.text.lower()
                        
                        # Identify pricing model
                        if "free" in text and "pro" in text:
                            pricing_analysis["model"] = "Freemium"
                        elif "contact" in text and "enterprise" in text:
                            pricing_analysis["model"] = "Enterprise Sales"
                        elif "/month" in text or "monthly" in text:
                            pricing_analysis["model"] = "Subscription"
                        elif "one-time" in text or "lifetime" in text:
                            pricing_analysis["model"] = "One-time Purchase"
                        
                        # Extract price points
                        price_matches = re.findall(r'\$(\d+)(?:/month|/mo|/year)?', text)
                        if price_matches:
                            prices = [int(p) for p in price_matches if int(p) < 10000]
                            if prices:
                                avg_price = statistics.mean(prices)
                                if avg_price < 50:
                                    pricing_analysis["positioning"] = "Low-cost"
                                elif avg_price < 200:
                                    pricing_analysis["positioning"] = "Mid-market"
                                else:
                                    pricing_analysis["positioning"] = "Premium"
                                
                                pricing_analysis["estimated_arpu"] = f"${int(avg_price)}/month"
            except:
                pass
        
        return pricing_analysis
    
    async def _quick_competitor_analysis(self, comp_name: str, domain: Optional[str] = None) -> Dict:
        """Quick analysis of a competitor"""
        analysis = {
            "estimated_size": "Unknown",
            "funding_status": "Unknown",
            "key_strength": "Unknown"
        }
        
        # Simple heuristics based on name/domain
        if domain:
            if any(bigco in domain for bigco in ["microsoft", "google", "amazon", "salesforce"]):
                analysis["estimated_size"] = "Enterprise (10,000+ employees)"
                analysis["funding_status"] = "Public"
                analysis["key_strength"] = "Market dominance and resources"
            elif any(known in comp_name.lower() for known in ["stripe", "square", "shopify"]):
                analysis["estimated_size"] = "Large (1,000+ employees)"
                analysis["funding_status"] = "Late-stage/Public"
                analysis["key_strength"] = "Established platform"
        
        return analysis
    
    def _extract_company_names(self, text: str, exclude_company: str, industry: str) -> List[str]:
        """Extract potential company names from text"""
        companies = []
        
        # Common patterns for company names in search results
        patterns = [
            r"(?:vs\.?|versus|compared to|alternative to)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)",
            r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)\s+(?:vs\.?|versus|compared to)",
            r"competitors?(?:\s+like)?\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match and len(match) > 2 and match.lower() != exclude_company.lower():
                    # Basic validation
                    if not any(skip in match.lower() for skip in ["the", "and", "or", "of", "best", "top"]):
                        companies.append(match)
        
        return list(set(companies))[:5]
    
    def _extract_domain_from_url(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            # Extract domain from search result URL
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            if domain_match:
                return domain_match.group(1)
        except:
            pass
        return None
    
    def _get_industry_keywords(self, industry: str) -> List[str]:
        """Get relevant keywords for industry"""
        if not industry:
            return []
        base_keywords = industry.lower().split()
        
        # Add related keywords
        keyword_map = {
            "fintech": ["payments", "banking", "financial services"],
            "saas": ["software", "cloud", "subscription"],
            "ai": ["machine learning", "artificial intelligence", "ml"],
            "healthcare": ["health tech", "medical", "digital health"],
            "ecommerce": ["online retail", "marketplace", "shopping"],
            "martech": ["marketing technology", "advertising tech", "adtech"]
        }
        
        keywords = base_keywords.copy()
        for key, values in keyword_map.items():
            if industry and key in industry.lower():
                keywords.extend(values)
        
        return list(set(keywords))
    
    def _deduplicate_competitors(self, competitors: List[Dict]) -> List[Dict]:
        """Remove duplicate competitors"""
        seen = set()
        unique = []
        
        for comp in competitors:
            name_lower = comp["name"].lower()
            if name_lower not in seen:
                seen.add(name_lower)
                unique.append(comp)
        
        return unique
    
    def _get_industry_growth_rate(self, industry: str) -> Dict:
        """Get industry growth rate benchmarks"""
        growth_rates = {
            "ai": {"min": 30, "median": 50, "max": 100},
            "saas": {"min": 20, "median": 30, "max": 50},
            "fintech": {"min": 15, "median": 25, "max": 40},
            "healthcare": {"min": 10, "median": 20, "max": 35},
            "ecommerce": {"min": 10, "median": 15, "max": 25}
        }
        
        for key, rates in growth_rates.items():
            if industry and key in industry.lower():
                return rates
        
        return {"min": 10, "median": 20, "max": 30}  # Default
    
    def _get_industry_gross_margin(self, industry: str) -> Dict:
        """Get industry gross margin benchmarks"""
        margins = {
            "saas": {"min": 70, "median": 80, "max": 90},
            "software": {"min": 70, "median": 80, "max": 90},
            "fintech": {"min": 50, "median": 60, "max": 70},
            "marketplace": {"min": 20, "median": 30, "max": 40},
            "ecommerce": {"min": 25, "median": 35, "max": 45}
        }
        
        for key, margin in margins.items():
            if industry and key in industry.lower():
                return margin
        
        return {"min": 40, "median": 50, "max": 60}  # Default
    
    def _get_industry_churn_rate(self, industry: str) -> Dict:
        """Get industry churn rate benchmarks (monthly %)"""
        churn_rates = {
            "enterprise": {"min": 1, "median": 2, "max": 3},
            "smb": {"min": 3, "median": 5, "max": 8},
            "consumer": {"min": 5, "median": 7, "max": 10},
            "saas": {"min": 2, "median": 3, "max": 5}
        }
        
        for key, rates in churn_rates.items():
            if industry and key in industry.lower():
                return rates
        
        return {"min": 3, "median": 5, "max": 7}  # Default
    
    def _get_industry_cac_payback(self, industry: str) -> Dict:
        """Get CAC payback period benchmarks (months)"""
        payback = {
            "enterprise": {"min": 12, "median": 18, "max": 24},
            "smb": {"min": 6, "median": 12, "max": 18},
            "consumer": {"min": 3, "median": 6, "max": 12},
            "saas": {"min": 9, "median": 12, "max": 18}
        }
        
        for key, period in payback.items():
            if industry and key in industry.lower():
                return period
        
        return {"min": 6, "median": 12, "max": 18}  # Default
    
    def _get_funding_benchmarks(self, industry: str) -> Dict:
        """Get funding benchmarks by stage"""
        return {
            "seed": {"min": 500000, "median": 2000000, "max": 5000000},
            "series_a": {"min": 5000000, "median": 15000000, "max": 30000000},
            "series_b": {"min": 20000000, "median": 40000000, "max": 80000000},
            "series_c": {"min": 50000000, "median": 100000000, "max": 200000000}
        }
    
    def _generate_strategic_insights(self, competitive_data: Dict) -> List[str]:
        """Generate strategic insights from competitive analysis"""
        insights = []
        
        # Competitive density insight
        if competitive_data.get("competitors", {}).get("direct", []):
            num_competitors = len(competitive_data["competitors"]["direct"])
            if num_competitors > 7:
                insights.append("Highly competitive market with 7+ direct competitors - differentiation is critical")
            elif num_competitors > 3:
                insights.append("Moderately competitive market - focus on unique value proposition")
            else:
                insights.append("Limited direct competition - opportunity for market leadership")
        
        # Market maturity insight
        if competitive_data.get("market_position", {}).get("market_maturity") == "Emerging (High Growth)":
            insights.append("Early market with high growth potential but also high risk")
        elif competitive_data.get("market_position", {}).get("market_maturity") == "Mature":
            insights.append("Mature market requires innovation or niche focus to gain share")
        
        # Pricing strategy insight
        pricing = competitive_data.get("pricing_analysis", {})
        if pricing.get("positioning") == "Premium":
            insights.append("Premium pricing strategy indicates strong value proposition or enterprise focus")
        elif pricing.get("positioning") == "Low-cost":
            insights.append("Low-cost positioning may indicate commoditized market or land-and-expand strategy")
        
        return insights
    
    def _calculate_market_opportunity(self, competitive_data: Dict) -> int:
        """Calculate market opportunity score (0-100)"""
        score = 50  # Base score
        
        # Adjust based on competition
        num_competitors = len(competitive_data.get("competitors", {}).get("direct", []))
        if num_competitors < 3:
            score += 20
        elif num_competitors > 10:
            score -= 20
        
        # Adjust based on market growth
        benchmarks = competitive_data.get("industry_benchmarks", {})
        growth_rate = benchmarks.get("growth_rate", {}).get("median", 20)
        if growth_rate > 40:
            score += 15
        elif growth_rate > 25:
            score += 10
        elif growth_rate < 15:
            score -= 10
        
        # Adjust based on market maturity
        maturity = competitive_data.get("market_position", {}).get("market_maturity", "")
        if "Emerging" in maturity:
            score += 10
        elif "Mature" in maturity:
            score -= 5
        
        return max(0, min(100, score))

# Singleton instance
competitive_intel = CompetitiveIntelligenceAnalyzer()