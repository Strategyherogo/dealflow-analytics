#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.real_data_sources import real_data_fetcher
from app.enhanced_data_fetcher import enhanced_intel
from app.competitive_intelligence import competitive_intel
from app.technical_due_diligence import tech_dd_analyzer
from app.investment_signals import investment_signals
from app.social_sentiment_analyzer import social_sentiment

async def test_analyze():
    print("Testing data fetchers...")
    
    company_name = "Cohere"
    domain = "cohere.com"
    
    try:
        # Test each component individually
        print("\n1. Testing real data fetcher...")
        real_data = await real_data_fetcher.get_real_investment_data(company_name, domain)
        print(f"✓ Real data fetcher OK")
        
        print("\n2. Testing enhanced intelligence...")
        enhanced = await enhanced_intel.get_comprehensive_intelligence(company_name, domain)
        print(f"✓ Enhanced intelligence OK")
        
        print("\n3. Testing competitive intelligence...")
        competitive = await competitive_intel.analyze_competitive_landscape(company_name, "AI", domain)
        print(f"✓ Competitive intelligence OK")
        
        print("\n4. Testing technical DD...")
        tech_dd = await tech_dd_analyzer.analyze_technical_stack(company_name, domain)
        print(f"✓ Technical DD OK")
        
        print("\n5. Testing social sentiment...")
        social = await social_sentiment.analyze_social_sentiment(company_name, domain)
        print(f"✓ Social sentiment OK")
        
        print("\n6. Testing investment signals...")
        all_data = {
            "company": {"name": company_name, "domain": domain},
            **real_data,
            "intelligence": enhanced,
            "competitive_intelligence": competitive,
            "technical_dd": tech_dd,
            "social_sentiment": social
        }
        signals = await investment_signals.generate_investment_signals(all_data)
        print(f"✓ Investment signals OK")
        
        print("\n✅ All components working!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analyze())