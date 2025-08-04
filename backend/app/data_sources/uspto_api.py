"""
USPTO Patent API Integration
Analyze company innovation through patent activity
"""

import httpx
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
import json

class USPTOAPI:
    BASE_URL = "https://api.patentsview.org/patents/query"
    
    async def search_patents(self, company_name: str) -> Dict:
        """Search for patents by company name"""
        try:
            async with httpx.AsyncClient() as client:
                # Search for patents
                patents = await self._search_company_patents(client, company_name)
                
                # Analyze patent portfolio
                portfolio_analysis = self._analyze_patent_portfolio(patents)
                
                # Calculate innovation metrics
                innovation_metrics = self._calculate_innovation_metrics(patents)
                
                return {
                    "company_name": company_name,
                    "total_patents": len(patents),
                    "recent_patents": portfolio_analysis["recent_patents"],
                    "patent_categories": portfolio_analysis["categories"],
                    "innovation_metrics": innovation_metrics,
                    "top_patents": patents[:5],  # Most recent 5
                    "data_quality": self._assess_data_quality(patents)
                }
                
        except Exception as e:
            return {"error": f"USPTO data fetch failed: {str(e)}"}
    
    async def _search_company_patents(self, client: httpx.AsyncClient, company_name: str) -> List[Dict]:
        """Search USPTO for company patents"""
        try:
            # Prepare search query
            query = {
                "q": {
                    "_or": [
                        {"assignee_organization": company_name},
                        {"assignee_organization": f"{company_name} Inc"},
                        {"assignee_organization": f"{company_name} Corporation"},
                        {"assignee_organization": f"{company_name} LLC"}
                    ]
                },
                "f": [
                    "patent_number",
                    "patent_title",
                    "patent_date",
                    "patent_abstract",
                    "assignee_organization",
                    "cpc_category"
                ],
                "s": [
                    {"patent_date": "desc"}
                ],
                "o": {
                    "per_page": 50
                }
            }
            
            response = await client.post(
                self.BASE_URL,
                json=query,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                patents = data.get("patents", [])
                
                # Process patent data
                processed_patents = []
                for patent in patents:
                    processed_patents.append({
                        "number": patent.get("patent_number"),
                        "title": patent.get("patent_title"),
                        "date": patent.get("patent_date"),
                        "abstract": patent.get("patent_abstract", "")[:200] + "...",
                        "assignee": patent.get("assignee_organization"),
                        "categories": patent.get("cpc_category", [])
                    })
                
                return processed_patents
            
            return []
            
        except Exception:
            return []
    
    def _analyze_patent_portfolio(self, patents: List[Dict]) -> Dict:
        """Analyze patent portfolio characteristics"""
        if not patents:
            return {"recent_patents": 0, "categories": {}}
        
        # Count recent patents (last 3 years)
        three_years_ago = datetime.now() - timedelta(days=3*365)
        recent_patents = 0
        
        # Category distribution
        categories = {}
        
        for patent in patents:
            # Check if recent
            try:
                patent_date = datetime.strptime(patent["date"], "%Y-%m-%d")
                if patent_date > three_years_ago:
                    recent_patents += 1
            except:
                pass
            
            # Count categories
            for cat in patent.get("categories", []):
                if cat:
                    categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "recent_patents": recent_patents,
            "categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])
        }
    
    def _calculate_innovation_metrics(self, patents: List[Dict]) -> Dict:
        """Calculate innovation metrics from patent data"""
        if not patents:
            return {
                "innovation_score": 0,
                "patent_velocity": 0,
                "technology_diversity": 0
            }
        
        # Patent velocity (patents per year)
        try:
            dates = [datetime.strptime(p["date"], "%Y-%m-%d") for p in patents if p.get("date")]
            if len(dates) > 1:
                date_range = (max(dates) - min(dates)).days / 365.25
                velocity = len(patents) / max(date_range, 1)
            else:
                velocity = 0
        except:
            velocity = 0
        
        # Technology diversity (number of unique categories)
        unique_categories = set()
        for patent in patents:
            unique_categories.update(patent.get("categories", []))
        
        # Innovation score (combined metric)
        innovation_score = min(100, int(
            (len(patents) * 0.3) +  # Total patents
            (velocity * 10) +       # Patent velocity
            (len(unique_categories) * 2)  # Technology diversity
        ))
        
        return {
            "innovation_score": innovation_score,
            "patent_velocity": round(velocity, 1),
            "technology_diversity": len(unique_categories)
        }
    
    def _assess_data_quality(self, patents: List[Dict]) -> Dict:
        """Assess quality of patent data"""
        if not patents:
            return {"score": 0, "status": "no_patents"}
        
        if len(patents) < 5:
            return {"score": 0.3, "status": "few_patents"}
        elif len(patents) < 20:
            return {"score": 0.7, "status": "moderate_portfolio"}
        else:
            return {"score": 1.0, "status": "strong_portfolio"}

# Export singleton instance
uspto_api = USPTOAPI()