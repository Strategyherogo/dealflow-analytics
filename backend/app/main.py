from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
import asyncio
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv
import redis
import json
import hashlib
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="DealFlow Analytics API",
    description="VC investment analysis API with free data sources",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://ifcleeldbnhpnabnnfeohhammpfnbacf",
        "chrome-extension://*",
        "http://localhost:*",
        "http://localhost:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Redis connection for caching
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )
    redis_client.ping()
except:
    redis_client = None
    print("Warning: Redis not available, caching disabled")

# Request/Response Models
class CompanyAnalysisRequest(BaseModel):
    name: str
    domain: Optional[str] = None
    linkedinUrl: Optional[HttpUrl] = None
    industry: Optional[str] = None
    employeeCount: Optional[str] = None
    description: Optional[str] = None

class GrowthSignals(BaseModel):
    employeeGrowth: Optional[str] = None
    webTraffic: Optional[str] = None
    techStack: Optional[str] = None
    patentActivity: Optional[str] = None
    newsVelocity: Optional[str] = None
    githubActivity: Optional[str] = None
    engineeringScore: Optional[str] = None
    mediaSentiment: Optional[str] = None
    hiringSignal: Optional[str] = None
    webTech: Optional[str] = None

class MarketAnalysis(BaseModel):
    tam: Optional[int] = None
    growthRate: Optional[float] = None
    competitors: Optional[List[str]] = None

class AIThesis(BaseModel):
    summary: str
    strengths: List[str]
    risks: List[str]
    recommendation: str
    similarCompanies: Optional[List[Dict[str, str]]] = None

class CompanyAnalysisResponse(BaseModel):
    investmentScore: int
    fundingHistory: Optional[List[Dict[str, Any]]] = None
    growthSignals: Optional[GrowthSignals] = None
    marketAnalysis: Optional[MarketAnalysis] = None
    aiThesis: Optional[AIThesis] = None
    intelligence: Optional[Dict[str, Any]] = None
    competitiveIntelligence: Optional[Dict[str, Any]] = None
    technicalDueDiligence: Optional[Dict[str, Any]] = None
    investmentSignals: Optional[Dict[str, Any]] = None
    socialSentiment: Optional[Dict[str, Any]] = None
    dataMetrics: Optional[Dict[str, Any]] = None
    hiringData: Optional[Dict[str, Any]] = None
    dataSources: List[str]
    analysisTimestamp: str

# Data source integrations
from .data_sources.sec_edgar import sec_edgar
from .data_sources.github_api import github_api
from .data_sources.wikipedia_api import wikipedia_api
from .data_sources.uspto_api import uspto_api
from .data_sources.news_api import news_api

from .analyzer import CompanyAnalyzer
from .real_ai_analyzer import real_ai_analyzer

# Optional imports - PDF generation
try:
    from .report_generator import PDFReportGenerator
    from .enhanced_pdf_generator import EnhancedPDFReportGenerator
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PDF generation not available - reportlab not installed")

from .real_data_sources import real_data_fetcher
from .enhanced_data_fetcher import enhanced_intel
from .competitive_intelligence import competitive_intel
from .technical_due_diligence import tech_dd_analyzer
from .investment_signals import investment_signals
from .social_sentiment_analyzer import social_sentiment
from .data_metrics_engine import data_metrics_engine
from .hiring_tracker import HiringTracker
from .csv_exporter import CSVExporter

# Initialize analyzers
company_analyzer = CompanyAnalyzer()
if PDF_AVAILABLE:
    pdf_generator = PDFReportGenerator()
    enhanced_pdf_generator = EnhancedPDFReportGenerator()
else:
    pdf_generator = None
    enhanced_pdf_generator = None
hiring_tracker = HiringTracker()

@app.get("/")
async def root():
    return {
        "message": "DealFlow Analytics API",
        "version": "1.0.0",
        "endpoints": ["/api/analyze", "/api/export-pdf", "/api/company-updates"]
    }

