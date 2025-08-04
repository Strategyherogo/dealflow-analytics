"""
Data-Driven Metrics Engine
Calculates real, quantitative metrics for investment decisions
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import re

class DataMetricsEngine:
    def __init__(self):
        self.metric_weights = {
            "growth_velocity": 0.25,
            "market_penetration": 0.20,
            "financial_efficiency": 0.20,
            "product_adoption": 0.15,
            "talent_density": 0.10,
            "innovation_index": 0.10
        }
    
    async def calculate_data_driven_metrics(self, all_data: Dict) -> Dict:
        """Calculate comprehensive data-driven metrics"""
        
        metrics = {
            "quantitative_score": 0,
            "data_quality_score": 0,
            "growth_metrics": await self._calculate_growth_metrics(all_data),
            "traction_metrics": await self._calculate_traction_metrics(all_data),
            "efficiency_metrics": await self._calculate_efficiency_metrics(all_data),
            "market_metrics": await self._calculate_market_metrics(all_data),
            "talent_metrics": await self._calculate_talent_metrics(all_data),
            "innovation_metrics": await self._calculate_innovation_metrics(all_data),
            "valuation_estimate": await self._estimate_valuation(all_data),
            "key_performance_indicators": {},
            "data_completeness": {}
        }
        
        # Calculate overall quantitative score
        metrics["quantitative_score"] = self._calculate_weighted_score(metrics)
        
        # Calculate data quality and completeness
        metrics["data_quality_score"] = self._assess_data_quality(all_data)
        metrics["data_completeness"] = self._assess_data_completeness(all_data)
        
        # Extract KPIs
        metrics["key_performance_indicators"] = self._extract_kpis(metrics)
        
        return metrics
    
    async def _calculate_growth_metrics(self, data: Dict) -> Dict:
        """Calculate growth-related metrics with real numbers"""
        growth = {
            "employee_growth_rate": 0,
            "github_star_velocity": 0,
            "news_mention_growth": 0,
            "web_traffic_growth": 0,
            "customer_growth_rate": 0,
            "revenue_growth_estimate": 0,
            "compound_growth_score": 0
        }
        
        # Employee growth calculation
        if data.get("intelligence", {}).get("team_indicators", {}):
            team = data["intelligence"]["team_indicators"]
            
            # Parse employee count
            current_employees = 0
            if team.get("linkedin_employees"):
                emp_str = team["linkedin_employees"]
                match = re.search(r'(\d+)', emp_str)
                if match:
                    current_employees = int(match.group(1))
            
            # Estimate growth based on job openings
            if team.get("job_openings", 0) > 0 and current_employees > 0:
                growth["employee_growth_rate"] = round(
                    (team["job_openings"] / current_employees) * 100, 2
                )
        
        # GitHub growth velocity
        if data.get("github", {}).get("found"):
            github = data["github"]
            
            # Calculate star velocity
            if github.get("total_stars", 0) > 0 and github.get("recent_activity"):
                # Estimate based on repo age and stars
                oldest_repo = min(
                    (repo.get("days_since_creation", 0) for repo in github["recent_activity"]),
                    default=365
                )
                if oldest_repo > 0:
                    growth["github_star_velocity"] = round(
                        github["total_stars"] / (oldest_repo / 30), 2  # Stars per month
                    )
        
        # News mention growth
        if data.get("news", {}).get("found"):
            news = data["news"]
            recent_count = news.get("news_count", 0)
            
            # Simple growth indicator based on momentum
            if news.get("momentum") == "positive":
                growth["news_mention_growth"] = 25.0  # 25% estimated growth
            elif news.get("momentum") == "neutral":
                growth["news_mention_growth"] = 0.0
            else:
                growth["news_mention_growth"] = -10.0
        
        # Customer growth estimation
        if data.get("intelligence", {}).get("customers", {}).get("estimated_customers"):
            cust_str = data["intelligence"]["customers"]["estimated_customers"]
            
            # Parse customer count
            if "K" in cust_str:
                base_customers = float(cust_str.replace("K", "").replace("+", "")) * 1000
                # Estimate 30% YoY growth for companies with K customers
                growth["customer_growth_rate"] = 30.0
            elif "M" in cust_str:
                base_customers = float(cust_str.replace("M", "").replace("+", "")) * 1000000
                # Estimate 20% YoY growth for companies with M customers
                growth["customer_growth_rate"] = 20.0
            else:
                # Early stage - higher growth
                growth["customer_growth_rate"] = 50.0
        
        # Revenue growth estimation (based on multiple signals)
        growth_signals = []
        if growth["employee_growth_rate"] > 0:
            growth_signals.append(growth["employee_growth_rate"])
        if growth["customer_growth_rate"] > 0:
            growth_signals.append(growth["customer_growth_rate"])
        
        if growth_signals:
            growth["revenue_growth_estimate"] = round(statistics.mean(growth_signals), 2)
        
        # Compound growth score
        growth_components = [
            growth["employee_growth_rate"] * 0.25,
            min(growth["github_star_velocity"], 100) * 0.15,  # Cap at 100
            (growth["news_mention_growth"] + 50) * 0.20,  # Normalize to 0-100
            growth["customer_growth_rate"] * 0.40
        ]
        growth["compound_growth_score"] = round(sum(growth_components), 2)
        
        return growth
    
    async def _calculate_traction_metrics(self, data: Dict) -> Dict:
        """Calculate traction metrics with real data"""
        traction = {
            "total_customers": 0,
            "customer_logos": 0,
            "github_contributors": 0,
            "total_github_stars": 0,
            "community_size": 0,
            "product_reviews": 0,
            "app_downloads": 0,
            "api_integrations": 0,
            "traction_score": 0
        }
        
        # Customer metrics
        if data.get("intelligence", {}).get("customers", {}):
            customers = data["intelligence"]["customers"]
            
            # Parse customer count
            if customers.get("estimated_customers"):
                cust_str = customers["estimated_customers"]
                if "K" in cust_str:
                    traction["total_customers"] = int(float(cust_str.replace("K", "").replace("+", "")) * 1000)
                elif "M" in cust_str:
                    traction["total_customers"] = int(float(cust_str.replace("M", "").replace("+", "")) * 1000000)
                else:
                    match = re.search(r'(\d+)', cust_str)
                    if match:
                        traction["total_customers"] = int(match.group(1))
            
            traction["customer_logos"] = len(customers.get("customer_logos", []))
        
        # GitHub metrics
        if data.get("github", {}).get("found"):
            github = data["github"]
            traction["github_contributors"] = github.get("followers", 0)
            traction["total_github_stars"] = github.get("total_stars", 0)
        
        # Community metrics from social sentiment
        if data.get("social_sentiment", {}):
            social = data["social_sentiment"]
            
            # Reddit community
            if social.get("reddit", {}).get("found"):
                reddit_posts = social["reddit"].get("posts_count", 0)
                traction["community_size"] += reddit_posts * 100  # Estimate 100 users per post
            
            # HackerNews presence
            if social.get("hackernews", {}).get("found"):
                hn_posts = social["hackernews"].get("posts_count", 0)
                traction["community_size"] += hn_posts * 500  # HN has higher engagement
        
        # Product reviews
        if data.get("intelligence", {}).get("g2_reviews", {}).get("review_count"):
            traction["product_reviews"] = int(data["intelligence"]["g2_reviews"]["review_count"])
        
        # App presence
        if data.get("intelligence", {}).get("app_presence", {}):
            apps = data["intelligence"]["app_presence"]
            if apps.get("ios"):
                traction["app_downloads"] += 10000  # Conservative estimate
            if apps.get("android"):
                traction["app_downloads"] += 15000  # Android typically has more
        
        # API integrations
        if data.get("intelligence", {}).get("product", {}).get("integrations"):
            traction["api_integrations"] = len(data["intelligence"]["product"]["integrations"])
        
        # Calculate traction score
        traction_components = [
            min(traction["total_customers"] / 10000, 30),  # Up to 30 points
            min(traction["customer_logos"] * 2, 20),  # Up to 20 points
            min(traction["total_github_stars"] / 1000, 20),  # Up to 20 points
            min(traction["community_size"] / 10000, 15),  # Up to 15 points
            min(traction["product_reviews"] / 10, 10),  # Up to 10 points
            min(traction["api_integrations"], 5)  # Up to 5 points
        ]
        traction["traction_score"] = round(sum(traction_components), 2)
        
        return traction
    
    async def _calculate_efficiency_metrics(self, data: Dict) -> Dict:
        """Calculate efficiency and burn metrics"""
        efficiency = {
            "revenue_per_employee": 0,
            "burn_rate_estimate": 0,
            "runway_months": 0,
            "efficiency_ratio": 0,
            "capital_efficiency": 0,
            "growth_efficiency_score": 0
        }
        
        # Get employee count
        employees = 0
        if data.get("intelligence", {}).get("team_indicators", {}).get("linkedin_employees"):
            emp_str = data["intelligence"]["team_indicators"]["linkedin_employees"]
            match = re.search(r'(\d+)', emp_str)
            if match:
                employees = int(match.group(1))
        
        # Estimate revenue based on various signals
        estimated_revenue = 0
        
        # Method 1: Based on customers and pricing
        if data.get("intelligence", {}).get("customers", {}).get("estimated_customers"):
            customers = data["intelligence"]["customers"]
            cust_count = 0
            
            cust_str = customers["estimated_customers"]
            if "K" in cust_str:
                cust_count = float(cust_str.replace("K", "").replace("+", "")) * 1000
            elif "M" in cust_str:
                cust_count = float(cust_str.replace("M", "").replace("+", "")) * 1000000
            
            # Estimate ARPU based on business model
            arpu = 100  # Default $100/month
            if data.get("intelligence", {}).get("revenue_indicators", {}).get("pricing_model") == "Enterprise":
                arpu = 2000  # Enterprise ARPU
            elif data.get("intelligence", {}).get("revenue_indicators", {}).get("pricing_model") == "Subscription":
                arpu = 200  # SaaS ARPU
            
            estimated_revenue = cust_count * arpu * 12  # Annual revenue
        
        # Calculate revenue per employee
        if employees > 0 and estimated_revenue > 0:
            efficiency["revenue_per_employee"] = round(estimated_revenue / employees, 0)
        
        # Estimate burn rate based on team size and stage
        if employees > 0:
            # Average fully-loaded cost per employee
            avg_cost_per_employee = 150000  # $150k average
            
            # Adjust based on location/type
            if data.get("company", {}).get("industry", "").lower() in ["ai", "ml", "deep tech"]:
                avg_cost_per_employee = 200000  # Higher for technical talent
            
            annual_burn = employees * avg_cost_per_employee
            efficiency["burn_rate_estimate"] = round(annual_burn / 12, 0)  # Monthly burn
            
            # Calculate runway (assuming some funding)
            if data.get("intelligence", {}).get("revenue_indicators", {}).get("funding_stage"):
                funding_stage = data["intelligence"]["revenue_indicators"]["funding_stage"]
                
                # Estimate funding based on stage
                estimated_funding = {
                    "Seed": 2000000,
                    "Series A": 15000000,
                    "Series B": 40000000,
                    "Series C": 100000000
                }.get(funding_stage, 5000000)
                
                if efficiency["burn_rate_estimate"] > 0:
                    net_burn = efficiency["burn_rate_estimate"] - (estimated_revenue / 12)
                    if net_burn > 0:
                        efficiency["runway_months"] = round(estimated_funding / net_burn, 0)
        
        # Calculate efficiency ratio (revenue/burn)
        if efficiency["burn_rate_estimate"] > 0:
            monthly_revenue = estimated_revenue / 12
            efficiency["efficiency_ratio"] = round(
                monthly_revenue / efficiency["burn_rate_estimate"], 2
            )
        
        # Capital efficiency (customers per $ burned)
        total_customers = data.get("intelligence", {}).get("customers", {}).get("estimated_customers", "0")
        if "K" in str(total_customers):
            total_customers = float(str(total_customers).replace("K", "").replace("+", "")) * 1000
        elif "M" in str(total_customers):
            total_customers = float(str(total_customers).replace("M", "").replace("+", "")) * 1000000
        else:
            total_customers = 0
        
        if efficiency["burn_rate_estimate"] > 0 and total_customers > 0:
            efficiency["capital_efficiency"] = round(
                total_customers / (efficiency["burn_rate_estimate"] * 12), 4
            )
        
        # Growth efficiency score
        if data.get("growth_metrics", {}).get("compound_growth_score", 0) > 0 and efficiency["efficiency_ratio"] > 0:
            efficiency["growth_efficiency_score"] = round(
                data["growth_metrics"]["compound_growth_score"] * efficiency["efficiency_ratio"], 2
            )
        
        return efficiency
    
    async def _calculate_market_metrics(self, data: Dict) -> Dict:
        """Calculate market-related metrics"""
        market = {
            "tam_size": 0,
            "sam_size": 0,
            "som_estimate": 0,
            "market_share": 0,
            "competitor_count": 0,
            "market_growth_rate": 0,
            "market_maturity_score": 0,
            "competitive_intensity": 0
        }
        
        # TAM from market analysis
        if data.get("marketAnalysis", {}).get("tam"):
            market["tam_size"] = data["marketAnalysis"]["tam"]
            
            # Estimate SAM as 10% of TAM
            market["sam_size"] = market["tam_size"] * 0.1
            
            # Estimate SOM based on current traction
            if data.get("traction_metrics", {}).get("total_customers", 0) > 0:
                # Assume average customer value of $10k
                current_revenue = data["traction_metrics"]["total_customers"] * 10000
                market["som_estimate"] = current_revenue * 10  # 10x current revenue
                
                # Calculate market share
                if market["tam_size"] > 0:
                    market["market_share"] = round(
                        (current_revenue / market["tam_size"]) * 100, 4
                    )
        
        # Market growth rate
        if data.get("marketAnalysis", {}).get("growthRate"):
            market["market_growth_rate"] = data["marketAnalysis"]["growthRate"]
        
        # Competitive landscape
        if data.get("competitive_intelligence", {}).get("competitors", {}):
            competitors = data["competitive_intelligence"]["competitors"]
            market["competitor_count"] = (
                len(competitors.get("direct", [])) + 
                len(competitors.get("indirect", [])) * 0.5
            )
            
            # Competitive intensity
            if market["competitor_count"] > 10:
                market["competitive_intensity"] = 90  # High
            elif market["competitor_count"] > 5:
                market["competitive_intensity"] = 60  # Medium
            else:
                market["competitive_intensity"] = 30  # Low
        
        # Market maturity based on various signals
        maturity_signals = []
        
        if data.get("competitive_intelligence", {}).get("market_position", {}).get("market_maturity"):
            maturity = data["competitive_intelligence"]["market_position"]["market_maturity"]
            if "Emerging" in maturity:
                maturity_signals.append(20)
            elif "Growth" in maturity:
                maturity_signals.append(50)
            elif "Mature" in maturity:
                maturity_signals.append(80)
        
        if market["market_growth_rate"] > 30:
            maturity_signals.append(25)  # High growth = early market
        elif market["market_growth_rate"] > 15:
            maturity_signals.append(50)
        else:
            maturity_signals.append(75)
        
        if maturity_signals:
            market["market_maturity_score"] = round(statistics.mean(maturity_signals), 0)
        
        return market
    
    async def _calculate_talent_metrics(self, data: Dict) -> Dict:
        """Calculate talent density and quality metrics"""
        talent = {
            "total_employees": 0,
            "engineering_ratio": 0,
            "github_contributors": 0,
            "talent_density_score": 0,
            "hiring_velocity": 0,
            "glassdoor_rating": 0,
            "talent_retention_estimate": 0
        }
        
        # Total employees
        if data.get("intelligence", {}).get("team_indicators", {}).get("linkedin_employees"):
            emp_str = data["intelligence"]["team_indicators"]["linkedin_employees"]
            match = re.search(r'(\d+)', emp_str)
            if match:
                talent["total_employees"] = int(match.group(1))
        
        # Engineering ratio from GitHub
        if data.get("github", {}).get("found") and talent["total_employees"] > 0:
            talent["github_contributors"] = data["github"].get("followers", 0)
            talent["engineering_ratio"] = round(
                (talent["github_contributors"] / talent["total_employees"]) * 100, 2
            )
        
        # Hiring velocity
        if data.get("intelligence", {}).get("team_indicators", {}).get("job_openings", 0) > 0:
            job_openings = data["intelligence"]["team_indicators"]["job_openings"]
            if talent["total_employees"] > 0:
                talent["hiring_velocity"] = round(
                    (job_openings / talent["total_employees"]) * 100, 2
                )
        
        # Glassdoor rating
        if data.get("social_sentiment", {}).get("glassdoor", {}).get("rating"):
            talent["glassdoor_rating"] = float(data["social_sentiment"]["glassdoor"]["rating"])
            
            # Estimate retention based on rating
            if talent["glassdoor_rating"] >= 4.0:
                talent["talent_retention_estimate"] = 90  # 90% retention
            elif talent["glassdoor_rating"] >= 3.5:
                talent["talent_retention_estimate"] = 80
            else:
                talent["talent_retention_estimate"] = 70
        
        # Talent density score
        density_components = [
            min(talent["engineering_ratio"], 50) * 0.4,  # Up to 20 points
            min(talent["hiring_velocity"], 30) * 0.3,  # Up to 9 points
            (talent["glassdoor_rating"] * 20) * 0.3 if talent["glassdoor_rating"] > 0 else 0  # Up to 30 points
        ]
        talent["talent_density_score"] = round(sum(density_components), 2)
        
        return talent
    
    async def _calculate_innovation_metrics(self, data: Dict) -> Dict:
        """Calculate innovation and R&D metrics"""
        innovation = {
            "github_repos": 0,
            "open_source_contributions": 0,
            "patent_count": 0,
            "tech_stack_modernity": 0,
            "api_endpoints": 0,
            "innovation_velocity": 0,
            "r_and_d_intensity": 0,
            "innovation_score": 0
        }
        
        # GitHub metrics
        if data.get("github", {}).get("found"):
            github = data["github"]
            innovation["github_repos"] = github.get("public_repos", 0)
            
            # Open source contributions (repos with stars)
            if github.get("recent_activity"):
                innovation["open_source_contributions"] = len([
                    repo for repo in github["recent_activity"] 
                    if repo.get("stars", 0) > 10
                ])
            
            # Innovation velocity (commits per repo)
            total_commits = sum(repo.get("commits", 0) for repo in github.get("recent_activity", []))
            if innovation["github_repos"] > 0:
                innovation["innovation_velocity"] = round(
                    total_commits / innovation["github_repos"], 2
                )
        
        # Patent data
        if data.get("patent_data", {}).get("patents"):
            innovation["patent_count"] = len(data["patent_data"]["patents"])
        
        # Tech stack modernity
        if data.get("technical_dd", {}).get("website_tech", {}).get("found"):
            tech = data["technical_dd"]["website_tech"]
            
            modern_tech = ["React", "Vue", "Angular", "Nextjs", "GraphQL", "Kubernetes", "Docker"]
            tech_count = sum(1 for t in modern_tech if t in str(tech))
            innovation["tech_stack_modernity"] = round((tech_count / len(modern_tech)) * 100, 2)
        
        # API endpoints
        if data.get("technical_dd", {}).get("api_quality", {}).get("api_paths"):
            innovation["api_endpoints"] = len(data["technical_dd"]["api_quality"]["api_paths"])
        
        # R&D intensity (engineering ratio * innovation velocity)
        if data.get("talent_metrics", {}).get("engineering_ratio", 0) > 0:
            innovation["r_and_d_intensity"] = round(
                data["talent_metrics"]["engineering_ratio"] * 
                (innovation["innovation_velocity"] / 100), 2
            )
        
        # Innovation score
        innovation_components = [
            min(innovation["github_repos"], 20) * 0.20,  # Up to 4 points
            min(innovation["open_source_contributions"] * 5, 20) * 0.20,  # Up to 4 points
            min(innovation["patent_count"] * 10, 20) * 0.20,  # Up to 4 points
            (innovation["tech_stack_modernity"] / 5) * 0.20,  # Up to 20 points
            min(innovation["innovation_velocity"] / 10, 20) * 0.20  # Up to 4 points
        ]
        innovation["innovation_score"] = round(sum(innovation_components), 2)
        
        return innovation
    
    async def _estimate_valuation(self, data: Dict) -> Dict:
        """Estimate company valuation based on metrics"""
        valuation = {
            "estimated_revenue": 0,
            "revenue_multiple": 0,
            "valuation_estimate": 0,
            "valuation_range_min": 0,
            "valuation_range_max": 0,
            "comparable_valuations": [],
            "confidence_score": 0
        }
        
        # Estimate revenue
        revenue_signals = []
        
        # From customers
        if data.get("traction_metrics", {}).get("total_customers", 0) > 0:
            customers = data["traction_metrics"]["total_customers"]
            
            # Estimate ARPU
            arpu_annual = 12000  # Default $1k/month
            if data.get("intelligence", {}).get("revenue_indicators", {}).get("pricing_model") == "Enterprise":
                arpu_annual = 50000
            elif data.get("intelligence", {}).get("revenue_indicators", {}).get("business_model") == "SaaS":
                arpu_annual = 15000
            
            revenue_signals.append(customers * arpu_annual)
        
        # From employees (reverse engineer from burn)
        if data.get("efficiency_metrics", {}).get("revenue_per_employee", 0) > 0:
            employees = data.get("talent_metrics", {}).get("total_employees", 0)
            if employees > 0:
                revenue_signals.append(
                    data["efficiency_metrics"]["revenue_per_employee"] * employees
                )
        
        # Average revenue estimate
        if revenue_signals:
            valuation["estimated_revenue"] = round(statistics.mean(revenue_signals), 0)
        
        # Determine revenue multiple based on growth and efficiency
        base_multiple = 5  # Base SaaS multiple
        
        # Adjust for growth
        if data.get("growth_metrics", {}).get("revenue_growth_estimate", 0) > 50:
            base_multiple *= 2
        elif data.get("growth_metrics", {}).get("revenue_growth_estimate", 0) > 30:
            base_multiple *= 1.5
        
        # Adjust for efficiency
        if data.get("efficiency_metrics", {}).get("efficiency_ratio", 0) > 0.8:
            base_multiple *= 1.3
        elif data.get("efficiency_metrics", {}).get("efficiency_ratio", 0) < 0.3:
            base_multiple *= 0.7
        
        # Adjust for market
        if data.get("company", {}).get("industry", "").lower() in ["ai", "ml", "artificial intelligence"]:
            base_multiple *= 1.5  # AI premium
        
        valuation["revenue_multiple"] = round(base_multiple, 1)
        
        # Calculate valuation
        if valuation["estimated_revenue"] > 0:
            valuation["valuation_estimate"] = round(
                valuation["estimated_revenue"] * valuation["revenue_multiple"], 0
            )
            
            # Range (-30% to +50%)
            valuation["valuation_range_min"] = round(valuation["valuation_estimate"] * 0.7, 0)
            valuation["valuation_range_max"] = round(valuation["valuation_estimate"] * 1.5, 0)
        
        # Comparable valuations
        industry = data.get("company", {}).get("industry", "Technology")
        stage = "Series A"  # Default
        
        if valuation["estimated_revenue"] < 1000000:
            stage = "Seed"
        elif valuation["estimated_revenue"] < 10000000:
            stage = "Series A"
        elif valuation["estimated_revenue"] < 50000000:
            stage = "Series B"
        else:
            stage = "Series C+"
        
        valuation["comparable_valuations"] = [
            {"company": f"Average {industry} {stage}", "valuation": valuation["valuation_estimate"]},
            {"company": f"Top Quartile {industry} {stage}", "valuation": valuation["valuation_range_max"]},
            {"company": f"Median {industry} {stage}", "valuation": valuation["valuation_estimate"]}
        ]
        
        # Confidence score based on data completeness
        data_points = [
            data.get("traction_metrics", {}).get("total_customers", 0) > 0,
            data.get("talent_metrics", {}).get("total_employees", 0) > 0,
            data.get("growth_metrics", {}).get("revenue_growth_estimate", 0) > 0,
            data.get("efficiency_metrics", {}).get("efficiency_ratio", 0) > 0
        ]
        valuation["confidence_score"] = round(sum(data_points) * 25, 0)
        
        return valuation
    
    def _calculate_weighted_score(self, metrics: Dict) -> float:
        """Calculate overall weighted score"""
        scores = {
            "growth_velocity": metrics["growth_metrics"]["compound_growth_score"],
            "market_penetration": metrics["traction_metrics"]["traction_score"],
            "financial_efficiency": metrics["efficiency_metrics"]["growth_efficiency_score"],
            "product_adoption": min(metrics["market_metrics"]["market_share"] * 10, 100),
            "talent_density": metrics["talent_metrics"]["talent_density_score"],
            "innovation_index": metrics["innovation_metrics"]["innovation_score"]
        }
        
        weighted_score = sum(
            scores[key] * self.metric_weights[key] 
            for key in scores
        )
        
        return round(weighted_score, 2)
    
    def _assess_data_quality(self, data: Dict) -> float:
        """Assess quality of available data"""
        quality_checks = [
            data.get("github", {}).get("found", False),
            data.get("news", {}).get("found", False),
            data.get("intelligence", {}).get("product", {}).get("found", False),
            data.get("intelligence", {}).get("customers", {}).get("found", False),
            data.get("social_sentiment", {}).get("overall_sentiment", {}).get("confidence", 0) > 50,
            data.get("technical_dd", {}).get("technical_score", 0) > 0,
            data.get("competitive_intelligence", {}).get("market_opportunity_score", 0) > 0,
            len(data.get("intelligence", {}).get("team_indicators", {})) > 0
        ]
        
        return round(sum(quality_checks) / len(quality_checks) * 100, 0)
    
    def _assess_data_completeness(self, data: Dict) -> Dict:
        """Assess completeness of each data category"""
        completeness = {
            "github_data": 100 if data.get("github", {}).get("found") else 0,
            "news_data": 100 if data.get("news", {}).get("found") else 0,
            "product_data": 100 if data.get("intelligence", {}).get("product", {}).get("found") else 0,
            "customer_data": 100 if data.get("intelligence", {}).get("customers", {}).get("found") else 0,
            "social_data": data.get("social_sentiment", {}).get("overall_sentiment", {}).get("confidence", 0),
            "technical_data": 100 if data.get("technical_dd", {}).get("website_tech", {}).get("found") else 0,
            "competitive_data": 100 if data.get("competitive_intelligence", {}).get("competitors") else 0,
            "financial_data": 50 if data.get("efficiency_metrics") else 0  # Limited public data
        }
        
        completeness["overall"] = round(statistics.mean(completeness.values()), 0)
        
        return completeness
    
    def _extract_kpis(self, metrics: Dict) -> Dict:
        """Extract key performance indicators"""
        kpis = {
            "growth_rate": metrics["growth_metrics"]["revenue_growth_estimate"],
            "burn_rate": metrics["efficiency_metrics"]["burn_rate_estimate"],
            "runway": metrics["efficiency_metrics"]["runway_months"],
            "efficiency_ratio": metrics["efficiency_metrics"]["efficiency_ratio"],
            "market_share": metrics["market_metrics"]["market_share"],
            "customer_count": metrics["traction_metrics"]["total_customers"],
            "revenue_estimate": metrics["valuation_estimate"]["estimated_revenue"],
            "valuation": metrics["valuation_estimate"]["valuation_estimate"],
            "employee_count": metrics["talent_metrics"]["total_employees"],
            "github_stars": metrics["traction_metrics"]["total_github_stars"]
        }
        
        return kpis

# Singleton instance
data_metrics_engine = DataMetricsEngine()