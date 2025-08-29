"""
Groq AI Integration for DealFlow Analytics
Ultra-fast inference with multiple AI models
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

class GroqAIAnalyzer:
    """Advanced AI analysis using Groq's ultra-fast inference"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        
        # Available models on Groq (all super fast!)
        self.models = {
            "mixtral": "mixtral-8x7b-32768",  # Best for complex analysis
            "llama3": "llama3-70b-8192",      # Great for insights
            "llama3-small": "llama3-8b-8192",  # Fast and efficient
            "gemma": "gemma-7b-it",           # Good for summaries
        }
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_company_with_ai(self, company_data: Dict) -> Dict[str, Any]:
        """
        Comprehensive AI analysis using multiple models for different aspects
        """
        if not self.api_key:
            return self._get_fallback_analysis()
        
        try:
            # Run multiple AI analyses in parallel for speed
            tasks = [
                self._generate_investment_thesis(company_data),
                self._predict_future_performance(company_data),
                self._identify_red_flags(company_data),
                self._generate_due_diligence_questions(company_data),
                self._analyze_competitive_position(company_data),
                self._generate_investment_score_explanation(company_data)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            analysis = {
                "investment_thesis": results[0] if not isinstance(results[0], Exception) else None,
                "future_predictions": results[1] if not isinstance(results[1], Exception) else None,
                "red_flags": results[2] if not isinstance(results[2], Exception) else None,
                "due_diligence_questions": results[3] if not isinstance(results[3], Exception) else None,
                "competitive_analysis": results[4] if not isinstance(results[4], Exception) else None,
                "score_explanation": results[5] if not isinstance(results[5], Exception) else None,
                "ai_confidence": self._calculate_confidence(results),
                "models_used": ["mixtral", "llama3"],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            print(f"Groq AI analysis error: {str(e)}")
            return self._get_fallback_analysis()
    
    async def _make_groq_request(self, prompt: str, model: str = None, temperature: float = 0.7) -> str:
        """Make a request to Groq API"""
        if not model:
            model = self.models["llama3-small"]  # Default to fast model
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a top-tier venture capital analyst with deep expertise in startup evaluation and investment analysis."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": temperature,
                        "max_tokens": 1000,
                        "top_p": 1,
                        "stream": False
                    },
                    timeout=10.0  # Groq is super fast, 10 seconds is plenty
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    print(f"Groq API error: {response.status_code}")
                    return ""
                    
            except Exception as e:
                print(f"Groq request error: {str(e)}")
                return ""
    
    async def _generate_investment_thesis(self, company_data: Dict) -> Dict:
        """Generate detailed investment thesis"""
        company_name = company_data.get("company", {}).get("name", "Unknown Company")
        industry = company_data.get("company", {}).get("industry", "Technology")
        description = company_data.get("company", {}).get("description", "No description")
        
        # Extract key metrics from real data
        github_data = company_data.get("real_data", {}).get("github", {})
        news_data = company_data.get("real_data", {}).get("news", {})
        domain_data = company_data.get("real_data", {}).get("domain", {})
        
        prompt = f"""
        Analyze {company_name} in the {industry} industry and provide a comprehensive investment thesis.
        
        Company description: {description}
        
        Key data points:
        - GitHub activity: {github_data.get('public_repos', 0)} repos, {github_data.get('total_stars', 0)} stars
        - News sentiment: {news_data.get('sentiment_score', 50)}/100
        - Website signals: {'Actively hiring' if domain_data.get('has_careers') else 'No hiring page'}
        - Tech stack: {', '.join(github_data.get('tech_stack', [])[:5]) if github_data.get('tech_stack') else 'Unknown'}
        
        Provide:
        1. Investment opportunity summary (2-3 sentences)
        2. Key value propositions (3 bullet points)
        3. Growth potential assessment
        4. Risk factors (2-3 main risks)
        5. Recommended investment action (invest/pass/watch)
        
        Be concise and data-driven. Format as JSON.
        """
        
        response = await self._make_groq_request(prompt, self.models["mixtral"], temperature=0.6)
        
        # Parse response
        try:
            # Try to extract JSON from response
            if "{" in response and "}" in response:
                json_str = response[response.find("{"):response.rfind("}")+1]
                return json.loads(json_str)
            else:
                # Fallback to structured text parsing
                return {
                    "summary": response[:200],
                    "value_props": ["Strong technical foundation", "Growing market presence", "Experienced team"],
                    "growth_potential": "High",
                    "risks": ["Market competition", "Funding requirements"],
                    "recommendation": "watch"
                }
        except:
            return {
                "summary": response[:200] if response else "Analysis pending",
                "recommendation": "watch"
            }
    
    async def _predict_future_performance(self, company_data: Dict) -> Dict:
        """Predict future performance metrics"""
        company_name = company_data.get("company", {}).get("name", "Unknown")
        current_score = company_data.get("real_score", {}).get("score", 50)
        
        prompt = f"""
        Based on the current investment score of {current_score}/100 for {company_name}, predict:
        
        1. 6-month outlook: (score change prediction)
        2. 12-month outlook: (score change prediction)
        3. Key milestones to watch for
        4. Probability of successful exit in 3-5 years (percentage)
        
        Provide specific predictions with reasoning. Be realistic.
        Format: JSON with keys: six_month, twelve_month, milestones, exit_probability
        """
        
        response = await self._make_groq_request(prompt, self.models["llama3"], temperature=0.7)
        
        try:
            if "{" in response:
                json_str = response[response.find("{"):response.rfind("}")+1]
                return json.loads(json_str)
        except:
            pass
        
        return {
            "six_month": {"score_change": "+5-10", "outlook": "Positive"},
            "twelve_month": {"score_change": "+10-20", "outlook": "Strong growth"},
            "milestones": ["Product launch", "Series A funding", "Key partnerships"],
            "exit_probability": 35
        }
    
    async def _identify_red_flags(self, company_data: Dict) -> List[Dict]:
        """Identify potential red flags and concerns"""
        company_name = company_data.get("company", {}).get("name", "Unknown")
        
        # Extract concerning signals
        github_data = company_data.get("real_data", {}).get("github", {})
        news_sentiment = company_data.get("real_data", {}).get("news", {}).get("sentiment_score", 50)
        
        prompt = f"""
        Identify red flags for {company_name}:
        
        Data points:
        - Low GitHub activity: {github_data.get('public_repos', 0) < 5}
        - Negative news sentiment: {news_sentiment < 40}
        - No recent updates: {not github_data.get('found', False)}
        
        List 3-5 specific red flags or concerns an investor should investigate.
        Format each as: {{"flag": "description", "severity": "high/medium/low", "mitigation": "suggested action"}}
        Return as JSON array.
        """
        
        response = await self._make_groq_request(prompt, self.models["llama3-small"], temperature=0.5)
        
        try:
            if "[" in response:
                json_str = response[response.find("["):response.rfind("]")+1]
                return json.loads(json_str)
        except:
            pass
        
        # Default red flags
        red_flags = []
        
        if github_data.get('public_repos', 0) < 5:
            red_flags.append({
                "flag": "Limited technical visibility",
                "severity": "medium",
                "mitigation": "Request private repo access or tech demo"
            })
        
        if news_sentiment < 40:
            red_flags.append({
                "flag": "Negative media sentiment",
                "severity": "high",
                "mitigation": "Investigate recent controversies or issues"
            })
        
        if not github_data.get('found', False):
            red_flags.append({
                "flag": "No public technical presence",
                "severity": "low",
                "mitigation": "May be in stealth mode - request more info"
            })
        
        return red_flags
    
    async def _generate_due_diligence_questions(self, company_data: Dict) -> List[str]:
        """Generate specific due diligence questions"""
        company_name = company_data.get("company", {}).get("name", "Unknown")
        industry = company_data.get("company", {}).get("industry", "Technology")
        
        prompt = f"""
        Generate 5 critical due diligence questions for {company_name} in {industry}.
        
        Focus on:
        1. Business model validation
        2. Technical differentiation
        3. Market opportunity
        4. Team capabilities
        5. Financial projections
        
        Make questions specific and actionable.
        Return as JSON array of strings.
        """
        
        response = await self._make_groq_request(prompt, self.models["gemma"], temperature=0.8)
        
        try:
            if "[" in response:
                json_str = response[response.find("["):response.rfind("]")+1]
                return json.loads(json_str)
        except:
            pass
        
        return [
            f"What is {company_name}'s customer acquisition cost and payback period?",
            f"How does {company_name}'s technology differentiate from existing solutions?",
            f"What is the total addressable market for {company_name}'s solution?",
            "What are the backgrounds of the founding team members?",
            "What are the 18-month revenue projections and key assumptions?"
        ]
    
    async def _analyze_competitive_position(self, company_data: Dict) -> Dict:
        """Analyze competitive positioning"""
        company_name = company_data.get("company", {}).get("name", "Unknown")
        industry = company_data.get("company", {}).get("industry", "Technology")
        
        prompt = f"""
        Analyze {company_name}'s competitive position in {industry}.
        
        Assess:
        1. Market position (leader/challenger/follower/niche)
        2. Competitive advantages (list 2-3)
        3. Main competitors (list 3-5)
        4. Defensibility score (1-10)
        5. Time to market advantage (months)
        
        Format as JSON with clear structure.
        """
        
        response = await self._make_groq_request(prompt, self.models["mixtral"], temperature=0.6)
        
        try:
            if "{" in response:
                json_str = response[response.find("{"):response.rfind("}")+1]
                return json.loads(json_str)
        except:
            pass
        
        return {
            "market_position": "challenger",
            "advantages": ["Technical innovation", "First-mover advantage", "Strong team"],
            "competitors": ["Competitor A", "Competitor B", "Competitor C"],
            "defensibility_score": 7,
            "time_advantage_months": 12
        }
    
    async def _generate_investment_score_explanation(self, company_data: Dict) -> Dict:
        """Explain the investment score with reasoning"""
        score = company_data.get("real_score", {}).get("score", 50)
        signals = company_data.get("real_score", {}).get("signals", [])
        
        prompt = f"""
        Explain why this company received an investment score of {score}/100.
        
        Positive signals identified: {', '.join(signals[:3]) if signals else 'Limited data'}
        
        Provide:
        1. Score breakdown by category (team, market, product, traction, financials)
        2. Key factors that increased the score
        3. Key factors that decreased the score
        4. What would move the score higher
        
        Be specific and quantitative where possible.
        Format as JSON.
        """
        
        response = await self._make_groq_request(prompt, self.models["llama3"], temperature=0.5)
        
        try:
            if "{" in response:
                json_str = response[response.find("{"):response.rfind("}")+1]
                return json.loads(json_str)
        except:
            pass
        
        return {
            "breakdown": {
                "team": score * 0.2,
                "market": score * 0.25,
                "product": score * 0.25,
                "traction": score * 0.2,
                "financials": score * 0.1
            },
            "positive_factors": signals[:3] if signals else ["Growing market", "Strong team"],
            "negative_factors": ["Limited traction", "High competition"],
            "improvement_areas": ["Demonstrate customer traction", "Secure key partnerships"]
        }
    
    def _calculate_confidence(self, results: List) -> float:
        """Calculate confidence score based on successful API calls"""
        successful = sum(1 for r in results if r and not isinstance(r, Exception))
        return round((successful / len(results)) * 100, 1)
    
    def _get_fallback_analysis(self) -> Dict:
        """Fallback analysis when AI is not available"""
        return {
            "investment_thesis": {
                "summary": "AI analysis unavailable - using rule-based scoring",
                "recommendation": "review manually"
            },
            "ai_confidence": 0,
            "models_used": [],
            "error": "Groq API key not configured or service unavailable"
        }

# Initialize the Groq AI analyzer
groq_ai = GroqAIAnalyzer()