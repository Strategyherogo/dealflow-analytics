"""
Enhanced PDF Report Generator with Professional VC-Grade Analysis
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY, TA_LEFT
from reportlab.platypus.flowables import HRFlowable
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics import renderPDF
from reportlab.platypus.flowables import Flowable
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from datetime import datetime, timedelta
import io
import os
from typing import Dict, Any, List
import tempfile
import numpy as np

class ExecutiveSummaryBox(Flowable):
    """Custom flowable for executive summary box"""
    def __init__(self, width, height, data):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.data = data
    
    def draw(self):
        # Draw box
        self.canv.setStrokeColor(colors.HexColor('#3498db'))
        self.canv.setFillColor(colors.HexColor('#ecf5ff'))
        self.canv.roundRect(0, 0, self.width, self.height, 10, fill=1, stroke=1)
        
        # Add content
        y = self.height - 20
        self.canv.setFillColor(colors.HexColor('#2c3e50'))
        self.canv.setFont('Helvetica-Bold', 14)
        self.canv.drawString(20, y, "KEY INVESTMENT HIGHLIGHTS")
        
        y -= 30
        self.canv.setFont('Helvetica', 10)
        for item in self.data[:5]:
            self.canv.drawString(30, y, f"• {item}")
            y -= 20

class EnhancedPDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup enhanced custom styles for professional look"""
        # Executive Summary style
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=18,
            borderColor=colors.HexColor('#3498db'),
            borderWidth=2,
            borderPadding=10,
            backColor=colors.HexColor('#f8f9fa')
        ))
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=self.styles['Title'],
            fontSize=36,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=40,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section Title
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=30,
            spaceAfter=15,
            borderColor=colors.HexColor('#3498db'),
            borderWidth=0,
            borderPadding=0,
            leftIndent=0,
            fontName='Helvetica-Bold'
        ))
        
        # Metric Box style
        self.styles.add(ParagraphStyle(
            name='MetricBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            backColor=colors.HexColor('#f0f4f8'),
            borderColor=colors.HexColor('#d1d9e0'),
            borderWidth=1,
            borderPadding=8
        ))
        
        # Highlight style
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#27ae60'),
            fontName='Helvetica-Bold'
        ))
        
        # Risk style
        self.styles.add(ParagraphStyle(
            name='Risk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#e74c3c'),
            fontName='Helvetica-Bold'
        ))
        
        # Quote style
        self.styles.add(ParagraphStyle(
            name='Quote',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#555555'),
            leftIndent=30,
            rightIndent=30,
            fontName='Helvetica-Oblique',
            borderColor=colors.HexColor('#3498db'),
            borderWidth=2,
            borderPadding=10,
            borderRadius=5
        ))
    
    async def generate_enhanced_memo(self, company_data: Dict, analysis_data: Dict) -> str:
        """Generate enhanced investment memo PDF with professional analysis"""
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        filename = temp_file.name
        temp_file.close()
        
        # Create document with custom page setup
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=60,
            title=f"{company_data.get('name', 'Company')} - Investment Analysis",
            author="DealFlow Analytics",
            subject="Confidential Investment Memo"
        )
        
        # Build enhanced content
        story = []
        
        # Cover Page
        story.extend(self._create_enhanced_cover_page(company_data, analysis_data))
        story.append(PageBreak())
        
        # Executive Summary with Key Metrics Dashboard
        story.extend(self._create_executive_dashboard(company_data, analysis_data))
        story.append(PageBreak())
        
        # Investment Thesis & Recommendation
        story.extend(self._create_investment_recommendation(analysis_data))
        
        # Market Opportunity & TAM Analysis
        story.extend(self._create_market_opportunity_analysis(analysis_data))
        
        # Product Deep Dive & Competitive Positioning
        story.extend(self._create_product_deep_dive(company_data, analysis_data))
        
        # Financial Analysis & Unit Economics
        story.extend(self._create_financial_analysis(analysis_data))
        
        # Team & Execution Analysis
        story.extend(self._create_team_analysis(analysis_data))
        
        # Growth Strategy & Scalability
        story.extend(self._create_growth_strategy(analysis_data))
        
        # Risk Matrix & Mitigation
        story.extend(self._create_risk_matrix(analysis_data))
        
        # Exit Strategy & Return Scenarios
        story.extend(self._create_exit_scenarios(analysis_data))
        
        # Due Diligence Checklist
        story.extend(self._create_dd_checklist(analysis_data))
        
        # Appendix with Raw Data
        story.extend(self._create_appendix(analysis_data))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        
        return filename
    
    def _create_enhanced_cover_page(self, company_data: Dict, analysis_data: Dict) -> List:
        """Create professional cover page with key metrics"""
        elements = []
        
        # Add space at top
        elements.append(Spacer(1, 1.5*inch))
        
        # Company Name
        elements.append(Paragraph(
            f"<b>{company_data.get('name', 'Company Name')}</b>",
            self.styles['CoverTitle']
        ))
        
        # Tagline
        intelligence = analysis_data.get("intelligence", {})
        if intelligence.get("product", {}).get("description"):
            tagline = intelligence["product"]["description"][:150]
            elements.append(Paragraph(
                f"<i>{tagline}</i>",
                ParagraphStyle(
                    name='Tagline',
                    parent=self.styles['Normal'],
                    fontSize=14,
                    textColor=colors.HexColor('#7f8c8d'),
                    alignment=TA_CENTER,
                    spaceAfter=30
                )
            ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Investment Memo Title
        elements.append(Paragraph(
            "CONFIDENTIAL INVESTMENT MEMORANDUM",
            ParagraphStyle(
                name='MemoTitle',
                parent=self.styles['Normal'],
                fontSize=16,
                textColor=colors.HexColor('#34495e'),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceAfter=40
            )
        ))
        
        # Key Metrics Grid
        score = analysis_data.get("investmentScore", 0)
        score_color = self._get_score_color(score)
        
        # Create metrics table
        metrics_data = []
        
        # Row 1
        metrics_data.append([
            f"<b>Investment Score</b>\n<font size='20' color='{score_color}'>{score}/100</font>",
            f"<b>Sector</b>\n{company_data.get('industry', 'Technology')}",
            f"<b>Stage</b>\n{self._determine_stage(analysis_data)}"
        ])
        
        # Row 2
        team_size = "N/A"
        if analysis_data.get("hiringData", {}).get("team_size", {}).get("current"):
            team_size = f"{analysis_data['hiringData']['team_size']['current']:,}"
        
        funding = self._get_latest_funding(analysis_data)
        valuation = "N/A"
        if analysis_data.get("dataMetrics", {}).get("valuation_estimate", {}).get("estimated_valuation"):
            val = analysis_data["dataMetrics"]["valuation_estimate"]["estimated_valuation"]
            valuation = f"${val/1000000:.1f}M"
        
        metrics_data.append([
            f"<b>Team Size</b>\n{team_size}",
            f"<b>Last Funding</b>\n{funding}",
            f"<b>Est. Valuation</b>\n{valuation}"
        ])
        
        # Row 3
        growth_rate = "N/A"
        if analysis_data.get("dataMetrics", {}).get("growth_metrics", {}).get("employee_growth_rate"):
            growth_rate = f"{analysis_data['dataMetrics']['growth_metrics']['employee_growth_rate']:.0f}%"
        
        burn_rate = "N/A"
        if analysis_data.get("dataMetrics", {}).get("efficiency_metrics", {}).get("burn_rate"):
            burn = analysis_data["dataMetrics"]["efficiency_metrics"]["burn_rate"]
            burn_rate = f"${burn/1000:.0f}K/mo"
        
        runway = "N/A"
        if analysis_data.get("dataMetrics", {}).get("efficiency_metrics", {}).get("runway_months"):
            runway = f"{analysis_data['dataMetrics']['efficiency_metrics']['runway_months']:.0f} months"
        
        metrics_data.append([
            f"<b>Growth Rate</b>\n{growth_rate} YoY",
            f"<b>Burn Rate</b>\n{burn_rate}",
            f"<b>Runway</b>\n{runway}"
        ])
        
        t = Table(metrics_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d9e0')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ]))
        
        elements.append(t)
        
        # Date and Confidentiality
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph(
            f"Prepared: {datetime.now().strftime('%B %d, %Y')}",
            ParagraphStyle(
                name='Date',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_CENTER,
                spaceAfter=10
            )
        ))
        
        elements.append(Paragraph(
            "STRICTLY CONFIDENTIAL - PROPRIETARY AND CONFIDENTIAL INFORMATION",
            ParagraphStyle(
                name='Confidential',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#e74c3c'),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
        ))
        
        return elements
    
    def _create_executive_dashboard(self, company_data: Dict, analysis_data: Dict) -> List:
        """Create executive dashboard with key metrics and visualizations"""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.3*inch))
        
        # Investment Highlights Box
        highlights = self._extract_investment_highlights(analysis_data)
        if highlights:
            box = ExecutiveSummaryBox(7*inch, 120, highlights)
            elements.append(box)
            elements.append(Spacer(1, 0.3*inch))
        
        # One-line thesis
        ai_thesis = analysis_data.get("aiThesis", {})
        if ai_thesis.get("summary"):
            elements.append(Paragraph(
                f"<b>Investment Thesis:</b> {ai_thesis['summary'][:200]}",
                self.styles['ExecutiveSummary']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Key Metrics Dashboard
        elements.append(Paragraph("<b>KEY METRICS AT A GLANCE</b>", self.styles['SectionTitle']))
        
        # Create metrics visualization
        metrics_viz = self._create_metrics_visualization(analysis_data)
        if metrics_viz:
            elements.append(metrics_viz)
            elements.append(Spacer(1, 0.3*inch))
        
        # Quick Stats Table
        quick_stats = []
        
        # Customer metrics
        if analysis_data.get("intelligence", {}).get("customers", {}).get("estimated_customers"):
            customers = analysis_data["intelligence"]["customers"]["estimated_customers"]
            quick_stats.append(["Estimated Customers", customers])
        
        # Revenue metrics
        if analysis_data.get("dataMetrics", {}).get("efficiency_metrics", {}).get("revenue_per_employee"):
            rev_per_emp = analysis_data["dataMetrics"]["efficiency_metrics"]["revenue_per_employee"]
            quick_stats.append(["Revenue/Employee", f"${rev_per_emp:,.0f}"])
        
        # GitHub metrics
        if analysis_data.get("dataMetrics", {}).get("traction_metrics", {}).get("github_stars"):
            stars = analysis_data["dataMetrics"]["traction_metrics"]["github_stars"]
            quick_stats.append(["GitHub Stars", f"{stars:,}"])
        
        # News sentiment
        if analysis_data.get("socialSentiment", {}).get("news", {}).get("sentiment_score"):
            sentiment = analysis_data["socialSentiment"]["news"]["sentiment_score"]
            quick_stats.append(["Media Sentiment", f"{sentiment}% positive"])
        
        # Market opportunity
        if analysis_data.get("competitiveIntelligence", {}).get("market_opportunity_score"):
            opp_score = analysis_data["competitiveIntelligence"]["market_opportunity_score"]
            quick_stats.append(["Market Opportunity", f"{opp_score}/100"])
        
        # Technical score
        if analysis_data.get("technicalDueDiligence", {}).get("technical_score"):
            tech_score = analysis_data["technicalDueDiligence"]["technical_score"]
            quick_stats.append(["Technical Score", f"{tech_score}/100"])
        
        if quick_stats:
            # Split into two columns
            col1 = quick_stats[:len(quick_stats)//2]
            col2 = quick_stats[len(quick_stats)//2:]
            
            # Pad shorter column
            while len(col1) < len(col2):
                col1.append(["", ""])
            while len(col2) < len(col1):
                col2.append(["", ""])
            
            combined_data = []
            for i in range(len(col1)):
                combined_data.append([
                    col1[i][0], col1[i][1],
                    col2[i][0] if i < len(col2) else "", 
                    col2[i][1] if i < len(col2) else ""
                ])
            
            t = Table(combined_data, colWidths=[1.7*inch, 1.5*inch, 1.7*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ]))
            elements.append(t)
        
        return elements
    
    def _create_investment_recommendation(self, analysis_data: Dict) -> List:
        """Create investment recommendation section with clear action items"""
        elements = []
        
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("INVESTMENT RECOMMENDATION", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Recommendation Box
        ai_thesis = analysis_data.get("aiThesis", {})
        recommendation = ai_thesis.get("recommendation", "HOLD")
        rec_color = self._get_recommendation_color(recommendation)
        
        # Create recommendation box
        rec_data = [[
            f"<font size='16' color='{rec_color}'><b>{recommendation.upper()}</b></font>"
        ]]
        
        t = Table(rec_data, colWidths=[7*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOX', (0, 0), (-1, -1), 2, rec_color),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2*inch))
        
        # Investment Rationale
        elements.append(Paragraph("<b>Investment Rationale</b>", self.styles['SectionTitle']))
        
        # Strengths
        if ai_thesis.get("strengths"):
            elements.append(Paragraph("<b>Key Strengths:</b>", self.styles['Highlight']))
            for strength in ai_thesis["strengths"][:5]:
                elements.append(Paragraph(f"✓ {strength}", ParagraphStyle(
                    name='Strength',
                    parent=self.styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#27ae60'),
                    leftIndent=20,
                    spaceAfter=8
                )))
            elements.append(Spacer(1, 0.2*inch))
        
        # Risks
        if ai_thesis.get("risks"):
            elements.append(Paragraph("<b>Key Risks:</b>", self.styles['Risk']))
            for risk in ai_thesis["risks"][:5]:
                elements.append(Paragraph(f"⚠ {risk}", ParagraphStyle(
                    name='RiskItem',
                    parent=self.styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#e74c3c'),
                    leftIndent=20,
                    spaceAfter=8
                )))
            elements.append(Spacer(1, 0.2*inch))
        
        # Proposed Terms (if applicable)
        if recommendation in ["STRONG BUY", "BUY"]:
            elements.append(Paragraph("<b>Proposed Investment Terms</b>", self.styles['SectionTitle']))
            
            terms_data = []
            
            # Valuation
            if analysis_data.get("dataMetrics", {}).get("valuation_estimate", {}).get("estimated_valuation"):
                val = analysis_data["dataMetrics"]["valuation_estimate"]["estimated_valuation"]
                terms_data.append(["Pre-money Valuation", f"${val/1000000:.1f}M"])
            
            # Suggested investment
            terms_data.append(["Suggested Investment", "$500K - $2M"])
            terms_data.append(["Investment Type", "Series A Preferred"])
            terms_data.append(["Board Representation", "1 Board Seat + 1 Observer"])
            terms_data.append(["Pro-rata Rights", "Yes"])
            
            if terms_data:
                t = Table(terms_data, colWidths=[3*inch, 4*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ]))
                elements.append(t)
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_market_opportunity_analysis(self, analysis_data: Dict) -> List:
        """Create detailed market opportunity analysis"""
        elements = []
        
        elements.append(Paragraph("MARKET OPPORTUNITY", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # TAM/SAM/SOM Analysis
        market_data = analysis_data.get("marketAnalysis", {})
        if market_data.get("tam"):
            tam = market_data["tam"]
            sam = tam * 0.3  # Estimate SAM as 30% of TAM
            som = tam * 0.05  # Estimate SOM as 5% of TAM
            
            market_size_data = [
                ["Market Segment", "Size", "Description"],
                ["TAM (Total Addressable Market)", f"${tam/1000000000:.1f}B", "Total market demand for product/service"],
                ["SAM (Serviceable Addressable Market)", f"${sam/1000000000:.1f}B", "Market segment company can reach"],
                ["SOM (Serviceable Obtainable Market)", f"${som/1000000000:.1f}B", "Realistic market share in near term"]
            ]
            
            t = Table(market_size_data, colWidths=[2.5*inch, 1.5*inch, 3*inch])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.3*inch))
        
        # Market Growth
        if market_data.get("growthRate"):
            elements.append(Paragraph(
                f"<b>Market Growth Rate:</b> {market_data['growthRate']:.1f}% CAGR",
                self.styles['Highlight']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Market Dynamics
        competitive_data = analysis_data.get("competitiveIntelligence", {})
        if competitive_data.get("market_position"):
            pos = competitive_data["market_position"]
            elements.append(Paragraph("<b>Market Dynamics</b>", self.styles['SectionTitle']))
            
            dynamics_data = []
            if pos.get("market_segment"):
                dynamics_data.append(["Market Segment", pos["market_segment"]])
            if pos.get("market_maturity"):
                dynamics_data.append(["Market Maturity", pos["market_maturity"]])
            if pos.get("competitive_intensity"):
                dynamics_data.append(["Competitive Intensity", pos["competitive_intensity"]])
            
            if dynamics_data:
                t = Table(dynamics_data, colWidths=[2*inch, 5*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(t)
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_product_deep_dive(self, company_data: Dict, analysis_data: Dict) -> List:
        """Create comprehensive product analysis with competitive comparison"""
        elements = []
        
        elements.append(Paragraph("PRODUCT & COMPETITIVE ANALYSIS", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        intelligence = analysis_data.get("intelligence", {})
        
        # Product Overview
        if intelligence.get("product", {}).get("description"):
            elements.append(Paragraph("<b>Product Overview</b>", self.styles['SectionTitle']))
            elements.append(Paragraph(
                intelligence["product"]["description"],
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Core Features & Differentiation
        if intelligence.get("product", {}).get("features"):
            elements.append(Paragraph("<b>Core Features & Capabilities</b>", self.styles['SectionTitle']))
            
            features = intelligence["product"]["features"][:8]
            # Split into two columns
            mid = len(features) // 2
            col1 = features[:mid]
            col2 = features[mid:]
            
            feature_data = []
            for i in range(max(len(col1), len(col2))):
                row = []
                if i < len(col1):
                    row.extend(["✓", col1[i]])
                else:
                    row.extend(["", ""])
                if i < len(col2):
                    row.extend(["✓", col2[i]])
                else:
                    row.extend(["", ""])
                feature_data.append(row)
            
            t = Table(feature_data, colWidths=[0.3*inch, 3.2*inch, 0.3*inch, 3.2*inch])
            t.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#27ae60')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.3*inch))
        
        # Competitive SWOT Analysis
        elements.append(Paragraph("<b>SWOT Analysis</b>", self.styles['SectionTitle']))
        
        swot_data = self._generate_swot_analysis(analysis_data)
        swot_table = [
            ["STRENGTHS", "WEAKNESSES"],
            [swot_data["strengths"], swot_data["weaknesses"]],
            ["OPPORTUNITIES", "THREATS"],
            [swot_data["opportunities"], swot_data["threats"]]
        ]
        
        t = Table(swot_table, colWidths=[3.5*inch, 3.5*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#27ae60')),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#e74c3c')),
            ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#3498db')),
            ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d0d0d0')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_financial_analysis(self, analysis_data: Dict) -> List:
        """Create detailed financial analysis section"""
        elements = []
        
        elements.append(Paragraph("FINANCIAL ANALYSIS", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Unit Economics
        elements.append(Paragraph("<b>Unit Economics & Key Metrics</b>", self.styles['SectionTitle']))
        
        metrics = analysis_data.get("dataMetrics", {})
        financial_data = []
        
        # Revenue metrics
        if metrics.get("efficiency_metrics", {}).get("revenue_per_employee"):
            rev_per_emp = metrics["efficiency_metrics"]["revenue_per_employee"]
            financial_data.append(["Revenue per Employee", f"${rev_per_emp:,.0f}", self._get_metric_status(rev_per_emp, 150000)])
        
        # Burn metrics
        if metrics.get("efficiency_metrics", {}).get("burn_rate"):
            burn = metrics["efficiency_metrics"]["burn_rate"]
            financial_data.append(["Monthly Burn Rate", f"${burn:,.0f}", "Monitor"])
        
        # Runway
        if metrics.get("efficiency_metrics", {}).get("runway_months"):
            runway = metrics["efficiency_metrics"]["runway_months"]
            status = "Healthy" if runway > 18 else "Caution" if runway > 12 else "Critical"
            financial_data.append(["Runway", f"{runway:.1f} months", status])
        
        # Capital efficiency
        if metrics.get("efficiency_metrics", {}).get("capital_efficiency"):
            cap_eff = metrics["efficiency_metrics"]["capital_efficiency"]
            status = "Excellent" if cap_eff > 1.5 else "Good" if cap_eff > 1 else "Poor"
            financial_data.append(["Capital Efficiency", f"{cap_eff:.2f}x", status])
        
        # CAC/LTV (estimated)
        financial_data.append(["Est. CAC", "$500-2000", "Industry Avg"])
        financial_data.append(["Est. LTV", "$5000-20000", "To Verify"])
        financial_data.append(["LTV/CAC Ratio", "3-10x", "Healthy"])
        
        if financial_data:
            financial_data.insert(0, ["Metric", "Value", "Status"])
            t = Table(financial_data, colWidths=[2.5*inch, 2*inch, 2.5*inch])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.3*inch))
        
        # Growth Trajectory Chart
        if metrics.get("growth_metrics"):
            elements.append(Paragraph("<b>Growth Trajectory</b>", self.styles['SectionTitle']))
            growth_chart = self._create_growth_chart(metrics["growth_metrics"])
            if growth_chart:
                elements.append(growth_chart)
                elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_team_analysis(self, analysis_data: Dict) -> List:
        """Create team and execution analysis"""
        elements = []
        
        elements.append(Paragraph("TEAM & EXECUTION", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        hiring_data = analysis_data.get("hiringData", {})
        
        # Team Composition & Growth
        if hiring_data.get("team_size"):
            elements.append(Paragraph("<b>Team Composition & Growth</b>", self.styles['SectionTitle']))
            
            team_data = []
            team_size = hiring_data["team_size"]
            
            if team_size.get("current"):
                team_data.append(["Current Team Size", f"{team_size['current']:,} employees"])
            if team_size.get("growth_rate"):
                team_data.append(["YoY Growth Rate", f"{team_size['growth_rate']:.0f}%"])
            if hiring_data.get("total_open_positions"):
                team_data.append(["Open Positions", str(hiring_data["total_open_positions"])])
            
            # Department breakdown
            if hiring_data.get("engineering_roles"):
                team_data.append(["Engineering Roles", str(hiring_data["engineering_roles"])])
            if hiring_data.get("sales_roles"):
                team_data.append(["Sales Roles", str(hiring_data["sales_roles"])])
            if hiring_data.get("product_roles"):
                team_data.append(["Product Roles", str(hiring_data["product_roles"])])
            
            if team_data:
                t = Table(team_data, colWidths=[3*inch, 4*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Hiring Signals
        if hiring_data.get("hiring_insights"):
            elements.append(Paragraph("<b>Hiring Insights</b>", self.styles['SectionTitle']))
            for insight in hiring_data["hiring_insights"][:3]:
                elements.append(Paragraph(f"• {insight}", self.styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Technical Capabilities
        tech_dd = analysis_data.get("technicalDueDiligence", {})
        if tech_dd.get("technical_score"):
            elements.append(Paragraph("<b>Technical Capabilities</b>", self.styles['SectionTitle']))
            elements.append(Paragraph(
                f"Technical Score: {tech_dd['technical_score']}/100",
                self.styles['Highlight'] if tech_dd['technical_score'] > 70 else self.styles['Risk']
            ))
            
            if tech_dd.get("technical_strengths"):
                for strength in tech_dd["technical_strengths"][:3]:
                    elements.append(Paragraph(f"✓ {strength}", self.styles['Normal']))
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_growth_strategy(self, analysis_data: Dict) -> List:
        """Create growth strategy and scalability analysis"""
        elements = []
        
        elements.append(Paragraph("GROWTH STRATEGY & SCALABILITY", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Growth Drivers
        elements.append(Paragraph("<b>Key Growth Drivers</b>", self.styles['SectionTitle']))
        
        growth_drivers = []
        
        # Product-led growth
        if analysis_data.get("intelligence", {}).get("product", {}).get("features"):
            growth_drivers.append("• Product-led growth through feature expansion")
        
        # Market expansion
        if analysis_data.get("marketAnalysis", {}).get("growthRate", 0) > 10:
            growth_drivers.append("• Expanding market with high growth rate")
        
        # Team scaling
        if analysis_data.get("hiringData", {}).get("total_open_positions", 0) > 10:
            growth_drivers.append("• Aggressive hiring indicating scaling phase")
        
        # Geographic expansion
        if analysis_data.get("hiringData", {}).get("remote_positions", 0) > 0:
            growth_drivers.append("• Geographic expansion through remote hiring")
        
        for driver in growth_drivers:
            elements.append(Paragraph(driver, self.styles['Normal']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Scalability Factors
        elements.append(Paragraph("<b>Scalability Assessment</b>", self.styles['SectionTitle']))
        
        scalability_data = [
            ["Factor", "Status", "Impact"],
            ["Technology Stack", "Modern & Scalable", "High"],
            ["Unit Economics", "Improving", "Medium"],
            ["Market Size", f"${analysis_data.get('marketAnalysis', {}).get('tam', 0)/1000000000:.1f}B TAM", "High"],
            ["Team Quality", "Strong Technical Team", "High"],
            ["Capital Efficiency", f"{analysis_data.get('dataMetrics', {}).get('efficiency_metrics', {}).get('capital_efficiency', 1):.1f}x", "Medium"]
        ]
        
        t = Table(scalability_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_risk_matrix(self, analysis_data: Dict) -> List:
        """Create comprehensive risk matrix"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("RISK ASSESSMENT MATRIX", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#e74c3c')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Risk Matrix Table
        risk_data = [
            ["Risk Category", "Likelihood", "Impact", "Mitigation Strategy"],
            ["Market Risk", "Medium", "High", "Diversified customer base, multiple verticals"],
            ["Competition", "High", "Medium", "Strong differentiation, rapid innovation"],
            ["Technology Risk", "Low", "High", "Modern tech stack, strong engineering team"],
            ["Execution Risk", "Medium", "High", "Experienced team, clear roadmap"],
            ["Financial Risk", "Medium", "Medium", f"{analysis_data.get('dataMetrics', {}).get('efficiency_metrics', {}).get('runway_months', 12):.0f} months runway"],
            ["Regulatory Risk", "Low", "Low", "Compliant with current regulations"],
            ["Team Risk", "Low", "High", "Strong retention, aggressive hiring"]
        ]
        
        t = Table(risk_data, colWidths=[1.8*inch, 1.3*inch, 1.3*inch, 2.6*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            # Color code likelihood
            ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#f39c12')),  # Medium
            ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#e74c3c')),  # High
            ('TEXTCOLOR', (1, 3), (1, 3), colors.HexColor('#27ae60')),  # Low
            ('TEXTCOLOR', (1, 4), (1, 4), colors.HexColor('#f39c12')),  # Medium
            ('TEXTCOLOR', (1, 5), (1, 5), colors.HexColor('#f39c12')),  # Medium
            ('TEXTCOLOR', (1, 6), (1, 6), colors.HexColor('#27ae60')),  # Low
            ('TEXTCOLOR', (1, 7), (1, 7), colors.HexColor('#27ae60')),  # Low
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Key Risk Factors
        ai_thesis = analysis_data.get("aiThesis", {})
        if ai_thesis.get("risks"):
            elements.append(Paragraph("<b>Key Risk Factors</b>", self.styles['SectionTitle']))
            for i, risk in enumerate(ai_thesis["risks"][:5], 1):
                elements.append(Paragraph(f"{i}. {risk}", self.styles['Risk']))
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_exit_scenarios(self, analysis_data: Dict) -> List:
        """Create exit strategy scenarios"""
        elements = []
        
        elements.append(Paragraph("EXIT STRATEGY & RETURN SCENARIOS", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Current Valuation
        current_val = 50  # Default $50M
        if analysis_data.get("dataMetrics", {}).get("valuation_estimate", {}).get("estimated_valuation"):
            current_val = analysis_data["dataMetrics"]["valuation_estimate"]["estimated_valuation"] / 1000000
        
        # Exit Scenarios Table
        exit_data = [
            ["Scenario", "Timeline", "Exit Valuation", "Multiple", "IRR"],
            ["Conservative", "5 years", f"${current_val * 3:.0f}M", "3x", "25%"],
            ["Base Case", "4 years", f"${current_val * 5:.0f}M", "5x", "50%"],
            ["Optimistic", "3 years", f"${current_val * 10:.0f}M", "10x", "115%"],
            ["Home Run", "5 years", f"${current_val * 20:.0f}M", "20x", "82%"]
        ]
        
        t = Table(exit_data, colWidths=[1.5*inch, 1.3*inch, 1.5*inch, 1.3*inch, 1.3*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3*inch))
        
        # Potential Acquirers
        elements.append(Paragraph("<b>Potential Exit Routes</b>", self.styles['SectionTitle']))
        
        exit_routes = [
            "• Strategic Acquisition by major tech company",
            "• Financial buyer (PE) rollup strategy",
            "• IPO (if reaching $100M+ ARR)",
            "• Secondary sale to growth equity fund",
            "• Management buyout with PE backing"
        ]
        
        for route in exit_routes:
            elements.append(Paragraph(route, self.styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Comparable Exits
        ai_thesis = analysis_data.get("aiThesis", {})
        if ai_thesis.get("similarCompanies"):
            elements.append(Paragraph("<b>Comparable Company Exits</b>", self.styles['SectionTitle']))
            
            comp_data = [["Company", "Exit Value", "Multiple", "Acquirer"]]
            for comp in ai_thesis["similarCompanies"][:5]:
                comp_data.append([
                    comp.get("name", ""),
                    comp.get("outcome", "N/A"),
                    "N/A",
                    "Strategic"
                ])
            
            t = Table(comp_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(t)
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_dd_checklist(self, analysis_data: Dict) -> List:
        """Create due diligence checklist"""
        elements = []
        
        elements.append(Paragraph("DUE DILIGENCE CHECKLIST", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # DD Checklist Table
        dd_data = [
            ["Category", "Item", "Status", "Priority"],
            ["Legal", "Corporate structure & cap table", "Pending", "High"],
            ["Legal", "IP ownership & patents", "Pending", "High"],
            ["Legal", "Employment agreements", "Pending", "Medium"],
            ["Financial", "Historical financials (3 years)", "Pending", "High"],
            ["Financial", "Unit economics validation", "Pending", "High"],
            ["Financial", "Customer contracts review", "Pending", "High"],
            ["Technical", "Code review & architecture", "Partial", "High"],
            ["Technical", "Security audit", "Pending", "Medium"],
            ["Technical", "Scalability assessment", "Complete", "High"],
            ["Commercial", "Customer references (10+)", "Pending", "High"],
            ["Commercial", "Churn analysis", "Pending", "High"],
            ["Commercial", "Competitive deep dive", "Complete", "Medium"],
            ["Team", "Background checks", "Pending", "High"],
            ["Team", "Reference checks", "Pending", "High"],
            ["Team", "Culture assessment", "Pending", "Medium"]
        ]
        
        t = Table(dd_data, colWidths=[1.5*inch, 3*inch, 1.2*inch, 1.2*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            # Color code status
            ('TEXTCOLOR', (2, 1), (2, -1), colors.HexColor('#f39c12')),  # Pending
            ('TEXTCOLOR', (2, 7), (2, 7), colors.HexColor('#e67e22')),  # Partial
            ('TEXTCOLOR', (2, 9), (2, 9), colors.HexColor('#27ae60')),  # Complete
            ('TEXTCOLOR', (2, 12), (2, 12), colors.HexColor('#27ae60')),  # Complete
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_appendix(self, analysis_data: Dict) -> List:
        """Create appendix with additional data"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("APPENDIX - DATA SOURCES", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Data Sources
        sources = analysis_data.get("dataSources", [])
        if sources:
            elements.append(Paragraph("<b>Data Sources Used</b>", self.styles['SectionTitle']))
            for source in sources:
                elements.append(Paragraph(f"• {source}", self.styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Analysis Timestamp
        elements.append(Paragraph(
            f"<i>Analysis conducted on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
            self.styles['Normal']
        ))
        
        # Disclaimer
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            "DISCLAIMER",
            self.styles['SectionTitle']
        ))
        elements.append(Paragraph(
            "This memorandum contains confidential and proprietary information and is provided for informational purposes only. "
            "The information contained herein is based on publicly available data and automated analysis. "
            "No representation or warranty, express or implied, is made as to the accuracy or completeness of the information. "
            "Recipients should conduct their own due diligence before making any investment decisions.",
            ParagraphStyle(
                name='Disclaimer',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_JUSTIFY
            )
        ))
        
        return elements
    
    # Helper methods
    def _get_score_color(self, score: int) -> str:
        """Get color based on score"""
        if score >= 80:
            return '#27ae60'
        elif score >= 60:
            return '#f39c12'
        elif score >= 40:
            return '#e67e22'
        else:
            return '#e74c3c'
    
    def _get_recommendation_color(self, recommendation: str) -> str:
        """Get color based on recommendation"""
        rec_upper = recommendation.upper()
        if "STRONG BUY" in rec_upper:
            return colors.HexColor('#27ae60')
        elif "BUY" in rec_upper:
            return colors.HexColor('#2ecc71')
        elif "HOLD" in rec_upper:
            return colors.HexColor('#f39c12')
        else:
            return colors.HexColor('#e74c3c')
    
    def _determine_stage(self, analysis_data: Dict) -> str:
        """Determine company stage"""
        team_size = 0
        if analysis_data.get("hiringData", {}).get("team_size", {}).get("current"):
            team_size = analysis_data["hiringData"]["team_size"]["current"]
        
        if team_size < 10:
            return "Pre-Seed"
        elif team_size < 25:
            return "Seed"
        elif team_size < 100:
            return "Series A"
        elif team_size < 250:
            return "Series B"
        else:
            return "Series C+"
    
    def _get_latest_funding(self, analysis_data: Dict) -> str:
        """Get latest funding information"""
        funding_history = analysis_data.get("fundingHistory", [])
        if funding_history and len(funding_history) > 0:
            latest = funding_history[0]
            amount = latest.get("amount", "Undisclosed")
            round_type = latest.get("round", "Unknown")
            return f"{amount} ({round_type})"
        return "No funding data"
    
    def _extract_investment_highlights(self, analysis_data: Dict) -> List[str]:
        """Extract key investment highlights"""
        highlights = []
        
        # Score-based highlight
        score = analysis_data.get("investmentScore", 0)
        if score >= 70:
            highlights.append(f"High investment score of {score}/100")
        
        # Market size
        if analysis_data.get("marketAnalysis", {}).get("tam"):
            tam = analysis_data["marketAnalysis"]["tam"]
            highlights.append(f"Large TAM of ${tam/1000000000:.1f}B")
        
        # Growth rate
        if analysis_data.get("dataMetrics", {}).get("growth_metrics", {}).get("employee_growth_rate", 0) > 30:
            rate = analysis_data["dataMetrics"]["growth_metrics"]["employee_growth_rate"]
            highlights.append(f"Rapid growth at {rate:.0f}% YoY")
        
        # Technical strength
        if analysis_data.get("technicalDueDiligence", {}).get("technical_score", 0) > 70:
            highlights.append("Strong technical foundation")
        
        # Customer traction
        if analysis_data.get("intelligence", {}).get("customers", {}).get("estimated_customers"):
            highlights.append("Proven customer traction")
        
        return highlights[:5]
    
    def _create_metrics_visualization(self, analysis_data: Dict) -> Image:
        """Create metrics visualization chart"""
        try:
            # Create a simple bar chart of key scores
            fig, ax = plt.subplots(figsize=(7, 3))
            
            categories = []
            scores = []
            
            # Investment Score
            if analysis_data.get("investmentScore"):
                categories.append("Overall")
                scores.append(analysis_data["investmentScore"])
            
            # Technical Score
            if analysis_data.get("technicalDueDiligence", {}).get("technical_score"):
                categories.append("Technical")
                scores.append(analysis_data["technicalDueDiligence"]["technical_score"])
            
            # Market Opportunity
            if analysis_data.get("competitiveIntelligence", {}).get("market_opportunity_score"):
                categories.append("Market")
                scores.append(analysis_data["competitiveIntelligence"]["market_opportunity_score"])
            
            # Data Score
            if analysis_data.get("dataMetrics", {}).get("quantitative_score"):
                categories.append("Data")
                scores.append(analysis_data["dataMetrics"]["quantitative_score"])
            
            if categories and scores:
                colors_list = [self._get_score_color(s) for s in scores]
                bars = ax.bar(categories, scores, color=colors_list)
                
                ax.set_ylim(0, 100)
                ax.set_ylabel('Score')
                ax.set_title('Investment Metrics Dashboard')
                ax.grid(axis='y', alpha=0.3)
                
                # Add value labels on bars
                for bar, score in zip(bars, scores):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{score:.0f}', ha='center', va='bottom')
                
                plt.tight_layout()
                
                # Save to buffer
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                plt.close()
                
                return Image(buf, width=6*inch, height=2.5*inch)
        except:
            return None
    
    def _generate_swot_analysis(self, analysis_data: Dict) -> Dict:
        """Generate SWOT analysis from data"""
        swot = {
            "strengths": "",
            "weaknesses": "",
            "opportunities": "",
            "threats": ""
        }
        
        # Strengths
        strengths = []
        if analysis_data.get("aiThesis", {}).get("strengths"):
            strengths = analysis_data["aiThesis"]["strengths"][:3]
        swot["strengths"] = "\n".join([f"• {s}" for s in strengths]) if strengths else "• Strong product foundation\n• Growing team\n• Technical capabilities"
        
        # Weaknesses
        weaknesses = []
        if analysis_data.get("dataMetrics", {}).get("efficiency_metrics", {}).get("burn_rate", 0) > 500000:
            weaknesses.append("High burn rate")
        if analysis_data.get("dataMetrics", {}).get("efficiency_metrics", {}).get("runway_months", 24) < 12:
            weaknesses.append("Limited runway")
        swot["weaknesses"] = "\n".join([f"• {w}" for w in weaknesses]) if weaknesses else "• Limited market presence\n• Unproven unit economics"
        
        # Opportunities  
        opportunities = [
            "Large addressable market",
            "Growing industry demand",
            "Expansion opportunities"
        ]
        swot["opportunities"] = "\n".join([f"• {o}" for o in opportunities])
        
        # Threats
        threats = []
        if analysis_data.get("aiThesis", {}).get("risks"):
            threats = analysis_data["aiThesis"]["risks"][:3]
        swot["threats"] = "\n".join([f"• {t}" for t in threats]) if threats else "• Competitive pressure\n• Market volatility\n• Execution risk"
        
        return swot
    
    def _create_growth_chart(self, growth_metrics: Dict) -> Image:
        """Create growth trajectory chart"""
        try:
            fig, ax = plt.subplots(figsize=(6, 3))
            
            # Mock historical data based on growth rate
            growth_rate = growth_metrics.get("employee_growth_rate", 30) / 100
            current = 100
            months = list(range(-12, 13, 3))
            values = []
            
            for month in months:
                if month <= 0:
                    values.append(current * (1 + growth_rate) ** (month/12))
                else:
                    values.append(current * (1 + growth_rate * 0.8) ** (month/12))  # Slightly lower projected
            
            ax.plot(months, values, marker='o', linewidth=2, markersize=6, color='#3498db')
            ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
            ax.fill_between(months, values, alpha=0.2, color='#3498db')
            
            ax.set_xlabel('Months from Present')
            ax.set_ylabel('Relative Growth')
            ax.set_title('Growth Trajectory')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            return Image(buf, width=5*inch, height=2.5*inch)
        except:
            return None
    
    def _get_metric_status(self, value: float, benchmark: float) -> str:
        """Get status based on benchmark"""
        if value >= benchmark * 1.2:
            return "Excellent"
        elif value >= benchmark:
            return "Good"
        elif value >= benchmark * 0.7:
            return "Average"
        else:
            return "Below Average"
    
    def _add_footer(self, canvas, doc):
        """Add footer to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawString(inch, 0.5*inch, f"DealFlow Analytics - Confidential - Page {doc.page}")
        canvas.drawString(6.5*inch, 0.5*inch, datetime.now().strftime("%B %Y"))
        canvas.restoreState()