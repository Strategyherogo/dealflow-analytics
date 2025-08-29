"""
Advanced Multi-Model AI Orchestration for DealFlow Analytics
Implements MCP (Model Context Protocol) for enhanced context management
"""

import os
import json
import asyncio
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import httpx
from pydantic import BaseModel, Field
import numpy as np
from collections import defaultdict
import redis
import pickle

class AIProvider(Enum):
    """Available AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    COHERE = "cohere"
    MISTRAL = "mistral"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"
    LLAMA = "llama"
    PERPLEXITY = "perplexity"

class AIModelConfig(BaseModel):
    """Configuration for each AI model"""
    provider: AIProvider
    model_name: str
    api_key: str
    base_url: str
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_per_1k_tokens: float = 0.01
    speed_ms: int = 1000  # Average response time
    capabilities: List[str] = Field(default_factory=list)
    
class MCPContext(BaseModel):
    """Model Context Protocol for maintaining conversation state"""
    company_id: str
    session_id: str
    context_history: List[Dict[str, Any]] = Field(default_factory=list)
    enriched_data: Dict[str, Any] = Field(default_factory=dict)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    analysis_cache: Dict[str, Any] = Field(default_factory=dict)
    
class AIOrchestrator:
    """
    Advanced AI orchestration with multi-model support and MCP integration
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.models = self._initialize_models()
        self.mcp_contexts: Dict[str, MCPContext] = {}
        self.model_performance_stats = defaultdict(lambda: {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0,
            "avg_response_time": 0,
            "success_rate": 0
        })
        
    def _initialize_models(self) -> Dict[AIProvider, AIModelConfig]:
        """Initialize all available AI models"""
        models = {}
        
        # OpenAI GPT-4
        if os.getenv("OPENAI_API_KEY"):
            models[AIProvider.OPENAI] = AIModelConfig(
                provider=AIProvider.OPENAI,
                model_name="gpt-4-turbo-preview",
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url="https://api.openai.com/v1",
                max_tokens=8192,
                temperature=0.7,
                cost_per_1k_tokens=0.03,
                speed_ms=2000,
                capabilities=["analysis", "code", "vision", "function_calling"]
            )
        
        # Anthropic Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            models[AIProvider.ANTHROPIC] = AIModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-3-opus-20240229",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                base_url="https://api.anthropic.com/v1",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.015,
                speed_ms=1500,
                capabilities=["analysis", "code", "reasoning", "creative"]
            )
        
        # Groq (Ultra-fast)
        if os.getenv("GROQ_API_KEY"):
            models[AIProvider.GROQ] = AIModelConfig(
                provider=AIProvider.GROQ,
                model_name="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1",
                max_tokens=32768,
                temperature=0.7,
                cost_per_1k_tokens=0.001,
                speed_ms=100,  # Ultra-fast!
                capabilities=["analysis", "speed", "bulk_processing"]
            )
        
        # Cohere
        if os.getenv("COHERE_API_KEY"):
            models[AIProvider.COHERE] = AIModelConfig(
                provider=AIProvider.COHERE,
                model_name="command-r-plus",
                api_key=os.getenv("COHERE_API_KEY"),
                base_url="https://api.cohere.ai/v1",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.002,
                speed_ms=800,
                capabilities=["rag", "search", "classification"]
            )
        
        # Google Gemini
        if os.getenv("GOOGLE_API_KEY"):
            models[AIProvider.GOOGLE] = AIModelConfig(
                provider=AIProvider.GOOGLE,
                model_name="gemini-pro",
                api_key=os.getenv("GOOGLE_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1",
                max_tokens=8192,
                temperature=0.7,
                cost_per_1k_tokens=0.001,
                speed_ms=1000,
                capabilities=["multimodal", "reasoning", "code"]
            )
        
        # Perplexity (Web-aware)
        if os.getenv("PERPLEXITY_API_KEY"):
            models[AIProvider.PERPLEXITY] = AIModelConfig(
                provider=AIProvider.PERPLEXITY,
                model_name="pplx-70b-online",
                api_key=os.getenv("PERPLEXITY_API_KEY"),
                base_url="https://api.perplexity.ai",
                max_tokens=4096,
                temperature=0.7,
                cost_per_1k_tokens=0.005,
                speed_ms=2500,
                capabilities=["web_search", "real_time", "citations"]
            )
            
        return models
    
    async def orchestrate_analysis(
        self,
        company_data: Dict[str, Any],
        analysis_type: str = "comprehensive",
        user_tier: str = "premium"
    ) -> Dict[str, Any]:
        """
        Orchestrate multi-model analysis based on requirements and user tier
        """
        # Create or retrieve MCP context
        company_id = self._generate_company_id(company_data)
        context = self._get_or_create_context(company_id, company_data)
        
        # Check cache first
        cache_key = f"analysis:{company_id}:{analysis_type}"
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Select optimal model combination based on analysis type
        model_strategy = self._select_model_strategy(analysis_type, user_tier)
        
        # Execute parallel analysis with different models
        analysis_tasks = []
        for task_type, provider in model_strategy.items():
            if provider in self.models:
                analysis_tasks.append(
                    self._execute_model_task(
                        provider,
                        task_type,
                        company_data,
                        context
                    )
                )
        
        # Gather results
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Combine and synthesize results
        combined_analysis = self._synthesize_results(results, model_strategy)
        
        # Update MCP context
        self._update_context(context, combined_analysis)
        
        # Cache results
        if self.redis_client:
            self.redis_client.setex(
                cache_key,
                3600,  # 1 hour cache
                json.dumps(combined_analysis)
            )
        
        return combined_analysis
    
    def _select_model_strategy(
        self,
        analysis_type: str,
        user_tier: str
    ) -> Dict[str, AIProvider]:
        """
        Select optimal model combination based on analysis requirements
        """
        strategies = {
            "comprehensive": {
                "investment_thesis": AIProvider.OPENAI,
                "competitive_analysis": AIProvider.ANTHROPIC,
                "market_research": AIProvider.PERPLEXITY,
                "quick_metrics": AIProvider.GROQ,
                "technical_dd": AIProvider.GOOGLE,
                "risk_assessment": AIProvider.COHERE
            },
            "quick": {
                "summary": AIProvider.GROQ,
                "metrics": AIProvider.GROQ,
                "recommendation": AIProvider.GROQ
            },
            "deep_dive": {
                "detailed_thesis": AIProvider.ANTHROPIC,
                "market_analysis": AIProvider.PERPLEXITY,
                "competitor_intel": AIProvider.OPENAI,
                "technical_analysis": AIProvider.GOOGLE
            }
        }
        
        # Adjust based on user tier
        if user_tier == "free":
            # Use only fast, cheap models
            return {k: AIProvider.GROQ for k in strategies.get(analysis_type, {}).keys()}
        elif user_tier == "pro":
            # Mix of models
            return strategies.get(analysis_type, strategies["quick"])
        else:  # Enterprise
            # All premium models
            return strategies.get(analysis_type, strategies["comprehensive"])
    
    async def _execute_model_task(
        self,
        provider: AIProvider,
        task_type: str,
        company_data: Dict[str, Any],
        context: MCPContext
    ) -> Dict[str, Any]:
        """
        Execute a specific analysis task with the selected model
        """
        model_config = self.models[provider]
        
        # Prepare prompt based on task type
        prompt = self._prepare_prompt(task_type, company_data, context)
        
        # Make API call based on provider
        start_time = datetime.utcnow()
        
        try:
            if provider == AIProvider.OPENAI:
                result = await self._call_openai(model_config, prompt)
            elif provider == AIProvider.ANTHROPIC:
                result = await self._call_anthropic(model_config, prompt)
            elif provider == AIProvider.GROQ:
                result = await self._call_groq(model_config, prompt)
            elif provider == AIProvider.PERPLEXITY:
                result = await self._call_perplexity(model_config, prompt)
            elif provider == AIProvider.GOOGLE:
                result = await self._call_google(model_config, prompt)
            elif provider == AIProvider.COHERE:
                result = await self._call_cohere(model_config, prompt)
            else:
                result = {"error": f"Provider {provider} not implemented"}
            
            # Update performance stats
            elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_performance_stats(provider, elapsed_ms, True)
            
            return {
                "task_type": task_type,
                "provider": provider.value,
                "result": result,
                "elapsed_ms": elapsed_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self._update_performance_stats(provider, 0, False)
            return {
                "task_type": task_type,
                "provider": provider.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _call_openai(
        self,
        config: AIModelConfig,
        prompt: str
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "tokens_used": data.get("usage", {}).get("total_tokens", 0)
            }
    
    async def _call_anthropic(
        self,
        config: AIModelConfig,
        prompt: str
    ) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.base_url}/messages",
                headers={
                    "x-api-key": config.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["content"][0]["text"],
                "tokens_used": data.get("usage", {}).get("total_tokens", 0)
            }
    
    async def _call_groq(
        self,
        config: AIModelConfig,
        prompt: str
    ) -> Dict[str, Any]:
        """Call Groq API (ultra-fast)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature
                },
                timeout=10.0  # Groq is super fast
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "tokens_used": data.get("usage", {}).get("total_tokens", 0)
            }
    
    async def _call_perplexity(
        self,
        config: AIModelConfig,
        prompt: str
    ) -> Dict[str, Any]:
        """Call Perplexity API (with web search)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature,
                    "return_citations": True,
                    "search_recency_filter": "week"
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "citations": data.get("citations", []),
                "tokens_used": data.get("usage", {}).get("total_tokens", 0)
            }
    
    async def _call_google(
        self,
        config: AIModelConfig,
        prompt: str
    ) -> Dict[str, Any]:
        """Call Google Gemini API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.base_url}/models/{config.model_name}:generateContent",
                headers={"Content-Type": "application/json"},
                params={"key": config.api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": config.temperature,
                        "maxOutputTokens": config.max_tokens
                    }
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["candidates"][0]["content"]["parts"][0]["text"],
                "tokens_used": 0  # Google doesn't provide token count
            }
    
    async def _call_cohere(
        self,
        config: AIModelConfig,
        prompt: str
    ) -> Dict[str, Any]:
        """Call Cohere API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.base_url}/chat",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.model_name,
                    "message": prompt,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "connectors": [{"id": "web-search"}]  # Enable web search
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data["text"],
                "documents": data.get("documents", []),
                "tokens_used": data.get("meta", {}).get("billed_units", {}).get("input_tokens", 0)
            }
    
    def _prepare_prompt(
        self,
        task_type: str,
        company_data: Dict[str, Any],
        context: MCPContext
    ) -> str:
        """
        Prepare task-specific prompts with MCP context
        """
        base_context = f"""
        Company: {company_data.get('name')}
        Industry: {company_data.get('industry')}
        Description: {company_data.get('description')}
        Employee Count: {company_data.get('employeeCount')}
        Domain: {company_data.get('domain')}
        
        Additional Context from Previous Analysis:
        {json.dumps(context.enriched_data, indent=2) if context.enriched_data else 'None'}
        """
        
        prompts = {
            "investment_thesis": f"""
                {base_context}
                
                As a top-tier VC partner, provide a comprehensive investment thesis for this company.
                Include:
                1. Executive Summary (2-3 sentences)
                2. Key Investment Highlights (3-5 bullet points)
                3. Market Opportunity & TAM Analysis
                4. Competitive Advantages
                5. Growth Potential & Scalability
                6. Risk Factors & Mitigation
                7. Recommended Investment Strategy
                8. Expected Returns (1-3-5 year projections)
                
                Format as structured JSON.
            """,
            
            "competitive_analysis": f"""
                {base_context}
                
                Conduct a deep competitive analysis:
                1. Identify top 5-10 direct competitors
                2. Market positioning matrix
                3. Competitive advantages/disadvantages
                4. Market share estimates
                5. Technology differentiation
                6. Customer acquisition strategy comparison
                7. Pricing strategy analysis
                8. Partnership and ecosystem comparison
                
                Include specific company names and data points.
                Format as structured JSON.
            """,
            
            "market_research": f"""
                {base_context}
                
                Provide real-time market research:
                1. Current market size and growth rate
                2. Key market trends (last 6 months)
                3. Recent funding rounds in the sector
                4. Regulatory changes and impact
                5. Customer sentiment and demand signals
                6. Technology adoption curves
                7. Geographic market opportunities
                8. Exit opportunities and recent M&A activity
                
                Include citations and recent data points.
                Format as structured JSON.
            """,
            
            "technical_dd": f"""
                {base_context}
                
                Perform technical due diligence assessment:
                1. Technology stack evaluation
                2. Scalability assessment
                3. Security posture
                4. Data architecture
                5. API and integration capabilities
                6. Development velocity metrics
                7. Technical debt assessment
                8. Innovation pipeline
                9. IP and patent portfolio
                10. Technical team assessment
                
                Format as structured JSON with severity ratings.
            """,
            
            "risk_assessment": f"""
                {base_context}
                
                Comprehensive risk assessment:
                1. Market risks (competition, demand, timing)
                2. Technology risks (scalability, security, obsolescence)
                3. Financial risks (burn rate, runway, unit economics)
                4. Team risks (key person, experience gaps)
                5. Regulatory risks (compliance, legal)
                6. Customer concentration risks
                7. Supply chain risks
                8. Reputation risks
                
                Rate each risk: Low/Medium/High/Critical
                Provide mitigation strategies.
                Format as structured JSON.
            """,
            
            "quick_metrics": f"""
                {base_context}
                
                Provide key metrics snapshot:
                - Investment Score (0-100)
                - Growth Rate Estimate
                - Market Opportunity Score
                - Team Strength Score
                - Technology Score
                - Competitive Position
                - Exit Potential
                - Risk Level
                
                Format as structured JSON with brief explanations.
            """
        }
        
        return prompts.get(
            task_type,
            prompts["quick_metrics"]
        )
    
    def _synthesize_results(
        self,
        results: List[Dict[str, Any]],
        model_strategy: Dict[str, AIProvider]
    ) -> Dict[str, Any]:
        """
        Synthesize results from multiple models into cohesive analysis
        """
        synthesized = {
            "multi_model_analysis": True,
            "models_used": list(set(r.get("provider") for r in results if not r.get("error"))),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "confidence_score": 0,
            "synthesis": {}
        }
        
        # Aggregate successful results
        successful_results = [r for r in results if not r.get("error")]
        failed_results = [r for r in results if r.get("error")]
        
        # Calculate confidence based on success rate
        success_rate = len(successful_results) / len(results) if results else 0
        synthesized["confidence_score"] = round(success_rate * 100)
        
        # Combine results by task type
        for result in successful_results:
            task_type = result.get("task_type")
            if task_type:
                try:
                    content = result.get("result", {}).get("content", "")
                    if content:
                        # Try to parse as JSON if possible
                        try:
                            parsed_content = json.loads(content)
                        except:
                            parsed_content = {"raw_content": content}
                        
                        synthesized["synthesis"][task_type] = {
                            "data": parsed_content,
                            "provider": result.get("provider"),
                            "response_time_ms": result.get("elapsed_ms"),
                            "citations": result.get("result", {}).get("citations", [])
                        }
                except Exception as e:
                    print(f"Error processing result for {task_type}: {e}")
        
        # Add error summary if any
        if failed_results:
            synthesized["errors"] = [
                {
                    "task": r.get("task_type"),
                    "provider": r.get("provider"),
                    "error": r.get("error")
                }
                for r in failed_results
            ]
        
        # Generate executive summary from all results
        synthesized["executive_summary"] = self._generate_executive_summary(synthesized["synthesis"])
        
        return synthesized
    
    def _generate_executive_summary(self, synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate executive summary from synthesized results
        """
        summary = {
            "investment_recommendation": "STRONG BUY",
            "confidence": 85,
            "key_strengths": [],
            "key_risks": [],
            "action_items": []
        }
        
        # Extract key points from each analysis
        if "investment_thesis" in synthesis:
            thesis_data = synthesis["investment_thesis"].get("data", {})
            if isinstance(thesis_data, dict):
                summary["key_strengths"].extend(
                    thesis_data.get("highlights", [])[:3]
                )
        
        if "risk_assessment" in synthesis:
            risk_data = synthesis["risk_assessment"].get("data", {})
            if isinstance(risk_data, dict):
                # Extract high/critical risks
                for risk_type, risk_info in risk_data.items():
                    if isinstance(risk_info, dict) and risk_info.get("level") in ["High", "Critical"]:
                        summary["key_risks"].append(f"{risk_type}: {risk_info.get('description', '')}")
        
        if "competitive_analysis" in synthesis:
            competitive_data = synthesis["competitive_analysis"].get("data", {})
            if isinstance(competitive_data, dict):
                position = competitive_data.get("market_position", "Unknown")
                summary["competitive_position"] = position
        
        # Generate action items
        summary["action_items"] = [
            "Schedule deep-dive call with management team",
            "Conduct customer reference checks",
            "Review financial model and unit economics",
            "Assess technical architecture scalability",
            "Analyze competitive differentiation"
        ]
        
        return summary
    
    def _get_or_create_context(
        self,
        company_id: str,
        company_data: Dict[str, Any]
    ) -> MCPContext:
        """
        Get or create MCP context for a company
        """
        if company_id not in self.mcp_contexts:
            self.mcp_contexts[company_id] = MCPContext(
                company_id=company_id,
                session_id=hashlib.md5(
                    f"{company_id}:{datetime.utcnow().isoformat()}".encode()
                ).hexdigest(),
                enriched_data=company_data
            )
        
        return self.mcp_contexts[company_id]
    
    def _update_context(
        self,
        context: MCPContext,
        analysis: Dict[str, Any]
    ):
        """
        Update MCP context with new analysis results
        """
        context.context_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "multi_model",
            "summary": analysis.get("executive_summary")
        })
        
        # Update enriched data
        context.enriched_data.update({
            "last_analysis": datetime.utcnow().isoformat(),
            "models_used": analysis.get("models_used", []),
            "confidence_score": analysis.get("confidence_score")
        })
        
        # Cache analysis results
        context.analysis_cache[datetime.utcnow().isoformat()] = analysis
        
        # Trim history if too long
        if len(context.context_history) > 20:
            context.context_history = context.context_history[-20:]
    
    def _generate_company_id(self, company_data: Dict[str, Any]) -> str:
        """
        Generate unique company ID
        """
        unique_string = f"{company_data.get('name', '')}:{company_data.get('domain', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _update_performance_stats(
        self,
        provider: AIProvider,
        elapsed_ms: float,
        success: bool
    ):
        """
        Update model performance statistics
        """
        stats = self.model_performance_stats[provider]
        stats["total_requests"] += 1
        
        if success:
            # Update average response time
            prev_avg = stats["avg_response_time"]
            total = stats["total_requests"]
            stats["avg_response_time"] = (prev_avg * (total - 1) + elapsed_ms) / total
            
            # Update success rate
            stats["success_rate"] = (
                (stats["success_rate"] * (total - 1) + 100) / total
            )
        else:
            # Update success rate for failure
            total = stats["total_requests"]
            stats["success_rate"] = (
                stats["success_rate"] * (total - 1) / total
            )
    
    async def natural_language_query(
        self,
        query: str,
        context: Optional[MCPContext] = None
    ) -> Dict[str, Any]:
        """
        Process natural language queries about companies
        
        Examples:
        - "Find me Series A SaaS companies with 50%+ growth"
        - "Show companies similar to Stripe but earlier stage"
        - "Which companies have the best engineering teams?"
        """
        # Use Perplexity or GPT-4 for query understanding
        provider = AIProvider.PERPLEXITY if AIProvider.PERPLEXITY in self.models else AIProvider.OPENAI
        
        if provider not in self.models:
            return {"error": "No suitable model available for NL queries"}
        
        prompt = f"""
        Parse this investment query and return structured search criteria:
        
        Query: {query}
        
        Return JSON with:
        - stage: funding stage filter
        - industry: industry/vertical filter
        - metrics: key metrics to evaluate
        - growth_rate: minimum growth rate
        - geography: location filter
        - other_criteria: any other specific requirements
        - similar_to: companies to use as reference
        """
        
        result = await self._execute_model_task(
            provider,
            "query_parsing",
            {"query": query},
            context or MCPContext(company_id="query", session_id="temp")
        )
        
        return result
    
    def get_model_recommendations(
        self,
        task_type: str,
        budget: float = None,
        speed_required: bool = False
    ) -> List[AIProvider]:
        """
        Get recommended models for a specific task
        """
        recommendations = []
        
        # Task-specific recommendations
        task_preferences = {
            "quick_analysis": [AIProvider.GROQ, AIProvider.GOOGLE],
            "deep_analysis": [AIProvider.ANTHROPIC, AIProvider.OPENAI],
            "web_research": [AIProvider.PERPLEXITY, AIProvider.COHERE],
            "technical": [AIProvider.OPENAI, AIProvider.GOOGLE],
            "creative": [AIProvider.ANTHROPIC, AIProvider.OPENAI]
        }
        
        preferred = task_preferences.get(task_type, [AIProvider.GROQ])
        
        for provider in preferred:
            if provider in self.models:
                config = self.models[provider]
                
                # Check budget constraint
                if budget and config.cost_per_1k_tokens > budget:
                    continue
                
                # Check speed requirement
                if speed_required and config.speed_ms > 1000:
                    continue
                
                recommendations.append(provider)
        
        return recommendations