"""
AI Investment Analyzer
Uses Claude API to generate investment thesis
"""

import os
from typing import Dict, List, Optional
from anthropic import Anthropic
import json

class AIInvestmentAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
    
    async def generate_thesis(self, company_data: Dict, analysis_result: Dict) -> Optional[Dict]:
        """Generate AI investment thesis using Claude"""
        if not self.client:
            # Return mock data if no API key
            return self._generate_mock_thesis(company_data, analysis_result)
        
        try:
            # Prepare context for Claude
            context = self._prepare_context(company_data, analysis_result)
            
            # Generate investment thesis
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.7,
                system="You are an expert venture capital investment analyst. Analyze companies and provide concise, actionable investment recommendations.",
                messages=[
                    {
                        "role": "user",
                        "content": f"""Analyze this company for venture capital investment potential:

{context}

Provide your analysis in this exact JSON format:
{{
    "summary": "2-sentence executive summary of the investment opportunity",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "risks": ["risk 1", "risk 2", "risk 3"],
    "recommendation": "STRONG BUY/BUY/HOLD/PASS with brief reasoning",
    "similarCompanies": [
        {{"name": "Company 1", "outcome": "Success/Failure", "reason": "Brief comparison"}},
        {{"name": "Company 2", "outcome": "Success/Failure", "reason": "Brief comparison"}}
    ]
}}"""
                    }
                ]
            )
            
            # Parse response
            thesis_text = response.content[0].text
            
            # Extract JSON from response
            try:
                # Find JSON in response
                import re
                json_match = re.search(r'\{.*\}', thesis_text, re.DOTALL)
                if json_match:
                    thesis = json.loads(json_match.group())
                    return thesis
                else:
                    # Fallback parsing
                    return self._parse_text_response(thesis_text)
            except:
                return self._parse_text_response(thesis_text)
                
        except Exception as e:
            print(f"AI analysis error: {str(e)}")
            return self._generate_mock_thesis(company_data, analysis_result)
    
    def _prepare_context(self, company_data: Dict, analysis_result: Dict) -> str:
        """Prepare context for AI analysis"""
        company = company_data.get("company", {})
        
        context_parts = [
            f"Company: {company.get('name', 'Unknown')}",
            f"Industry: {company.get('industry', 'Not specified')}",
            f"Employees: {company.get('employeeCount', 'Unknown')}",
            f"Description: {company.get('description', 'No description')}",
            f"\nInvestment Score: {analysis_result.get('investment_score', 0)}/100",
            f"\nScore Breakdown:"
        ]
        
        # Add score breakdown
        for score_type, score in analysis_result.get("score_breakdown", {}).items():
            context_parts.append(f"- {score_type.replace('_', ' ').title()}: {score}/100")
        
        # Add growth signals
        growth_signals = analysis_result.get("growth_signals", {})
        if growth_signals:
            context_parts.append("\nGrowth Signals:")
            for signal, value in growth_signals.items():
                if value and value != "Data not available":
                    context_parts.append(f"- {signal}: {value}")
        
        # Add data from sources
        context_parts.append("\nData Points:")
        
        # GitHub data
        github_data = company_data.get("github_data", {})
        if isinstance(github_data, dict) and not "error" in github_data:
            if github_data.get("repository_stats"):
                stats = github_data["repository_stats"]
                context_parts.append(f"- GitHub: {stats.get('total_repos', 0)} repos, {stats.get('total_stars', 0)} stars")
        
        # Patent data
        patent_data = company_data.get("patent_data", {})
        if isinstance(patent_data, dict) and not "error" in patent_data:
            context_parts.append(f"- Patents: {patent_data.get('total_patents', 0)} total, {patent_data.get('recent_patents', 0)} recent")
        
        # News data
        news_data = company_data.get("news_data", {})
        if isinstance(news_data, dict) and not "error" in news_data:
            metrics = news_data.get("metrics", {})
            context_parts.append(f"- Media: {metrics.get('sentiment_score', 50)}% positive sentiment, {metrics.get('news_velocity', 0)} articles/week")
        
        return "\n".join(context_parts)
    
    def _parse_text_response(self, text: str) -> Dict:
        """Parse non-JSON text response"""
        # Basic parsing fallback
        return {
            "summary": "Analysis complete. See detailed findings below.",
            "strengths": ["Strong market presence", "Growing team", "Innovation focus"],
            "risks": ["Market competition", "Scaling challenges", "Funding needs"],
            "recommendation": "HOLD - Requires further due diligence",
            "similarCompanies": []
        }
    
    def _generate_mock_thesis(self, company_data: Dict, analysis_result: Dict) -> Dict:
        """Generate mock thesis when API is not available"""
        score = analysis_result.get("investment_score", 50)
        company_name = company_data.get("company", {}).get("name", "Company")
        
        if score >= 80:
            return {
                "summary": f"{company_name} shows exceptional growth potential with strong fundamentals. The company demonstrates clear product-market fit and scalable business model.",
                "strengths": [
                    "Strong technical team with proven execution",
                    "Growing market with significant TAM",
                    "Clear competitive advantages and moat"
                ],
                "risks": [
                    "Intense competition from established players",
                    "Regulatory uncertainty in target markets",
                    "High burn rate requires additional funding"
                ],
                "recommendation": "STRONG BUY - Exceptional investment opportunity",
                "similarCompanies": [
                    {"name": "Stripe", "outcome": "Success", "reason": "Similar API-first approach and developer focus"},
                    {"name": "Plaid", "outcome": "Success", "reason": "Comparable B2B infrastructure play"}
                ]
            }
        elif score >= 60:
            return {
                "summary": f"{company_name} presents a solid investment opportunity with good growth metrics. The company shows promise but faces some execution risks.",
                "strengths": [
                    "Experienced founding team",
                    "Product gaining market traction",
                    "Reasonable valuation for the stage"
                ],
                "risks": [
                    "Unproven scalability of business model",
                    "Limited differentiation from competitors",
                    "Customer concentration risk"
                ],
                "recommendation": "BUY - Good opportunity with manageable risks",
                "similarCompanies": [
                    {"name": "Canva", "outcome": "Success", "reason": "Similar growth trajectory at this stage"},
                    {"name": "Quibi", "outcome": "Failure", "reason": "Risk of market timing issues"}
                ]
            }
        elif score >= 40:
            return {
                "summary": f"{company_name} shows potential but significant risks remain. The investment case requires careful consideration and additional due diligence.",
                "strengths": [
                    "Innovative approach to market problem",
                    "Early customer validation",
                    "Low current valuation"
                ],
                "risks": [
                    "Unclear path to profitability",
                    "Strong incumbent competition",
                    "Limited funding runway"
                ],
                "recommendation": "HOLD - Monitor progress before investing",
                "similarCompanies": [
                    {"name": "Blue Apron", "outcome": "Failure", "reason": "Similar unit economics challenges"},
                    {"name": "Warby Parker", "outcome": "Success", "reason": "Potential for similar turnaround"}
                ]
            }
        else:
            return {
                "summary": f"{company_name} faces significant challenges with limited growth indicators. The investment thesis is weak at current valuation.",
                "strengths": [
                    "Addressing real market need",
                    "Some technical capabilities",
                    "Passionate founding team"
                ],
                "risks": [
                    "Weak financial metrics and burn rate",
                    "Limited market traction after extended period",
                    "Significant competitive disadvantages"
                ],
                "recommendation": "PASS - Does not meet investment criteria",
                "similarCompanies": [
                    {"name": "Theranos", "outcome": "Failure", "reason": "Similar red flags in metrics"},
                    {"name": "Pets.com", "outcome": "Failure", "reason": "Comparable market timing issues"}
                ]
            }
    
    def _determine_recommendation(self, score: int) -> str:
        """Determine recommendation based on score"""
        if score >= 80:
            return "STRONG BUY"
        elif score >= 60:
            return "BUY"
        elif score >= 40:
            return "HOLD"
        else:
            return "PASS"