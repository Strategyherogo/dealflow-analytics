"""
PDF Report Generator
Creates professional investment memos like Sequoia
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus.flowables import HRFlowable
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from datetime import datetime
import io
import os
from typing import Dict, Any, List
import tempfile

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom styles for professional look"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=20,
            spaceAfter=12,
            borderColor=colors.HexColor('#3498db'),
            borderWidth=0,
            borderPadding=0
        ))
        
        # Subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceBefore=12,
            spaceAfter=8
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d')
        ))
    
    async def generate_memo(self, company_data: Dict, analysis_data: Dict) -> str:
        """Generate investment memo PDF"""
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        filename = temp_file.name
        temp_file.close()
        
        # Create document
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Title page
        story.extend(self._create_title_page(company_data, analysis_data))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(company_data, analysis_data))
        
        # Company overview
        story.extend(self._create_company_overview(company_data))
        
        # Product & Customer Intelligence
        story.extend(self._create_product_intelligence_section(company_data, analysis_data))
        
        # Financial metrics
        story.extend(self._create_financial_section(analysis_data))
        
        # Market analysis
        story.extend(self._create_market_analysis(analysis_data))
        
        # Competitive Intelligence
        story.extend(self._create_competitive_intelligence_section(analysis_data))
        
        # Technical Due Diligence
        story.extend(self._create_technical_dd_section(analysis_data))
        
        # Recent News & Media Coverage
        story.extend(self._create_news_section(analysis_data))
        
        # Investment Signals & Data Metrics
        story.extend(self._create_investment_signals_section(analysis_data))
        
        # Hiring & Team Growth
        story.extend(self._create_hiring_section(analysis_data))
        
        # Investment thesis
        story.extend(self._create_investment_thesis(analysis_data))
        
        # Risk analysis
        story.extend(self._create_risk_analysis(analysis_data))
        
        # Comparable companies
        story.extend(self._create_comparables(analysis_data))
        
        # Data sources
        story.extend(self._create_data_sources(analysis_data))
        
        # Build PDF
        doc.build(story)
        
        return filename
    
    def _create_title_page(self, company_data: Dict, analysis_data: Dict) -> List:
        """Create title page"""
        elements = []
        
        # Logo placeholder
        elements.append(Spacer(1, 2*inch))
        
        # Title
        company_name = company_data.get("name", "Unknown Company")
        elements.append(Paragraph(
            f"<b>{company_name}</b>",
            self.styles['CustomTitle']
        ))
        
        # Subtitle
        elements.append(Paragraph(
            "Investment Analysis Memorandum",
            self.styles['CustomSubheading']
        ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Key metrics table
        score = analysis_data.get("investmentScore", 0)
        score_color = self._get_score_color(score)
        
        data = [
            ["Investment Score", f"<font color='{score_color}'><b>{score}/100</b></font>"],
            ["Analysis Date", datetime.now().strftime("%B %d, %Y")],
            ["Industry", company_data.get("industry", "Not specified")],
            ["Employees", company_data.get("employeeCount", "Not available")]
        ]
        
        t = Table(data, colWidths=[3*inch, 2*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(t)
        
        # Footer
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(
            "DealFlow Analytics | Confidential",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#95a5a6'),
                alignment=TA_CENTER
            )
        ))
        
        return elements
    
    def _create_executive_summary(self, company_data: Dict, analysis_data: Dict) -> List:
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # AI thesis summary
        ai_thesis = analysis_data.get("aiThesis", {})
        if ai_thesis and ai_thesis.get("summary"):
            elements.append(Paragraph(ai_thesis["summary"], self.styles['CustomBody']))
        else:
            elements.append(Paragraph(
                f"{company_data.get('name', 'The company')} operates in the {company_data.get('industry', 'technology')} sector. "
                f"Based on our analysis of multiple data sources, the company receives an investment score of {analysis_data.get('investmentScore', 'N/A')}/100.",
                self.styles['CustomBody']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Key strengths and risks in columns
        if ai_thesis:
            strengths = ai_thesis.get("strengths", [])
            risks = ai_thesis.get("risks", [])
            
            data = [["Key Strengths", "Key Risks"]]
            max_items = max(len(strengths), len(risks))
            
            for i in range(max_items):
                strength = f"• {strengths[i]}" if i < len(strengths) else ""
                risk = f"• {risks[i]}" if i < len(risks) else ""
                data.append([strength, risk])
            
            t = Table(data, colWidths=[3.5*inch, 3.5*inch])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ]))
            
            elements.append(t)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Recommendation
        if ai_thesis and ai_thesis.get("recommendation"):
            rec_color = self._get_recommendation_color(ai_thesis["recommendation"])
            elements.append(Paragraph(
                f"<b>Recommendation:</b> <font color='{rec_color}'><b>{ai_thesis['recommendation']}</b></font>",
                self.styles['CustomBody']
            ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _create_company_overview(self, company_data: Dict) -> List:
        """Create company overview section"""
        elements = []
        
        elements.append(Paragraph("Company Overview", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Company description
        if company_data.get("description"):
            elements.append(Paragraph(company_data["description"], self.styles['CustomBody']))
        
        # Company details table
        details = []
        if company_data.get("website"):
            details.append(["Website", company_data["website"]])
        if company_data.get("headquarters"):
            details.append(["Headquarters", company_data["headquarters"]])
        if company_data.get("founded"):
            details.append(["Founded", company_data["founded"]])
        
        if details:
            t = Table(details, colWidths=[2*inch, 5*inch])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(Spacer(1, 0.2*inch))
            elements.append(t)
        
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _create_product_intelligence_section(self, company_data: Dict, analysis_data: Dict) -> List:
        """Create comprehensive product and customer intelligence section"""
        elements = []
        
        elements.append(Paragraph("Product & Customer Intelligence", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Get intelligence data
        intelligence = analysis_data.get("intelligence", {})
        
        # Product Details
        if intelligence.get("product", {}).get("found"):
            product = intelligence["product"]
            
            elements.append(Paragraph("<b>Product Overview</b>", self.styles['CustomSubheading']))
            
            if product.get("description"):
                elements.append(Paragraph(product["description"], self.styles['CustomBody']))
                elements.append(Spacer(1, 0.1*inch))
            
            # Key Features
            if product.get("features"):
                elements.append(Paragraph("<b>Key Features:</b>", self.styles['CustomBody']))
                feature_data = []
                for i, feature in enumerate(product["features"][:10], 1):
                    feature_data.append([f"{i}.", feature])
                
                if feature_data:
                    t = Table(feature_data, colWidths=[0.5*inch, 6.5*inch])
                    t.setStyle(TableStyle([
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    elements.append(t)
                    elements.append(Spacer(1, 0.2*inch))
            
            # Pricing Information
            if product.get("pricing"):
                elements.append(Paragraph("<b>Pricing:</b>", self.styles['CustomBody']))
                pricing_text = " | ".join(product["pricing"][:3])
                elements.append(Paragraph(pricing_text, self.styles['Metric']))
                elements.append(Spacer(1, 0.2*inch))
        
        # Customer Intelligence
        if intelligence.get("customers", {}).get("found"):
            customers = intelligence["customers"]
            
            elements.append(Paragraph("<b>Customer Base</b>", self.styles['CustomSubheading']))
            
            # Customer metrics
            metrics = []
            if customers.get("estimated_customers"):
                metrics.append(["Estimated Customers", customers["estimated_customers"]])
            if customers.get("customer_segments"):
                metrics.append(["Customer Segments", ", ".join(customers["customer_segments"])])
            if customers.get("customer_logos"):
                logo_count = len(customers["customer_logos"])
                sample_logos = ", ".join(customers["customer_logos"][:5])
                if logo_count > 5:
                    sample_logos += f" + {logo_count - 5} more"
                metrics.append(["Notable Customers", sample_logos])
            
            if metrics:
                t = Table(metrics, colWidths=[2*inch, 5*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
            
            # Customer testimonials
            if customers.get("testimonials"):
                elements.append(Paragraph("<b>Customer Testimonials:</b>", self.styles['CustomBody']))
                for testimonial in customers["testimonials"][:2]:
                    quote_text = f'"{testimonial["text"]}"'
                    if testimonial.get("author"):
                        quote_text += f"\n- {testimonial['author']}"
                    elements.append(Paragraph(quote_text, ParagraphStyle(
                        name='Quote',
                        parent=self.styles['CustomBody'],
                        fontSize=10,
                        textColor=colors.HexColor('#555555'),
                        leftIndent=20,
                        rightIndent=20,
                        spaceAfter=12
                    )))
        
        # Market Presence
        elements.append(Paragraph("<b>Market Presence & Validation</b>", self.styles['CustomSubheading']))
        
        presence_data = []
        
        # LinkedIn
        if intelligence.get("linkedin", {}).get("found"):
            linkedin = intelligence["linkedin"]
            if linkedin.get("employees"):
                presence_data.append(["LinkedIn", f"{linkedin['employees']} employees"])
        
        # G2 Reviews
        if intelligence.get("g2_reviews", {}).get("found"):
            g2 = intelligence["g2_reviews"]
            g2_text = []
            if g2.get("rating"):
                g2_text.append(f"Rating: {g2['rating']}/5")
            if g2.get("review_count"):
                g2_text.append(f"{g2['review_count']} reviews")
            if g2_text:
                presence_data.append(["G2 Crowd", " | ".join(g2_text)])
        
        # ProductHunt
        if intelligence.get("producthunt", {}).get("found"):
            presence_data.append(["ProductHunt", "Featured"])
        
        # App Presence
        app_presence = intelligence.get("app_presence", {})
        if app_presence.get("ios") or app_presence.get("android"):
            apps = []
            if app_presence.get("ios"):
                apps.append("iOS")
            if app_presence.get("android"):
                apps.append("Android")
            presence_data.append(["Mobile Apps", " & ".join(apps)])
        
        # Revenue Indicators
        rev_indicators = intelligence.get("revenue_indicators", {})
        if rev_indicators.get("business_model"):
            presence_data.append(["Business Model", rev_indicators["business_model"]])
        if rev_indicators.get("pricing_model"):
            presence_data.append(["Pricing Model", rev_indicators["pricing_model"]])
        if rev_indicators.get("funding_stage"):
            presence_data.append(["Funding Stage", rev_indicators["funding_stage"]])
        
        if presence_data:
            t = Table(presence_data, colWidths=[2*inch, 5*inch])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(t)
        
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _create_financial_section(self, analysis_data: Dict) -> List:
        """Create financial metrics section"""
        elements = []
        
        elements.append(Paragraph("Financial Metrics & Growth", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Score breakdown chart
        score_breakdown = analysis_data.get("score_breakdown", {})
        if score_breakdown:
            # Create bar chart
            fig, ax = plt.subplots(figsize=(6, 4))
            scores = list(score_breakdown.values())
            labels = [k.replace('_score', '').title() for k in score_breakdown.keys()]
            
            bars = ax.barh(labels, scores)
            
            # Color bars based on score
            for i, (bar, score) in enumerate(zip(bars, scores)):
                if score >= 80:
                    bar.set_color('#27ae60')
                elif score >= 60:
                    bar.set_color('#f39c12')
                elif score >= 40:
                    bar.set_color('#e67e22')
                else:
                    bar.set_color('#e74c3c')
            
            ax.set_xlabel('Score')
            ax.set_xlim(0, 100)
            ax.set_title('Investment Score Breakdown')
            
            # Save to buffer
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=150)
            buf.seek(0)
            plt.close()
            
            # Add to PDF
            img = Image(buf, width=5*inch, height=3*inch)
            elements.append(img)
        
        # Growth signals
        growth_signals = analysis_data.get("growthSignals", {})
        if growth_signals:
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("Growth Indicators", self.styles['CustomSubheading']))
            
            signal_data = []
            for key, value in growth_signals.items():
                if value and value != "Data not available":
                    signal_data.append([key.replace('_', ' ').title(), str(value)])
            
            if signal_data:
                t = Table(signal_data, colWidths=[3*inch, 4*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(t)
        
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _create_market_analysis(self, analysis_data: Dict) -> List:
        """Create market analysis section"""
        elements = []
        
        elements.append(Paragraph("Market Analysis", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        market = analysis_data.get("marketAnalysis", {})
        
        if market.get("tam"):
            elements.append(Paragraph(
                f"<b>Total Addressable Market (TAM):</b> ${market['tam']:,.0f}",
                self.styles['CustomBody']
            ))
        
        if market.get("growthRate"):
            elements.append(Paragraph(
                f"<b>Market Growth Rate:</b> {market['growthRate']:.1f}% annually",
                self.styles['CustomBody']
            ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _create_competitive_intelligence_section(self, analysis_data: Dict) -> List:
        """Create competitive intelligence section with product comparison"""
        elements = []
        
        competitive_data = analysis_data.get("competitiveIntelligence", {})
        if not competitive_data or not competitive_data.get("competitors"):
            return elements
        
        elements.append(Paragraph("Competitive Intelligence & Product Analysis", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Product Description in Plain English
        intelligence = analysis_data.get("intelligence", {})
        if intelligence.get("product", {}).get("description"):
            elements.append(Paragraph("<b>What They Do</b>", self.styles['CustomSubheading']))
            elements.append(Paragraph(
                intelligence["product"]["description"],
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Market Opportunity Score
        if competitive_data.get("market_opportunity_score") is not None:
            score = competitive_data["market_opportunity_score"]
            color = self._get_score_color(score)
            elements.append(Paragraph(
                f"<b>Market Opportunity Score:</b> <font color='{color}'>{score}/100</font>",
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Product Comparison Table
        if competitive_data.get("competitors", {}).get("direct"):
            elements.append(Paragraph("<b>Product Comparison vs Competitors</b>", self.styles['CustomSubheading']))
            
            # Create comparison data
            company_name = analysis_data.get("company", {}).get("name", "Company")
            comp_data = [["Aspect", company_name, "Key Competitors"]]
            
            # Product Focus
            product_desc = "N/A"
            if intelligence.get("product", {}).get("features"):
                features = intelligence["product"]["features"][:3]
                product_desc = ", ".join(features) if features else "N/A"
            
            comp_data.append([
                "Product Focus",
                product_desc[:100] + "..." if len(product_desc) > 100 else product_desc,
                "Varies by competitor"
            ])
            
            # Pricing
            pricing = "N/A"
            if intelligence.get("product", {}).get("pricing"):
                pricing = ", ".join(intelligence["product"]["pricing"][:2])
            comp_data.append(["Pricing Model", pricing[:50] or "N/A", "Market standard pricing"])
            
            # Target Market
            target_market = "N/A"
            if intelligence.get("customers", {}).get("customer_segments"):
                target_market = ", ".join(intelligence["customers"]["customer_segments"][:2])
            comp_data.append(["Target Market", target_market or "N/A", "Similar segments"])
            
            # Strengths
            strengths = []
            if analysis_data.get("aiThesis", {}).get("strengths"):
                strengths = analysis_data["aiThesis"]["strengths"][:2]
            comp_data.append([
                "Key Strengths",
                ", ".join(strengths) if strengths else "Under analysis",
                "Established presence"
            ])
            
            # Market Size
            if analysis_data.get("marketAnalysis", {}).get("tam"):
                tam = analysis_data["marketAnalysis"]["tam"]
                comp_data.append([
                    "Market Size (TAM)",
                    f"${tam:,.0f}",
                    "Same addressable market"
                ])
            
            t = Table(comp_data, colWidths=[1.5*inch, 2.75*inch, 2.75*inch])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.3*inch))
            
            # Competitors List
            elements.append(Paragraph("<b>Direct Competitors</b>", self.styles['CustomSubheading']))
            
            comp_list_data = [["Company", "Size", "Key Differentiator"]]
            for comp in competitive_data["competitors"]["direct"][:5]:
                comp_list_data.append([
                    comp.get("name", ""),
                    comp.get("analysis", {}).get("estimated_size", "Unknown"),
                    comp.get("analysis", {}).get("key_strength", "N/A")[:50] + "..." if len(comp.get("analysis", {}).get("key_strength", "N/A")) > 50 else comp.get("analysis", {}).get("key_strength", "N/A")
                ])
            
            if len(comp_list_data) > 1:
                t = Table(comp_list_data, colWidths=[2*inch, 1.5*inch, 3.5*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.3*inch))
        
        # Strategic Insights
        if competitive_data.get("strategic_insights"):
            elements.append(Paragraph("<b>Strategic Insights</b>", self.styles['CustomSubheading']))
            for insight in competitive_data["strategic_insights"][:3]:
                elements.append(Paragraph(f"• {insight}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Market Position
        if competitive_data.get("market_position"):
            pos = competitive_data["market_position"]
            elements.append(Paragraph("<b>Market Position</b>", self.styles['CustomSubheading']))
            if pos.get("market_segment"):
                elements.append(Paragraph(f"<b>Segment:</b> {pos['market_segment']}", self.styles['Metric']))
            if pos.get("market_maturity"):
                elements.append(Paragraph(f"<b>Maturity:</b> {pos['market_maturity']}", self.styles['Metric']))
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_technical_dd_section(self, analysis_data: Dict) -> List:
        """Create technical due diligence section"""
        elements = []
        
        tech_data = analysis_data.get("technicalDueDiligence", {})
        if not tech_data or tech_data.get("technical_score") is None:
            return elements
        
        elements.append(Paragraph("Technical Due Diligence", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Technical Score
        score = tech_data["technical_score"]
        color = self._get_score_color(score)
        elements.append(Paragraph(
            f"<b>Technical Score:</b> <font color='{color}'>{score}/100</font>",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Technology Stack
        if tech_data.get("website_tech", {}).get("found"):
            tech = tech_data["website_tech"]
            elements.append(Paragraph("<b>Technology Stack</b>", self.styles['CustomSubheading']))
            
            tech_items = []
            if tech.get("frontend"):
                tech_items.append(["Frontend", ", ".join(tech["frontend"])])
            if tech.get("infrastructure"):
                tech_items.append(["Infrastructure", ", ".join(tech["infrastructure"])])
            if tech.get("cdn"):
                tech_items.append(["CDN", tech["cdn"]])
            if tech.get("analytics"):
                tech_items.append(["Analytics", ", ".join(tech["analytics"])])
            
            if tech_items:
                t = Table(tech_items, colWidths=[2*inch, 5*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Security Analysis
        if tech_data.get("security", {}).get("found"):
            security = tech_data["security"]
            elements.append(Paragraph("<b>Security Analysis</b>", self.styles['CustomSubheading']))
            elements.append(Paragraph(
                f"Security Score: {security.get('score', 0)}/100",
                self.styles['CustomBody']
            ))
            
            if security.get("vulnerabilities"):
                elements.append(Paragraph("<b>Vulnerabilities:</b>", self.styles['Metric']))
                for vuln in security["vulnerabilities"][:3]:
                    elements.append(Paragraph(f"• {vuln}", ParagraphStyle(
                        name='Vulnerability',
                        parent=self.styles['CustomBody'],
                        textColor=colors.HexColor('#e74c3c'),
                        fontSize=10
                    )))
            elements.append(Spacer(1, 0.2*inch))
        
        # Technical Strengths & Risks
        if tech_data.get("technical_strengths"):
            elements.append(Paragraph("<b>Technical Strengths</b>", self.styles['CustomSubheading']))
            for strength in tech_data["technical_strengths"][:3]:
                elements.append(Paragraph(f"✓ {strength}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        
        if tech_data.get("technical_risks"):
            elements.append(Paragraph("<b>Technical Risks</b>", self.styles['CustomSubheading']))
            for risk in tech_data["technical_risks"][:3]:
                elements.append(Paragraph(f"⚠ {risk}", ParagraphStyle(
                    name='Risk',
                    parent=self.styles['CustomBody'],
                    textColor=colors.HexColor('#e74c3c')
                )))
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_news_section(self, analysis_data: Dict) -> List:
        """Create recent news and media coverage section"""
        elements = []
        
        # Check for news in multiple places
        news_data = None
        
        # Try to get news from real_data
        real_data = analysis_data.get("real_data", {})
        if real_data.get("news", {}).get("found"):
            news_data = real_data["news"]
        
        # Try to get news from socialSentiment
        social_sentiment = analysis_data.get("socialSentiment", {})
        if not news_data and social_sentiment.get("news", {}).get("found"):
            news_data = social_sentiment["news"]
        
        # Try to get news from investmentSignals
        investment_signals = analysis_data.get("investmentSignals", {})
        if not news_data and investment_signals.get("recent_news"):
            news_data = {
                "found": True,
                "recent_news": investment_signals["recent_news"],
                "news_count": len(investment_signals.get("recent_news", [])),
                "sentiment_score": investment_signals.get("sentiment_score", 50)
            }
        
        if not news_data or not news_data.get("found"):
            return elements
        
        elements.append(Paragraph("Recent News & Media Coverage", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # News Sentiment Score
        if news_data.get("sentiment_score") is not None:
            sentiment = news_data["sentiment_score"]
            sentiment_color = self._get_score_color(sentiment)
            momentum = news_data.get("momentum", "neutral")
            
            elements.append(Paragraph(
                f"<b>Media Sentiment:</b> <font color='{sentiment_color}'>{sentiment}/100</font> ({momentum})",
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Recent News Articles
        recent_news = news_data.get("recent_news", [])
        if recent_news:
            elements.append(Paragraph("<b>Recent Headlines</b>", self.styles['CustomSubheading']))
            
            news_table_data = []
            for i, article in enumerate(recent_news[:10], 1):
                # Handle different news data formats
                if isinstance(article, dict):
                    title = article.get("title", article.get("headline", ""))
                    date = article.get("date", article.get("published_date", ""))
                    source = article.get("source", "")
                    
                    # Format date if present
                    if date:
                        try:
                            # Try to parse and format date
                            from datetime import datetime
                            if "ago" in str(date).lower():
                                date_str = date
                            else:
                                date_str = date
                        except:
                            date_str = str(date)
                    else:
                        date_str = "Recent"
                    
                    # Create news item
                    if title:
                        # Truncate long titles
                        if len(title) > 80:
                            title = title[:77] + "..."
                        
                        news_item = [
                            str(i),
                            title,
                            date_str,
                            source[:20] if source else ""
                        ]
                        news_table_data.append(news_item)
                else:
                    # Handle string format
                    title = str(article)
                    if len(title) > 80:
                        title = title[:77] + "..."
                    news_table_data.append([str(i), title, "Recent", ""])
            
            if news_table_data:
                # Add header
                news_table_data.insert(0, ["#", "Headline", "Date", "Source"])
                
                t = Table(news_table_data, colWidths=[0.3*inch, 4.5*inch, 1.2*inch, 1*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.3*inch))
        
        # Media Highlights or Key Themes
        if news_data.get("key_themes"):
            elements.append(Paragraph("<b>Key Media Themes</b>", self.styles['CustomSubheading']))
            for theme in news_data["key_themes"][:5]:
                elements.append(Paragraph(f"• {theme}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Press Coverage Summary
        if news_data.get("news_count"):
            elements.append(Paragraph(
                f"<i>Total of {news_data['news_count']} news articles found in recent coverage</i>",
                self.styles['Metric']
            ))
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_investment_signals_section(self, analysis_data: Dict) -> List:
        """Create investment signals and data metrics section"""
        elements = []
        
        # Get data metrics
        data_metrics = analysis_data.get("dataMetrics", {})
        investment_signals = analysis_data.get("investmentSignals", {})
        
        if not data_metrics and not investment_signals:
            return elements
        
        elements.append(Paragraph("Investment Signals & Data Metrics", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Quantitative Score
        if data_metrics.get("quantitative_score") is not None:
            score = data_metrics["quantitative_score"]
            score_color = self._get_score_color(score)
            elements.append(Paragraph(
                f"<b>Quantitative Data Score:</b> <font color='{score_color}'>{score}/100</font>",
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Growth Metrics
        if data_metrics.get("growth_metrics"):
            growth = data_metrics["growth_metrics"]
            elements.append(Paragraph("<b>Growth Metrics</b>", self.styles['CustomSubheading']))
            
            growth_data = []
            if growth.get("employee_growth_rate"):
                growth_data.append(["Employee Growth", f"{growth['employee_growth_rate']:.1f}% YoY"])
            if growth.get("star_velocity"):
                growth_data.append(["GitHub Star Velocity", f"{growth['star_velocity']:.1f} stars/month"])
            if growth.get("customer_growth_estimate"):
                growth_data.append(["Customer Growth", f"{growth['customer_growth_estimate']:.1f}% estimated"])
            if growth.get("traffic_growth"):
                growth_data.append(["Web Traffic Growth", f"{growth['traffic_growth']:.1f}%"])
            
            if growth_data:
                t = Table(growth_data, colWidths=[3*inch, 4*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Traction Metrics
        if data_metrics.get("traction_metrics"):
            traction = data_metrics["traction_metrics"]
            elements.append(Paragraph("<b>Traction Indicators</b>", self.styles['CustomSubheading']))
            
            traction_data = []
            if traction.get("customer_count"):
                traction_data.append(["Estimated Customers", str(traction["customer_count"])])
            if traction.get("github_stars"):
                traction_data.append(["GitHub Stars", f"{traction['github_stars']:,}"])
            if traction.get("community_size"):
                traction_data.append(["Community Size", f"{traction['community_size']:,}"])
            if traction.get("app_downloads"):
                traction_data.append(["App Downloads", traction["app_downloads"]])
            
            if traction_data:
                t = Table(traction_data, colWidths=[3*inch, 4*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Efficiency Metrics
        if data_metrics.get("efficiency_metrics"):
            efficiency = data_metrics["efficiency_metrics"]
            elements.append(Paragraph("<b>Efficiency Metrics</b>", self.styles['CustomSubheading']))
            
            eff_data = []
            if efficiency.get("revenue_per_employee"):
                eff_data.append(["Revenue per Employee", f"${efficiency['revenue_per_employee']:,.0f}"])
            if efficiency.get("burn_rate"):
                eff_data.append(["Monthly Burn Rate", f"${efficiency['burn_rate']:,.0f}"])
            if efficiency.get("runway_months"):
                eff_data.append(["Runway", f"{efficiency['runway_months']:.1f} months"])
            if efficiency.get("capital_efficiency"):
                eff_data.append(["Capital Efficiency", f"{efficiency['capital_efficiency']:.2f}x"])
            
            if eff_data:
                t = Table(eff_data, colWidths=[3*inch, 4*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Valuation Estimate
        if data_metrics.get("valuation_estimate"):
            valuation = data_metrics["valuation_estimate"]
            elements.append(Paragraph("<b>Valuation Analysis</b>", self.styles['CustomSubheading']))
            
            val_data = []
            if valuation.get("estimated_valuation"):
                val_data.append(["Estimated Valuation", f"${valuation['estimated_valuation']:,.0f}"])
            if valuation.get("revenue_multiple"):
                val_data.append(["Revenue Multiple", f"{valuation['revenue_multiple']:.1f}x"])
            if valuation.get("confidence"):
                val_data.append(["Confidence Level", valuation["confidence"]])
            if valuation.get("methodology"):
                val_data.append(["Methodology", valuation["methodology"]])
            
            if val_data:
                t = Table(val_data, colWidths=[3*inch, 4*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Investment Signals Summary
        if investment_signals.get("signal_summary"):
            elements.append(Paragraph("<b>Key Investment Signals</b>", self.styles['CustomSubheading']))
            
            signals = investment_signals["signal_summary"]
            signal_data = []
            
            if signals.get("positive_signals"):
                for signal in signals["positive_signals"][:5]:
                    signal_data.append(["✓", signal, "Positive"])
            
            if signals.get("negative_signals"):
                for signal in signals["negative_signals"][:3]:
                    signal_data.append(["⚠", signal, "Caution"])
            
            if signal_data:
                t = Table(signal_data, colWidths=[0.5*inch, 5.5*inch, 1*inch])
                t.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#7f8c8d')),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_hiring_section(self, analysis_data: Dict) -> List:
        """Create hiring and team growth section"""
        elements = []
        
        hiring_data = analysis_data.get("hiringData", {})
        if not hiring_data or not hiring_data.get("found"):
            return elements
        
        elements.append(Paragraph("Hiring & Team Growth", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        # Hiring Overview
        if hiring_data.get("total_open_positions"):
            trend = hiring_data.get("hiring_velocity", {}).get("trending", "stable")
            trend_color = '#27ae60' if "growth" in trend else '#f39c12' if trend == "selective_hiring" else '#3498db'
            
            elements.append(Paragraph(
                f"<b>Open Positions:</b> <font color='{trend_color}'>{hiring_data['total_open_positions']} roles</font> ({trend.replace('_', ' ').title()})",
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Team Size & Growth
        if hiring_data.get("team_size", {}).get("current"):
            team_size = hiring_data["team_size"]
            elements.append(Paragraph("<b>Team Size & Growth</b>", self.styles['CustomSubheading']))
            
            team_data = []
            if team_size.get("current"):
                team_data.append(["Current Team Size", f"{team_size['current']:,} employees"])
            if team_size.get("growth_rate"):
                growth_color = '#27ae60' if team_size["growth_rate"] > 30 else '#f39c12'
                team_data.append(["Growth Rate", f"{team_size['growth_rate']:.0f}% YoY"])
            if team_size.get("6_months_ago"):
                team_data.append(["6 Months Ago", f"{team_size['6_months_ago']:,} employees"])
            if team_size.get("1_year_ago"):
                team_data.append(["1 Year Ago", f"{team_size['1_year_ago']:,} employees"])
            
            if team_data:
                t = Table(team_data, colWidths=[3*inch, 4*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Hiring by Department
        if hiring_data.get("hiring_velocity", {}).get("departments_hiring"):
            elements.append(Paragraph("<b>Departments Hiring</b>", self.styles['CustomSubheading']))
            
            dept_data = [["Department", "Open Roles"]]
            if hiring_data.get("engineering_roles", 0) > 0:
                dept_data.append(["Engineering", str(hiring_data["engineering_roles"])])
            if hiring_data.get("sales_roles", 0) > 0:
                dept_data.append(["Sales", str(hiring_data["sales_roles"])])
            if hiring_data.get("product_roles", 0) > 0:
                dept_data.append(["Product", str(hiring_data["product_roles"])])
            if hiring_data.get("operations_roles", 0) > 0:
                dept_data.append(["Operations", str(hiring_data["operations_roles"])])
            if hiring_data.get("leadership_roles", 0) > 0:
                dept_data.append(["Leadership", str(hiring_data["leadership_roles"])])
            
            if len(dept_data) > 1:
                t = Table(dept_data, colWidths=[3*inch, 2*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Key Open Roles
        if hiring_data.get("key_roles"):
            elements.append(Paragraph("<b>Key Open Positions</b>", self.styles['CustomSubheading']))
            
            role_data = []
            for i, role in enumerate(hiring_data["key_roles"][:8], 1):
                title = role.get("title", "")
                location = role.get("location", "")
                if location and len(location) > 20:
                    location = location[:17] + "..."
                
                role_data.append([
                    str(i),
                    title[:50] + "..." if len(title) > 50 else title,
                    location or "Not specified"
                ])
            
            if role_data:
                role_data.insert(0, ["#", "Position", "Location"])
                t = Table(role_data, colWidths=[0.3*inch, 4.7*inch, 2*inch])
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Hiring Insights
        if hiring_data.get("hiring_insights"):
            elements.append(Paragraph("<b>Hiring Insights</b>", self.styles['CustomSubheading']))
            for insight in hiring_data["hiring_insights"][:5]:
                elements.append(Paragraph(f"• {insight}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Growth Signals
        if hiring_data.get("growth_signals"):
            elements.append(Paragraph("<b>Growth Signals</b>", self.styles['CustomSubheading']))
            for signal in hiring_data["growth_signals"][:3]:
                elements.append(Paragraph(f"✓ {signal}", ParagraphStyle(
                    name='GrowthSignal',
                    parent=self.styles['CustomBody'],
                    textColor=colors.HexColor('#27ae60')
                )))
            elements.append(Spacer(1, 0.2*inch))
        
        # Hiring Platforms
        if hiring_data.get("hiring_platforms"):
            platforms_text = ", ".join(hiring_data["hiring_platforms"])
            elements.append(Paragraph(
                f"<i>Recruiting on: {platforms_text}</i>",
                self.styles['Metric']
            ))
        
        # Remote positions
        if hiring_data.get("remote_positions", 0) > 0:
            remote_pct = (hiring_data["remote_positions"] / hiring_data["total_open_positions"]) * 100
            elements.append(Paragraph(
                f"<i>{hiring_data['remote_positions']} remote positions ({remote_pct:.0f}% of openings)</i>",
                self.styles['Metric']
            ))
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_investment_thesis(self, analysis_data: Dict) -> List:
        """Create investment thesis section"""
        elements = []
        
        elements.append(Paragraph("Investment Thesis", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        ai_thesis = analysis_data.get("aiThesis", {})
        
        # Investment score visualization
        score = analysis_data.get("investmentScore", 0)
        elements.append(Paragraph(
            f"<b>Overall Investment Score:</b> {score}/100",
            self.styles['CustomBody']
        ))
        
        # Score interpretation
        if score >= 80:
            interpretation = "Exceptional investment opportunity with strong fundamentals"
        elif score >= 60:
            interpretation = "Solid investment opportunity with good growth potential"
        elif score >= 40:
            interpretation = "Moderate opportunity requiring careful consideration"
        else:
            interpretation = "High-risk investment with significant challenges"
        
        elements.append(Paragraph(interpretation, self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _create_risk_analysis(self, analysis_data: Dict) -> List:
        """Create risk analysis section"""
        elements = []
        
        elements.append(Paragraph("Risk Analysis", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        ai_thesis = analysis_data.get("aiThesis", {})
        risks = ai_thesis.get("risks", [])
        
        if risks:
            for i, risk in enumerate(risks, 1):
                elements.append(Paragraph(f"{i}. {risk}", self.styles['CustomBody']))
        else:
            elements.append(Paragraph(
                "Risk assessment requires additional due diligence.",
                self.styles['CustomBody']
            ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _create_comparables(self, analysis_data: Dict) -> List:
        """Create comparable companies section"""
        elements = []
        
        ai_thesis = analysis_data.get("aiThesis", {})
        comparables = ai_thesis.get("similarCompanies", [])
        
        if comparables:
            elements.append(Paragraph("Comparable Companies", self.styles['CustomHeading']))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
            elements.append(Spacer(1, 0.2*inch))
            
            comp_data = [["Company", "Outcome", "Comparison"]]
            for comp in comparables:
                comp_data.append([
                    comp.get("name", ""),
                    comp.get("outcome", ""),
                    comp.get("reason", "")
                ])
            
            t = Table(comp_data, colWidths=[2*inch, 1.5*inch, 3.5*inch])
            t.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(t)
            elements.append(Spacer(1, 0.5*inch))
        
        return elements
    
    def _create_data_sources(self, analysis_data: Dict) -> List:
        """Create data sources section"""
        elements = []
        
        elements.append(Paragraph("Data Sources", self.styles['CustomHeading']))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3498db')))
        elements.append(Spacer(1, 0.2*inch))
        
        sources = analysis_data.get("dataSources", [])
        
        if sources:
            elements.append(Paragraph(
                "This analysis is based on data from the following sources:",
                self.styles['CustomBody']
            ))
            
            for source in sources:
                elements.append(Paragraph(f"• {source}", self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            f"Analysis conducted on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['Metric']
        ))
        
        return elements
    
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
            return '#27ae60'
        elif "BUY" in rec_upper:
            return '#2ecc71'
        elif "HOLD" in rec_upper:
            return '#f39c12'
        else:
            return '#e74c3c'