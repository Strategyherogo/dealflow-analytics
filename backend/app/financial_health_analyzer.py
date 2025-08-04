"""
Financial Health & Burn Rate Analyzer
Estimates financial metrics from public signals
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import statistics

class FinancialHealthAnalyzer:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    
    async def analyze_financial_health(self, 
                                     company_name: str, 
                                     domain: Optional[str] = None,
                                     employee_count: Optional[str] = None,
                                     funding_data: Optional[List] = None,
                                     intelligence_data: Optional[Dict] = None) -> Dict:
        """Comprehensive financial health analysis"""
        
        # Run all financial analyses in parallel
        tasks = [
            self.estimate_burn_rate(company_name, employee_count, funding_data),
            self.analyze_revenue_signals(company_name, domain, intelligence_data),
            self.calculate_runway(funding_data, employee_count),
            self.analyze_growth_efficiency(intelligence_data),
            self.estimate_valuation_metrics(company_name, funding_data, intelligence_data)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        financial_health = {
            "burn_rate": results[0] if not isinstance(results[0], Exception) else {},
            "revenue_signals": results[1] if not isinstance(results[1], Exception) else {},
            "runway": results[2] if not isinstance(results[2], Exception) else {},
            "growth_efficiency": results[3] if not isinstance(results[3], Exception) else {},
            "valuation": results[4] if not isinstance(results[4], Exception) else {}
        }
        
        # Generate financial health score and insights
        financial_health["health_score"] = self._calculate_health_score(financial_health)
        financial_health["financial_risks"] = self._identify_financial_risks(financial_health)
        financial_health["financial_strengths"] = self._identify_financial_strengths(financial_health)
        financial_health["funding_recommendation"] = self._generate_funding_recommendation(financial_health)
        
        return financial_health
    
    async def estimate_burn_rate(self, company_name: str, employee_count: Optional[str] = None, funding_data: Optional[List] = None) -> Dict:
        """Estimate monthly burn rate based on public signals"""
        burn_rate = {
            "estimated_monthly_burn": None,
            "confidence": "low",
            "breakdown": {
                "salaries": 0,
                "infrastructure": 0,
                "marketing": 0,
                "other": 0
            },
            "signals": []
        }
        
        # Extract employee count
        employee_number = self._parse_employee_count(employee_count)
        
        if employee_number:
            # Estimate salary costs
            # Assume average tech salary of $120k/year ($10k/month)
            # Adjust based on company stage
            avg_salary_per_month = 10000
            
            if funding_data and len(funding_data) > 0:
                # Later stage companies pay more
                if any("series c" in str(round).lower() or "series d" in str(round).lower() for round in funding_data):
                    avg_salary_per_month = 15000
                elif any("series b" in str(round).lower() for round in funding_data):
                    avg_salary_per_month = 12000
            
            salary_burn = employee_number * avg_salary_per_month
            burn_rate["breakdown"]["salaries"] = salary_burn
            burn_rate["signals"].append(f"Estimated {employee_number} employees")
            
            # Estimate infrastructure costs (20% of salaries)
            burn_rate["breakdown"]["infrastructure"] = int(salary_burn * 0.2)
            
            # Estimate marketing (15% of salaries for B2B, 30% for B2C)
            burn_rate["breakdown"]["marketing"] = int(salary_burn * 0.15)
            
            # Other costs (10%)
            burn_rate["breakdown"]["other"] = int(salary_burn * 0.1)
            
            # Total burn
            total_burn = sum(burn_rate["breakdown"].values())
            burn_rate["estimated_monthly_burn"] = total_burn
            
            # Confidence based on data quality
            if employee_number > 10:
                burn_rate["confidence"] = "medium"
                if funding_data and len(funding_data) > 0:
                    burn_rate["confidence"] = "high"
        
        return burn_rate
    
    async def analyze_revenue_signals(self, company_name: str, domain: Optional[str] = None, intelligence_data: Optional[Dict] = None) -> Dict:
        """Analyze revenue signals from various sources"""
        revenue_analysis = {
            "estimated_arr": None,
            "revenue_stage": "unknown",
            "revenue_model": None,
            "pricing_signals": [],
            "customer_signals": []
        }
        
        # Extract pricing from intelligence data
        if intelligence_data and intelligence_data.get("product", {}).get("pricing"):
            pricing_info = intelligence_data["product"]["pricing"]
            revenue_analysis["pricing_signals"] = pricing_info[:3]
            
            # Try to extract price points
            prices = []
            for price_str in pricing_info:
                price_matches = re.findall(r'\$(\d+)(?:/month|/mo)?', str(price_str))
                prices.extend([int(p) for p in price_matches if int(p) < 10000])
            
            if prices:
                avg_price = statistics.mean(prices)
                revenue_analysis["revenue_model"] = "Subscription" if "/mo" in str(pricing_info) else "One-time"
        
        # Extract customer count
        if intelligence_data and intelligence_data.get("customers", {}).get("estimated_customers"):
            customer_str = intelligence_data["customers"]["estimated_customers"]
            revenue_analysis["customer_signals"].append(f"Customer base: {customer_str}")
            
            # Parse customer count
            customer_count = self._parse_customer_count(customer_str)
            
            # Estimate ARR if we have pricing and customers
            if customer_count and prices:
                # Conservative estimate: assume 30% are paying customers
                paying_customers = int(customer_count * 0.3)
                monthly_revenue = paying_customers * avg_price
                estimated_arr = monthly_revenue * 12
                
                revenue_analysis["estimated_arr"] = estimated_arr
                
                # Determine revenue stage
                if estimated_arr >= 100_000_000:
                    revenue_analysis["revenue_stage"] = "Scale ($100M+)"
                elif estimated_arr >= 10_000_000:
                    revenue_analysis["revenue_stage"] = "Growth ($10M-$100M)"
                elif estimated_arr >= 1_000_000:
                    revenue_analysis["revenue_stage"] = "Traction ($1M-$10M)"
                elif estimated_arr >= 100_000:
                    revenue_analysis["revenue_stage"] = "Early Revenue ($100K-$1M)"
                else:
                    revenue_analysis["revenue_stage"] = "Pre-Revenue/Early (<$100K)"
        
        # Business model indicators
        if intelligence_data and intelligence_data.get("revenue_indicators", {}).get("business_model"):
            revenue_analysis["revenue_model"] = intelligence_data["revenue_indicators"]["business_model"]
        
        return revenue_analysis
    
    async def calculate_runway(self, funding_data: Optional[List] = None, employee_count: Optional[str] = None) -> Dict:
        """Calculate estimated runway based on funding and burn rate"""
        runway = {
            "months_remaining": None,
            "runway_status": "unknown",
            "last_funding": None,
            "total_raised": 0
        }
        
        if funding_data and len(funding_data) > 0:
            # Calculate total raised
            total_raised = 0
            last_round = None
            
            for round_data in funding_data:
                if isinstance(round_data, dict) and round_data.get("amount"):
                    total_raised += round_data["amount"]
                    if not last_round or round_data.get("date", "") > last_round.get("date", ""):
                        last_round = round_data
            
            runway["total_raised"] = total_raised
            runway["last_funding"] = last_round
            
            # Estimate runway based on typical burn rates
            if last_round and last_round.get("amount"):
                last_amount = last_round["amount"]
                
                # Estimate burn based on funding stage
                if "seed" in str(last_round.get("type", "")).lower():
                    monthly_burn = last_amount / 18  # 18 month runway typical
                elif "series a" in str(last_round.get("type", "")).lower():
                    monthly_burn = last_amount / 24  # 24 month runway
                elif "series b" in str(last_round.get("type", "")).lower():
                    monthly_burn = last_amount / 18  # 18 month runway
                else:
                    monthly_burn = last_amount / 12  # Conservative 12 month
                
                # Calculate months since last funding
                if last_round.get("date"):
                    try:
                        funding_date = datetime.fromisoformat(last_round["date"])
                        months_elapsed = (datetime.now() - funding_date).days / 30
                        
                        remaining_cash = last_amount - (monthly_burn * months_elapsed)
                        if remaining_cash > 0:
                            runway["months_remaining"] = int(remaining_cash / monthly_burn)
                            
                            # Status
                            if runway["months_remaining"] < 6:
                                runway["runway_status"] = "Critical (<6 months)"
                            elif runway["months_remaining"] < 12:
                                runway["runway_status"] = "Low (6-12 months)"
                            elif runway["months_remaining"] < 18:
                                runway["runway_status"] = "Moderate (12-18 months)"
                            else:
                                runway["runway_status"] = "Healthy (18+ months)"
                    except:
                        pass
        
        return runway
    
    async def analyze_growth_efficiency(self, intelligence_data: Optional[Dict] = None) -> Dict:
        """Analyze growth efficiency metrics"""
        efficiency = {
            "growth_efficiency_score": 50,
            "metrics": {
                "rule_of_40": None,
                "burn_multiple": None,
                "magic_number": None,
                "ltv_cac_ratio": None
            },
            "efficiency_signals": []
        }
        
        # Analyze based on available signals
        if intelligence_data:
            # Customer growth signals
            if intelligence_data.get("customers", {}).get("estimated_customers"):
                efficiency["efficiency_signals"].append("Active customer acquisition")
                efficiency["growth_efficiency_score"] += 10
            
            # Product-market fit signals
            if intelligence_data.get("g2_reviews", {}).get("rating"):
                rating = float(intelligence_data["g2_reviews"]["rating"])
                if rating >= 4.5:
                    efficiency["efficiency_signals"].append(f"Strong product-market fit (G2: {rating}/5)")
                    efficiency["growth_efficiency_score"] += 15
            
            # Hiring efficiency
            if intelligence_data.get("team_indicators", {}).get("job_openings", 0) > 10:
                efficiency["efficiency_signals"].append("Aggressive hiring indicates growth mode")
                efficiency["growth_efficiency_score"] += 5
        
        return efficiency
    
    async def estimate_valuation_metrics(self, company_name: str, funding_data: Optional[List] = None, intelligence_data: Optional[Dict] = None) -> Dict:
        """Estimate valuation and related metrics"""
        valuation = {
            "estimated_valuation": None,
            "valuation_method": None,
            "multiples": {},
            "comparables": []
        }
        
        # Get last valuation from funding data
        if funding_data and len(funding_data) > 0:
            last_round = max(funding_data, key=lambda x: x.get("date", "") if isinstance(x, dict) else "")
            if isinstance(last_round, dict) and last_round.get("valuation"):
                valuation["estimated_valuation"] = last_round["valuation"]
                valuation["valuation_method"] = "Last funding round"
            elif isinstance(last_round, dict) and last_round.get("amount"):
                # Estimate based on typical dilution (20%)
                amount = last_round["amount"]
                estimated_val = amount * 5  # 20% dilution assumption
                valuation["estimated_valuation"] = estimated_val
                valuation["valuation_method"] = "Estimated from funding amount"
        
        # Industry multiples
        if intelligence_data and intelligence_data.get("revenue_indicators", {}).get("business_model"):
            model = intelligence_data["revenue_indicators"]["business_model"]
            if "SaaS" in model:
                valuation["multiples"]["ev_revenue"] = "5-15x (SaaS average)"
                valuation["multiples"]["growth_adjusted"] = "1-2x (ARR growth rate)"
            elif "Marketplace" in model:
                valuation["multiples"]["ev_gmv"] = "0.5-2x (Gross Merchandise Value)"
            elif "API" in model:
                valuation["multiples"]["ev_revenue"] = "10-20x (Developer tools)"
        
        return valuation
    
    def _parse_employee_count(self, employee_str: Optional[str]) -> Optional[int]:
        """Parse employee count from string"""
        if not employee_str:
            return None
        
        # Remove commas and extract numbers
        numbers = re.findall(r'\d+', employee_str.replace(',', ''))
        if numbers:
            # Take the first/largest number
            return int(numbers[0])
        
        return None
    
    def _parse_customer_count(self, customer_str: str) -> Optional[int]:
        """Parse customer count from string like '10K+' or '1M+'"""
        if not customer_str:
            return None
        
        # Look for patterns like 10K, 1M, 500+
        match = re.search(r'(\d+(?:\.\d+)?)\s*([KMB]?)\+?', customer_str)
        if match:
            number = float(match.group(1))
            suffix = match.group(2).upper() if match.group(2) else ''
            
            if suffix == 'K':
                return int(number * 1000)
            elif suffix == 'M':
                return int(number * 1000000)
            elif suffix == 'B':
                return int(number * 1000000000)
            else:
                return int(number)
        
        return None
    
    def _calculate_health_score(self, financial_data: Dict) -> int:
        """Calculate overall financial health score"""
        score = 50  # Base score
        
        # Burn rate factors
        if financial_data["burn_rate"].get("estimated_monthly_burn"):
            if financial_data["burn_rate"]["confidence"] == "high":
                score += 5
        
        # Revenue factors
        if financial_data["revenue_signals"].get("revenue_stage"):
            stage = financial_data["revenue_signals"]["revenue_stage"]
            if "Scale" in stage:
                score += 30
            elif "Growth" in stage:
                score += 20
            elif "Traction" in stage:
                score += 15
            elif "Early Revenue" in stage:
                score += 10
        
        # Runway factors
        if financial_data["runway"].get("runway_status"):
            status = financial_data["runway"]["runway_status"]
            if "Healthy" in status:
                score += 15
            elif "Moderate" in status:
                score += 5
            elif "Low" in status:
                score -= 10
            elif "Critical" in status:
                score -= 20
        
        # Efficiency factors
        efficiency_score = financial_data["growth_efficiency"].get("growth_efficiency_score", 50)
        score += int((efficiency_score - 50) * 0.3)
        
        return max(0, min(100, score))
    
    def _identify_financial_risks(self, financial_data: Dict) -> List[str]:
        """Identify financial risks"""
        risks = []
        
        # Runway risks
        if financial_data["runway"].get("months_remaining"):
            months = financial_data["runway"]["months_remaining"]
            if months < 6:
                risks.append(f"Critical runway: Only {months} months remaining")
            elif months < 12:
                risks.append(f"Fundraising pressure: {months} months runway")
        
        # Burn rate risks
        if financial_data["burn_rate"].get("estimated_monthly_burn"):
            burn = financial_data["burn_rate"]["estimated_monthly_burn"]
            if burn > 1000000:
                risks.append(f"High burn rate: ${burn/1000000:.1f}M/month")
        
        # Revenue risks
        if financial_data["revenue_signals"].get("revenue_stage") in ["Pre-Revenue/Early (<$100K)", "unknown"]:
            risks.append("Limited or no revenue traction")
        
        # Valuation risks
        if financial_data["valuation"].get("estimated_valuation"):
            val = financial_data["valuation"]["estimated_valuation"]
            if val > 1000000000:  # $1B+
                risks.append("High valuation may limit upside potential")
        
        return risks
    
    def _identify_financial_strengths(self, financial_data: Dict) -> List[str]:
        """Identify financial strengths"""
        strengths = []
        
        # Revenue strengths
        if financial_data["revenue_signals"].get("estimated_arr"):
            arr = financial_data["revenue_signals"]["estimated_arr"]
            if arr > 10000000:
                strengths.append(f"Strong revenue traction: ${arr/1000000:.1f}M ARR")
            elif arr > 1000000:
                strengths.append(f"Solid revenue base: ${arr/1000000:.1f}M ARR")
        
        # Runway strengths
        if financial_data["runway"].get("runway_status") == "Healthy (18+ months)":
            strengths.append("Healthy runway provides strategic flexibility")
        
        # Efficiency strengths
        efficiency_signals = financial_data["growth_efficiency"].get("efficiency_signals", [])
        if efficiency_signals:
            strengths.extend(efficiency_signals[:2])
        
        # Funding strengths
        if financial_data["runway"].get("total_raised", 0) > 50000000:
            total = financial_data["runway"]["total_raised"]
            strengths.append(f"Well-funded: ${total/1000000:.0f}M raised to date")
        
        return strengths
    
    def _generate_funding_recommendation(self, financial_data: Dict) -> str:
        """Generate funding recommendation"""
        health_score = financial_data["health_score"]
        runway_months = financial_data["runway"].get("months_remaining")
        revenue_stage = financial_data["revenue_signals"].get("revenue_stage", "unknown")
        
        if health_score >= 80:
            return "Strong position - raise opportunistically for growth acceleration"
        elif health_score >= 60:
            if runway_months and runway_months < 12:
                return "Begin fundraising process within 3-6 months"
            else:
                return "Focus on revenue growth before next raise"
        elif health_score >= 40:
            if runway_months and runway_months < 9:
                return "Urgent: Start fundraising immediately"
            else:
                return "Improve unit economics before raising"
        else:
            if "Pre-Revenue" in revenue_stage:
                return "Focus on achieving product-market fit before institutional funding"
            else:
                return "Consider bridge round or strategic alternatives"

# Singleton instance
financial_analyzer = FinancialHealthAnalyzer()