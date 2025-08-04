"""
News API Integration
Track company mentions and sentiment in news
"""

import httpx
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
import os
from collections import Counter

class NewsAPI:
    # Using NewsAPI.org free tier as fallback
    NEWSAPI_URL = "https://newsapi.org/v2/everything"
    # Google News RSS as primary (no API key needed)
    GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")  # Optional
    
    async def get_recent_news(self, company_name: str) -> Dict:
        """Get recent news mentions for a company"""
        try:
            async with httpx.AsyncClient() as client:
                # Try Google News RSS first (no API key needed)
                articles = await self._get_google_news(client, company_name)
                
                # Fallback to NewsAPI if available
                if not articles and self.api_key:
                    articles = await self._get_newsapi_articles(client, company_name)
                
                # Analyze news data
                news_analysis = self._analyze_news_coverage(articles)
                
                # Calculate sentiment and velocity
                metrics = self._calculate_news_metrics(articles)
                
                return {
                    "company_name": company_name,
                    "total_articles": len(articles),
                    "recent_articles": articles[:10],  # Top 10 most recent
                    "news_analysis": news_analysis,
                    "metrics": metrics,
                    "data_quality": self._assess_data_quality(articles)
                }
                
        except Exception as e:
            return {"error": f"News data fetch failed: {str(e)}"}
    
    async def _get_google_news(self, client: httpx.AsyncClient, company_name: str) -> List[Dict]:
        """Get news from Google News RSS (no API key required)"""
        try:
            import xml.etree.ElementTree as ET
            from urllib.parse import quote
            
            # Search Google News RSS
            response = await client.get(
                f"{self.GOOGLE_NEWS_RSS}?q={quote(company_name)}&hl=en-US&gl=US&ceid=US:en"
            )
            
            if response.status_code == 200:
                articles = []
                root = ET.fromstring(response.content)
                
                # Parse RSS items
                for item in root.findall(".//item")[:30]:  # Get up to 30 articles
                    title = item.find("title")
                    link = item.find("link")
                    pub_date = item.find("pubDate")
                    source = item.find("source")
                    
                    if title is not None and link is not None:
                        article = {
                            "title": title.text,
                            "url": link.text,
                            "published_at": pub_date.text if pub_date is not None else None,
                            "source": source.text if source is not None else "Unknown",
                            "description": ""  # RSS doesn't include description
                        }
                        
                        # Basic sentiment from title
                        article["sentiment"] = self._analyze_title_sentiment(title.text)
                        articles.append(article)
                
                return articles
            
            return []
            
        except Exception:
            return []
    
    async def _get_newsapi_articles(self, client: httpx.AsyncClient, company_name: str) -> List[Dict]:
        """Get news from NewsAPI.org (requires API key)"""
        try:
            # Calculate date range (last 30 days)
            to_date = datetime.now()
            from_date = to_date - timedelta(days=30)
            
            params = {
                "q": f'"{company_name}"',  # Exact phrase
                "from": from_date.strftime("%Y-%m-%d"),
                "to": to_date.strftime("%Y-%m-%d"),
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": self.api_key
            }
            
            response = await client.get(self.NEWSAPI_URL, params=params)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for article in data.get("articles", [])[:30]:
                    processed_article = {
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "published_at": article.get("publishedAt", ""),
                        "sentiment": self._analyze_title_sentiment(article.get("title", ""))
                    }
                    articles.append(processed_article)
                
                return articles
            
            return []
            
        except Exception:
            return []
    
    def _analyze_title_sentiment(self, title: str) -> str:
        """Simple sentiment analysis based on keywords"""
        if not title:
            return "neutral"
        
        title_lower = title.lower()
        
        # Positive indicators
        positive_words = [
            "growth", "success", "profit", "gain", "rise", "surge", "breakthrough",
            "innovation", "expand", "win", "achieve", "record", "boost", "strong"
        ]
        
        # Negative indicators
        negative_words = [
            "loss", "decline", "fall", "drop", "lawsuit", "investigation", "scandal",
            "layoff", "cuts", "weak", "struggle", "fail", "crash", "plunge"
        ]
        
        positive_count = sum(1 for word in positive_words if word in title_lower)
        negative_count = sum(1 for word in negative_words if word in title_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _analyze_news_coverage(self, articles: List[Dict]) -> Dict:
        """Analyze patterns in news coverage"""
        if not articles:
            return {
                "coverage_trend": "none",
                "main_topics": [],
                "source_diversity": 0
            }
        
        # Source diversity
        sources = [a.get("source", "Unknown") for a in articles]
        unique_sources = len(set(sources))
        
        # Topic extraction (simple keyword based)
        all_titles = " ".join([a.get("title", "") for a in articles])
        words = all_titles.lower().split()
        
        # Filter common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
        meaningful_words = [w for w in words if len(w) > 4 and w not in stop_words]
        
        # Get top topics
        word_counts = Counter(meaningful_words)
        main_topics = [word for word, _ in word_counts.most_common(5)]
        
        # Coverage trend
        if len(articles) > 20:
            coverage_trend = "high"
        elif len(articles) > 10:
            coverage_trend = "moderate"
        elif len(articles) > 0:
            coverage_trend = "low"
        else:
            coverage_trend = "none"
        
        return {
            "coverage_trend": coverage_trend,
            "main_topics": main_topics,
            "source_diversity": unique_sources
        }
    
    def _calculate_news_metrics(self, articles: List[Dict]) -> Dict:
        """Calculate news-based metrics"""
        if not articles:
            return {
                "news_velocity": 0,
                "sentiment_score": 50,
                "media_attention_score": 0
            }
        
        # News velocity (articles per week)
        try:
            dates = []
            for article in articles:
                pub_date = article.get("published_at")
                if pub_date:
                    # Handle different date formats
                    try:
                        date = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                        dates.append(date)
                    except:
                        pass
            
            if dates:
                date_range = (max(dates) - min(dates)).days / 7  # weeks
                velocity = len(articles) / max(date_range, 1)
            else:
                velocity = 0
        except:
            velocity = 0
        
        # Sentiment score
        sentiments = [a.get("sentiment", "neutral") for a in articles]
        positive = sentiments.count("positive")
        negative = sentiments.count("negative")
        total = len(sentiments)
        
        if total > 0:
            sentiment_score = int((positive / total) * 100)
        else:
            sentiment_score = 50
        
        # Media attention score
        attention_score = min(100, len(articles) * 3)
        
        return {
            "news_velocity": round(velocity, 1),
            "sentiment_score": sentiment_score,
            "media_attention_score": attention_score
        }
    
    def _assess_data_quality(self, articles: List[Dict]) -> Dict:
        """Assess quality of news data"""
        if not articles:
            return {"score": 0, "status": "no_coverage"}
        
        if len(articles) < 5:
            return {"score": 0.3, "status": "minimal_coverage"}
        elif len(articles) < 15:
            return {"score": 0.7, "status": "moderate_coverage"}
        else:
            return {"score": 1.0, "status": "high_coverage"}

# Export singleton instance
news_api = NewsAPI()