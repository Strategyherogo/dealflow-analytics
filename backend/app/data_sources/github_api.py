"""
GitHub API Integration
Analyze tech companies through their open source presence
"""

import httpx
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os

class GitHubAPI:
    BASE_URL = "https://api.github.com"
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")  # Optional, increases rate limit
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DealFlow-Analytics"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    async def get_organization_data(self, company_name: str) -> Dict:
        """Get GitHub organization data for a company"""
        try:
            async with httpx.AsyncClient() as client:
                # Search for organization
                org_name = await self._find_organization(client, company_name)
                if not org_name:
                    return {"error": "Organization not found on GitHub"}
                
                # Get organization details
                org_data = await self._get_org_details(client, org_name)
                
                # Get repository statistics
                repo_stats = await self._get_repository_stats(client, org_name)
                
                # Get contributor statistics
                contributor_stats = await self._get_contributor_stats(client, org_name)
                
                # Calculate growth metrics
                growth_metrics = self._calculate_growth_metrics(repo_stats, contributor_stats)
                
                return {
                    "organization": org_name,
                    "profile": org_data,
                    "repository_stats": repo_stats,
                    "contributor_stats": contributor_stats,
                    "growth_metrics": growth_metrics,
                    "tech_stack": self._analyze_tech_stack(repo_stats),
                    "data_quality": self._assess_data_quality(org_data, repo_stats)
                }
                
        except Exception as e:
            return {"error": f"GitHub data fetch failed: {str(e)}"}
    
    async def _find_organization(self, client: httpx.AsyncClient, company_name: str) -> Optional[str]:
        """Search for company GitHub organization"""
        try:
            # Try exact match first
            search_terms = [
                company_name.lower().replace(" ", ""),
                company_name.lower().replace(" ", "-"),
                company_name.split()[0].lower()  # First word only
            ]
            
            for term in search_terms:
                response = await client.get(
                    f"{self.BASE_URL}/search/users",
                    params={"q": f"{term} type:org", "per_page": 5},
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    results = response.json()
                    if results["total_count"] > 0:
                        # Return the most relevant result
                        return results["items"][0]["login"]
            
            return None
            
        except Exception:
            return None
    
    async def _get_org_details(self, client: httpx.AsyncClient, org_name: str) -> Dict:
        """Get organization profile details"""
        try:
            response = await client.get(
                f"{self.BASE_URL}/orgs/{org_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "blog": data.get("blog"),
                    "location": data.get("location"),
                    "public_repos": data.get("public_repos", 0),
                    "created_at": data.get("created_at"),
                    "followers": data.get("followers", 0)
                }
            
            return {}
            
        except Exception:
            return {}
    
    async def _get_repository_stats(self, client: httpx.AsyncClient, org_name: str) -> Dict:
        """Get repository statistics for organization"""
        try:
            # Get top repositories
            response = await client.get(
                f"{self.BASE_URL}/orgs/{org_name}/repos",
                params={"sort": "pushed", "per_page": 30},
                headers=self.headers
            )
            
            if response.status_code == 200:
                repos = response.json()
                
                # Aggregate statistics
                total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
                total_forks = sum(repo.get("forks_count", 0) for repo in repos)
                total_watchers = sum(repo.get("watchers_count", 0) for repo in repos)
                
                # Language distribution
                languages = {}
                for repo in repos:
                    lang = repo.get("language")
                    if lang:
                        languages[lang] = languages.get(lang, 0) + 1
                
                # Recent activity
                recent_repos = [r for r in repos if self._is_recently_active(r.get("pushed_at"))]
                
                return {
                    "total_repos": len(repos),
                    "total_stars": total_stars,
                    "total_forks": total_forks,
                    "total_watchers": total_watchers,
                    "languages": languages,
                    "active_repos": len(recent_repos),
                    "top_repos": [
                        {
                            "name": r["name"],
                            "stars": r["stargazers_count"],
                            "description": r.get("description"),
                            "language": r.get("language")
                        }
                        for r in sorted(repos, key=lambda x: x["stargazers_count"], reverse=True)[:5]
                    ]
                }
            
            return {}
            
        except Exception:
            return {}
    
    async def _get_contributor_stats(self, client: httpx.AsyncClient, org_name: str) -> Dict:
        """Get contributor statistics (limited by API)"""
        try:
            # Get members (public members only without auth)
            response = await client.get(
                f"{self.BASE_URL}/orgs/{org_name}/members",
                headers=self.headers
            )
            
            if response.status_code == 200:
                members = response.json()
                
                return {
                    "public_members": len(members),
                    "estimated_contributors": len(members) * 3  # Rough estimate
                }
            
            return {"public_members": 0, "estimated_contributors": 0}
            
        except Exception:
            return {"public_members": 0, "estimated_contributors": 0}
    
    def _is_recently_active(self, pushed_at: str) -> bool:
        """Check if repository was recently active"""
        if not pushed_at:
            return False
        
        pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        return (datetime.now(pushed_date.tzinfo) - pushed_date).days < 90
    
    def _calculate_growth_metrics(self, repo_stats: Dict, contributor_stats: Dict) -> Dict:
        """Calculate growth indicators from GitHub data"""
        return {
            "activity_score": min(100, repo_stats.get("active_repos", 0) * 10),
            "popularity_score": min(100, int(repo_stats.get("total_stars", 0) / 100)),
            "community_score": min(100, contributor_stats.get("estimated_contributors", 0)),
            "tech_diversity": len(repo_stats.get("languages", {}))
        }
    
    def _analyze_tech_stack(self, repo_stats: Dict) -> List[str]:
        """Analyze primary technologies used"""
        languages = repo_stats.get("languages", {})
        # Sort by usage and return top languages
        return sorted(languages.keys(), key=lambda x: languages[x], reverse=True)[:5]
    
    def _assess_data_quality(self, org_data: Dict, repo_stats: Dict) -> Dict:
        """Assess quality of GitHub data"""
        if not org_data or repo_stats.get("total_repos", 0) == 0:
            return {"score": 0, "status": "no_data"}
        
        if repo_stats.get("total_repos", 0) < 5:
            return {"score": 0.3, "status": "minimal_presence"}
        elif repo_stats.get("active_repos", 0) > 5:
            return {"score": 1.0, "status": "strong_presence"}
        else:
            return {"score": 0.7, "status": "moderate_presence"}

# Export singleton instance
github_api = GitHubAPI()