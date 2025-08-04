"""
SEC EDGAR API Integration
Free access to company financial filings
"""

import httpx
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

class SECEdgarAPI:
    BASE_URL = "https://data.sec.gov"
    ARCHIVES_URL = "https://www.sec.gov/Archives/edgar"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "DealFlow Analytics (admin@dealflow.com)"
        }
    
    async def get_company_filings(self, company_name: str) -> Dict:
        """Get recent SEC filings for a company"""
        try:
            async with httpx.AsyncClient() as client:
                # Search for company CIK
                cik = await self._search_company_cik(client, company_name)
                if not cik:
                    return {"error": "Company not found in SEC database"}
                
                # Get recent filings
                filings = await self._get_recent_filings(client, cik)
                
                # Parse key financial data
                financial_data = await self._parse_financial_data(client, filings)
                
                return {
                    "company_name": company_name,
                    "cik": cik,
                    "filings": filings[:5],  # Latest 5 filings
                    "financial_metrics": financial_data,
                    "data_quality": self._assess_data_quality(filings)
                }
                
        except Exception as e:
            return {"error": f"SEC data fetch failed: {str(e)}"}
    
    async def _search_company_cik(self, client: httpx.AsyncClient, company_name: str) -> Optional[str]:
        """Search for company CIK number"""
        try:
            # Clean company name
            search_term = company_name.lower().replace(" inc", "").replace(" corp", "")
            
            # Use company tickers endpoint
            response = await client.get(
                f"{self.BASE_URL}/submissions/CIK-lookup-data.json",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                # Search through companies
                for cik, info in data.items():
                    if search_term in info.get("title", "").lower():
                        return cik.zfill(10)  # CIK should be 10 digits
            
            return None
            
        except Exception:
            return None
    
    async def _get_recent_filings(self, client: httpx.AsyncClient, cik: str) -> List[Dict]:
        """Get recent filings for a CIK"""
        try:
            response = await client.get(
                f"{self.BASE_URL}/submissions/CIK{cik}.json",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                recent_filings = []
                
                filings = data.get("filings", {}).get("recent", {})
                forms = filings.get("form", [])
                dates = filings.get("filingDate", [])
                accessions = filings.get("accessionNumber", [])
                
                for i in range(min(20, len(forms))):  # Get last 20 filings
                    if forms[i] in ["10-K", "10-Q", "8-K", "20-F", "S-1", "424B4"]:
                        recent_filings.append({
                            "form": forms[i],
                            "filing_date": dates[i],
                            "accession_number": accessions[i].replace("-", ""),
                            "url": f"{self.ARCHIVES_URL}/data/{cik}/{accessions[i].replace('-', '')}/{accessions[i]}-index.html"
                        })
                
                return recent_filings
            
            return []
            
        except Exception:
            return []
    
    async def _parse_financial_data(self, client: httpx.AsyncClient, filings: List[Dict]) -> Dict:
        """Extract key financial metrics from filings"""
        financial_data = {
            "revenue": None,
            "net_income": None,
            "total_assets": None,
            "cash": None,
            "growth_rate": None,
            "burn_rate": None
        }
        
        # Find most recent 10-K or 10-Q
        for filing in filings:
            if filing["form"] in ["10-K", "10-Q"]:
                # In production, would parse XBRL data
                # For now, return sample data structure
                financial_data.update({
                    "latest_filing": filing["form"],
                    "filing_date": filing["filing_date"],
                    "has_financial_data": True
                })
                break
        
        return financial_data
    
    def _assess_data_quality(self, filings: List[Dict]) -> Dict:
        """Assess quality and recency of SEC data"""
        if not filings:
            return {"score": 0, "status": "no_data"}
        
        latest_date = datetime.strptime(filings[0]["filing_date"], "%Y-%m-%d")
        days_old = (datetime.now() - latest_date).days
        
        if days_old < 100:  # Recent filing
            return {"score": 1.0, "status": "current", "days_since_filing": days_old}
        elif days_old < 200:
            return {"score": 0.7, "status": "recent", "days_since_filing": days_old}
        else:
            return {"score": 0.3, "status": "outdated", "days_since_filing": days_old}

# Export singleton instance
sec_edgar = SECEdgarAPI()