"""
Real data sources that actually fetch interesting company data
"""

import httpx
import asyncio
from typing import Dict, List, Optional
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup

class RealCompanyDataFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    
    async def get_crunchbase_data(self, company_name: str) -> Dict:
        """Scrape basic data from Crunchbase (public pages)"""
        try:
            async with httpx.AsyncClient() as client:
                # Clean company name for URL
                company_slug = company_name.lower().replace(" ", "-").replace(".", "")
                url = f"https://www.crunchbase.com/organization/{company_slug}"
                
                response = await client.get(url, headers=self.headers, follow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract visible data from page
                    data = {
                        "url": url,
                        "found": True
                    }
                    
                    # Try to find funding info
                    funding_elements = soup.find_all(string=re.compile(r'\$[\d\.]+[MBK]'))
                    if funding_elements:
                        data["funding_mentions"] = [elem.strip() for elem in funding_elements[:3]]
                    
                    return data
                    
        except Exception as e:
            pass
        
        return {"found": False}
    
    async def get_github_activity(self, company_name: str) -> Dict:
        """Get real GitHub organization data"""
        try:
            async with httpx.AsyncClient() as client:
                # Try common variations
                org_names = [
                    company_name.lower().replace(" ", ""),
                    company_name.lower().replace(" ", "-"),
                    company_name.lower().split()[0]  # First word only
                ]
                
                for org_name in org_names:
                    response = await client.get(
                        f"https://api.github.com/orgs/{org_name}",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        org_data = response.json()
                        
                        # Get repositories
                        repos_response = await client.get(
                            f"https://api.github.com/orgs/{org_name}/repos?sort=updated&per_page=10",
                            headers=self.headers
                        )
                        
                        repos = repos_response.json() if repos_response.status_code == 200 else []
                        
                        # Calculate metrics
                        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
                        total_forks = sum(repo.get("forks_count", 0) for repo in repos)
                        
                        # Get recent activity
                        recent_updates = []
                        for repo in repos[:5]:
                            if repo.get("updated_at"):
                                days_ago = (datetime.now() - datetime.fromisoformat(repo["updated_at"].replace("Z", "+00:00"))).days
                                recent_updates.append({
                                    "repo": repo["name"],
                                    "stars": repo.get("stargazers_count", 0),
                                    "days_since_update": days_ago,
                                    "language": repo.get("language", "Unknown")
                                })
                        
                        return {
                            "found": True,
                            "name": org_data.get("name"),
                            "public_repos": org_data.get("public_repos", 0),
                            "followers": org_data.get("followers", 0),
                            "total_stars": total_stars,
                            "total_forks": total_forks,
                            "created_at": org_data.get("created_at"),
                            "recent_activity": recent_updates,
                            "tech_stack": list(set([r.get("language") for r in repos if r.get("language")])),
                            "description": org_data.get("description"),
                            "blog": org_data.get("blog"),
                            "engineering_score": min(100, (total_stars / 10) + (org_data.get("public_repos", 0) * 2))
                        }
                        
        except Exception as e:
            pass
            
        return {"found": False}
    
    async def get_news_sentiment(self, company_name: str) -> Dict:
        """Get recent news and sentiment"""
        try:
            async with httpx.AsyncClient() as client:
                # Use Google News RSS
                response = await client.get(
                    f"https://news.google.com/rss/search?q={company_name}+startup+funding&hl=en-US&gl=US&ceid=US:en",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'xml')
                    items = soup.find_all('item')[:10]
                    
                    news_data = []
                    positive_keywords = ['funding', 'raises', 'growth', 'expands', 'launches', 'partnership', 'revenue', 'unicorn', 'acquisition', 'ipo']
                    negative_keywords = ['layoffs', 'cuts', 'losses', 'shutdown', 'lawsuit', 'investigation', 'breach', 'bankruptcy']
                    
                    sentiment_score = 50  # Neutral baseline
                    
                    for item in items:
                        title = item.find('title').text if item.find('title') else ""
                        pub_date = item.find('pubDate').text if item.find('pubDate') else ""
                        
                        # Simple sentiment analysis
                        title_lower = title.lower()
                        for keyword in positive_keywords:
                            if keyword in title_lower:
                                sentiment_score += 5
                                break
                        for keyword in negative_keywords:
                            if keyword in title_lower:
                                sentiment_score -= 10
                                break
                        
                        news_data.append({
                            "title": title,
                            "date": pub_date,
                            "source": item.find('source').text if item.find('source') else "Unknown"
                        })
                    
                    return {
                        "found": True,
                        "recent_news": news_data[:5],
                        "news_count": len(news_data),
                        "sentiment_score": max(0, min(100, sentiment_score)),
                        "momentum": "positive" if sentiment_score > 60 else "negative" if sentiment_score < 40 else "neutral"
                    }
                    
        except Exception as e:
            pass
            
        return {"found": False}
    
    async def get_domain_info(self, domain: str) -> Dict:
        """Get domain/website information"""
        try:
            async with httpx.AsyncClient() as client:
                # Check if website is up
                response = await client.get(f"https://{domain}", headers=self.headers, follow_redirects=True, timeout=5.0)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract meta information
                    meta_description = soup.find('meta', attrs={'name': 'description'})
                    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
                    
                    # Look for technology indicators
                    tech_indicators = {
                        "react": "React" in response.text,
                        "angular": "angular" in response.text.lower(),
                        "vue": "Vue" in response.text,
                        "wordpress": "wp-content" in response.text,
                        "shopify": "shopify" in response.text.lower(),
                        "aws": "amazonaws.com" in response.text,
                        "cloudflare": "cloudflare" in str(response.headers)
                    }
                    
                    # Look for company size indicators
                    size_indicators = []
                    text_lower = response.text.lower()
                    if "enterprise" in text_lower:
                        size_indicators.append("enterprise")
                    if "startup" in text_lower:
                        size_indicators.append("startup")
                    if any(phrase in text_lower for phrase in ["fortune 500", "nasdaq", "nyse"]):
                        size_indicators.append("public")
                    
                    return {
                        "found": True,
                        "status": "active",
                        "description": meta_description.get('content') if meta_description else None,
                        "keywords": meta_keywords.get('content').split(',') if meta_keywords else [],
                        "tech_stack": [tech for tech, found in tech_indicators.items() if found],
                        "size_indicators": size_indicators,
                        "has_blog": "/blog" in response.text or "blog." in domain,
                        "has_careers": "/careers" in response.text or "/jobs" in response.text,
                        "ssl_enabled": response.url.startswith("https")
                    }
                    
        except Exception as e:
            pass
            
        return {"found": False}

    async def calculate_investment_score(self, all_data: Dict) -> Dict:
        """Calculate a real investment score based on actual data"""
        score = 50  # Base score
        signals = []
        
        # GitHub presence (up to 20 points)
        if all_data.get("github", {}).get("found"):
            github = all_data["github"]
            if github.get("total_stars", 0) > 1000:
                score += 10
                signals.append("Strong open source presence")
            elif github.get("total_stars", 0) > 100:
                score += 5
                signals.append("Active open source contributor")
            
            if github.get("public_repos", 0) > 10:
                score += 5
                signals.append("Transparent engineering culture")
            
            # Recent activity
            recent = github.get("recent_activity", [])
            if recent and recent[0].get("days_since_update", 999) < 7:
                score += 5
                signals.append("Very active development")
        
        # News sentiment (up to 20 points)
        if all_data.get("news", {}).get("found"):
            news = all_data["news"]
            if news.get("sentiment_score", 50) > 70:
                score += 15
                signals.append("Positive media coverage")
            elif news.get("sentiment_score", 50) > 60:
                score += 10
                signals.append("Generally positive news")
            elif news.get("sentiment_score", 50) < 30:
                score -= 10
                signals.append("Negative news coverage")
            
            if news.get("news_count", 0) > 5:
                score += 5
                signals.append("High media visibility")
        
        # Website quality (up to 10 points)
        if all_data.get("domain", {}).get("found"):
            domain = all_data["domain"]
            if domain.get("ssl_enabled"):
                score += 2
            if domain.get("has_careers"):
                score += 3
                signals.append("Hiring - growth signal")
            if len(domain.get("tech_stack", [])) > 2:
                score += 5
                signals.append("Modern tech stack")
        
        # Crunchbase presence
        if all_data.get("crunchbase", {}).get("found"):
            score += 5
            signals.append("Established company profile")
        
        # Time in business (from GitHub)
        if all_data.get("github", {}).get("created_at"):
            created = datetime.fromisoformat(all_data["github"]["created_at"].replace("Z", "+00:00"))
            years = (datetime.now(created.tzinfo) - created).days / 365
            if years > 5:
                score += 5
                signals.append(f"Established {int(years)} years ago")
            elif years < 1:
                signals.append("Early stage (<1 year)")
        
        return {
            "score": max(0, min(100, score)),
            "signals": signals,
            "data_quality": len([v for v in all_data.values() if v.get("found", False)]) / len(all_data)
        }

# Singleton instance
real_data_fetcher = RealCompanyDataFetcher()