"""
Advanced Investment Analytics Engine for DealFlow Analytics
Predictive models, portfolio optimization, and success pattern recognition
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import scipy.optimize as optimize
from dataclasses import dataclass
import asyncio
import httpx

class InvestmentStage(Enum):
    """Investment stages"""
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D_PLUS = "series_d_plus"
    GROWTH = "growth"
    PRE_IPO = "pre_ipo"

@dataclass
class CompanyMetrics:
    """Company performance metrics"""
    revenue_growth_rate: float
    burn_rate: float
    runway_months: float
    gross_margin: float
    cac_payback_months: float
    ltv_cac_ratio: float
    nps_score: float
    employee_growth_rate: float
    market_share: float
    competitive_moat_score: float

@dataclass
class ExitPrediction:
    """Exit prediction model output"""
    exit_probability: float
    expected_exit_value: float
    expected_time_to_exit_years: float
    likely_exit_type: str  # IPO, M&A, Secondary
    confidence_score: float
    key_drivers: List[str]
    risk_factors: List[str]

@dataclass
class PortfolioOptimization:
    """Portfolio optimization results"""
    recommended_allocation: Dict[str, float]
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    diversification_score: float
    correlation_matrix: np.ndarray

class InvestmentAnalytics:
    """
    Advanced analytics engine for investment decisions
    """
    
    def __init__(self):
        self.exit_model = None
        self.success_predictor = None
        self.valuation_model = None
        self.pattern_recognizer = None
        self.market_comparables_cache = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """
        Initialize ML models for predictions
        """
        # Exit prediction model
        self.exit_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Success prediction model
        self.success_predictor = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # Load pre-trained models if available
        self._load_pretrained_models()
    
    def _load_pretrained_models(self):
        """
        Load pre-trained models from storage
        """
        # In production, load from cloud storage or model registry
        # For now, we'll use synthetic training
        self._train_synthetic_models()
    
    def _train_synthetic_models(self):
        """
        Train models with synthetic data for demonstration
        """
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: revenue_growth, burn_rate, market_size, team_score, etc.
        X_train = np.random.randn(n_samples, 10)
        
        # Exit values (in millions)
        y_exit = np.exp(3 + 0.5 * X_train[:, 0] - 0.3 * X_train[:, 1] + np.random.randn(n_samples) * 0.5)
        
        # Success labels (0 or 1)
        y_success = (y_exit > np.median(y_exit)).astype(int)
        
        # Train models
        self.exit_model.fit(X_train, y_exit)
        self.success_predictor.fit(X_train, y_success)
    
    async def predict_exit_valuation(
        self,
        company_data: Dict[str, Any],
        metrics: CompanyMetrics
    ) -> ExitPrediction:
        """
        Predict exit valuation and timeline using ML models
        """
        # Prepare features
        features = self._prepare_features(company_data, metrics)
        
        # Make predictions
        exit_value = self.exit_model.predict([features])[0]
        success_prob = self.success_predictor.predict_proba([features])[0][1]
        
        # Estimate time to exit based on stage
        stage = company_data.get("funding_stage", "seed")
        time_to_exit = self._estimate_time_to_exit(stage)
        
        # Determine likely exit type
        exit_type = self._predict_exit_type(exit_value, company_data)
        
        # Identify key drivers and risks
        key_drivers = self._identify_key_drivers(features, self.exit_model)
        risk_factors = self._identify_risk_factors(company_data, metrics)
        
        return ExitPrediction(
            exit_probability=success_prob,
            expected_exit_value=exit_value * 1_000_000,  # Convert to dollars
            expected_time_to_exit_years=time_to_exit,
            likely_exit_type=exit_type,
            confidence_score=self._calculate_confidence(features),
            key_drivers=key_drivers,
            risk_factors=risk_factors
        )
    
    def _prepare_features(
        self,
        company_data: Dict[str, Any],
        metrics: CompanyMetrics
    ) -> np.ndarray:
        """
        Prepare feature vector for ML models
        """
        features = [
            metrics.revenue_growth_rate,
            metrics.burn_rate,
            metrics.runway_months / 12,  # Convert to years
            metrics.gross_margin,
            metrics.ltv_cac_ratio,
            metrics.employee_growth_rate,
            metrics.market_share,
            metrics.competitive_moat_score,
            self._encode_stage(company_data.get("funding_stage", "seed")),
            self._encode_industry(company_data.get("industry", "other"))
        ]
        
        return np.array(features)
    
    def _encode_stage(self, stage: str) -> float:
        """
        Encode funding stage as numeric value
        """
        stage_values = {
            "pre_seed": 1,
            "seed": 2,
            "series_a": 3,
            "series_b": 4,
            "series_c": 5,
            "series_d": 6,
            "growth": 7
        }
        return stage_values.get(stage.lower(), 2)
    
    def _encode_industry(self, industry: str) -> float:
        """
        Encode industry as numeric value
        """
        hot_industries = ["ai", "fintech", "biotech", "saas", "climate"]
        if any(hot in industry.lower() for hot in hot_industries):
            return 2.0
        return 1.0
    
    def _estimate_time_to_exit(self, stage: str) -> float:
        """
        Estimate years to exit based on funding stage
        """
        stage_to_exit = {
            "pre_seed": 7.5,
            "seed": 6.5,
            "series_a": 5.0,
            "series_b": 4.0,
            "series_c": 3.0,
            "series_d": 2.0,
            "growth": 1.5
        }
        return stage_to_exit.get(stage.lower(), 5.0)
    
    def _predict_exit_type(
        self,
        exit_value: float,
        company_data: Dict[str, Any]
    ) -> str:
        """
        Predict most likely exit type
        """
        # Simplified heuristics
        if exit_value > 1000:  # $1B+
            return "IPO"
        elif exit_value > 100:  # $100M+
            return "Strategic Acquisition"
        else:
            return "Acqui-hire or Secondary"
    
    def _identify_key_drivers(
        self,
        features: np.ndarray,
        model: RandomForestRegressor
    ) -> List[str]:
        """
        Identify key value drivers using feature importance
        """
        feature_names = [
            "Revenue Growth",
            "Burn Efficiency",
            "Runway",
            "Gross Margin",
            "LTV/CAC Ratio",
            "Team Growth",
            "Market Share",
            "Competitive Moat",
            "Funding Stage",
            "Industry Hotness"
        ]
        
        importances = model.feature_importances_
        top_features = np.argsort(importances)[-5:][::-1]
        
        return [feature_names[i] for i in top_features]
    
    def _identify_risk_factors(
        self,
        company_data: Dict[str, Any],
        metrics: CompanyMetrics
    ) -> List[str]:
        """
        Identify key risk factors
        """
        risks = []
        
        # Check burn rate
        if metrics.burn_rate > 500000:  # $500K/month
            risks.append("High burn rate (>${:.0f}K/month)".format(metrics.burn_rate/1000))
        
        # Check runway
        if metrics.runway_months < 12:
            risks.append("Limited runway (<12 months)")
        
        # Check unit economics
        if metrics.ltv_cac_ratio < 3:
            risks.append("Weak unit economics (LTV/CAC < 3)")
        
        # Check growth rate
        if metrics.revenue_growth_rate < 0.5:  # <50% YoY
            risks.append("Below-benchmark growth rate")
        
        # Market risks
        if metrics.market_share < 0.05:  # <5%
            risks.append("Low market share in competitive market")
        
        return risks
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """
        Calculate confidence score for predictions
        """
        # Base confidence on feature completeness and model performance
        base_confidence = 0.7
        
        # Adjust based on data quality
        if np.any(np.isnan(features)):
            base_confidence -= 0.2
        
        # Could add more sophisticated confidence estimation
        return min(max(base_confidence, 0.3), 0.95)
    
    async def optimize_portfolio(
        self,
        current_portfolio: List[Dict[str, Any]],
        available_deals: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> PortfolioOptimization:
        """
        Optimize portfolio allocation using Modern Portfolio Theory
        """
        # Prepare return and risk matrices
        returns, risks = await self._calculate_returns_and_risks(
            current_portfolio + available_deals
        )
        
        # Calculate correlation matrix
        correlation_matrix = await self._calculate_correlations(
            current_portfolio + available_deals
        )
        
        # Run optimization
        optimal_weights = self._optimize_allocation(
            returns,
            risks,
            correlation_matrix,
            constraints
        )
        
        # Calculate portfolio metrics
        portfolio_return = np.dot(optimal_weights, returns)
        portfolio_risk = np.sqrt(
            np.dot(optimal_weights, np.dot(correlation_matrix, optimal_weights))
        )
        
        sharpe_ratio = (portfolio_return - 0.02) / portfolio_risk  # Assuming 2% risk-free rate
        
        # Create allocation recommendations
        all_companies = current_portfolio + available_deals
        recommended_allocation = {
            company["name"]: weight
            for company, weight in zip(all_companies, optimal_weights)
            if weight > 0.01  # Only include significant allocations
        }
        
        return PortfolioOptimization(
            recommended_allocation=recommended_allocation,
            expected_return=portfolio_return,
            expected_risk=portfolio_risk,
            sharpe_ratio=sharpe_ratio,
            diversification_score=self._calculate_diversification(optimal_weights),
            correlation_matrix=correlation_matrix
        )
    
    async def _calculate_returns_and_risks(
        self,
        companies: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate expected returns and risks for companies
        """
        returns = []
        risks = []
        
        for company in companies:
            # Simulate return calculation (would use real models in production)
            metrics = self._extract_metrics(company)
            
            # Expected return based on stage and metrics
            expected_return = self._calculate_expected_return(company, metrics)
            returns.append(expected_return)
            
            # Risk based on stage and uncertainty
            risk = self._calculate_risk(company, metrics)
            risks.append(risk)
        
        return np.array(returns), np.array(risks)
    
    def _calculate_expected_return(
        self,
        company: Dict[str, Any],
        metrics: CompanyMetrics
    ) -> float:
        """
        Calculate expected return for a company
        """
        # Base return by stage
        stage_returns = {
            "seed": 0.50,  # 50% expected annual return
            "series_a": 0.40,
            "series_b": 0.30,
            "series_c": 0.25,
            "growth": 0.20
        }
        
        base_return = stage_returns.get(
            company.get("funding_stage", "seed").lower(),
            0.30
        )
        
        # Adjust for company quality
        quality_multiplier = 1.0
        
        if metrics.revenue_growth_rate > 1.0:  # >100% growth
            quality_multiplier += 0.2
        
        if metrics.ltv_cac_ratio > 3:
            quality_multiplier += 0.1
        
        if metrics.competitive_moat_score > 0.7:
            quality_multiplier += 0.15
        
        return base_return * quality_multiplier
    
    def _calculate_risk(
        self,
        company: Dict[str, Any],
        metrics: CompanyMetrics
    ) -> float:
        """
        Calculate risk (volatility) for a company
        """
        # Base risk by stage
        stage_risks = {
            "seed": 0.40,  # 40% volatility
            "series_a": 0.35,
            "series_b": 0.30,
            "series_c": 0.25,
            "growth": 0.20
        }
        
        base_risk = stage_risks.get(
            company.get("funding_stage", "seed").lower(),
            0.35
        )
        
        # Adjust for company-specific factors
        if metrics.runway_months < 6:
            base_risk += 0.10
        
        if metrics.burn_rate > 1_000_000:  # >$1M/month
            base_risk += 0.05
        
        return base_risk
    
    async def _calculate_correlations(
        self,
        companies: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Calculate correlation matrix between companies
        """
        n = len(companies)
        correlation_matrix = np.eye(n)  # Start with identity matrix
        
        for i in range(n):
            for j in range(i + 1, n):
                # Calculate correlation based on industry, stage, geography
                correlation = self._calculate_pairwise_correlation(
                    companies[i],
                    companies[j]
                )
                correlation_matrix[i, j] = correlation
                correlation_matrix[j, i] = correlation
        
        return correlation_matrix
    
    def _calculate_pairwise_correlation(
        self,
        company1: Dict[str, Any],
        company2: Dict[str, Any]
    ) -> float:
        """
        Calculate correlation between two companies
        """
        correlation = 0.3  # Base correlation
        
        # Same industry increases correlation
        if company1.get("industry") == company2.get("industry"):
            correlation += 0.3
        
        # Same stage increases correlation
        if company1.get("funding_stage") == company2.get("funding_stage"):
            correlation += 0.2
        
        # Same geography increases correlation
        if company1.get("location") == company2.get("location"):
            correlation += 0.1
        
        return min(correlation, 0.9)  # Cap at 0.9
    
    def _optimize_allocation(
        self,
        returns: np.ndarray,
        risks: np.ndarray,
        correlation_matrix: np.ndarray,
        constraints: Dict[str, Any]
    ) -> np.ndarray:
        """
        Optimize portfolio allocation using quadratic programming
        """
        n = len(returns)
        
        # Objective: Maximize Sharpe ratio
        def negative_sharpe(weights):
            portfolio_return = np.dot(weights, returns)
            portfolio_variance = np.dot(weights, np.dot(correlation_matrix, weights))
            portfolio_risk = np.sqrt(portfolio_variance)
            
            # Sharpe ratio (assuming 2% risk-free rate)
            sharpe = (portfolio_return - 0.02) / portfolio_risk
            return -sharpe  # Negative because we minimize
        
        # Constraints
        cons = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
        ]
        
        # Add custom constraints
        if "max_concentration" in constraints:
            max_conc = constraints["max_concentration"]
            for i in range(n):
                cons.append({
                    'type': 'ineq',
                    'fun': lambda x, i=i: max_conc - x[i]
                })
        
        if "min_companies" in constraints:
            min_comp = constraints["min_companies"]
            cons.append({
                'type': 'ineq',
                'fun': lambda x: np.sum(x > 0.01) - min_comp
            })
        
        # Bounds (0 to 1 for each weight)
        bounds = tuple((0, 1) for _ in range(n))
        
        # Initial guess (equal weights)
        x0 = np.array([1/n] * n)
        
        # Optimize
        result = optimize.minimize(
            negative_sharpe,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=cons
        )
        
        if result.success:
            return result.x
        else:
            # Return equal weights if optimization fails
            return x0
    
    def _calculate_diversification(self, weights: np.ndarray) -> float:
        """
        Calculate portfolio diversification score
        """
        # Use Herfindahl-Hirschman Index
        hhi = np.sum(weights ** 2)
        
        # Convert to diversification score (0 to 1, higher is better)
        n = len(weights)
        min_hhi = 1 / n  # Perfect diversification
        max_hhi = 1  # Single investment
        
        diversification = 1 - (hhi - min_hhi) / (max_hhi - min_hhi)
        return diversification
    
    def _extract_metrics(self, company: Dict[str, Any]) -> CompanyMetrics:
        """
        Extract or estimate company metrics
        """
        # In production, these would come from real data
        # For now, generate reasonable estimates
        
        return CompanyMetrics(
            revenue_growth_rate=company.get("revenue_growth", 0.8),
            burn_rate=company.get("burn_rate", 300000),
            runway_months=company.get("runway", 18),
            gross_margin=company.get("gross_margin", 0.7),
            cac_payback_months=company.get("cac_payback", 12),
            ltv_cac_ratio=company.get("ltv_cac", 3.5),
            nps_score=company.get("nps", 40),
            employee_growth_rate=company.get("employee_growth", 0.5),
            market_share=company.get("market_share", 0.02),
            competitive_moat_score=company.get("moat_score", 0.6)
        )
    
    async def identify_success_patterns(
        self,
        historical_deals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identify patterns in successful investments
        """
        # Separate successful and unsuccessful deals
        successful = [d for d in historical_deals if d.get("outcome") == "successful"]
        unsuccessful = [d for d in historical_deals if d.get("outcome") != "successful"]
        
        if not successful or not unsuccessful:
            return {"error": "Insufficient historical data"}
        
        # Extract features for pattern analysis
        success_features = self._extract_pattern_features(successful)
        fail_features = self._extract_pattern_features(unsuccessful)
        
        # Perform statistical analysis
        patterns = {
            "success_indicators": self._find_success_indicators(
                success_features,
                fail_features
            ),
            "failure_predictors": self._find_failure_predictors(
                success_features,
                fail_features
            ),
            "optimal_entry_points": self._find_optimal_entry_points(successful),
            "team_patterns": self._analyze_team_patterns(successful),
            "market_timing": self._analyze_market_timing(successful),
            "common_traits": self._find_common_traits(successful)
        }
        
        return patterns
    
    def _extract_pattern_features(
        self,
        deals: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Extract features for pattern analysis
        """
        features = []
        
        for deal in deals:
            metrics = self._extract_metrics(deal)
            
            feature_dict = {
                "revenue_growth": metrics.revenue_growth_rate,
                "burn_efficiency": metrics.runway_months / (metrics.burn_rate / 1_000_000),
                "ltv_cac": metrics.ltv_cac_ratio,
                "gross_margin": metrics.gross_margin,
                "market_share": metrics.market_share,
                "team_size": deal.get("team_size", 10),
                "founder_experience": deal.get("founder_experience_years", 5),
                "funding_stage": self._encode_stage(deal.get("funding_stage", "seed")),
                "industry_hot": self._encode_industry(deal.get("industry", "other"))
            }
            
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def _find_success_indicators(
        self,
        success_features: pd.DataFrame,
        fail_features: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """
        Find indicators that predict success
        """
        indicators = []
        
        for column in success_features.columns:
            success_mean = success_features[column].mean()
            fail_mean = fail_features[column].mean()
            
            if success_mean > fail_mean * 1.5:  # 50% higher in successful deals
                indicators.append({
                    "metric": column,
                    "success_avg": success_mean,
                    "failure_avg": fail_mean,
                    "importance": (success_mean - fail_mean) / fail_mean
                })
        
        # Sort by importance
        indicators.sort(key=lambda x: x["importance"], reverse=True)
        
        return indicators[:5]  # Top 5 indicators
    
    def _find_failure_predictors(
        self,
        success_features: pd.DataFrame,
        fail_features: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """
        Find predictors of failure
        """
        predictors = []
        
        for column in fail_features.columns:
            success_mean = success_features[column].mean()
            fail_mean = fail_features[column].mean()
            
            if fail_mean > success_mean * 1.5:  # 50% higher in failed deals
                predictors.append({
                    "metric": column,
                    "failure_avg": fail_mean,
                    "success_avg": success_mean,
                    "risk_factor": fail_mean / success_mean
                })
        
        predictors.sort(key=lambda x: x["risk_factor"], reverse=True)
        
        return predictors[:5]
    
    def _find_optimal_entry_points(
        self,
        successful_deals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Find optimal entry points for investments
        """
        entry_analysis = {
            "by_stage": {},
            "by_valuation": {},
            "by_metrics": {}
        }
        
        # Analyze by stage
        stage_returns = {}
        for deal in successful_deals:
            stage = deal.get("funding_stage", "unknown")
            return_multiple = deal.get("return_multiple", 1.0)
            
            if stage not in stage_returns:
                stage_returns[stage] = []
            stage_returns[stage].append(return_multiple)
        
        for stage, returns in stage_returns.items():
            entry_analysis["by_stage"][stage] = {
                "avg_return": np.mean(returns),
                "median_return": np.median(returns),
                "success_rate": len([r for r in returns if r > 1]) / len(returns)
            }
        
        return entry_analysis
    
    def _analyze_team_patterns(
        self,
        successful_deals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze patterns in successful teams
        """
        team_patterns = {
            "avg_team_size": np.mean([d.get("team_size", 10) for d in successful_deals]),
            "avg_founder_experience": np.mean([d.get("founder_experience_years", 5) for d in successful_deals]),
            "technical_founders": sum(1 for d in successful_deals if d.get("has_technical_founder", False)) / len(successful_deals),
            "repeat_founders": sum(1 for d in successful_deals if d.get("repeat_founder", False)) / len(successful_deals),
            "diverse_teams": sum(1 for d in successful_deals if d.get("diverse_team", False)) / len(successful_deals)
        }
        
        return team_patterns
    
    def _analyze_market_timing(
        self,
        successful_deals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze market timing patterns
        """
        timing_patterns = {
            "market_cycle": {},
            "seasonal_trends": {},
            "industry_waves": {}
        }
        
        # Analyze by market conditions
        for deal in successful_deals:
            market_condition = deal.get("market_condition", "normal")
            
            if market_condition not in timing_patterns["market_cycle"]:
                timing_patterns["market_cycle"][market_condition] = 0
            
            timing_patterns["market_cycle"][market_condition] += 1
        
        return timing_patterns
    
    def _find_common_traits(
        self,
        successful_deals: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Find common traits in successful investments
        """
        traits = []
        
        # Check for common characteristics
        if np.mean([d.get("revenue_growth", 0) for d in successful_deals]) > 1.0:
            traits.append("High revenue growth (>100% YoY)")
        
        if np.mean([d.get("gross_margin", 0) for d in successful_deals]) > 0.7:
            traits.append("Strong gross margins (>70%)")
        
        if np.mean([d.get("ltv_cac", 0) for d in successful_deals]) > 3:
            traits.append("Healthy unit economics (LTV/CAC > 3)")
        
        if sum(1 for d in successful_deals if d.get("network_effects", False)) / len(successful_deals) > 0.5:
            traits.append("Network effects present")
        
        if sum(1 for d in successful_deals if d.get("recurring_revenue", False)) / len(successful_deals) > 0.7:
            traits.append("Recurring revenue model")
        
        return traits
    
    async def calculate_investment_score(
        self,
        company_data: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive investment score
        """
        metrics = self._extract_metrics(company_data)
        
        # Component scores
        team_score = self._calculate_team_score(company_data)
        market_score = self._calculate_market_score(company_data, market_data)
        product_score = self._calculate_product_score(company_data)
        traction_score = self._calculate_traction_score(metrics)
        financials_score = self._calculate_financials_score(metrics)
        
        # Weighted average
        weights = {
            "team": 0.25,
            "market": 0.20,
            "product": 0.20,
            "traction": 0.20,
            "financials": 0.15
        }
        
        overall_score = (
            team_score * weights["team"] +
            market_score * weights["market"] +
            product_score * weights["product"] +
            traction_score * weights["traction"] +
            financials_score * weights["financials"]
        )
        
        return {
            "overall_score": round(overall_score),
            "components": {
                "team": round(team_score),
                "market": round(market_score),
                "product": round(product_score),
                "traction": round(traction_score),
                "financials": round(financials_score)
            },
            "recommendation": self._get_recommendation(overall_score),
            "confidence": self._calculate_score_confidence(company_data)
        }
    
    def _calculate_team_score(self, company_data: Dict[str, Any]) -> float:
        """Calculate team quality score"""
        score = 50  # Base score
        
        if company_data.get("repeat_founder"):
            score += 15
        
        if company_data.get("has_technical_founder"):
            score += 10
        
        if company_data.get("team_size", 0) > 10:
            score += 10
        
        if company_data.get("advisor_quality", 0) > 0.7:
            score += 15
        
        return min(score, 100)
    
    def _calculate_market_score(
        self,
        company_data: Dict[str, Any],
        market_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate market opportunity score"""
        score = 50
        
        if market_data:
            tam = market_data.get("tam", 0)
            if tam > 10_000_000_000:  # >$10B
                score += 20
            elif tam > 1_000_000_000:  # >$1B
                score += 10
            
            growth_rate = market_data.get("growth_rate", 0)
            if growth_rate > 0.3:  # >30% growth
                score += 15
            elif growth_rate > 0.15:  # >15% growth
                score += 10
        
        # Industry bonus
        hot_industries = ["ai", "climate", "biotech", "fintech"]
        if any(ind in company_data.get("industry", "").lower() for ind in hot_industries):
            score += 10
        
        return min(score, 100)
    
    def _calculate_product_score(self, company_data: Dict[str, Any]) -> float:
        """Calculate product quality score"""
        score = 50
        
        if company_data.get("has_moat"):
            score += 20
        
        if company_data.get("nps_score", 0) > 50:
            score += 15
        elif company_data.get("nps_score", 0) > 30:
            score += 10
        
        if company_data.get("product_market_fit"):
            score += 15
        
        return min(score, 100)
    
    def _calculate_traction_score(self, metrics: CompanyMetrics) -> float:
        """Calculate traction score"""
        score = 40
        
        if metrics.revenue_growth_rate > 2.0:  # >200% growth
            score += 25
        elif metrics.revenue_growth_rate > 1.0:  # >100% growth
            score += 15
        
        if metrics.employee_growth_rate > 1.0:  # Doubling team
            score += 15
        
        if metrics.market_share > 0.1:  # >10% market share
            score += 20
        elif metrics.market_share > 0.05:  # >5% market share
            score += 10
        
        return min(score, 100)
    
    def _calculate_financials_score(self, metrics: CompanyMetrics) -> float:
        """Calculate financial health score"""
        score = 40
        
        if metrics.gross_margin > 0.8:  # >80% gross margin
            score += 20
        elif metrics.gross_margin > 0.6:  # >60% gross margin
            score += 10
        
        if metrics.ltv_cac_ratio > 3:
            score += 20
        elif metrics.ltv_cac_ratio > 2:
            score += 10
        
        if metrics.runway_months > 18:
            score += 15
        elif metrics.runway_months > 12:
            score += 10
        
        if metrics.cac_payback_months < 12:
            score += 15
        elif metrics.cac_payback_months < 18:
            score += 10
        
        return min(score, 100)
    
    def _get_recommendation(self, score: float) -> str:
        """Get investment recommendation based on score"""
        if score >= 85:
            return "STRONG BUY - Exceptional opportunity"
        elif score >= 70:
            return "BUY - Strong investment case"
        elif score >= 55:
            return "CONSIDER - Promising with some risks"
        elif score >= 40:
            return "WATCH - Too early or needs improvement"
        else:
            return "PASS - Significant concerns"
    
    def _calculate_score_confidence(self, company_data: Dict[str, Any]) -> float:
        """Calculate confidence in the score"""
        confidence = 0.5
        
        # More data points increase confidence
        data_completeness = sum(
            1 for key in [
                "revenue", "burn_rate", "team_size",
                "funding_history", "gross_margin"
            ]
            if key in company_data and company_data[key] is not None
        ) / 5
        
        confidence += data_completeness * 0.4
        
        # Add small random factor for realism
        confidence += np.random.uniform(-0.05, 0.05)
        
        return min(max(confidence, 0.3), 0.95)