@app.post("/api/analyze", response_model=CompanyAnalysisResponse)
async def analyze_company(request: CompanyAnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze a company using multiple free data sources
    """
    # Create cache key
    company_name = request.name or "unknown"
    cache_key = f"analysis:{hashlib.md5(company_name.lower().encode()).hexdigest()}"
    
    # Check cache
    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    
    try:
        # First, try to get REAL data
        real_data_tasks = []
        
        # Get real GitHub data
        real_data_tasks.append(real_data_fetcher.get_github_activity(request.name))
        
        # Get real news sentiment
        real_data_tasks.append(real_data_fetcher.get_news_sentiment(request.name))
        
        # Get domain info if available
        if request.domain:
            real_data_tasks.append(real_data_fetcher.get_domain_info(request.domain))
        else:
            # Create a coroutine that returns a dict with found: False
            async def no_domain():
                return {"found": False}
            real_data_tasks.append(no_domain()) 
        
        # Get Crunchbase data
        real_data_tasks.append(real_data_fetcher.get_crunchbase_data(request.name))
        
        # Get comprehensive intelligence
        real_data_tasks.append(enhanced_intel.get_comprehensive_intelligence(request.name, request.domain))
        
        # Execute real data gathering
        real_results = await asyncio.gather(*real_data_tasks, return_exceptions=True)
        
        # Process real data first
        real_data = {
            "github": real_results[0] if not isinstance(real_results[0], Exception) else {"found": False},
            "news": real_results[1] if not isinstance(real_results[1], Exception) else {"found": False},
            "domain": real_results[2] if not isinstance(real_results[2], Exception) else {"found": False},
            "crunchbase": real_results[3] if not isinstance(real_results[3], Exception) else {"found": False},
            "intelligence": real_results[4] if not isinstance(real_results[4], Exception) else {"found": False}
        }
        
        # Now run advanced analyses that depend on initial data
        print(f"DEBUG: request.name={request.name}, request.industry={request.industry}, request.domain={request.domain}")
        advanced_tasks = [
            competitive_intel.analyze_competitive_landscape(request.name, request.industry or "technology", request.domain),
            tech_dd_analyzer.analyze_technical_stack(request.name, request.domain, real_data.get("github")),
            social_sentiment.analyze_social_sentiment(request.name, request.domain)
        ]
        
        advanced_results = await asyncio.gather(*advanced_tasks, return_exceptions=True)
        
        # Add advanced analyses to real data
        real_data["competitive_intelligence"] = advanced_results[0] if not isinstance(advanced_results[0], Exception) else {"found": False}
        real_data["technical_dd"] = advanced_results[1] if not isinstance(advanced_results[1], Exception) else {"found": False}
        real_data["social_sentiment"] = advanced_results[2] if not isinstance(advanced_results[2], Exception) else {"found": False}
        
        # Calculate real investment score
        real_score_data = await real_data_fetcher.calculate_investment_score(real_data)
        
        # Also gather data from original sources for additional context
        data_tasks = []
        if request.domain and ".com" in request.domain:
            data_tasks.append(sec_edgar.get_company_filings(request.name))
        data_tasks.append(github_api.get_organization_data(request.name))
        data_tasks.append(wikipedia_api.get_company_info(request.name))
        data_tasks.append(uspto_api.search_patents(request.name))
        data_tasks.append(news_api.get_recent_news(request.name))
        
        results = await asyncio.gather(*data_tasks, return_exceptions=True)
        
        # Combine all data INCLUDING REAL DATA
        combined_data = {
            "company": request.dict(),
            "real_data": real_data,  # Add real data
            "real_score": real_score_data,  # Add real score
            "sec_data": results[0] if len(results) > 0 and not isinstance(results[0], Exception) else None,
            "github_data": results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None,
            "wikipedia_data": results[2] if len(results) > 2 and not isinstance(results[2], Exception) else None,
            "patent_data": results[3] if len(results) > 3 and not isinstance(results[3], Exception) else None,
            "news_data": results[4] if len(results) > 4 and not isinstance(results[4], Exception) else None
        }
        
        # Analyze combined data
        analysis_result = await company_analyzer.analyze(combined_data)
        
        # Override with real data if available
        if real_score_data.get("score"):
            analysis_result["investment_score"] = real_score_data["score"]
        
        # Add real growth signals
        growth_signals = analysis_result.get("growth_signals", {})
        
        # Add GitHub metrics
        if real_data.get("github", {}).get("found"):
            github = real_data["github"]
            growth_signals["techStack"] = ", ".join(github.get("tech_stack", []))[:50] if github.get("tech_stack") else "Not available"
            growth_signals["githubActivity"] = f"{github.get('public_repos', 0)} repos, {github.get('total_stars', 0)} stars"
            if github.get("engineering_score"):
                growth_signals["engineeringScore"] = f"{github['engineering_score']}/100"
        
        # Add news sentiment
        if real_data.get("news", {}).get("found"):
            news = real_data["news"]
            growth_signals["mediaSentiment"] = f"{news.get('sentiment_score', 50)}/100 ({news.get('momentum', 'neutral')})"
            growth_signals["newsVelocity"] = f"{news.get('news_count', 0)} recent articles"
        
        # Add domain signals
        if real_data.get("domain", {}).get("found"):
            domain = real_data["domain"]
            if domain.get("has_careers"):
                growth_signals["hiringSignal"] = "Actively hiring"
            if domain.get("tech_stack"):
                growth_signals["webTech"] = ", ".join(domain["tech_stack"])
        
        # Generate investment signals based on all collected data
        all_data_for_signals = {
            "company": request.dict(),
            **real_data,
            **analysis_result,
            "marketAnalysis": analysis_result.get("market_analysis", {})
        }
        investment_signals_data = await investment_signals.generate_investment_signals(all_data_for_signals)
        
        # Get hiring data
        hiring_data = await hiring_tracker.get_comprehensive_hiring_data(
            request.name,
            request.domain
        )
        
        # Calculate data-driven metrics
        # First add basic metrics to the data
        all_data_for_signals["growth_metrics"] = {}
        all_data_for_signals["traction_metrics"] = {}
        all_data_for_signals["efficiency_metrics"] = {}
        all_data_for_signals["talent_metrics"] = {}
        all_data_for_signals["market_metrics"] = {}
        all_data_for_signals["innovation_metrics"] = {}
        all_data_for_signals["hiring_data"] = hiring_data
        
        data_metrics = await data_metrics_engine.calculate_data_driven_metrics(all_data_for_signals)
        
        # Generate AI insights with real data context
        ai_insights = await real_ai_analyzer.generate_thesis(combined_data, analysis_result)
        
        # Add real insights to AI thesis
        if ai_insights and real_score_data.get("signals"):
            # Prepend real signals to strengths
            real_strengths = real_score_data["signals"][:3]
            if "strengths" in ai_insights:
                ai_insights["strengths"] = real_strengths + ai_insights["strengths"][:2]
            else:
                ai_insights["strengths"] = real_strengths
        
        # Prepare response
        response = CompanyAnalysisResponse(
            investmentScore=analysis_result["investment_score"],
            fundingHistory=analysis_result.get("funding_history"),
            growthSignals=GrowthSignals(**growth_signals),
            marketAnalysis=MarketAnalysis(**analysis_result.get("market_analysis", {})),
            aiThesis=AIThesis(**ai_insights) if ai_insights else None,
            intelligence=real_data.get("intelligence", {}),
            competitiveIntelligence=real_data.get("competitive_intelligence", {}),
            technicalDueDiligence=real_data.get("technical_dd", {}),
            investmentSignals=investment_signals_data,
            socialSentiment=real_data.get("social_sentiment", {}),
            dataMetrics=data_metrics,
            hiringData=hiring_data,
            dataSources=analysis_result.get("data_sources", []) + ["GitHub API", "Google News", "Domain Analysis", "Company Website", "LinkedIn", "G2 Reviews", "DuckDuckGo Search", "Social Media Analysis", "Quantitative Metrics Engine", "Hiring Platforms"],
            analysisTimestamp=datetime.utcnow().isoformat()
        )
        
        # Cache result
        if redis_client:
            redis_client.setex(
                cache_key,
                86400,  # 24 hour TTL
                json.dumps(response.dict())
            )
        
        # Background task to update metrics
        background_tasks.add_task(
            track_analysis_metrics,
            request.name,
            analysis_result["investment_score"]
        )
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()  # This will print the full traceback to console
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/export-pdf")
async def export_pdf(request: Dict[str, Any]):
    """
    Generate PDF investment memo
    """
    if not PDF_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="PDF generation not available. Install reportlab and matplotlib."
        )
    try:
        # Ensure analysis data includes intelligence
        analysis_data = request["analysis"]
        
        # Get the intelligence data from the analysis if available
        if "intelligence" not in analysis_data and request.get("company"):
            # Fetch fresh intelligence if not in the request
            intelligence = await enhanced_intel.get_comprehensive_intelligence(
                request["company"].get("name"),
                request["company"].get("domain")
            )
            analysis_data["intelligence"] = intelligence
        
        # Add company data to analysis for PDF generator
        analysis_data["company"] = request.get("company", {})
        
        # Use enhanced PDF generator for better reports
        pdf_path = await enhanced_pdf_generator.generate_enhanced_memo(
            request["company"],
            analysis_data
        )
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"DealFlow_{request['company']['name']}_Analysis.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.post("/api/export-csv")
async def export_csv(request: Dict[str, Any]):
    """
    Generate CSV export of analysis data
    Secure CSV generation with sanitization
    """
    try:
        # Extract company and analysis data
        company_data = request.get("company", {})
        analysis_data = request.get("analysis", {})
        
        # Generate CSV
        csv_data = CSVExporter.generate_analysis_csv(company_data, analysis_data)
        
        # Create filename
        company_name = company_data.get("name", "Unknown").replace(" ", "_")
        filename = f"DealFlow_{company_name}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Return CSV response
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV generation failed: {str(e)}")

@app.post("/api/company-updates")
async def check_company_updates(request: Dict[str, Any]):
    """
    Check for updates on tracked companies
    """
    try:
        # Gather latest data
        latest_data = await company_analyzer.get_latest_data(
            request["name"],
            request.get("domain"),
            request.get("lastChecked")
        )
        
        # Compare with previous data
        has_changes = await company_analyzer.detect_significant_changes(
            request,
            latest_data
        )
        
        return {
            "hasSignificantChanges": has_changes,
            "data": latest_data,
            "summary": company_analyzer.summarize_changes(request, latest_data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update check failed: {str(e)}")

# Utility functions
async def track_analysis_metrics(company_name: str, score: int):
    """Track usage metrics for analysis"""
    if redis_client:
        # Increment analysis counter
        redis_client.hincrby("metrics:analyses", "total", 1)
        redis_client.hincrby("metrics:analyses", f"score_{score//10}0", 1)
        
        # Track company
        redis_client.sadd("metrics:companies", company_name)
        
        # Daily metrics
        today = datetime.utcnow().strftime("%Y-%m-%d")
        redis_client.hincrby(f"metrics:daily:{today}", "analyses", 1)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "redis": "connected" if redis_client else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/privacy-policy")
async def privacy_policy():
    """Serve privacy policy HTML"""
    privacy_file = Path(__file__).parent.parent.parent / "privacy-policy.html"
    if privacy_file.exists():
        return FileResponse(privacy_file, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Privacy policy not found")

# Rate limiting middleware
from .middleware import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)