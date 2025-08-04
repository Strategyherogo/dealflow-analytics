"""
Wikipedia API Integration
Get company history and background information
"""

import httpx
import asyncio
from typing import Dict, Optional
import re

class WikipediaAPI:
    BASE_URL = "https://en.wikipedia.org/api/rest_v1"
    SEARCH_URL = "https://en.wikipedia.org/w/api.php"
    
    async def get_company_info(self, company_name: str) -> Dict:
        """Get company information from Wikipedia"""
        try:
            async with httpx.AsyncClient() as client:
                # Search for company page
                page_title = await self._search_company_page(client, company_name)
                if not page_title:
                    return {"error": "Company not found on Wikipedia"}
                
                # Get page summary
                summary = await self._get_page_summary(client, page_title)
                
                # Extract structured data
                structured_data = await self._extract_structured_data(client, page_title)
                
                return {
                    "page_title": page_title,
                    "summary": summary,
                    "structured_data": structured_data,
                    "data_quality": self._assess_data_quality(summary, structured_data)
                }
                
        except Exception as e:
            return {"error": f"Wikipedia data fetch failed: {str(e)}"}
    
    async def _search_company_page(self, client: httpx.AsyncClient, company_name: str) -> Optional[str]:
        """Search for company Wikipedia page"""
        try:
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": f"{company_name} company",
                "srlimit": 5
            }
            
            response = await client.get(self.SEARCH_URL, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("query", {}).get("search", [])
                
                # Find most relevant result
                for result in results:
                    title = result.get("title", "").lower()
                    # Check if it's likely a company page
                    if any(term in title for term in ["company", "corporation", "inc", "ltd"]) or \
                       company_name.lower() in title:
                        return result.get("title")
                
                # Return first result if no specific company page found
                if results:
                    return results[0].get("title")
            
            return None
            
        except Exception:
            return None
    
    async def _get_page_summary(self, client: httpx.AsyncClient, page_title: str) -> Dict:
        """Get page summary from Wikipedia REST API"""
        try:
            # URL encode the title
            encoded_title = page_title.replace(" ", "_")
            
            response = await client.get(
                f"{self.BASE_URL}/page/summary/{encoded_title}"
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "extract": data.get("extract", ""),
                    "description": data.get("description", ""),
                    "timestamp": data.get("timestamp", "")
                }
            
            return {}
            
        except Exception:
            return {}
    
    async def _extract_structured_data(self, client: httpx.AsyncClient, page_title: str) -> Dict:
        """Extract structured data from Wikipedia page"""
        try:
            # Get full page content
            params = {
                "action": "query",
                "format": "json",
                "prop": "revisions|categories",
                "titles": page_title,
                "rvprop": "content",
                "rvlimit": 1
            }
            
            response = await client.get(self.SEARCH_URL, params=params)
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                
                structured_data = {
                    "founded": None,
                    "founders": [],
                    "headquarters": None,
                    "industry": None,
                    "products": [],
                    "revenue": None,
                    "employees": None,
                    "website": None
                }
                
                # Extract from infobox (simplified - in production would parse wikitext)
                for page_id, page_data in pages.items():
                    content = page_data.get("revisions", [{}])[0].get("*", "")
                    
                    # Extract founded year
                    founded_match = re.search(r"founded\s*=\s*.*?(\d{4})", content, re.I)
                    if founded_match:
                        structured_data["founded"] = founded_match.group(1)
                    
                    # Extract headquarters
                    hq_match = re.search(r"headquarters\s*=\s*\[\[(.*?)\]\]", content, re.I)
                    if hq_match:
                        structured_data["headquarters"] = hq_match.group(1)
                    
                    # Extract industry
                    industry_match = re.search(r"industry\s*=\s*\[\[(.*?)\]\]", content, re.I)
                    if industry_match:
                        structured_data["industry"] = industry_match.group(1)
                    
                    # Categories can indicate company type
                    categories = [cat.get("title", "") for cat in page_data.get("categories", [])]
                    structured_data["categories"] = categories
                
                return structured_data
            
            return {}
            
        except Exception:
            return {}
    
    def _assess_data_quality(self, summary: Dict, structured_data: Dict) -> Dict:
        """Assess quality of Wikipedia data"""
        if not summary.get("extract"):
            return {"score": 0, "status": "no_data"}
        
        # Check data completeness
        extract_length = len(summary.get("extract", ""))
        fields_populated = sum(1 for v in structured_data.values() if v)
        
        if extract_length > 500 and fields_populated > 3:
            return {"score": 1.0, "status": "comprehensive"}
        elif extract_length > 200:
            return {"score": 0.7, "status": "moderate"}
        else:
            return {"score": 0.3, "status": "minimal"}

# Export singleton instance
wikipedia_api = WikipediaAPI()