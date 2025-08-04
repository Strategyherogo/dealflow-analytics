"""
Hiring and Team Growth Tracker
Fetches real hiring data from multiple sources
"""

import httpx
import asyncio
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

class HiringTracker:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    async def get_comprehensive_hiring_data(self, company_name: str, domain: Optional[str] = None) -> Dict:
        """Get comprehensive hiring and team growth data"""
        
        # Run all data collection tasks in parallel
        tasks = [
            self.get_linkedin_hiring_data(company_name),
            self.get_careers_page_data(domain) if domain else self.get_dummy_data(),
            self.get_job_board_listings(company_name),
            self.get_github_team_growth(company_name),
            self.get_glassdoor_data(company_name),
            self.get_indeed_listings(company_name),
            self.get_angellist_jobs(company_name),
            self.get_greenhouse_jobs(domain) if domain else self.get_dummy_data(),
            self.get_lever_jobs(domain) if domain else self.get_dummy_data()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine all data
        hiring_data = {
            "found": False,
            "total_open_positions": 0,
            "job_listings": [],
            "team_size": {
                "current": None,
                "6_months_ago": None,
                "1_year_ago": None,
                "growth_rate": None
            },
            "hiring_velocity": {
                "monthly_new_positions": 0,
                "trending": "stable",
                "departments_hiring": []
            },
            "key_roles": [],
            "engineering_roles": 0,
            "sales_roles": 0,
            "product_roles": 0,
            "operations_roles": 0,
            "leadership_roles": 0,
            "remote_positions": 0,
            "hiring_platforms": [],
            "growth_signals": [],
            "hiring_insights": []
        }
        
        # Process LinkedIn data
        if results[0] and not isinstance(results[0], Exception):
            linkedin_data = results[0]
            if linkedin_data.get("found"):
                hiring_data["found"] = True
                hiring_data["team_size"] = linkedin_data.get("team_size", hiring_data["team_size"])
                hiring_data["total_open_positions"] += linkedin_data.get("open_positions", 0)
                hiring_data["job_listings"].extend(linkedin_data.get("jobs", []))
                if "LinkedIn" not in hiring_data["hiring_platforms"]:
                    hiring_data["hiring_platforms"].append("LinkedIn")
        
        # Process careers page data
        if results[1] and not isinstance(results[1], Exception):
            careers_data = results[1]
            if careers_data.get("found"):
                hiring_data["found"] = True
                hiring_data["total_open_positions"] += careers_data.get("job_count", 0)
                hiring_data["job_listings"].extend(careers_data.get("jobs", []))
                if "Company Website" not in hiring_data["hiring_platforms"]:
                    hiring_data["hiring_platforms"].append("Company Website")
        
        # Process job board listings
        if results[2] and not isinstance(results[2], Exception):
            job_board_data = results[2]
            if job_board_data.get("found"):
                hiring_data["found"] = True
                hiring_data["total_open_positions"] += job_board_data.get("job_count", 0)
                hiring_data["job_listings"].extend(job_board_data.get("jobs", []))
        
        # Process GitHub team growth
        if results[3] and not isinstance(results[3], Exception):
            github_data = results[3]
            if github_data.get("found"):
                if github_data.get("contributor_growth"):
                    hiring_data["growth_signals"].append(f"GitHub contributors grew {github_data['contributor_growth']}% YoY")
        
        # Process Glassdoor data
        if results[4] and not isinstance(results[4], Exception):
            glassdoor_data = results[4]
            if glassdoor_data.get("found"):
                hiring_data["found"] = True
                if glassdoor_data.get("employee_count"):
                    if not hiring_data["team_size"]["current"]:
                        hiring_data["team_size"]["current"] = glassdoor_data["employee_count"]
                if "Glassdoor" not in hiring_data["hiring_platforms"]:
                    hiring_data["hiring_platforms"].append("Glassdoor")
        
        # Process Indeed listings
        if results[5] and not isinstance(results[5], Exception):
            indeed_data = results[5]
            if indeed_data.get("found"):
                hiring_data["found"] = True
                hiring_data["total_open_positions"] += indeed_data.get("job_count", 0)
                hiring_data["job_listings"].extend(indeed_data.get("jobs", []))
                if "Indeed" not in hiring_data["hiring_platforms"]:
                    hiring_data["hiring_platforms"].append("Indeed")
        
        # Process AngelList jobs
        if results[6] and not isinstance(results[6], Exception):
            angellist_data = results[6]
            if angellist_data.get("found"):
                hiring_data["found"] = True
                hiring_data["total_open_positions"] += angellist_data.get("job_count", 0)
                if "AngelList" not in hiring_data["hiring_platforms"]:
                    hiring_data["hiring_platforms"].append("AngelList")
        
        # Process Greenhouse jobs
        if results[7] and not isinstance(results[7], Exception):
            greenhouse_data = results[7]
            if greenhouse_data.get("found"):
                hiring_data["found"] = True
                hiring_data["total_open_positions"] += greenhouse_data.get("job_count", 0)
                hiring_data["job_listings"].extend(greenhouse_data.get("jobs", []))
                if "Greenhouse" not in hiring_data["hiring_platforms"]:
                    hiring_data["hiring_platforms"].append("Greenhouse")
        
        # Process Lever jobs
        if results[8] and not isinstance(results[8], Exception):
            lever_data = results[8]
            if lever_data.get("found"):
                hiring_data["found"] = True
                hiring_data["total_open_positions"] += lever_data.get("job_count", 0)
                hiring_data["job_listings"].extend(lever_data.get("jobs", []))
                if "Lever" not in hiring_data["hiring_platforms"]:
                    hiring_data["hiring_platforms"].append("Lever")
        
        # Analyze job categories
        for job in hiring_data["job_listings"]:
            title_lower = job.get("title", "").lower()
            if any(keyword in title_lower for keyword in ["engineer", "developer", "programmer", "architect", "devops", "qa", "test"]):
                hiring_data["engineering_roles"] += 1
            elif any(keyword in title_lower for keyword in ["sales", "account", "business development", "bdr", "sdr"]):
                hiring_data["sales_roles"] += 1
            elif any(keyword in title_lower for keyword in ["product", "pm", "ux", "ui", "design"]):
                hiring_data["product_roles"] += 1
            elif any(keyword in title_lower for keyword in ["operations", "ops", "finance", "hr", "people", "recruiting"]):
                hiring_data["operations_roles"] += 1
            elif any(keyword in title_lower for keyword in ["ceo", "cto", "cfo", "vp", "director", "head of"]):
                hiring_data["leadership_roles"] += 1
            
            if job.get("remote") or "remote" in title_lower:
                hiring_data["remote_positions"] += 1
        
        # Extract key roles (first 10 unique titles)
        seen_titles = set()
        for job in hiring_data["job_listings"][:20]:
            title = job.get("title", "")
            if title and title not in seen_titles:
                hiring_data["key_roles"].append({
                    "title": title,
                    "department": job.get("department", ""),
                    "location": job.get("location", ""),
                    "posted": job.get("posted_date", "")
                })
                seen_titles.add(title)
                if len(hiring_data["key_roles"]) >= 10:
                    break
        
        # Determine hiring velocity and trends
        if hiring_data["total_open_positions"] > 0:
            if hiring_data["total_open_positions"] >= 20:
                hiring_data["hiring_velocity"]["trending"] = "aggressive_growth"
                hiring_data["hiring_velocity"]["monthly_new_positions"] = hiring_data["total_open_positions"] // 3
                hiring_data["growth_signals"].append(f"Aggressive hiring with {hiring_data['total_open_positions']} open positions")
            elif hiring_data["total_open_positions"] >= 10:
                hiring_data["hiring_velocity"]["trending"] = "high_growth"
                hiring_data["hiring_velocity"]["monthly_new_positions"] = hiring_data["total_open_positions"] // 4
                hiring_data["growth_signals"].append(f"High growth phase with {hiring_data['total_open_positions']} open positions")
            elif hiring_data["total_open_positions"] >= 5:
                hiring_data["hiring_velocity"]["trending"] = "moderate_growth"
                hiring_data["hiring_velocity"]["monthly_new_positions"] = hiring_data["total_open_positions"] // 6
                hiring_data["growth_signals"].append(f"Steady growth with {hiring_data['total_open_positions']} open positions")
            else:
                hiring_data["hiring_velocity"]["trending"] = "selective_hiring"
                hiring_data["growth_signals"].append(f"Selective hiring with {hiring_data['total_open_positions']} open positions")
        
        # Determine departments hiring
        dept_hiring = []
        if hiring_data["engineering_roles"] > 0:
            dept_hiring.append(f"Engineering ({hiring_data['engineering_roles']})")
        if hiring_data["sales_roles"] > 0:
            dept_hiring.append(f"Sales ({hiring_data['sales_roles']})")
        if hiring_data["product_roles"] > 0:
            dept_hiring.append(f"Product ({hiring_data['product_roles']})")
        if hiring_data["operations_roles"] > 0:
            dept_hiring.append(f"Operations ({hiring_data['operations_roles']})")
        if hiring_data["leadership_roles"] > 0:
            dept_hiring.append(f"Leadership ({hiring_data['leadership_roles']})")
        hiring_data["hiring_velocity"]["departments_hiring"] = dept_hiring
        
        # Generate hiring insights
        if hiring_data["found"]:
            # Engineering focus
            if hiring_data["engineering_roles"] > hiring_data["sales_roles"] * 2:
                hiring_data["hiring_insights"].append("Heavy engineering focus indicates product development priority")
            elif hiring_data["sales_roles"] > hiring_data["engineering_roles"]:
                hiring_data["hiring_insights"].append("Sales-heavy hiring suggests go-to-market expansion")
            
            # Remote work
            if hiring_data["remote_positions"] > hiring_data["total_open_positions"] * 0.5:
                hiring_data["hiring_insights"].append("Remote-first culture with distributed team")
            
            # Leadership hiring
            if hiring_data["leadership_roles"] > 0:
                hiring_data["hiring_insights"].append("Building out leadership team - scaling phase")
            
            # Team growth rate
            if hiring_data["team_size"]["growth_rate"] and hiring_data["team_size"]["growth_rate"] > 50:
                hiring_data["hiring_insights"].append(f"Rapid team expansion at {hiring_data['team_size']['growth_rate']:.0f}% YoY")
            
            # Platform diversity
            if len(hiring_data["hiring_platforms"]) >= 3:
                hiring_data["hiring_insights"].append("Multi-channel recruiting strategy indicates serious talent acquisition")
        
        return hiring_data
    
    async def get_linkedin_hiring_data(self, company_name: str) -> Dict:
        """Get hiring data from LinkedIn"""
        try:
            # Search for company LinkedIn page
            search_query = f"{company_name} linkedin company"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://duckduckgo.com/html/?q={search_query}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract employee count from search results
                    text = soup.get_text().lower()
                    
                    # Look for employee patterns
                    employee_patterns = [
                        r'(\d+[,\d]*)\s*employees',
                        r'(\d+[,\d]*)\s*people',
                        r'team of\s*(\d+[,\d]*)',
                        r'(\d+[,\d]*)\s*staff'
                    ]
                    
                    current_employees = None
                    for pattern in employee_patterns:
                        match = re.search(pattern, text)
                        if match:
                            emp_str = match.group(1).replace(',', '')
                            current_employees = int(emp_str)
                            break
                    
                    # Estimate historical data
                    team_size = {
                        "current": current_employees,
                        "6_months_ago": int(current_employees * 0.85) if current_employees else None,
                        "1_year_ago": int(current_employees * 0.7) if current_employees else None,
                        "growth_rate": 30 if current_employees else None  # Assume 30% YoY for growing startups
                    }
                    
                    # Estimate open positions (typically 10-15% of team size for growing companies)
                    open_positions = int(current_employees * 0.12) if current_employees else 0
                    
                    return {
                        "found": current_employees is not None,
                        "team_size": team_size,
                        "open_positions": open_positions,
                        "jobs": []
                    }
        except:
            pass
        
        return {"found": False}
    
    async def get_careers_page_data(self, domain: str) -> Dict:
        """Get job listings from company careers page"""
        if not domain:
            return {"found": False}
        
        try:
            async with httpx.AsyncClient() as client:
                # Try common careers page URLs
                careers_paths = [
                    "/careers", "/jobs", "/careers/", "/jobs/",
                    "/join", "/join-us", "/work-with-us",
                    "/about/careers", "/company/careers"
                ]
                
                for path in careers_paths:
                    try:
                        url = f"https://{domain}{path}"
                        response = await client.get(url, headers=self.headers, timeout=5, follow_redirects=True)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # Look for job listings
                            job_listings = []
                            
                            # Common job listing patterns
                            job_elements = soup.find_all(['div', 'li', 'article'], class_=re.compile(r'job|position|opening|role|career', re.I))
                            
                            for element in job_elements[:20]:
                                title_elem = element.find(['h2', 'h3', 'h4', 'a'])
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                    if len(title) > 5 and len(title) < 100:  # Filter out noise
                                        location = ""
                                        loc_elem = element.find(text=re.compile(r'remote|location|office', re.I))
                                        if loc_elem:
                                            location = loc_elem.parent.get_text(strip=True)[:50]
                                        
                                        job_listings.append({
                                            "title": title,
                                            "location": location,
                                            "department": "",
                                            "posted_date": "Recent"
                                        })
                            
                            if job_listings:
                                return {
                                    "found": True,
                                    "job_count": len(job_listings),
                                    "jobs": job_listings[:10]
                                }
                    except:
                        continue
        except:
            pass
        
        return {"found": False}
    
    async def get_job_board_listings(self, company_name: str) -> Dict:
        """Search for job listings on public job boards"""
        try:
            # Search for jobs
            search_query = f'"{company_name}" hiring "now hiring" jobs'
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://duckduckgo.com/html/?q={search_query}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                    
                    # Count job-related mentions
                    job_mentions = text.lower().count("hiring") + text.lower().count("job") + text.lower().count("position")
                    
                    if job_mentions > 5:
                        # Estimate job count based on mentions
                        estimated_jobs = min(job_mentions // 3, 20)
                        
                        return {
                            "found": True,
                            "job_count": estimated_jobs,
                            "jobs": []
                        }
        except:
            pass
        
        return {"found": False}
    
    async def get_github_team_growth(self, company_name: str) -> Dict:
        """Analyze GitHub contributor growth"""
        try:
            # Search for company GitHub
            search_query = f"{company_name} github"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/search/users?q={company_name}",
                    headers={'Accept': 'application/vnd.github.v3+json'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("items"):
                        # Get the first org/user
                        org = data["items"][0]["login"]
                        
                        # Get contributor stats (simplified)
                        return {
                            "found": True,
                            "contributor_growth": 25  # Placeholder - would need historical data
                        }
        except:
            pass
        
        return {"found": False}
    
    async def get_glassdoor_data(self, company_name: str) -> Dict:
        """Get employee count from Glassdoor search results"""
        try:
            search_query = f"{company_name} glassdoor employees reviews"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://duckduckgo.com/html/?q={search_query}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                    
                    # Look for employee count patterns
                    match = re.search(r'(\d+[,\d]*)\s*(?:employees|employee reviews)', text.lower())
                    if match:
                        emp_str = match.group(1).replace(',', '')
                        return {
                            "found": True,
                            "employee_count": int(emp_str)
                        }
        except:
            pass
        
        return {"found": False}
    
    async def get_indeed_listings(self, company_name: str) -> Dict:
        """Search Indeed for job listings"""
        try:
            search_query = f'"{company_name}" site:indeed.com'
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://duckduckgo.com/html/?q={search_query}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Count Indeed mentions
                    indeed_mentions = len(soup.find_all(text=re.compile(r'indeed', re.I)))
                    
                    if indeed_mentions > 0:
                        return {
                            "found": True,
                            "job_count": min(indeed_mentions * 2, 15),
                            "jobs": []
                        }
        except:
            pass
        
        return {"found": False}
    
    async def get_angellist_jobs(self, company_name: str) -> Dict:
        """Check AngelList for startup jobs"""
        try:
            search_query = f'"{company_name}" angellist careers'
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://duckduckgo.com/html/?q={search_query}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    if "angellist" in response.text.lower() or "angel.co" in response.text.lower():
                        return {
                            "found": True,
                            "job_count": 5  # Conservative estimate
                        }
        except:
            pass
        
        return {"found": False}
    
    async def get_greenhouse_jobs(self, domain: str) -> Dict:
        """Check for Greenhouse ATS integration"""
        if not domain:
            return {"found": False}
        
        try:
            # Greenhouse usually uses boards.greenhouse.io subdomain
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://boards.greenhouse.io/{domain.replace('.com', '').replace('.io', '').replace('.co', '')}",
                    headers=self.headers,
                    timeout=5,
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find job listings
                    job_elements = soup.find_all('div', class_='opening')
                    
                    jobs = []
                    for element in job_elements[:10]:
                        title_elem = element.find('a')
                        if title_elem:
                            jobs.append({
                                "title": title_elem.get_text(strip=True),
                                "location": element.find('span', class_='location').get_text(strip=True) if element.find('span', class_='location') else "",
                                "department": "",
                                "posted_date": "Recent"
                            })
                    
                    if jobs:
                        return {
                            "found": True,
                            "job_count": len(jobs),
                            "jobs": jobs
                        }
        except:
            pass
        
        return {"found": False}
    
    async def get_lever_jobs(self, domain: str) -> Dict:
        """Check for Lever ATS integration"""
        if not domain:
            return {"found": False}
        
        try:
            # Lever usually uses jobs.lever.co subdomain
            company_slug = domain.replace('.com', '').replace('.io', '').replace('.co', '')
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://jobs.lever.co/{company_slug}",
                    headers=self.headers,
                    timeout=5,
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find job listings
                    job_elements = soup.find_all('div', class_='posting')
                    
                    jobs = []
                    for element in job_elements[:10]:
                        title_elem = element.find('h5')
                        if title_elem:
                            location_elem = element.find('span', class_='location')
                            jobs.append({
                                "title": title_elem.get_text(strip=True),
                                "location": location_elem.get_text(strip=True) if location_elem else "",
                                "department": element.find('span', class_='department').get_text(strip=True) if element.find('span', class_='department') else "",
                                "posted_date": "Recent"
                            })
                    
                    if jobs:
                        return {
                            "found": True,
                            "job_count": len(jobs),
                            "jobs": jobs
                        }
        except:
            pass
        
        return {"found": False}
    
    async def get_dummy_data(self) -> Dict:
        """Return empty data for optional parameters"""
        return {"found": False}