"""
Technical Due Diligence Analyzer
Analyzes technical stack, architecture, security, and engineering practices
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import hashlib
from urllib.parse import urlparse

class TechnicalDueDiligenceAnalyzer:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        # Technology indicators
        self.tech_indicators = {
            "frontend": {
                "react": ["react", "jsx", "_app.js", "React."],
                "vue": ["vue", "v-if", "v-for", "Vue."],
                "angular": ["ng-", "angular", "Angular"],
                "nextjs": ["_next", "next.js", "Next.js"],
                "svelte": ["svelte", "Svelte"]
            },
            "backend": {
                "nodejs": ["express", "node", "npm"],
                "python": ["django", "flask", "fastapi"],
                "ruby": ["rails", "ruby"],
                "java": ["spring", "java"],
                "go": ["golang", "gin"]
            },
            "infrastructure": {
                "aws": ["amazonaws.com", "cloudfront", "s3."],
                "gcp": ["googleapis.com", "google-cloud"],
                "azure": ["azure", "microsoft"],
                "cloudflare": ["cloudflare", "cf-"],
                "vercel": ["vercel", "now.sh"],
                "netlify": ["netlify"]
            },
            "database": {
                "postgresql": ["postgres", "pg_"],
                "mysql": ["mysql"],
                "mongodb": ["mongodb", "mongo"],
                "redis": ["redis"],
                "elasticsearch": ["elastic", "elasticsearch"]
            },
            "monitoring": {
                "datadog": ["datadog", "dd-"],
                "sentry": ["sentry", "raven"],
                "newrelic": ["newrelic", "nr-"],
                "logstash": ["logstash"],
                "prometheus": ["prometheus"]
            }
        }
    
    async def analyze_technical_stack(self, company_name: str, domain: Optional[str], github_data: Optional[Dict] = None) -> Dict:
        """Comprehensive technical due diligence"""
        
        tasks = []
        
        if domain:
            tasks.extend([
                self.analyze_website_tech(domain),
                self.check_security_headers(domain),
                self.analyze_performance_metrics(domain),
                self.check_api_documentation(domain),
                self.analyze_mobile_readiness(domain)
            ])
        
        if github_data and github_data.get("found"):
            tasks.append(self.analyze_github_quality(github_data))
        else:
            tasks.append(asyncio.create_task(asyncio.coroutine(lambda: {"found": False})()))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        tech_analysis = {
            "website_tech": results[0] if domain and not isinstance(results[0], Exception) else {"found": False},
            "security": results[1] if domain and not isinstance(results[1], Exception) else {"found": False},
            "performance": results[2] if domain and not isinstance(results[2], Exception) else {"found": False},
            "api_quality": results[3] if domain and not isinstance(results[3], Exception) else {"found": False},
            "mobile_readiness": results[4] if domain and not isinstance(results[4], Exception) else {"found": False},
            "code_quality": results[5] if not isinstance(results[5], Exception) else {"found": False}
        }
        
        # Generate overall technical score
        tech_analysis["technical_score"] = self._calculate_technical_score(tech_analysis)
        tech_analysis["technical_risks"] = self._identify_technical_risks(tech_analysis)
        tech_analysis["technical_strengths"] = self._identify_technical_strengths(tech_analysis)
        tech_analysis["recommendations"] = self._generate_technical_recommendations(tech_analysis)
        
        return tech_analysis
    
    async def analyze_website_tech(self, domain: str) -> Dict:
        """Analyze website technology stack"""
        tech_stack = {
            "found": False,
            "frontend": [],
            "backend": [],
            "infrastructure": [],
            "analytics": [],
            "cdn": None,
            "ssl": False,
            "http2": False,
            "technologies": []
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{domain}",
                    headers=self.headers,
                    follow_redirects=True,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    tech_stack["found"] = True
                    tech_stack["ssl"] = response.url.scheme == "https"
                    tech_stack["http2"] = response.http_version == "HTTP/2"
                    
                    # Check headers for technology hints
                    headers = dict(response.headers)
                    
                    # Server technology
                    if "server" in headers:
                        server = headers["server"].lower()
                        if "nginx" in server:
                            tech_stack["infrastructure"].append("Nginx")
                        elif "apache" in server:
                            tech_stack["infrastructure"].append("Apache")
                        elif "cloudflare" in server:
                            tech_stack["cdn"] = "Cloudflare"
                    
                    # Check for CDN
                    if "cf-ray" in headers:
                        tech_stack["cdn"] = "Cloudflare"
                    elif "x-amz-cf-id" in headers:
                        tech_stack["cdn"] = "AWS CloudFront"
                    
                    # Analyze page content
                    content = response.text.lower()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Detect frontend frameworks
                    for framework, indicators in self.tech_indicators["frontend"].items():
                        if any(indicator in content for indicator in indicators):
                            tech_stack["frontend"].append(framework.capitalize())
                    
                    # Detect analytics
                    analytics_patterns = {
                        "Google Analytics": ["google-analytics.com", "ga.js", "gtag"],
                        "Segment": ["segment.com", "analytics.js"],
                        "Mixpanel": ["mixpanel.com"],
                        "Amplitude": ["amplitude.com"],
                        "Heap": ["heap.io"]
                    }
                    
                    for analytics, patterns in analytics_patterns.items():
                        if any(pattern in content for pattern in patterns):
                            tech_stack["analytics"].append(analytics)
                    
                    # Check meta tags for technology hints
                    generator = soup.find("meta", {"name": "generator"})
                    if generator:
                        tech_stack["technologies"].append(generator.get("content", ""))
                    
                    # Infrastructure detection from resource URLs
                    scripts = soup.find_all("script", src=True)
                    for script in scripts:
                        src = script["src"]
                        for infra, indicators in self.tech_indicators["infrastructure"].items():
                            if any(indicator in src for indicator in indicators):
                                if infra.upper() not in tech_stack["infrastructure"]:
                                    tech_stack["infrastructure"].append(infra.upper())
                    
        except Exception as e:
            tech_stack["error"] = str(e)
        
        return tech_stack
    
    async def check_security_headers(self, domain: str) -> Dict:
        """Check security headers and HTTPS configuration"""
        security = {
            "found": False,
            "score": 0,
            "headers": {},
            "vulnerabilities": [],
            "recommendations": []
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{domain}",
                    headers=self.headers,
                    follow_redirects=True,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    security["found"] = True
                    headers = dict(response.headers)
                    
                    # Security headers to check
                    security_headers = {
                        "strict-transport-security": {"present": False, "weight": 20},
                        "x-content-type-options": {"present": False, "weight": 10},
                        "x-frame-options": {"present": False, "weight": 10},
                        "content-security-policy": {"present": False, "weight": 20},
                        "x-xss-protection": {"present": False, "weight": 10},
                        "referrer-policy": {"present": False, "weight": 5},
                        "permissions-policy": {"present": False, "weight": 5}
                    }
                    
                    # Check each header
                    for header, config in security_headers.items():
                        if header in headers:
                            config["present"] = True
                            security["headers"][header] = headers[header]
                            security["score"] += config["weight"]
                        else:
                            security["vulnerabilities"].append(f"Missing {header} header")
                            security["recommendations"].append(f"Add {header} header for better security")
                    
                    # Additional security checks
                    
                    # Check for exposed sensitive paths
                    sensitive_paths = [
                        "/.git/", "/.env", "/admin", "/wp-admin", 
                        "/phpmyadmin", "/.DS_Store", "/config.json"
                    ]
                    
                    for path in sensitive_paths:
                        try:
                            check_response = await client.get(
                                f"https://{domain}{path}",
                                headers=self.headers,
                                timeout=3.0,
                                follow_redirects=False
                            )
                            if check_response.status_code not in [404, 403]:
                                security["vulnerabilities"].append(f"Exposed path: {path}")
                                security["score"] -= 10
                        except:
                            pass
                    
                    # Check SSL/TLS configuration
                    if response.url.scheme == "https":
                        security["score"] += 20
                    else:
                        security["vulnerabilities"].append("Not using HTTPS")
                        security["score"] -= 20
                    
        except Exception as e:
            security["error"] = str(e)
        
        # Normalize score
        security["score"] = max(0, min(100, security["score"]))
        
        return security
    
    async def analyze_performance_metrics(self, domain: str) -> Dict:
        """Analyze website performance indicators"""
        performance = {
            "found": False,
            "load_time": None,
            "size": None,
            "requests": 0,
            "optimization": {
                "compression": False,
                "caching": False,
                "minification": False,
                "lazy_loading": False
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                start_time = datetime.now()
                response = await client.get(
                    f"https://{domain}",
                    headers=self.headers,
                    follow_redirects=True,
                    timeout=15.0
                )
                load_time = (datetime.now() - start_time).total_seconds()
                
                if response.status_code == 200:
                    performance["found"] = True
                    performance["load_time"] = round(load_time, 2)
                    performance["size"] = len(response.content)
                    
                    # Check compression
                    if "content-encoding" in response.headers:
                        if "gzip" in response.headers["content-encoding"] or "br" in response.headers["content-encoding"]:
                            performance["optimization"]["compression"] = True
                    
                    # Check caching headers
                    cache_headers = ["cache-control", "expires", "etag"]
                    if any(header in response.headers for header in cache_headers):
                        performance["optimization"]["caching"] = True
                    
                    # Check for minification (simple heuristic)
                    content = response.text
                    if len(content) > 1000:
                        # Check if JavaScript is minified
                        if "<script" in content:
                            script_density = len(re.findall(r'\s+', content)) / len(content)
                            if script_density < 0.1:  # Low whitespace ratio suggests minification
                                performance["optimization"]["minification"] = True
                    
                    # Check for lazy loading
                    if any(pattern in content.lower() for pattern in ["loading=\"lazy\"", "lazyload", "lazy-load"]):
                        performance["optimization"]["lazy_loading"] = True
                    
                    # Count external requests (approximate)
                    soup = BeautifulSoup(content, 'html.parser')
                    external_resources = (
                        len(soup.find_all("script", src=True)) +
                        len(soup.find_all("link", rel="stylesheet")) +
                        len(soup.find_all("img", src=True))
                    )
                    performance["requests"] = external_resources
                    
        except Exception as e:
            performance["error"] = str(e)
        
        return performance
    
    async def check_api_documentation(self, domain: str) -> Dict:
        """Check for API documentation and developer resources"""
        api_quality = {
            "found": False,
            "has_docs": False,
            "api_paths": [],
            "developer_friendly": False,
            "api_standards": []
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Common API documentation paths
                doc_paths = [
                    "/api", "/api/docs", "/docs", "/documentation",
                    "/developers", "/api/v1", "/swagger", "/openapi",
                    "/graphql", "/api-docs", "/developer"
                ]
                
                for path in doc_paths:
                    try:
                        response = await client.get(
                            f"https://{domain}{path}",
                            headers=self.headers,
                            timeout=5.0,
                            follow_redirects=True
                        )
                        
                        if response.status_code == 200:
                            api_quality["found"] = True
                            api_quality["has_docs"] = True
                            api_quality["api_paths"].append(path)
                            
                            content = response.text.lower()
                            
                            # Check for API standards
                            if "openapi" in content or "swagger" in content:
                                api_quality["api_standards"].append("OpenAPI/Swagger")
                            if "graphql" in content:
                                api_quality["api_standards"].append("GraphQL")
                            if "rest" in content or "restful" in content:
                                api_quality["api_standards"].append("REST")
                            
                            # Check for developer-friendly features
                            dev_features = ["authentication", "rate limit", "sdk", "example", "tutorial"]
                            if sum(1 for feature in dev_features if feature in content) >= 3:
                                api_quality["developer_friendly"] = True
                            
                            break  # Found API docs, no need to check more paths
                            
                    except:
                        continue
                
                # Check robots.txt for API paths
                try:
                    robots_response = await client.get(f"https://{domain}/robots.txt", timeout=3.0)
                    if robots_response.status_code == 200:
                        if "/api" in robots_response.text:
                            api_quality["found"] = True
                except:
                    pass
                    
        except Exception as e:
            api_quality["error"] = str(e)
        
        return api_quality
    
    async def analyze_mobile_readiness(self, domain: str) -> Dict:
        """Check mobile optimization and app presence"""
        mobile = {
            "found": False,
            "responsive": False,
            "mobile_optimized": False,
            "pwa": False,
            "app_links": {
                "ios": None,
                "android": None
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Mobile user agent
                mobile_headers = {
                    **self.headers,
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
                }
                
                response = await client.get(
                    f"https://{domain}",
                    headers=mobile_headers,
                    follow_redirects=True,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    mobile["found"] = True
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check viewport meta tag
                    viewport = soup.find("meta", {"name": "viewport"})
                    if viewport:
                        mobile["responsive"] = True
                        mobile["mobile_optimized"] = True
                    
                    # Check for PWA manifest
                    manifest = soup.find("link", {"rel": "manifest"})
                    if manifest:
                        mobile["pwa"] = True
                    
                    # Check for app smart banners or links
                    app_banner = soup.find("meta", {"name": "apple-itunes-app"})
                    if app_banner:
                        mobile["app_links"]["ios"] = "App Store"
                    
                    play_banner = soup.find("meta", {"name": "google-play-app"})
                    if play_banner:
                        mobile["app_links"]["android"] = "Google Play"
                    
                    # Check for app download links
                    links = soup.find_all("a", href=True)
                    for link in links:
                        href = link["href"].lower()
                        if "apps.apple.com" in href or "itunes.apple.com" in href:
                            mobile["app_links"]["ios"] = link["href"]
                        elif "play.google.com" in href:
                            mobile["app_links"]["android"] = link["href"]
                            
        except Exception as e:
            mobile["error"] = str(e)
        
        return mobile
    
    async def analyze_github_quality(self, github_data: Dict) -> Dict:
        """Analyze code quality from GitHub data"""
        code_quality = {
            "found": True,
            "metrics": {
                "activity_score": 0,
                "maintenance_score": 0,
                "community_score": 0,
                "documentation_score": 0
            },
            "indicators": {
                "has_ci_cd": False,
                "has_tests": False,
                "has_docs": False,
                "has_contributing": False,
                "has_security_policy": False,
                "active_maintenance": False
            },
            "tech_debt_indicators": []
        }
        
        if not github_data.get("found"):
            return {"found": False}
        
        # Activity score based on recent updates
        if github_data.get("recent_activity"):
            recent_repos = [r for r in github_data["recent_activity"] if r.get("days_since_update", 999) < 30]
            if len(recent_repos) > 3:
                code_quality["metrics"]["activity_score"] = 90
                code_quality["indicators"]["active_maintenance"] = True
            elif len(recent_repos) > 1:
                code_quality["metrics"]["activity_score"] = 70
            else:
                code_quality["metrics"]["activity_score"] = 40
        
        # Community score based on stars and forks
        total_stars = github_data.get("total_stars", 0)
        if total_stars > 1000:
            code_quality["metrics"]["community_score"] = 90
        elif total_stars > 100:
            code_quality["metrics"]["community_score"] = 70
        elif total_stars > 10:
            code_quality["metrics"]["community_score"] = 50
        else:
            code_quality["metrics"]["community_score"] = 30
        
        # Tech stack diversity
        tech_stack = github_data.get("tech_stack", [])
        if len(tech_stack) > 3:
            code_quality["metrics"]["maintenance_score"] = 80
        elif len(tech_stack) > 1:
            code_quality["metrics"]["maintenance_score"] = 60
        else:
            code_quality["metrics"]["maintenance_score"] = 40
        
        # Estimate documentation score
        if github_data.get("description"):
            code_quality["metrics"]["documentation_score"] = 60
            code_quality["indicators"]["has_docs"] = True
        
        # Tech debt indicators
        if github_data.get("recent_activity"):
            # Check for repos not updated in 90+ days
            stale_repos = [r for r in github_data["recent_activity"] if r.get("days_since_update", 0) > 90]
            if stale_repos:
                code_quality["tech_debt_indicators"].append(f"{len(stale_repos)} repositories appear abandoned")
        
        # Estimate CI/CD and testing based on common patterns
        if any(lang in tech_stack for lang in ["TypeScript", "JavaScript", "Python", "Go"]):
            # These languages commonly have good testing practices
            code_quality["indicators"]["has_tests"] = True
            code_quality["indicators"]["has_ci_cd"] = True
        
        return code_quality
    
    def _calculate_technical_score(self, tech_analysis: Dict) -> int:
        """Calculate overall technical score"""
        score = 50  # Base score
        
        # Website technology (+/- 20)
        if tech_analysis["website_tech"].get("found"):
            tech = tech_analysis["website_tech"]
            if tech.get("ssl"):
                score += 5
            if tech.get("http2"):
                score += 5
            if tech.get("cdn"):
                score += 5
            if len(tech.get("frontend", [])) > 0:
                score += 5
        
        # Security (+/- 30)
        if tech_analysis["security"].get("found"):
            security_score = tech_analysis["security"].get("score", 50)
            score += int((security_score - 50) * 0.6)  # Weight security heavily
        
        # Performance (+/- 20)
        if tech_analysis["performance"].get("found"):
            perf = tech_analysis["performance"]
            if perf.get("load_time", 999) < 3:
                score += 10
            elif perf.get("load_time", 999) < 5:
                score += 5
            else:
                score -= 5
            
            # Optimization bonus
            optimizations = sum(1 for opt in perf.get("optimization", {}).values() if opt)
            score += optimizations * 2.5
        
        # API Quality (+/- 15)
        if tech_analysis["api_quality"].get("has_docs"):
            score += 10
            if tech_analysis["api_quality"].get("developer_friendly"):
                score += 5
        
        # Mobile (+/- 10)
        if tech_analysis["mobile_readiness"].get("mobile_optimized"):
            score += 5
            if tech_analysis["mobile_readiness"].get("pwa"):
                score += 5
        
        # Code Quality (+/- 15)
        if tech_analysis["code_quality"].get("found"):
            code_metrics = tech_analysis["code_quality"].get("metrics", {})
            avg_code_score = sum(code_metrics.values()) / max(len(code_metrics), 1)
            score += int((avg_code_score - 50) * 0.3)
        
        return max(0, min(100, score))
    
    def _identify_technical_risks(self, tech_analysis: Dict) -> List[str]:
        """Identify technical risks"""
        risks = []
        
        # Security risks
        if tech_analysis["security"].get("found"):
            vulnerabilities = tech_analysis["security"].get("vulnerabilities", [])
            if vulnerabilities:
                risks.append(f"Security vulnerabilities: {', '.join(vulnerabilities[:3])}")
        
        # Performance risks
        if tech_analysis["performance"].get("found"):
            if tech_analysis["performance"].get("load_time", 0) > 5:
                risks.append("Slow website performance may impact user experience and SEO")
            if tech_analysis["performance"].get("requests", 0) > 50:
                risks.append("High number of external requests impacts performance")
        
        # Mobile risks
        if not tech_analysis["mobile_readiness"].get("mobile_optimized"):
            risks.append("Lack of mobile optimization limits market reach")
        
        # Code quality risks
        if tech_analysis["code_quality"].get("found"):
            tech_debt = tech_analysis["code_quality"].get("tech_debt_indicators", [])
            if tech_debt:
                risks.extend(tech_debt[:2])
        
        # API risks
        if not tech_analysis["api_quality"].get("has_docs"):
            risks.append("No public API documentation limits integration opportunities")
        
        return risks
    
    def _identify_technical_strengths(self, tech_analysis: Dict) -> List[str]:
        """Identify technical strengths"""
        strengths = []
        
        # Infrastructure strengths
        if tech_analysis["website_tech"].get("found"):
            tech = tech_analysis["website_tech"]
            if tech.get("cdn"):
                strengths.append(f"Global CDN ({tech['cdn']}) ensures fast content delivery")
            if tech.get("infrastructure"):
                strengths.append(f"Enterprise-grade infrastructure: {', '.join(tech['infrastructure'][:3])}")
        
        # Security strengths
        if tech_analysis["security"].get("score", 0) > 80:
            strengths.append("Excellent security posture with comprehensive headers")
        
        # Performance strengths
        if tech_analysis["performance"].get("found"):
            if tech_analysis["performance"].get("load_time", 999) < 2:
                strengths.append("Exceptional website performance (<2s load time)")
            optimizations = tech_analysis["performance"].get("optimization", {})
            if sum(1 for opt in optimizations.values() if opt) >= 3:
                strengths.append("Well-optimized frontend with compression, caching, and minification")
        
        # Developer experience
        if tech_analysis["api_quality"].get("developer_friendly"):
            strengths.append("Developer-friendly API with comprehensive documentation")
        
        # Mobile strengths
        if tech_analysis["mobile_readiness"].get("pwa"):
            strengths.append("Progressive Web App provides native-like mobile experience")
        
        # Code quality strengths
        if tech_analysis["code_quality"].get("found"):
            metrics = tech_analysis["code_quality"].get("metrics", {})
            if metrics.get("activity_score", 0) > 80:
                strengths.append("Very active development with frequent updates")
            if metrics.get("community_score", 0) > 80:
                strengths.append("Strong developer community and open-source presence")
        
        return strengths
    
    def _generate_technical_recommendations(self, tech_analysis: Dict) -> List[str]:
        """Generate technical recommendations"""
        recommendations = []
        
        # Security recommendations
        if tech_analysis["security"].get("found"):
            missing_headers = [vuln.replace("Missing ", "") for vuln in tech_analysis["security"].get("vulnerabilities", []) if "Missing" in vuln]
            if missing_headers:
                recommendations.append(f"Implement security headers: {', '.join(missing_headers[:3])}")
        
        # Performance recommendations
        if tech_analysis["performance"].get("found"):
            perf = tech_analysis["performance"]
            if not perf.get("optimization", {}).get("compression"):
                recommendations.append("Enable gzip/brotli compression to reduce bandwidth")
            if perf.get("requests", 0) > 30:
                recommendations.append("Reduce external requests through bundling and lazy loading")
        
        # Mobile recommendations
        if not tech_analysis["mobile_readiness"].get("pwa"):
            recommendations.append("Consider implementing Progressive Web App for better mobile engagement")
        
        # API recommendations
        if not tech_analysis["api_quality"].get("has_docs"):
            recommendations.append("Create public API documentation to enable integrations")
        
        # General recommendations
        if tech_analysis["technical_score"] < 60:
            recommendations.append("Prioritize technical debt reduction and infrastructure modernization")
        
        return recommendations

# Singleton instance
tech_dd_analyzer = TechnicalDueDiligenceAnalyzer()