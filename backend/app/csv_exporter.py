"""
CSV Export functionality for DealFlow Analytics
Secure CSV generation with proper data sanitization
"""

import csv
import io
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
import re

class CSVExporter:
    """Secure CSV exporter for analysis data"""
    
    @staticmethod
    def sanitize_value(value: Any) -> str:
        """
        Sanitize values to prevent CSV injection attacks
        Removes potentially dangerous characters like =, +, -, @
        """
        if value is None:
            return ""
        
        # Convert to string
        str_value = str(value)
        
        # Remove potential CSV injection prefixes
        dangerous_prefixes = ['=', '+', '-', '@', '\t', '\r', '\n']
        if len(str_value) > 0 and str_value[0] in dangerous_prefixes:
            str_value = "'" + str_value
        
        # Remove any control characters
        str_value = re.sub(r'[\x00-\x1F\x7F]', '', str_value)
        
        return str_value
    
    @staticmethod
    def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested dictionaries for CSV export"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(CSVExporter.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to comma-separated strings
                if v and isinstance(v[0], dict):
                    # Complex list - just count items
                    items.append((f"{new_key}_count", len(v)))
                else:
                    # Simple list - join values
                    items.append((new_key, ', '.join(map(str, v))))
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def generate_analysis_csv(company_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> bytes:
        """Generate CSV file from analysis data"""
        
        # Combine company and analysis data
        combined_data = {
            'company_name': company_data.get('name', 'Unknown'),
            'company_url': company_data.get('url', ''),
            'company_domain': company_data.get('domain', ''),
            'company_industry': company_data.get('industry', ''),
            'company_employees': company_data.get('employeeCount', ''),
            'analysis_date': datetime.now().isoformat(),
            'investment_score': analysis_data.get('investmentScore', 0),
        }
        
        # Add growth signals
        if 'growthSignals' in analysis_data:
            signals = analysis_data['growthSignals']
            combined_data.update({
                'growth_employee': signals.get('employeeGrowth', ''),
                'growth_web_traffic': signals.get('webTraffic', ''),
                'growth_tech_stack': signals.get('techStack', ''),
                'growth_news_velocity': signals.get('newsVelocity', ''),
                'growth_media_sentiment': signals.get('mediaSentiment', ''),
            })
        
        # Add market analysis
        if 'marketAnalysis' in analysis_data:
            market = analysis_data['marketAnalysis']
            combined_data.update({
                'market_tam': market.get('tam', 0),
                'market_growth_rate': market.get('growthRate', 0),
                'market_competitors': ', '.join(market.get('competitors', [])) if market.get('competitors') else '',
            })
        
        # Add AI thesis summary
        if 'aiThesis' in analysis_data:
            thesis = analysis_data['aiThesis']
            combined_data.update({
                'ai_summary': thesis.get('summary', ''),
                'ai_recommendation': thesis.get('recommendation', ''),
                'ai_strengths': ', '.join(thesis.get('strengths', [])),
                'ai_risks': ', '.join(thesis.get('risks', [])),
            })
        
        # Add quantitative metrics if available
        if 'dataMetrics' in analysis_data:
            metrics = analysis_data['dataMetrics']
            if 'key_performance_indicators' in metrics:
                kpis = metrics['key_performance_indicators']
                combined_data.update({
                    'kpi_revenue_estimate': kpis.get('revenue_estimate', 0),
                    'kpi_customer_count': kpis.get('customer_count', 0),
                    'kpi_growth_rate': kpis.get('growth_rate', 0),
                    'kpi_burn_rate': kpis.get('burn_rate', 0),
                    'kpi_runway': kpis.get('runway', 0),
                })
        
        # Sanitize all values
        sanitized_data = {k: CSVExporter.sanitize_value(v) for k, v in combined_data.items()}
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=sanitized_data.keys())
        writer.writeheader()
        writer.writerow(sanitized_data)
        
        # Return as bytes
        return output.getvalue().encode('utf-8')
    
    @staticmethod
    def generate_bulk_csv(analyses: List[Dict[str, Any]]) -> bytes:
        """Generate CSV for multiple analyses"""
        if not analyses:
            return b"No data available"
        
        # Flatten all analyses
        flattened_data = []
        for analysis in analyses:
            flat = CSVExporter.flatten_dict(analysis)
            # Sanitize all values
            sanitized = {k: CSVExporter.sanitize_value(v) for k, v in flat.items()}
            flattened_data.append(sanitized)
        
        # Get all unique keys
        all_keys = set()
        for data in flattened_data:
            all_keys.update(data.keys())
        
        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=sorted(all_keys))
        writer.writeheader()
        writer.writerows(flattened_data)
        
        return output.getvalue().encode('utf-8')