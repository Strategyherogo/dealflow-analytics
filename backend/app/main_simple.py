"""
Simplified main.py for DealFlow Analytics API
Focuses on core functionality and payment endpoints
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="DealFlow Analytics API",
    description="VC investment analysis platform with payment support",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple request models
class CompanyAnalysisRequest(BaseModel):
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "DealFlow Analytics API",
        "version": "2.0.0",
        "endpoints": [
            "/api/analyze",
            "/api/create-checkout",
            "/api/verify-subscription",
            "/health"
        ]
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

# Payment endpoints - Simple test mode implementation
@app.post("/api/create-checkout")
async def create_checkout_session(request: Dict[str, Any]):
    """Create Stripe checkout session for subscription"""
    plan = request.get("plan", "pro")
    customer_id = request.get("customerId", f"cust_{datetime.now().timestamp()}")
    
    # Test mode response
    return {
        "checkoutUrl": f"https://checkout.stripe.com/test/{plan}_checkout",
        "sessionId": f"test_session_{plan}_{customer_id[:8]}",
        "plan": plan,
        "testMode": True
    }

@app.post("/api/verify-subscription")
async def verify_subscription(request: Dict[str, Any]):
    """Verify if a customer has an active subscription"""
    customer_id = request.get("customerId", "")
    
    # Test mode - simulate some customers having subscriptions
    has_subscription = len(customer_id) > 0 and ord(customer_id[0]) % 2 == 0
    
    if has_subscription:
        return {
            "active": True,
            "plan": "pro",
            "status": "active",
            "current_period_end": "2025-10-01T00:00:00Z",
            "testMode": True
        }
    return {
        "active": False,
        "testMode": True
    }

@app.post("/api/cancel-subscription")
async def cancel_subscription(request: Dict[str, Any]):
    """Cancel a customer's subscription"""
    return {
        "status": "cancelled",
        "message": "Test subscription cancelled",
        "testMode": True
    }

@app.post("/api/webhook")
async def handle_stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    return {
        "status": "success",
        "message": "Webhook received (test mode)",
        "testMode": True
    }

# Simplified analyze endpoint
@app.post("/api/analyze")
async def analyze_company(request: CompanyAnalysisRequest):
    """Analyze a company and return investment score"""
    
    # Simple scoring logic for testing
    score = 75
    if "ai" in request.name.lower() or "tech" in request.name.lower():
        score = 85
    if "blockchain" in request.name.lower() or "crypto" in request.name.lower():
        score = 65
    
    return {
        "company": request.name,
        "investmentScore": score,
        "analysis": {
            "strengths": ["Strong market position", "Innovative technology"],
            "risks": ["Market competition", "Regulatory uncertainty"],
            "recommendation": "CONSIDER" if score >= 70 else "PASS"
        },
        "timestamp": datetime.now().isoformat()
    }

# Legacy endpoints for compatibility
@app.post("/api/export-pdf")
async def export_pdf(request: Dict[str, Any]):
    """Export analysis as PDF (placeholder)"""
    return {
        "status": "success",
        "message": "PDF export not available in simplified mode",
        "data": request
    }

@app.get("/api/company-updates")
async def get_company_updates():
    """Get company updates (placeholder)"""
    return {
        "updates": [],
        "message": "Updates not available in simplified mode"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)