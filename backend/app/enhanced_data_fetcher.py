"""
Enhanced data fetcher for comprehensive company intelligence
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class EnhancedCompanyIntelligence:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    
    async def get_comprehensive_intelligence(self, company_name: str, domain: Optional[str] = None) -> Dict:
        """Gather comprehensive intelligence from all available sources"""
        
        # Run all intelligence gathering in parallel
        tasks = [
            self.get_product_details(company_name, domain),
            self.get_customer_intelligence(company_name, domain),
            self.get_linkedin_intelligence(company_name),
            self.get_twitter_presence(company_name),
            self.get_producthunt_data(company_name),
            self.get_g2_reviews(company_name),
            self.get_app_store_presence(company_name),
            self.get_revenue_indicators(company_name, domain),
            self.get_team_size_indicators(company_name, domain)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine all intelligence
        intelligence = {
            "product": results[0] if not isinstance(results[0], Exception) else {},
            "customers": results[1] if not isinstance(results[1], Exception) else {},
            "linkedin": results[2] if not isinstance(results[2], Exception) else {},
            "twitter": results[3] if not isinstance(results[3], Exception) else {},
            "producthunt": results[4] if not isinstance(results[4], Exception) else {},
            "g2_reviews": results[5] if not isinstance(results[5], Exception) else {},
            "app_presence": results[6] if not isinstance(results[6], Exception) else {},
            "revenue_indicators": results[7] if not isinstance(results[7], Exception) else {},
            "team_indicators": results[8] if not isinstance(results[8], Exception) else {}
        }
        
        # Generate executive summary
        intelligence["executive_summary"] = self._generate_executive_summary(intelligence)
        
        return intelligence
    
    async def get_product_details(self, company_name: str, domain: Optional[str]) -> Dict:
        """Extract detailed product information from website"""
        if not domain:
            return {"found": False}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", headers=self.headers, follow_redirects=True, timeout=10.0)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract product features
                    features = []
                    feature_keywords = ['features', 'benefits', 'capabilities', 'solutions']
                    
                    for keyword in feature_keywords:
                        # Look for sections with feature keywords
                        feature_sections = soup.find_all(['div', 'section'], class_=re.compile(f'.*{keyword}.*', re.I))
                        feature_sections.extend(soup.find_all(['div', 'section'], id=re.compile(f'.*{keyword}.*', re.I)))
                        
                        for section in feature_sections[:2]:  # Limit to avoid too much content
                            items = section.find_all(['li', 'h3', 'h4'])
                            features.extend([item.get_text(strip=True)[:100] for item in items[:10]])
                    
                    # Look for pricing information
                    pricing_info = None
                    pricing_elements = soup.find_all(text=re.compile(r'(\$\d+|€\d+|£\d+|/month|/year|/user|pricing)', re.I))
                    if pricing_elements:
                        pricing_info = [elem.strip()[:100] for elem in pricing_elements[:5]]
                    
                    # Extract product description from meta or first paragraph
                    product_desc = None
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc:
                        product_desc = meta_desc.get('content')
                    else:
                        # Try first substantive paragraph
                        paragraphs = soup.find_all('p')
                        for p in paragraphs[:10]:
                            text = p.get_text(strip=True)
                            if len(text) > 50 and company_name.lower() in text.lower():
                                product_desc = text[:300]
                                break
                    
                    # Look for use cases
                    use_cases = []
                    use_case_keywords = ['use cases', 'customers use', 'built for', 'designed for', 'helps you']
                    for keyword in use_case_keywords:
                        elements = soup.find_all(text=re.compile(keyword, re.I))
                        for elem in elements[:3]:
                            parent = elem.parent
                            if parent:
                                use_cases.append(parent.get_text(strip=True)[:200])
                    
                    # Look for integrations
                    integrations = []
                    integration_keywords = ['integrat', 'connect', 'works with', 'compatible']
                    for keyword in integration_keywords:
                        int_sections = soup.find_all(['div', 'section'], text=re.compile(keyword, re.I))
                        for section in int_sections[:2]:
                            # Look for logos or integration names
                            imgs = section.find_all('img', alt=True)
                            integrations.extend([img['alt'] for img in imgs[:10] if img['alt']])
                    
                    return {
                        "found": True,
                        "description": product_desc,
                        "features": list(set(features))[:15],  # Dedupe and limit
                        "pricing": pricing_info,
                        "use_cases": use_cases[:5],
                        "integrations": list(set(integrations))[:10],
                        "has_free_tier": any('free' in str(p).lower() for p in (pricing_info or [])),
                        "has_enterprise": any('enterprise' in response.text.lower() for _ in range(1))
                    }
                    
        except Exception as e:
            pass
        
        return {"found": False}
    
    async def get_customer_intelligence(self, company_name: str, domain: Optional[str]) -> Dict:
        """Extract customer information and testimonials"""
        if not domain:
            return {"found": False}
        
        try:
            async with httpx.AsyncClient() as client:
                # Check main site
                response = await client.get(f"https://{domain}", headers=self.headers, follow_redirects=True, timeout=10.0)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for customer logos
                    customer_logos = []
                    logo_sections = soup.find_all(['div', 'section'], class_=re.compile('.*(customer|client|logo|partner|trusted).*', re.I))
                    for section in logo_sections[:3]:
                        imgs = section.find_all('img', alt=True)
                        customer_logos.extend([img['alt'] for img in imgs if img['alt'] and len(img['alt']) > 2])
                    
                    # Look for customer numbers
                    customer_claims = []
                    # Pattern for "X customers", "X users", "X companies", etc.
                    number_patterns = [
                        r'(\d{1,3}(?:,\d{3})*|\d+[KMB]?)\+?\s*(?:customers|users|companies|organizations|teams|developers)',
                        r'(?:serves?|trusted by|used by|powers?)\s*(\d{1,3}(?:,\d{3})*|\d+[KMB]?)\+?',
                        r'(\d{1,3}(?:,\d{3})*|\d+[KMB]?)\+?\s*(?:active|monthly|daily)'
                    ]
                    
                    for pattern in number_patterns:
                        matches = soup.find_all(text=re.compile(pattern, re.I))
                        for match in matches[:3]:
                            customer_claims.append(match.strip()[:100])
                    
                    # Look for case studies
                    case_studies = []
                    case_study_links = soup.find_all('a', href=re.compile('case.stud|customer.stor|success.stor', re.I))
                    for link in case_study_links[:5]:
                        case_studies.append({
                            "title": link.get_text(strip=True),
                            "url": urljoin(f"https://{domain}", link.get('href'))
                        })
                    
                    # Look for testimonials
                    testimonials = []
                    testimonial_sections = soup.find_all(['div', 'blockquote'], class_=re.compile('.*(testimonial|quote|review).*', re.I))
                    for section in testimonial_sections[:5]:
                        text = section.get_text(strip=True)
                        if len(text) > 50 and len(text) < 500:
                            # Try to find author
                            author = None
                            author_elem = section.find(['cite', 'footer', 'p'], class_=re.compile('.*(author|name|title).*', re.I))
                            if author_elem:
                                author = author_elem.get_text(strip=True)
                            testimonials.append({
                                "text": text[:300],
                                "author": author
                            })
                    
                    # Try to find /customers or /case-studies page
                    customer_page_data = await self._fetch_customer_page(domain, client)
                    if customer_page_data:
                        customer_logos.extend(customer_page_data.get("logos", []))
                        customer_claims.extend(customer_page_data.get("claims", []))
                    
                    return {
                        "found": True,
                        "customer_logos": list(set(customer_logos))[:20],
                        "customer_claims": customer_claims[:5],
                        "case_studies": case_studies,
                        "testimonials": testimonials,
                        "estimated_customers": self._estimate_customer_count(customer_claims),
                        "customer_segments": self._identify_customer_segments(customer_logos + [t.get("author", "") for t in testimonials])
                    }
                    
        except Exception as e:
            pass
        
        return {"found": False}
    
    async def _fetch_customer_page(self, domain: str, client: httpx.AsyncClient) -> Optional[Dict]:
        """Try to fetch dedicated customer page"""
        customer_urls = [
            f"https://{domain}/customers",
            f"https://{domain}/case-studies",
            f"https://{domain}/success-stories",
            f"https://{domain}/clients"
        ]
        
        for url in customer_urls:
            try:
                response = await client.get(url, headers=self.headers, timeout=5.0)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    logos = []
                    imgs = soup.find_all('img', alt=True)
                    logos = [img['alt'] for img in imgs if img['alt'] and 'logo' not in img['alt'].lower()]
                    
                    claims = []
                    for text in soup.find_all(text=re.compile(r'\d+\+?\s*(?:customers|users|companies)', re.I)):
                        claims.append(text.strip()[:100])
                    
                    return {"logos": logos, "claims": claims}
            except:
                continue
        
        return None
    
    async def get_linkedin_intelligence(self, company_name: str) -> Dict:
        """Get LinkedIn presence indicators"""
        try:
            async with httpx.AsyncClient() as client:
                # Search for company on LinkedIn (this is limited without auth)
                search_url = f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}"
                response = await client.get(search_url, headers=self.headers, follow_redirects=True, timeout=10.0)
                
                if response.status_code == 200:
                    # Extract what we can from public page
                    text = response.text
                    
                    # Look for employee count in page
                    employee_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*employees', text, re.I)
                    employees = employee_match.group(1) if employee_match else None
                    
                    # Look for tagline
                    tagline_match = re.search(r'"tagline":"([^"]+)"', text)
                    tagline = tagline_match.group(1) if tagline_match else None
                    
                    return {
                        "found": True,
                        "employees": employees,
                        "tagline": tagline,
                        "url": search_url
                    }
                    
        except Exception as e:
            pass
        
        return {"found": False}
    
    async def get_twitter_presence(self, company_name: str) -> Dict:
        """Get Twitter/X presence and engagement metrics"""
        try:
            # Twitter is harder to scrape now, but we can check if account exists
            handle_variations = [
                company_name.lower().replace(" ", ""),
                company_name.lower().replace(" ", "_"),
                company_name.lower().split()[0]  # First word only
            ]
            
            async with httpx.AsyncClient() as client:
                for handle in handle_variations:
                    response = await client.get(
                        f"https://twitter.com/{handle}", 
                        headers=self.headers,
                        follow_redirects=False,
                        timeout=5.0
                    )
                    
                    if response.status_code in [200, 302]:  # Found
                        return {
                            "found": True,
                            "handle": f"@{handle}",
                            "url": f"https://twitter.com/{handle}"
                        }
        except:
            pass
        
        return {"found": False}
    
    async def get_producthunt_data(self, company_name: str) -> Dict:
        """Check ProductHunt presence"""
        try:
            async with httpx.AsyncClient() as client:
                search_response = await client.get(
                    f"https://www.producthunt.com/search?q={company_name}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if search_response.status_code == 200 and company_name.lower() in search_response.text.lower():
                    # Extract what we can from search results
                    soup = BeautifulSoup(search_response.text, 'html.parser')
                    
                    # Look for vote counts
                    votes = []
                    vote_elements = soup.find_all(text=re.compile(r'\d+\s*upvotes?', re.I))
                    for elem in vote_elements[:3]:
                        votes.append(elem.strip())
                    
                    return {
                        "found": True,
                        "presence": True,
                        "votes": votes
                    }
                    
        except Exception as e:
            pass
        
        return {"found": False}
    
    async def get_g2_reviews(self, company_name: str) -> Dict:
        """Check G2 Crowd presence for B2B SaaS"""
        try:
            async with httpx.AsyncClient() as client:
                # Try direct company URL
                company_slug = company_name.lower().replace(" ", "-")
                response = await client.get(
                    f"https://www.g2.com/products/{company_slug}/{company_slug}",
                    headers=self.headers,
                    follow_redirects=True,
                    timeout=10.0
                )
                
                if response.status_code == 200 and company_name.lower() in response.text.lower():
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for ratings
                    rating_match = re.search(r'(\d\.\d)\s*(?:out of 5|/5)', response.text)
                    rating = rating_match.group(1) if rating_match else None
                    
                    # Look for review count
                    review_match = re.search(r'(\d+)\s*reviews?', response.text, re.I)
                    reviews = review_match.group(1) if review_match else None
                    
                    return {
                        "found": True,
                        "rating": rating,
                        "review_count": reviews,
                        "url": response.url
                    }
                    
        except Exception as e:
            pass
        
        return {"found": False}
    
    async def get_app_store_presence(self, company_name: str) -> Dict:
        """Check for mobile app presence"""
        results = {"ios": False, "android": False}
        
        try:
            async with httpx.AsyncClient() as client:
                # Check iOS App Store
                ios_search = await client.get(
                    f"https://apps.apple.com/search?term={company_name}",
                    headers=self.headers,
                    timeout=5.0
                )
                if ios_search.status_code == 200 and company_name.lower() in ios_search.text.lower():
                    results["ios"] = True
                
                # Check Google Play Store (limited without API)
                play_search = await client.get(
                    f"https://play.google.com/store/search?q={company_name}&c=apps",
                    headers=self.headers,
                    timeout=5.0
                )
                if play_search.status_code == 200 and company_name.lower() in play_search.text.lower():
                    results["android"] = True
                    
        except:
            pass
        
        return results
    
    async def get_revenue_indicators(self, company_name: str, domain: Optional[str]) -> Dict:
        """Extract revenue and business model indicators"""
        indicators = {
            "business_model": None,
            "revenue_range": None,
            "funding_stage": None,
            "pricing_model": None
        }
        
        if not domain:
            return indicators
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}/pricing", headers=self.headers, timeout=5.0)
                if response.status_code != 200:
                    response = await client.get(f"https://{domain}", headers=self.headers, timeout=5.0)
                
                if response.status_code == 200:
                    text = response.text.lower()
                    
                    # Identify business model
                    if "saas" in text or "software as a service" in text:
                        indicators["business_model"] = "SaaS"
                    elif "marketplace" in text:
                        indicators["business_model"] = "Marketplace"
                    elif "platform" in text:
                        indicators["business_model"] = "Platform"
                    elif "api" in text and ("developer" in text or "integration" in text):
                        indicators["business_model"] = "API/Developer Tools"
                    
                    # Pricing model
                    if "freemium" in text or ("free" in text and "paid" in text):
                        indicators["pricing_model"] = "Freemium"
                    elif "subscription" in text or "/month" in text:
                        indicators["pricing_model"] = "Subscription"
                    elif "pay as you go" in text or "usage based" in text:
                        indicators["pricing_model"] = "Usage-based"
                    elif "enterprise" in text and "contact" in text:
                        indicators["pricing_model"] = "Enterprise"
                    
                    # Look for funding indicators
                    funding_matches = re.findall(r'series [a-e]|seed|pre-seed|\$\d+[MB]', text)
                    if funding_matches:
                        indicators["funding_stage"] = funding_matches[-1]  # Latest mention
                    
        except:
            pass
        
        return indicators
    
    async def get_team_size_indicators(self, company_name: str, domain: Optional[str]) -> Dict:
        """Estimate team size from various indicators"""
        indicators = {
            "github_contributors": 0,
            "linkedin_employees": None,
            "website_team_page": 0,
            "job_openings": 0,
            "estimated_size": None
        }
        
        try:
            if domain:
                async with httpx.AsyncClient() as client:
                    # Check team/about page
                    for path in ["/team", "/about", "/about-us", "/company"]:
                        try:
                            response = await client.get(f"https://{domain}{path}", headers=self.headers, timeout=5.0)
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.text, 'html.parser')
                                # Count team member sections
                                team_cards = soup.find_all(['div', 'article'], class_=re.compile('.*(team|member|person|staff).*', re.I))
                                if team_cards:
                                    indicators["website_team_page"] = len(team_cards)
                                break
                        except:
                            continue
                    
                    # Check careers page
                    for path in ["/careers", "/jobs", "/join", "/work-with-us"]:
                        try:
                            response = await client.get(f"https://{domain}{path}", headers=self.headers, timeout=5.0)
                            if response.status_code == 200:
                                # Count job listings
                                job_matches = re.findall(r'(?:position|role|opening|job)', response.text, re.I)
                                indicators["job_openings"] = min(len(job_matches), 50)  # Cap at 50
                                break
                        except:
                            continue
            
            # Estimate company size
            data_points = []
            if indicators["website_team_page"] > 0:
                data_points.append(indicators["website_team_page"] * 1.5)  # Usually shows partial team
            if indicators["job_openings"] > 0:
                data_points.append(indicators["job_openings"] * 10)  # Rough multiplier
            
            if data_points:
                avg_estimate = sum(data_points) / len(data_points)
                if avg_estimate < 10:
                    indicators["estimated_size"] = "1-10 (Seed)"
                elif avg_estimate < 50:
                    indicators["estimated_size"] = "11-50 (Series A)"
                elif avg_estimate < 200:
                    indicators["estimated_size"] = "51-200 (Series B)"
                elif avg_estimate < 500:
                    indicators["estimated_size"] = "201-500 (Series C)"
                else:
                    indicators["estimated_size"] = "500+ (Late Stage)"
                    
        except:
            pass
        
        return indicators
    
    def _estimate_customer_count(self, claims: List[str]) -> Optional[str]:
        """Extract and normalize customer count claims"""
        if not claims:
            return None
        
        numbers = []
        for claim in claims:
            # Extract numbers
            matches = re.findall(r'(\d{1,3}(?:,\d{3})*|\d+)([KMB]?)', claim)
            for match in matches:
                num_str, suffix = match
                num = int(num_str.replace(',', ''))
                
                # Convert K/M/B
                if suffix.upper() == 'K':
                    num *= 1000
                elif suffix.upper() == 'M':
                    num *= 1000000
                elif suffix.upper() == 'B':
                    num *= 1000000000
                
                numbers.append(num)
        
        if numbers:
            max_claim = max(numbers)
            if max_claim >= 1000000:
                return f"{max_claim/1000000:.1f}M+"
            elif max_claim >= 1000:
                return f"{max_claim/1000:.0f}K+"
            else:
                return f"{max_claim}+"
        
        return None
    
    def _identify_customer_segments(self, customer_data: List[str]) -> List[str]:
        """Identify customer segments from logos and testimonials"""
        segments = set()
        
        enterprise_keywords = ['fortune', '500', 'global', 'international', 'worldwide']
        startup_keywords = ['startup', 'ventures', 'labs', 'stealth']
        smb_keywords = ['small business', 'smb', 'local', 'agency']
        tech_keywords = ['tech', 'software', 'saas', 'cloud', 'digital']
        finance_keywords = ['bank', 'financial', 'fintech', 'insurance', 'capital']
        healthcare_keywords = ['health', 'medical', 'pharma', 'bio', 'care']
        
        combined_text = ' '.join(customer_data).lower()
        
        if any(kw in combined_text for kw in enterprise_keywords):
            segments.add("Enterprise")
        if any(kw in combined_text for kw in startup_keywords):
            segments.add("Startups")
        if any(kw in combined_text for kw in smb_keywords):
            segments.add("SMB")
        if any(kw in combined_text for kw in tech_keywords):
            segments.add("Technology")
        if any(kw in combined_text for kw in finance_keywords):
            segments.add("Financial Services")
        if any(kw in combined_text for kw in healthcare_keywords):
            segments.add("Healthcare")
        
        return list(segments)
    
    def _generate_executive_summary(self, intelligence: Dict) -> Dict:
        """Generate executive summary from all intelligence"""
        summary = {
            "product_summary": None,
            "customer_summary": None,
            "market_position": None,
            "key_metrics": [],
            "strengths": [],
            "concerns": []
        }
        
        # Product summary
        if intelligence.get("product", {}).get("found"):
            product = intelligence["product"]
            features_count = len(product.get("features", []))
            summary["product_summary"] = f"Offers {features_count} key features" 
            if product.get("has_free_tier"):
                summary["product_summary"] += " with a free tier"
            if product.get("has_enterprise"):
                summary["product_summary"] += " and enterprise solution"
        
        # Customer summary  
        if intelligence.get("customers", {}).get("found"):
            customers = intelligence["customers"]
            if customers.get("estimated_customers"):
                summary["customer_summary"] = f"Serves {customers['estimated_customers']} customers"
                if customers.get("customer_segments"):
                    summary["customer_summary"] += f" across {', '.join(customers['customer_segments'][:3])}"
        
        # Market position
        signals = []
        if intelligence.get("g2_reviews", {}).get("found"):
            g2 = intelligence["g2_reviews"]
            if g2.get("rating"):
                signals.append(f"G2 rating: {g2['rating']}/5")
        
        if intelligence.get("producthunt", {}).get("found"):
            signals.append("Featured on ProductHunt")
        
        if signals:
            summary["market_position"] = "Established market presence - " + ", ".join(signals)
        
        # Key metrics
        if intelligence.get("linkedin", {}).get("employees"):
            summary["key_metrics"].append(f"Employees: {intelligence['linkedin']['employees']}")
        
        if intelligence.get("revenue_indicators", {}).get("funding_stage"):
            summary["key_metrics"].append(f"Funding: {intelligence['revenue_indicators']['funding_stage']}")
        
        # Strengths
        if intelligence.get("customers", {}).get("customer_logos"):
            logo_count = len(intelligence["customers"]["customer_logos"])
            if logo_count > 10:
                summary["strengths"].append(f"Strong customer base with {logo_count}+ named customers")
        
        if intelligence.get("product", {}).get("integrations"):
            int_count = len(intelligence["product"]["integrations"])
            if int_count > 5:
                summary["strengths"].append(f"Robust ecosystem with {int_count}+ integrations")
        
        if intelligence.get("app_presence", {}).get("ios") or intelligence.get("app_presence", {}).get("android"):
            summary["strengths"].append("Multi-platform with mobile apps")
        
        # Concerns
        if not intelligence.get("g2_reviews", {}).get("found") and not intelligence.get("producthunt", {}).get("found"):
            summary["concerns"].append("Limited third-party validation")
        
        if not intelligence.get("customers", {}).get("testimonials"):
            summary["concerns"].append("No public customer testimonials found")
        
        return summary

# Singleton instance
enhanced_intel = EnhancedCompanyIntelligence()