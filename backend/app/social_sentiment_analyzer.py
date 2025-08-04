"""
Social Media Sentiment Analyzer
Analyzes sentiment across Twitter, Reddit, and other platforms
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
from urllib.parse import quote

class SocialSentimentAnalyzer:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    
    async def analyze_social_sentiment(self, company_name: str, domain: Optional[str] = None) -> Dict:
        """Comprehensive social media sentiment analysis"""
        
        tasks = [
            self.analyze_twitter_sentiment(company_name),
            self.analyze_reddit_sentiment(company_name),
            self.analyze_hackernews_sentiment(company_name, domain),
            self.analyze_youtube_presence(company_name),
            self.analyze_glassdoor_sentiment(company_name)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        social_data = {
            "twitter": results[0] if not isinstance(results[0], Exception) else {"found": False},
            "reddit": results[1] if not isinstance(results[1], Exception) else {"found": False},
            "hackernews": results[2] if not isinstance(results[2], Exception) else {"found": False},
            "youtube": results[3] if not isinstance(results[3], Exception) else {"found": False},
            "glassdoor": results[4] if not isinstance(results[4], Exception) else {"found": False}
        }
        
        # Calculate overall sentiment
        social_data["overall_sentiment"] = self._calculate_overall_sentiment(social_data)
        social_data["social_signals"] = self._extract_social_signals(social_data)
        social_data["viral_indicators"] = self._identify_viral_indicators(social_data)
        social_data["community_health"] = self._assess_community_health(social_data)
        
        return social_data
    
    async def analyze_twitter_sentiment(self, company_name: str) -> Dict:
        """Analyze Twitter/X sentiment (without API)"""
        sentiment_data = {
            "found": False,
            "mentions": 0,
            "sentiment": "neutral",
            "trending_topics": [],
            "influential_mentions": [],
            "engagement_level": "low"
        }
        
        try:
            # Search for company mentions using web search
            search_query = f"{company_name} twitter"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://html.duckduckgo.com/html/?q={quote(search_query)}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = soup.find_all('a', class_='result__a')
                    
                    twitter_mentions = 0
                    positive_keywords = ["amazing", "love", "excellent", "best", "innovative", "excited"]
                    negative_keywords = ["terrible", "hate", "worst", "scam", "avoid", "disappointed"]
                    
                    positive_count = 0
                    negative_count = 0
                    
                    for result in results[:20]:
                        text = result.get_text(strip=True).lower()
                        if "twitter.com" in result.get('href', '') or "x.com" in result.get('href', ''):
                            twitter_mentions += 1
                            
                            # Simple sentiment analysis
                            for keyword in positive_keywords:
                                if keyword in text:
                                    positive_count += 1
                                    break
                            for keyword in negative_keywords:
                                if keyword in text:
                                    negative_count += 1
                                    break
                    
                    if twitter_mentions > 0:
                        sentiment_data["found"] = True
                        sentiment_data["mentions"] = twitter_mentions
                        
                        # Determine sentiment
                        if positive_count > negative_count * 1.5:
                            sentiment_data["sentiment"] = "positive"
                        elif negative_count > positive_count * 1.5:
                            sentiment_data["sentiment"] = "negative"
                        else:
                            sentiment_data["sentiment"] = "neutral"
                        
                        # Engagement level
                        if twitter_mentions > 10:
                            sentiment_data["engagement_level"] = "high"
                        elif twitter_mentions > 5:
                            sentiment_data["engagement_level"] = "medium"
                        else:
                            sentiment_data["engagement_level"] = "low"
                            
        except Exception as e:
            pass
        
        return sentiment_data
    
    async def analyze_reddit_sentiment(self, company_name: str) -> Dict:
        """Analyze Reddit sentiment"""
        sentiment_data = {
            "found": False,
            "subreddits": [],
            "posts_count": 0,
            "sentiment": "neutral",
            "discussion_topics": [],
            "community_size": "unknown"
        }
        
        try:
            # Search Reddit discussions
            search_query = f"{company_name} site:reddit.com"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://html.duckduckgo.com/html/?q={quote(search_query)}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = soup.find_all('a', class_='result__a')
                    
                    subreddits = set()
                    discussion_topics = []
                    reddit_posts = 0
                    
                    positive_count = 0
                    negative_count = 0
                    
                    for result in results[:20]:
                        href = result.get('href', '')
                        text = result.get_text(strip=True)
                        
                        if "reddit.com/r/" in href:
                            reddit_posts += 1
                            
                            # Extract subreddit
                            subreddit_match = re.search(r'/r/([^/]+)', href)
                            if subreddit_match:
                                subreddits.add(subreddit_match.group(1))
                            
                            # Extract topic
                            if len(text) > 20:
                                discussion_topics.append(text[:100])
                            
                            # Sentiment analysis
                            text_lower = text.lower()
                            if any(word in text_lower for word in ["love", "great", "amazing", "best"]):
                                positive_count += 1
                            elif any(word in text_lower for word in ["hate", "scam", "terrible", "worst"]):
                                negative_count += 1
                    
                    if reddit_posts > 0:
                        sentiment_data["found"] = True
                        sentiment_data["subreddits"] = list(subreddits)[:5]
                        sentiment_data["posts_count"] = reddit_posts
                        sentiment_data["discussion_topics"] = discussion_topics[:5]
                        
                        # Determine sentiment
                        if positive_count > negative_count * 1.5:
                            sentiment_data["sentiment"] = "positive"
                        elif negative_count > positive_count * 1.5:
                            sentiment_data["sentiment"] = "negative"
                        else:
                            sentiment_data["sentiment"] = "mixed"
                        
                        # Community size estimation
                        if reddit_posts > 15:
                            sentiment_data["community_size"] = "large"
                        elif reddit_posts > 5:
                            sentiment_data["community_size"] = "medium"
                        else:
                            sentiment_data["community_size"] = "small"
                            
        except Exception as e:
            pass
        
        return sentiment_data
    
    async def analyze_hackernews_sentiment(self, company_name: str, domain: Optional[str] = None) -> Dict:
        """Analyze Hacker News sentiment"""
        sentiment_data = {
            "found": False,
            "posts_count": 0,
            "comments_sentiment": "neutral",
            "top_stories": [],
            "technical_validation": False
        }
        
        try:
            # Search HN via Algolia API (public)
            async with httpx.AsyncClient() as client:
                search_query = company_name
                if domain:
                    # Also search by domain
                    domain_search = domain.replace("www.", "")
                    search_query = f"{company_name} OR {domain_search}"
                
                response = await client.get(
                    f"http://hn.algolia.com/api/v1/search?query={quote(search_query)}&tags=story",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get("hits", [])
                    
                    if hits:
                        sentiment_data["found"] = True
                        sentiment_data["posts_count"] = len(hits)
                        
                        # Analyze top stories
                        for hit in hits[:5]:
                            story = {
                                "title": hit.get("title", ""),
                                "points": hit.get("points", 0),
                                "comments": hit.get("num_comments", 0),
                                "date": hit.get("created_at", "")
                            }
                            sentiment_data["top_stories"].append(story)
                        
                        # Calculate engagement metrics
                        total_points = sum(hit.get("points", 0) for hit in hits[:10])
                        total_comments = sum(hit.get("num_comments", 0) for hit in hits[:10])
                        
                        # Technical validation based on engagement
                        if total_points > 500 or total_comments > 100:
                            sentiment_data["technical_validation"] = True
                        
                        # Sentiment based on engagement
                        avg_points = total_points / min(len(hits), 10)
                        if avg_points > 100:
                            sentiment_data["comments_sentiment"] = "very positive"
                        elif avg_points > 50:
                            sentiment_data["comments_sentiment"] = "positive"
                        elif avg_points > 10:
                            sentiment_data["comments_sentiment"] = "neutral"
                        else:
                            sentiment_data["comments_sentiment"] = "low interest"
                            
        except Exception as e:
            pass
        
        return sentiment_data
    
    async def analyze_youtube_presence(self, company_name: str) -> Dict:
        """Analyze YouTube presence and content"""
        youtube_data = {
            "found": False,
            "channel_exists": False,
            "content_types": [],
            "engagement_indicators": [],
            "video_count_estimate": 0
        }
        
        try:
            # Search for company YouTube content
            search_query = f"{company_name} site:youtube.com"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://html.duckduckgo.com/html/?q={quote(search_query)}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = soup.find_all('a', class_='result__a')
                    
                    video_count = 0
                    content_types = set()
                    
                    for result in results[:15]:
                        href = result.get('href', '')
                        text = result.get_text(strip=True).lower()
                        
                        if "youtube.com" in href:
                            video_count += 1
                            
                            # Identify content types
                            if "demo" in text or "tutorial" in text:
                                content_types.add("Product Demos")
                            elif "webinar" in text or "conference" in text:
                                content_types.add("Webinars/Conferences")
                            elif "interview" in text or "podcast" in text:
                                content_types.add("Interviews")
                            elif "announcement" in text or "launch" in text:
                                content_types.add("Product Launches")
                            
                            # Check for official channel
                            if f"youtube.com/c/{company_name.lower()}" in href or \
                               f"youtube.com/@{company_name.lower()}" in href:
                                youtube_data["channel_exists"] = True
                    
                    if video_count > 0:
                        youtube_data["found"] = True
                        youtube_data["video_count_estimate"] = video_count
                        youtube_data["content_types"] = list(content_types)
                        
                        # Engagement indicators
                        if video_count > 10:
                            youtube_data["engagement_indicators"].append("Active video content strategy")
                        if youtube_data["channel_exists"]:
                            youtube_data["engagement_indicators"].append("Official YouTube channel")
                        if "Product Demos" in content_types:
                            youtube_data["engagement_indicators"].append("Educational content")
                            
        except Exception as e:
            pass
        
        return youtube_data
    
    async def analyze_glassdoor_sentiment(self, company_name: str) -> Dict:
        """Analyze Glassdoor reviews and ratings"""
        glassdoor_data = {
            "found": False,
            "rating": None,
            "review_highlights": [],
            "employee_sentiment": "unknown",
            "culture_indicators": []
        }
        
        try:
            # Search for Glassdoor reviews
            search_query = f"{company_name} glassdoor reviews"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://html.duckduckgo.com/html/?q={quote(search_query)}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = soup.find_all('a', class_='result__a')
                    
                    for result in results[:10]:
                        href = result.get('href', '')
                        text = result.get_text(strip=True)
                        
                        if "glassdoor.com" in href:
                            glassdoor_data["found"] = True
                            
                            # Look for rating
                            rating_match = re.search(r'(\d\.\d)\s*(?:stars?|rating)', text.lower())
                            if rating_match:
                                glassdoor_data["rating"] = float(rating_match.group(1))
                            
                            # Extract review highlights
                            snippet = result.find_next_sibling('a', class_='result__snippet')
                            if snippet:
                                glassdoor_data["review_highlights"].append(snippet.get_text(strip=True)[:150])
                            
                            # Analyze sentiment based on rating
                            if glassdoor_data["rating"]:
                                if glassdoor_data["rating"] >= 4.0:
                                    glassdoor_data["employee_sentiment"] = "positive"
                                    glassdoor_data["culture_indicators"].append("High employee satisfaction")
                                elif glassdoor_data["rating"] >= 3.5:
                                    glassdoor_data["employee_sentiment"] = "neutral"
                                    glassdoor_data["culture_indicators"].append("Average employee satisfaction")
                                else:
                                    glassdoor_data["employee_sentiment"] = "negative"
                                    glassdoor_data["culture_indicators"].append("Low employee satisfaction")
                            
                            break
                            
        except Exception as e:
            pass
        
        return glassdoor_data
    
    def _calculate_overall_sentiment(self, social_data: Dict) -> Dict:
        """Calculate overall social sentiment"""
        sentiment_scores = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }
        
        platform_weights = {
            "twitter": 0.25,
            "reddit": 0.25,
            "hackernews": 0.20,
            "glassdoor": 0.20,
            "youtube": 0.10
        }
        
        # Aggregate sentiments
        for platform, weight in platform_weights.items():
            if social_data[platform].get("found"):
                platform_sentiment = social_data[platform].get("sentiment") or \
                                   social_data[platform].get("comments_sentiment") or \
                                   social_data[platform].get("employee_sentiment")
                
                if platform_sentiment:
                    if "positive" in platform_sentiment:
                        sentiment_scores["positive"] += weight
                    elif "negative" in platform_sentiment:
                        sentiment_scores["negative"] += weight
                    else:
                        sentiment_scores["neutral"] += weight
        
        # Determine overall sentiment
        total_weight = sum(sentiment_scores.values())
        if total_weight > 0:
            if sentiment_scores["positive"] / total_weight > 0.6:
                overall = "Positive"
            elif sentiment_scores["negative"] / total_weight > 0.4:
                overall = "Negative"
            else:
                overall = "Mixed"
        else:
            overall = "Unknown"
        
        return {
            "sentiment": overall,
            "confidence": min(total_weight * 100, 100),
            "breakdown": sentiment_scores
        }
    
    def _extract_social_signals(self, social_data: Dict) -> List[str]:
        """Extract key social signals"""
        signals = []
        
        # Twitter signals
        if social_data["twitter"].get("engagement_level") == "high":
            signals.append("High Twitter engagement")
        
        # Reddit signals
        if social_data["reddit"].get("community_size") in ["medium", "large"]:
            signals.append(f"Active Reddit community ({social_data['reddit']['community_size']})")
        
        # HN signals
        if social_data["hackernews"].get("technical_validation"):
            signals.append("Strong technical validation on Hacker News")
        
        # YouTube signals
        if social_data["youtube"].get("channel_exists"):
            signals.append("Official YouTube presence")
        
        # Glassdoor signals
        if social_data["glassdoor"].get("rating", 0) >= 4.0:
            signals.append(f"High Glassdoor rating: {social_data['glassdoor']['rating']}/5")
        
        return signals
    
    def _identify_viral_indicators(self, social_data: Dict) -> Dict:
        """Identify viral growth indicators"""
        viral_score = 0
        indicators = []
        
        # High engagement metrics
        if social_data["twitter"].get("engagement_level") == "high":
            viral_score += 30
            indicators.append("High Twitter virality")
        
        # Multiple platform presence
        platforms_found = sum(1 for platform in ["twitter", "reddit", "hackernews", "youtube"]
                            if social_data[platform].get("found"))
        if platforms_found >= 3:
            viral_score += 20
            indicators.append(f"Present on {platforms_found} platforms")
        
        # HN front page potential
        if social_data["hackernews"].get("top_stories"):
            top_story_points = max(story.get("points", 0) 
                                 for story in social_data["hackernews"]["top_stories"])
            if top_story_points > 100:
                viral_score += 30
                indicators.append("Hacker News front page stories")
        
        # Reddit community
        if social_data["reddit"].get("posts_count", 0) > 10:
            viral_score += 20
            indicators.append("Viral Reddit discussions")
        
        return {
            "viral_potential": "High" if viral_score >= 70 else "Medium" if viral_score >= 40 else "Low",
            "viral_score": viral_score,
            "indicators": indicators
        }
    
    def _assess_community_health(self, social_data: Dict) -> Dict:
        """Assess overall community health"""
        health_score = 0
        health_indicators = []
        issues = []
        
        # Positive indicators
        if social_data["overall_sentiment"]["sentiment"] == "Positive":
            health_score += 30
            health_indicators.append("Positive community sentiment")
        
        if social_data["glassdoor"].get("employee_sentiment") == "positive":
            health_score += 25
            health_indicators.append("Happy employees")
        
        if social_data["reddit"].get("found") and social_data["reddit"]["sentiment"] != "negative":
            health_score += 20
            health_indicators.append("Active user community")
        
        # Negative indicators
        if social_data["overall_sentiment"]["sentiment"] == "Negative":
            health_score -= 30
            issues.append("Negative community sentiment")
        
        if social_data["glassdoor"].get("employee_sentiment") == "negative":
            health_score -= 20
            issues.append("Employee dissatisfaction")
        
        # Community engagement
        engagement_count = sum(1 for platform in ["twitter", "reddit", "youtube"]
                             if social_data[platform].get("found"))
        if engagement_count >= 2:
            health_score += 25
            health_indicators.append("Multi-platform engagement")
        
        return {
            "health_score": max(0, min(100, health_score)),
            "status": "Healthy" if health_score >= 70 else "Moderate" if health_score >= 40 else "Unhealthy",
            "positive_indicators": health_indicators,
            "issues": issues
        }

# Singleton instance
social_sentiment = SocialSentimentAnalyzer()