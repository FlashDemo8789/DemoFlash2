#!/usr/bin/env python3
"""
FLASH 2.0 Model Inference API
Production-ready FastAPI server for startup success predictions
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator, conint, confloat
from typing import Dict, List, Optional, Any, Union
import numpy as np
import pandas as pd
import catboost as cb
import joblib
import json
import logging
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import time
from functools import wraps
import hashlib
import secrets
from collections import defaultdict
from shap_explainer import FLASHExplainer
from stage_hierarchical_models import StageHierarchicalModel
from dna_pattern_analysis import StartupDNAAnalyzer
from temporal_models import TemporalPredictionModel
from industry_specific_models import IndustrySpecificModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security configuration
ENV = os.getenv('ENVIRONMENT', 'development')
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
API_KEY_HEADER = 'X-API-Key'
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # seconds

# Rate limiting storage
rate_limit_storage = defaultdict(list)

# Initialize FastAPI app
app = FastAPI(
    title="FLASH 2.0 API",
    description="AI-powered startup success prediction platform",
    version="2.0.0",
    docs_url="/docs" if ENV == "development" else None,
    redoc_url="/redoc" if ENV == "development" else None
)

# Configure CORS with security
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ENV == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600,
)

# Add trusted host middleware for production
if ENV == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[os.getenv('ALLOWED_HOSTS', '*.flash-platform.com').split(',')]
    )

# Rate limiting decorator
def rate_limit(max_requests: int = RATE_LIMIT_REQUESTS, window: int = RATE_LIMIT_WINDOW):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get client identifier (IP or API key)
            client_id = request.client.host
            if API_KEY_HEADER in request.headers:
                client_id = hashlib.sha256(request.headers[API_KEY_HEADER].encode()).hexdigest()
            
            # Clean old entries
            current_time = time.time()
            rate_limit_storage[client_id] = [
                timestamp for timestamp in rate_limit_storage[client_id]
                if current_time - timestamp < window
            ]
            
            # Check rate limit
            if len(rate_limit_storage[client_id]) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Max {max_requests} requests per {window} seconds."
                )
            
            # Record request
            rate_limit_storage[client_id].append(current_time)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Input validation middleware
@app.middleware("http")
async def validate_request_size(request: Request, call_next):
    if request.headers.get('content-length'):
        content_length = int(request.headers['content-length'])
        max_size = 1024 * 1024  # 1 MB
        if content_length > max_size:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request too large"}
            )
    response = await call_next(request)
    return response

# Model paths
MODEL_BASE_PATH = Path("models/v2_enhanced")
PILLAR_MODEL_PATH = Path("models/v2")
STAGE_MODEL_PATH = Path("models/stage_hierarchical")
MODELS = {}
PILLAR_MODELS = {}
STAGE_MODEL = None
DNA_ANALYZER = None
TEMPORAL_MODEL = None
INDUSTRY_MODEL = None
FEATURE_CONFIG = {}

# Feature definitions
CAPITAL_FEATURES = [
    "funding_stage", "total_capital_raised_usd", "cash_on_hand_usd", 
    "monthly_burn_usd", "runway_months", "annual_revenue_run_rate",
    "revenue_growth_rate_percent", "gross_margin_percent", "burn_multiple",
    "ltv_cac_ratio", "investor_tier_primary", "has_debt"
]

ADVANTAGE_FEATURES = [
    "patent_count", "network_effects_present", "has_data_moat",
    "regulatory_advantage_present", "tech_differentiation_score",
    "switching_cost_score", "brand_strength_score", "scalability_score",
    "product_stage", "product_retention_30d", "product_retention_90d"
]

MARKET_FEATURES = [
    "sector", "tam_size_usd", "sam_size_usd", "som_size_usd",
    "market_growth_rate_percent", "customer_count", "customer_concentration_percent",
    "user_growth_rate_percent", "net_dollar_retention_percent",
    "competition_intensity", "competitors_named_count", "dau_mau_ratio"
]

PEOPLE_FEATURES = [
    "founders_count", "team_size_full_time", "years_experience_avg",
    "domain_expertise_years_avg", "prior_startup_experience_count",
    "prior_successful_exits_count", "board_advisor_experience_score",
    "advisors_count", "team_diversity_percent", "key_person_dependency"
]

ALL_FEATURES = CAPITAL_FEATURES + ADVANTAGE_FEATURES + MARKET_FEATURES + PEOPLE_FEATURES


# Pydantic models for request/response
class StartupMetrics(BaseModel):
    """Input schema for startup metrics with enhanced validation"""
    # Capital metrics
    funding_stage: str = Field(..., description="Current funding stage", pattern="^(pre_seed|seed|series_a|series_b|series_c|growth)$")
    total_capital_raised_usd: confloat(ge=0, le=1e10) = Field(..., description="Total capital raised in USD")
    cash_on_hand_usd: confloat(ge=0, le=1e10) = Field(..., description="Current cash reserves")
    monthly_burn_usd: confloat(ge=0, le=1e8) = Field(..., description="Monthly burn rate")
    runway_months: Optional[confloat(ge=0, le=120)] = Field(None, description="Months of runway")
    annual_revenue_run_rate: confloat(ge=0, le=1e10) = Field(..., description="Annual revenue run rate")
    revenue_growth_rate_percent: confloat(ge=-100, le=1000) = Field(default=0, description="Revenue growth rate")
    gross_margin_percent: confloat(ge=-100, le=100) = Field(..., description="Gross margin percentage")
    burn_multiple: Optional[confloat(ge=0, le=100)] = Field(None, description="Burn multiple")
    ltv_cac_ratio: confloat(ge=0, le=100) = Field(default=0, description="LTV/CAC ratio")
    investor_tier_primary: str = Field(..., pattern="^(tier_1|tier_2|tier_3|none)$", description="Primary investor tier")
    has_debt: bool = Field(..., description="Has debt financing")
    
    # Advantage metrics
    patent_count: conint(ge=0, le=10000) = Field(default=0, description="Number of patents")
    network_effects_present: bool = Field(..., description="Network effects present")
    has_data_moat: bool = Field(..., description="Has data moat")
    regulatory_advantage_present: bool = Field(..., description="Regulatory advantage")
    tech_differentiation_score: confloat(ge=1, le=5) = Field(..., description="Tech differentiation (1-5)")
    switching_cost_score: confloat(ge=1, le=5) = Field(..., description="Switching cost (1-5)")
    brand_strength_score: confloat(ge=1, le=5) = Field(..., description="Brand strength (1-5)")
    scalability_score: confloat(ge=1, le=5) = Field(..., description="Scalability score (1-5)")
    product_stage: str = Field(..., pattern="^(concept|mvp|beta|launch|growth|mature)$", description="Product stage")
    product_retention_30d: confloat(ge=0, le=1) = Field(..., description="30-day retention")
    product_retention_90d: confloat(ge=0, le=1) = Field(..., description="90-day retention")
    
    # Market metrics
    sector: str = Field(..., max_length=100, description="Industry sector")
    tam_size_usd: confloat(ge=0, le=1e12) = Field(..., description="Total addressable market")
    sam_size_usd: confloat(ge=0, le=1e12) = Field(..., description="Serviceable addressable market")
    som_size_usd: confloat(ge=0, le=1e12) = Field(..., description="Serviceable obtainable market")
    market_growth_rate_percent: confloat(ge=-100, le=1000) = Field(..., description="Market growth rate")
    customer_count: conint(ge=0, le=1e9) = Field(..., description="Number of customers")
    customer_concentration_percent: confloat(ge=0, le=100) = Field(..., description="Customer concentration")
    user_growth_rate_percent: confloat(ge=-100, le=10000) = Field(..., description="User growth rate")
    net_dollar_retention_percent: confloat(ge=0, le=500) = Field(..., description="Net dollar retention")
    competition_intensity: confloat(ge=1, le=5) = Field(..., description="Competition intensity (1-5)")
    competitors_named_count: conint(ge=0, le=1000) = Field(..., description="Number of competitors")
    dau_mau_ratio: confloat(ge=0, le=1) = Field(..., description="DAU/MAU ratio")
    
    # People metrics
    founders_count: conint(ge=1, le=10) = Field(..., description="Number of founders")
    team_size_full_time: conint(ge=0, le=100000) = Field(..., description="Full-time team size")
    years_experience_avg: confloat(ge=0, le=50) = Field(..., description="Average years experience")
    domain_expertise_years_avg: confloat(ge=0, le=50) = Field(..., description="Domain expertise years")
    prior_startup_experience_count: conint(ge=0, le=100) = Field(..., description="Prior startup experience")
    prior_successful_exits_count: conint(ge=0, le=50) = Field(..., description="Successful exits")
    board_advisor_experience_score: confloat(ge=1, le=5) = Field(..., description="Board/advisor score (1-5)")
    advisors_count: conint(ge=0, le=1000) = Field(..., description="Number of advisors")
    team_diversity_percent: confloat(ge=0, le=100) = Field(..., description="Team diversity percentage")
    key_person_dependency: bool = Field(..., description="Key person dependency")
    
    class Config:
        max_anystr_length = 1000
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('runway_months', pre=True, always=True)
    def calculate_runway(cls, v, values):
        try:
            if v is None and 'cash_on_hand_usd' in values and 'monthly_burn_usd' in values:
                if values['monthly_burn_usd'] > 0:
                    return min(values['cash_on_hand_usd'] / values['monthly_burn_usd'], 120)
                return 120  # Default if no burn
        except (TypeError, ValueError):
            return 0
        return v if v is not None else 0
    
    @validator('burn_multiple', pre=True, always=True)
    def calculate_burn_multiple(cls, v, values):
        try:
            if v is None and 'monthly_burn_usd' in values and 'annual_revenue_run_rate' in values:
                annual_burn = values['monthly_burn_usd'] * 12
                if annual_burn > 0 and values['annual_revenue_run_rate'] > 0:
                    net_burn = annual_burn - values['annual_revenue_run_rate']
                    if net_burn > 0:
                        new_arr = values['annual_revenue_run_rate'] * 0.2
                        if new_arr > 0:
                            return min(net_burn / new_arr, 100)
                    return 0
                elif annual_burn > 0:
                    return 5
                return 0
        except (TypeError, ValueError, ZeroDivisionError):
            return 1
        return v if v is not None else 1
    
    @validator('tam_size_usd')
    def tam_greater_than_sam(cls, v, values):
        if 'sam_size_usd' in values and v < values['sam_size_usd']:
            raise ValueError('TAM must be greater than or equal to SAM')
        return v
    
    @validator('sam_size_usd')
    def sam_greater_than_som(cls, v, values):
        if 'som_size_usd' in values and v < values['som_size_usd']:
            raise ValueError('SAM must be greater than or equal to SOM')
        return v


class PredictionResponse(BaseModel):
    """Response schema for predictions"""
    success_probability: float = Field(..., ge=0, le=1)
    confidence_interval: Dict[str, float]
    risk_level: str
    key_insights: List[str]
    pillar_scores: Dict[str, float]
    recommendation: str
    timestamp: datetime
    # New comprehensive evaluation fields
    verdict: str = Field(default="PENDING")
    strength: str = Field(default="MODERATE")
    weighted_score: float = Field(default=0.5, ge=0, le=1)
    critical_failures: List[str] = Field(default_factory=list)
    below_threshold: List[str] = Field(default_factory=list)
    stage_thresholds: Dict[str, float] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    models_loaded: int
    version: str
    uptime_seconds: float


class AdvancedPredictionResponse(BaseModel):
    """Enhanced prediction response with advanced model insights"""
    success_probability: float
    confidence_score: float
    risk_factors: List[str]
    growth_indicators: List[str]
    pillar_scores: Dict[str, float]
    
    # Advanced model predictions
    stage_prediction: Optional[float] = None
    dna_pattern: Optional[Dict] = None
    temporal_predictions: Optional[Dict[str, float]] = None
    industry_insights: Optional[Dict] = None
    
    # Consolidated insights
    trajectory: Optional[str] = None
    critical_factors: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    
    # Include fields from standard response
    verdict: str = Field(default="PENDING")
    strength: str = Field(default="MODERATE")
    weighted_score: float = Field(default=0.5, ge=0, le=1)
    key_insights: List[str] = Field(default_factory=list)


# Helper functions
def create_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create engineered features matching training pipeline"""
    # Handle booleans
    bool_columns = ['has_debt', 'network_effects_present', 'has_data_moat', 
                   'regulatory_advantage_present', 'key_person_dependency']
    for col in bool_columns:
        if col in df.columns:
            df[col] = df[col].astype(int)
    
    # Financial health indicators
    df['capital_efficiency'] = df['annual_revenue_run_rate'] / (df['total_capital_raised_usd'] + 1)
    df['burn_efficiency'] = df['runway_months'] * df['monthly_burn_usd'] / (df['cash_on_hand_usd'] + 1)
    df['revenue_per_burn'] = df['annual_revenue_run_rate'] / (df['monthly_burn_usd'] * 12 + 1)
    
    # Team quality score
    df['team_quality'] = (
        df['years_experience_avg'] * 0.3 +
        df['domain_expertise_years_avg'] * 0.3 +
        df['prior_successful_exits_count'] * 10 +
        df['board_advisor_experience_score'] * 2
    )
    
    # Market opportunity
    df['market_capture'] = df['som_size_usd'] / (df['tam_size_usd'] + 1)
    df['growth_potential'] = df['market_growth_rate_percent'] * df['user_growth_rate_percent'] / 100
    
    # Competitive advantage
    df['moat_strength'] = (
        df['patent_count'].clip(0, 10) / 10 * 20 +
        df['network_effects_present'] * 25 +
        df['has_data_moat'] * 20 +
        df['switching_cost_score'] * 5 +
        df['brand_strength_score'] * 5
    )
    
    # Product-market fit
    df['pmf_score'] = (
        df['product_retention_30d'] * 30 +
        df['product_retention_90d'] * 20 +
        df['net_dollar_retention_percent'] / 2 +
        df['dau_mau_ratio'] * 50
    )
    
    # Risk indicators
    df['burn_risk'] = (df['runway_months'] < 12).astype(int)
    df['concentration_risk'] = (df['customer_concentration_percent'] > 50).astype(int)
    df['team_risk'] = df['key_person_dependency'].astype(int)
    
    # Stage encoding
    stage_map = {'Pre-seed': 0, 'Seed': 1, 'Series A': 2, 'Series B': 3, 'Series C+': 4}
    df['stage_numeric'] = df['funding_stage'].map(stage_map)
    
    # Interaction features
    df['stage_revenue_fit'] = df['stage_numeric'] * df['annual_revenue_run_rate'] / 1e6
    df['team_market_fit'] = df['team_quality'] * df['market_growth_rate_percent'] / 100
    
    return df


def load_stage_models():
    """Load stage-based hierarchical models"""
    global STAGE_MODEL
    try:
        if STAGE_MODEL_PATH.exists():
            STAGE_MODEL = StageHierarchicalModel()
            STAGE_MODEL.load_models(STAGE_MODEL_PATH)
            logger.info("Stage-based hierarchical models loaded successfully")
        else:
            logger.warning("Stage-based models not found, using base models only")
    except Exception as e:
        logger.error(f"Error loading stage models: {e}")
        STAGE_MODEL = None


def load_advanced_models():
    """Load all advanced ML models"""
    global DNA_ANALYZER, TEMPORAL_MODEL, INDUSTRY_MODEL
    
    try:
        # Load DNA Pattern Analyzer
        dna_path = Path("models/dna_analyzer")
        if dna_path.exists():
            DNA_ANALYZER = StartupDNAAnalyzer()
            DNA_ANALYZER.load(dna_path)
            logger.info("DNA pattern analyzer loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load DNA analyzer: {e}")
    
    try:
        # Load Temporal Models
        temporal_path = Path("models/temporal")
        if temporal_path.exists():
            TEMPORAL_MODEL = TemporalPredictionModel()
            TEMPORAL_MODEL.load(temporal_path)
            logger.info("Temporal models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load temporal models: {e}")
    
    try:
        # Load Industry-Specific Models
        industry_path = Path("models/industry_specific")
        if industry_path.exists():
            INDUSTRY_MODEL = IndustrySpecificModel()
            INDUSTRY_MODEL.load(industry_path)
            logger.info("Industry-specific models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load industry models: {e}")


def load_models():
    """Load all models into memory"""
    global MODELS, PILLAR_MODELS
    logger.info("Loading models...")
    
    try:
        # Load ensemble models
        for variant in ['conservative', 'aggressive', 'balanced', 'deep']:
            model_path = MODEL_BASE_PATH / f"{variant}_model.cbm"
            if model_path.exists():
                MODELS[variant] = cb.CatBoostClassifier()
                MODELS[variant].load_model(str(model_path))
                logger.info(f"Loaded {variant} model")
        
        # Load meta-learners
        for meta in ['logistic', 'nn']:
            model_path = MODEL_BASE_PATH / f"meta_{meta}.pkl"
            if model_path.exists():
                MODELS[f"meta_{meta}"] = joblib.load(model_path)
                logger.info(f"Loaded meta_{meta} model")
        
        # Load CatBoost meta
        meta_cb_path = MODEL_BASE_PATH / "meta_catboost_meta.cbm"
        if meta_cb_path.exists():
            MODELS['meta_catboost'] = cb.CatBoostClassifier()
            MODELS['meta_catboost'].load_model(str(meta_cb_path))
            logger.info("Loaded meta_catboost model")
        
        # Load v2 CAMP pillar models
        for pillar in ['capital', 'advantage', 'market', 'people']:
            model_path = PILLAR_MODEL_PATH / f"{pillar}_model.cbm"
            if model_path.exists():
                PILLAR_MODELS[pillar] = cb.CatBoostClassifier()
                PILLAR_MODELS[pillar].load_model(str(model_path))
                logger.info(f"Loaded {pillar} pillar model")
            else:
                logger.warning(f"Pillar model not found: {model_path}")
        
        logger.info(f"Successfully loaded {len(MODELS)} ensemble models and {len(PILLAR_MODELS)} pillar models")
        
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        raise


def get_stage_weights(funding_stage: str) -> Dict[str, float]:
    """Get pillar weights based on funding stage"""
    weights = {
        "Pre-seed": {"capital": 0.15, "advantage": 0.30, "market": 0.20, "people": 0.35},
        "Seed": {"capital": 0.20, "advantage": 0.30, "market": 0.25, "people": 0.25},
        "Series A": {"capital": 0.25, "advantage": 0.25, "market": 0.30, "people": 0.20},
        "Series B": {"capital": 0.25, "advantage": 0.25, "market": 0.30, "people": 0.20},
        "Series C": {"capital": 0.30, "advantage": 0.20, "market": 0.30, "people": 0.20}
    }
    return weights.get(funding_stage, weights["Seed"])


def get_stage_thresholds(funding_stage: str) -> Dict[str, float]:
    """Get minimum pillar thresholds based on funding stage"""
    thresholds = {
        "Pre-seed": {"capital": 0.30, "advantage": 0.40, "market": 0.30, "people": 0.50},
        "Seed": {"capital": 0.35, "advantage": 0.45, "market": 0.40, "people": 0.50},
        "Series A": {"capital": 0.45, "advantage": 0.50, "market": 0.50, "people": 0.45},
        "Series B": {"capital": 0.50, "advantage": 0.55, "market": 0.55, "people": 0.50},
        "Series C": {"capital": 0.55, "advantage": 0.60, "market": 0.60, "people": 0.55}
    }
    return thresholds.get(funding_stage, thresholds["Seed"])


def check_critical_failures(data: Dict[str, Any]) -> List[str]:
    """Check for critical failure conditions"""
    failures = []
    
    # Critical financial failures
    if data.get('runway_months', 0) < 3:
        failures.append("Less than 3 months runway - immediate funding required")
    
    if data.get('burn_multiple', 0) > 5:
        failures.append("Burning >5x revenue - unsustainable burn rate")
    
    # Critical market failures
    if data.get('customer_concentration_percent', 0) > 80:
        failures.append("Over 80% customer concentration - extreme dependency risk")
    
    if data.get('churn_rate', 0) > 20:
        failures.append("Monthly churn >20% - severe retention crisis")
    
    # Critical team failures
    if data.get('founders_count', 1) == 1 and data.get('key_person_dependency', True):
        failures.append("Single founder with high key person risk")
    
    return failures


def calculate_risk_adjusted_score(base_score: float, pillar_name: str, data: Dict[str, Any]) -> float:
    """Apply risk adjustments to pillar scores"""
    adjusted = base_score
    
    # Risk factors (negative adjustments)
    if pillar_name == "market":
        if data.get('customer_concentration_percent', 0) > 50:
            adjusted -= 0.1
        if data.get('regulatory_risk_score', 0) > 4:
            adjusted -= 0.15
        if data.get('competition_intensity', 0) >= 4:
            adjusted -= 0.05
    
    elif pillar_name == "capital":
        if data.get('has_debt', False) and data.get('debt_to_equity_ratio', 0) > 2:
            adjusted -= 0.1
        if data.get('investor_tier_primary') not in ['Tier 1', 'Tier 2']:
            adjusted -= 0.05
    
    elif pillar_name == "advantage":
        if not data.get('network_effects_present', False):
            adjusted -= 0.05
        if data.get('switching_cost_score', 0) < 3:
            adjusted -= 0.05
    
    elif pillar_name == "people":
        if data.get('prior_successful_exits_count', 0) == 0:
            adjusted -= 0.05
        if data.get('team_diversity_percent', 0) < 20:
            adjusted -= 0.05
    
    # Positive factors (positive adjustments)
    if pillar_name == "advantage" and data.get('patent_count', 0) > 5:
        adjusted += 0.05
    if pillar_name == "market" and data.get('net_dollar_retention_percent', 0) > 130:
        adjusted += 0.1
    if pillar_name == "people" and data.get('prior_successful_exits_count', 0) > 1:
        adjusted += 0.1
    
    return max(0, min(1, adjusted))  # Clamp between 0 and 1


def evaluate_startup_comprehensive(
    pillar_scores: Dict[str, float], 
    data: Dict[str, Any],
    base_probability: float
) -> Dict[str, Any]:
    """Comprehensive startup evaluation with stage-based criteria"""
    funding_stage = data.get('funding_stage', 'Seed')
    
    # 1. Check critical failures
    critical_failures = check_critical_failures(data)
    
    # 2. Apply risk adjustments to pillar scores
    adjusted_scores = {
        pillar: calculate_risk_adjusted_score(score, pillar, data)
        for pillar, score in pillar_scores.items()
    }
    
    # 3. Get stage-specific weights and thresholds
    weights = get_stage_weights(funding_stage)
    thresholds = get_stage_thresholds(funding_stage)
    
    # 4. Check which pillars are below threshold
    below_threshold = [
        pillar for pillar, score in adjusted_scores.items()
        if score < thresholds[pillar]
    ]
    
    # 5. Calculate weighted score
    weighted_score = sum(
        adjusted_scores[pillar] * weights[pillar]
        for pillar in adjusted_scores
    )
    
    # 6. Determine verdict and risk level
    if critical_failures:
        verdict = "FAIL"
        risk_level = "Critical Risk"
        strength = "CRITICAL"
    elif len(below_threshold) == 0 and weighted_score >= 0.6:
        verdict = "PASS"
        risk_level = "Low Risk"
        strength = "STRONG"
    elif len(below_threshold) <= 1 and weighted_score >= 0.55:
        verdict = "CONDITIONAL PASS"
        risk_level = "Medium Risk"
        strength = "MODERATE"
    elif weighted_score >= 0.5 and len(below_threshold) <= 2:
        verdict = "CONDITIONAL PASS"
        risk_level = "Medium-High Risk"
        strength = "WEAK"
    else:
        verdict = "FAIL"
        risk_level = "High Risk"
        strength = "WEAK"
    
    # 7. Adjust final probability based on comprehensive evaluation
    if verdict == "FAIL":
        adjusted_probability = min(base_probability, 0.45)
    elif verdict == "CONDITIONAL PASS":
        adjusted_probability = max(0.45, min(base_probability, 0.65))
    else:  # PASS
        adjusted_probability = max(0.55, base_probability)
    
    return {
        "verdict": verdict,
        "strength": strength,
        "risk_level": risk_level,
        "adjusted_probability": adjusted_probability,
        "weighted_score": weighted_score,
        "adjusted_pillar_scores": adjusted_scores,
        "below_threshold": below_threshold,
        "critical_failures": critical_failures,
        "stage_weights": weights,
        "stage_thresholds": thresholds
    }


def get_risk_level(probability: float, pillar_scores: Dict[str, float] = None) -> str:
    """Categorize risk based on success probability and pillar scores"""
    # Check for critical weaknesses in any pillar
    if pillar_scores:
        critical_pillars = [p for p, s in pillar_scores.items() if s < 0.3]
        weak_pillars = [p for p, s in pillar_scores.items() if s < 0.5]
        
        # If any pillar is critically weak, increase risk level
        if critical_pillars:
            if probability >= 0.7:
                return "Medium Risk (Critical weakness detected)"
            elif probability >= 0.5:
                return "High Risk"
            else:
                return "Very High Risk"
    
    # Standard risk levels with adjusted thresholds
    if probability >= 0.75:
        return "Low Risk"
    elif probability >= 0.6:
        return "Medium-Low Risk"
    elif probability >= 0.45:
        return "Medium Risk"
    elif probability >= 0.3:
        return "Medium-High Risk"
    elif probability >= 0.15:
        return "High Risk"
    else:
        return "Very High Risk"


def generate_insights(data: Dict[str, Any], prediction: float, pillar_scores: Dict[str, float] = None) -> List[str]:
    """Generate key insights based on the data and prediction"""
    insights = []
    
    # Critical warnings first
    if data['runway_months'] < 6:
        insights.append("🚨 CRITICAL: Less than 6 months runway - immediate funding needed")
    elif data['runway_months'] < 12:
        insights.append("⚠️ Warning: Runway below 12 months - plan next raise")
    
    if data['burn_multiple'] > 5:
        insights.append("🔥 High burn multiple - improve capital efficiency")
    
    # Pillar-specific insights
    if pillar_scores:
        # Capital insights
        if pillar_scores.get('capital', 0) > 0.7:
            insights.append("💪 Strong capital position with healthy metrics")
        elif pillar_scores.get('capital', 0) < 0.3:
            insights.append("💸 Capital concerns - focus on fundraising or revenue")
        
        # Advantage insights  
        if pillar_scores.get('advantage', 0) > 0.7:
            insights.append("🛡️ Strong competitive moat and differentiation")
        elif pillar_scores.get('advantage', 0) < 0.3:
            insights.append("⚡ Weak competitive position - build differentiation")
            
        # Market insights
        if pillar_scores.get('market', 0) > 0.7:
            insights.append("🎯 Excellent market fit and positioning")
        elif pillar_scores.get('market', 0) < 0.3:
            insights.append("📊 Market challenges - improve PMF and retention")
            
        # People insights
        if pillar_scores.get('people', 0) > 0.7:
            insights.append("👥 World-class team with proven experience")
        elif pillar_scores.get('people', 0) < 0.3:
            insights.append("🤝 Team gaps - hire senior talent or advisors")
    
    # Positive highlights
    if data['revenue_growth_rate_percent'] > 150:
        insights.append("🚀 Hypergrowth: {}% YoY revenue growth".format(data['revenue_growth_rate_percent']))
    elif data['revenue_growth_rate_percent'] > 100:
        insights.append("📈 Strong growth: {}% YoY revenue growth".format(data['revenue_growth_rate_percent']))
    
    if data['net_dollar_retention_percent'] > 120:
        insights.append("💎 Excellent NDR: {}% - strong expansion revenue".format(data['net_dollar_retention_percent']))
    
    if data['product_retention_30d'] > 0.8:
        insights.append("⭐ Outstanding product retention: {}% at 30 days".format(int(data['product_retention_30d'] * 100)))
    
    # Red flags
    if data['customer_concentration_percent'] > 50:
        insights.append("⚠️ High customer concentration risk: {}%".format(data['customer_concentration_percent']))
    
    if data.get('churn_rate', 0) > 10:
        insights.append("📉 High churn rate: {}% monthly".format(data.get('churn_rate', 0)))
    
    return insights[:6]  # Limit to 6 most important insights


def generate_recommendation(probability: float, pillar_scores: Dict[str, float], data: Dict[str, Any] = None) -> str:
    """Generate actionable recommendation with specific metrics"""
    # Analyze pillar strengths
    critical_pillars = [(p, s) for p, s in pillar_scores.items() if s < 0.3]
    weak_pillars = [(p, s) for p, s in pillar_scores.items() if 0.3 <= s < 0.5]
    strong_pillars = [(p, s) for p, s in pillar_scores.items() if s >= 0.7]
    
    # Detailed recommendations by pillar
    detailed_recs = {
        'capital': {
            'critical': "🚨 URGENT: Raise funding immediately or drastically cut burn. Target 18+ months runway.",
            'weak': "📊 Extend runway to 18+ months. Focus on revenue growth or raise bridge round.",
            'improve': "💰 Optimize burn rate and improve unit economics for next funding round."
        },
        'advantage': {
            'critical': "⚡ Build defensibility NOW: file patents, create network effects, or develop proprietary tech.",
            'weak': "🛡️ Strengthen moat: increase switching costs and build deeper technical differentiation.",
            'improve': "🚀 Enhance competitive position through product innovation and brand building."
        },
        'market': {
            'critical': "🎯 Fix product-market fit urgently. Consider pivot if retention < 40% at 30 days.",
            'weak': "📈 Improve retention metrics and reduce customer concentration below 30%.",
            'improve': "🌍 Expand market share and improve net dollar retention above 120%."
        },
        'people': {
            'critical': "👥 Hire senior talent immediately. Add experienced advisors in your domain.",
            'weak': "🤝 Strengthen leadership team and add board members with relevant exits.",
            'improve': "⭐ Scale team thoughtfully while maintaining culture and expertise."
        }
    }
    
    # Build recommendation based on overall score and pillar analysis
    rec_parts = []
    
    # Overall assessment
    if probability >= 0.75:
        rec_parts.append("🏆 STRONG POSITION! Ready to scale aggressively.")
    elif probability >= 0.6:
        rec_parts.append("✅ Solid foundation with clear growth path.")
    elif probability >= 0.45:
        rec_parts.append("⚠️ Moderate risk - focus on key improvements.")
    elif probability >= 0.3:
        rec_parts.append("🔶 Significant challenges - immediate action required.")
    else:
        rec_parts.append("🚨 CRITICAL: Major pivot or restructuring needed.")
    
    # Critical issues first
    if critical_pillars:
        rec_parts.append("CRITICAL FIXES:")
        for pillar, score in critical_pillars[:2]:  # Top 2 critical
            rec_parts.append(f"• {detailed_recs[pillar]['critical']}")
    
    # Then weak areas
    elif weak_pillars:
        rec_parts.append("PRIORITY IMPROVEMENTS:")
        for pillar, score in weak_pillars[:2]:  # Top 2 weak
            rec_parts.append(f"• {detailed_recs[pillar]['weak']}")
    
    # If doing well, focus on optimization
    elif probability >= 0.6:
        weakest = min(pillar_scores, key=pillar_scores.get)
        rec_parts.append(f"OPTIMIZE: {detailed_recs[weakest]['improve']}")
    
    # Add specific metric targets if data provided
    if data:
        targets = []
        if data.get('runway_months', 0) < 18:
            targets.append("runway 18+ months")
        if data.get('net_dollar_retention_percent', 0) < 110:
            targets.append("NDR >110%")
        if data.get('product_retention_30d', 0) < 0.6:
            targets.append("30d retention >60%")
        
        if targets:
            rec_parts.append(f"KEY TARGETS: {', '.join(targets)}")
    
    return " ".join(rec_parts)


# API endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    load_models()
    load_stage_models()
    load_advanced_models()


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "FLASH 2.0 API is running",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    import time
    
    return {
        "status": "healthy" if len(MODELS) > 0 else "unhealthy",
        "models_loaded": len(MODELS),
        "pillar_models_loaded": len(PILLAR_MODELS),
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/predict", response_model=PredictionResponse)
@rate_limit(max_requests=100, window=3600)
async def predict(request: Request, metrics: StartupMetrics):
    """Main prediction endpoint with rate limiting"""
    try:
        # Log request for monitoring
        logger.info(f"Prediction request from {request.client.host} for stage: {metrics.funding_stage}")
        # Convert to DataFrame
        data = pd.DataFrame([metrics.dict()])
        
        # Create engineered features
        data = create_engineered_features(data)
        
        # Get all features
        engineered_features = [
            'capital_efficiency', 'burn_efficiency', 'revenue_per_burn',
            'team_quality', 'market_capture', 'growth_potential',
            'moat_strength', 'pmf_score', 'burn_risk', 'concentration_risk',
            'team_risk', 'stage_numeric', 'stage_revenue_fit', 'team_market_fit'
        ]
        
        all_features = ALL_FEATURES + engineered_features
        
        # Get ensemble predictions
        ensemble_predictions = {}
        for variant in ['conservative', 'aggressive', 'balanced', 'deep']:
            if variant in MODELS:
                pred = MODELS[variant].predict_proba(data[all_features])[0, 1]
                ensemble_predictions[variant] = pred
        
        # Prepare meta features
        meta_features = pd.DataFrame([ensemble_predictions])
        meta_features['mean'] = meta_features.mean(axis=1)
        meta_features['std'] = meta_features.std(axis=1)
        meta_features['min'] = meta_features.min(axis=1)
        meta_features['max'] = meta_features.max(axis=1)
        
        # Get meta predictions
        meta_predictions = []
        if 'meta_logistic' in MODELS:
            meta_predictions.append(MODELS['meta_logistic'].predict_proba(meta_features)[0, 1])
        if 'meta_nn' in MODELS:
            meta_predictions.append(MODELS['meta_nn'].predict_proba(meta_features)[0, 1])
        if 'meta_catboost' in MODELS:
            meta_predictions.append(MODELS['meta_catboost'].predict_proba(meta_features)[0, 1])
        
        # Final prediction from base models
        base_prediction = np.mean(meta_predictions) if meta_predictions else np.mean(list(ensemble_predictions.values()))
        
        # Use stage-based model if available
        if STAGE_MODEL is not None:
            try:
                # Prepare data for stage model
                stage_data = pd.DataFrame([metrics.dict()])
                stage_proba = STAGE_MODEL.predict_proba(stage_data)[0, 1]
                
                # Blend predictions: 60% stage model, 40% base model
                final_prediction = 0.6 * stage_proba + 0.4 * base_prediction
                
                logger.info(f"Stage model prediction: {stage_proba:.3f}, Base: {base_prediction:.3f}, Final: {final_prediction:.3f}")
            except Exception as e:
                logger.error(f"Error using stage model: {e}")
                final_prediction = base_prediction
        else:
            final_prediction = base_prediction
        
        # Calculate confidence interval (simplified)
        std_dev = np.std(list(ensemble_predictions.values()))
        confidence_interval = {
            "lower": max(0, final_prediction - 1.96 * std_dev),
            "upper": min(1, final_prediction + 1.96 * std_dev)
        }
        
        # Calculate pillar scores using actual v2 CAMP pillar models
        pillar_scores = {}
        
        if PILLAR_MODELS:
            # Use actual pillar models for predictions
            if 'capital' in PILLAR_MODELS:
                capital_pred = PILLAR_MODELS['capital'].predict_proba(data[CAPITAL_FEATURES])[0, 1]
                pillar_scores['capital'] = float(capital_pred)
            
            if 'advantage' in PILLAR_MODELS:
                advantage_pred = PILLAR_MODELS['advantage'].predict_proba(data[ADVANTAGE_FEATURES])[0, 1]
                pillar_scores['advantage'] = float(advantage_pred)
            
            if 'market' in PILLAR_MODELS:
                market_pred = PILLAR_MODELS['market'].predict_proba(data[MARKET_FEATURES])[0, 1]
                pillar_scores['market'] = float(market_pred)
            
            if 'people' in PILLAR_MODELS:
                people_pred = PILLAR_MODELS['people'].predict_proba(data[PEOPLE_FEATURES])[0, 1]
                pillar_scores['people'] = float(people_pred)
            
            logger.info(f"Calculated pillar scores using v2 models: {pillar_scores}")
        else:
            # Fallback to simplified scores if pillar models not loaded
            logger.warning("Pillar models not loaded, using simplified scores")
            pillar_scores = {
                "capital": np.mean([data['capital_efficiency'].iloc[0], 1 - data['burn_risk'].iloc[0]]),
                "advantage": data['moat_strength'].iloc[0] / 100,
                "market": data['pmf_score'].iloc[0] / 100,
                "people": data['team_quality'].iloc[0] / 50
            }
            
            # Normalize pillar scores to 0-1
            for pillar in pillar_scores:
                pillar_scores[pillar] = min(1, max(0, pillar_scores[pillar]))
        
        # Perform comprehensive evaluation
        evaluation = evaluate_startup_comprehensive(
            pillar_scores=pillar_scores,
            data=metrics.dict(),
            base_probability=final_prediction
        )
        
        # Generate response with comprehensive evaluation
        response = PredictionResponse(
            success_probability=float(evaluation['adjusted_probability']),
            confidence_interval=confidence_interval,
            risk_level=evaluation['risk_level'],
            key_insights=generate_insights(metrics.dict(), evaluation['adjusted_probability'], evaluation['adjusted_pillar_scores']),
            pillar_scores=evaluation['adjusted_pillar_scores'],
            recommendation=generate_recommendation(evaluation['adjusted_probability'], evaluation['adjusted_pillar_scores'], metrics.dict()),
            timestamp=datetime.now(),
            # Add new fields to response
            verdict=evaluation['verdict'],
            strength=evaluation['strength'],
            weighted_score=evaluation['weighted_score'],
            critical_failures=evaluation['critical_failures'],
            below_threshold=evaluation['below_threshold'],
            stage_thresholds=evaluation['stage_thresholds']
        )
        
        # Log the response to verify structure
        logger.info(f"Response pillar_scores: {response.pillar_scores}")
        logger.info(f"Full response dict: {response.model_dump()}")
        
        return response
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict_advanced", response_model=AdvancedPredictionResponse)
@rate_limit(max_requests=100, window=3600)
async def predict_advanced(request: Request, metrics: StartupMetrics):
    """Advanced prediction endpoint using all models"""
    try:
        # First get standard prediction
        standard_response = await predict(request, metrics)
        
        # Prepare data for advanced models
        feature_dict = metrics.dict()
        df = pd.DataFrame([feature_dict])
        
        # DNA Pattern Analysis
        dna_pattern = None
        if DNA_ANALYZER:
            try:
                dna_pattern = DNA_ANALYZER.predict_growth_trajectory(df)
            except Exception as e:
                logger.error(f"DNA analysis error: {e}")
        
        # Temporal Predictions
        temporal_preds = None
        temporal_insights = None
        if TEMPORAL_MODEL:
            try:
                temporal_preds = TEMPORAL_MODEL.predict_temporal(df)
                # Convert arrays to floats
                temporal_preds = {
                    k: float(v[0]) if isinstance(v, np.ndarray) else float(v)
                    for k, v in temporal_preds.items()
                }
                temporal_insights = TEMPORAL_MODEL.get_temporal_insights(temporal_preds)
            except Exception as e:
                logger.error(f"Temporal prediction error: {e}")
        
        # Industry-Specific Insights
        industry_insights = None
        if INDUSTRY_MODEL and 'sector' in feature_dict:
            try:
                df['sector'] = feature_dict['sector']
                industry_insights = INDUSTRY_MODEL.get_industry_insights(feature_dict['sector'])
            except Exception as e:
                logger.error(f"Industry analysis error: {e}")
        
        # Stage-based prediction (already in standard response if available)
        stage_proba = getattr(standard_response, 'stage_prediction', None)
        
        # Generate consolidated insights
        all_recommendations = []
        critical_factors = []
        
        if dna_pattern:
            all_recommendations.extend(dna_pattern.get('success_indicators', []))
            critical_factors.extend(dna_pattern.get('risk_factors', []))
        
        if temporal_insights:
            all_recommendations.extend(temporal_insights.get('recommendations', []))
        
        # Calculate confidence score from interval width
        conf_interval = standard_response.confidence_interval
        interval_width = conf_interval['upper'] - conf_interval['lower']
        confidence_score = max(0.0, min(1.0, 1.0 - interval_width))
        
        # Extract risk factors and growth indicators from key insights
        risk_factors = [insight for insight in standard_response.key_insights if any(
            word in insight.lower() for word in ['critical', 'risk', 'concern', 'warning', 'urgent']
        )]
        growth_indicators = [insight for insight in standard_response.key_insights if any(
            word in insight.lower() for word in ['growth', 'excellent', 'strong', 'positive', 'advantage']
        )]
        
        # Build advanced response
        response = AdvancedPredictionResponse(
            success_probability=standard_response.success_probability,
            confidence_score=confidence_score,
            risk_factors=risk_factors[:3] if risk_factors else ["Assessment in progress"],
            growth_indicators=growth_indicators[:3] if growth_indicators else ["Assessment in progress"],
            pillar_scores=standard_response.pillar_scores,
            verdict=standard_response.verdict,
            strength=standard_response.strength,
            weighted_score=standard_response.weighted_score,
            key_insights=standard_response.key_insights,
            # Advanced features
            stage_prediction=stage_proba,
            dna_pattern=dna_pattern,
            temporal_predictions=temporal_preds,
            industry_insights=industry_insights,
            trajectory=temporal_insights.get('trajectory') if temporal_insights else None,
            critical_factors=list(set(critical_factors))[:5] if critical_factors else [],
            recommendations=list(set(all_recommendations))[:5] if all_recommendations else []
        )
        
        logger.info(f"Advanced prediction completed with DNA pattern: {dna_pattern.get('pattern_type') if dna_pattern else 'N/A'}")
        return response
        
    except Exception as e:
        logger.error(f"Advanced prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch_predict")
async def batch_predict(metrics_list: List[StartupMetrics]):
    """Batch prediction endpoint"""
    predictions = []
    for metrics in metrics_list:
        try:
            pred = await predict(metrics)
            predictions.append(pred)
        except Exception as e:
            predictions.append({"error": str(e), "metrics": metrics.dict()})
    
    return {"predictions": predictions, "count": len(predictions)}


@app.post("/explain")
@rate_limit(max_requests=50, window=3600)
async def explain_prediction(request: Request, metrics: StartupMetrics):
    """Get SHAP-based explanation for a prediction with rate limiting"""
    try:
        # Log request
        logger.info(f"Explanation request from {request.client.host}")
        # Initialize explainer if not already done
        if not hasattr(app.state, 'explainer'):
            app.state.explainer = FLASHExplainer(models_dir="models/v2")
        
        # Convert metrics to feature dict
        feature_dict = {}
        
        # Map API fields to model features
        feature_mapping = {
            # Capital features
            'funding_total_usd': metrics.total_capital_raised_usd,
            'funding_rounds': 2 if metrics.funding_stage in ['series_a', 'series_b'] else 1,
            'last_funding_amount_usd': metrics.total_capital_raised_usd * 0.6,  # Estimate
            'burn_rate': metrics.monthly_burn_usd,
            'runway_months': metrics.runway_months,
            'revenue_growth_rate': metrics.revenue_growth_rate_percent / 100,
            'gross_margin': metrics.gross_margin_percent / 100,
            'revenue_per_employee': metrics.annual_revenue_run_rate / max(metrics.team_size_full_time, 1),
            'customer_acquisition_cost': 1000,  # Default CAC
            'lifetime_value': metrics.ltv_cac_ratio * 1000,  # Derive from ratio
            'ltv_cac_ratio': metrics.ltv_cac_ratio,
            
            # Advantage features
            'has_patent': 1 if metrics.patent_count > 0 else 0,
            'tech_stack_complexity': 7,  # Default complexity
            'product_market_fit_score': 0.7,  # Default PMF
            'competitive_advantage_score': metrics.tech_differentiation_score / 5,
            'time_to_market_days': 180,  # Default 6 months
            'nps_score': 40,  # Default NPS
            'is_b2b': 1 if metrics.sector in ['enterprise', 'fintech', 'healthcare'] else 0,
            'is_saas': 1 if 'saas' in metrics.sector.lower() else 0,
            
            # Market features
            'market_size_billions': metrics.market_size_usd / 1e9,
            'market_growth_rate': metrics.market_growth_rate_percent / 100,
            'market_maturity_score': 0.5,  # Default
            'competitor_count': metrics.competitor_intensity * 20,
            'market_share': 0.02,  # Default 2% share
            'market_concentration': 0.3,  # Default
            'is_emerging_market': 0,  # Default
            'regulatory_complexity_score': 0.3,  # Default complexity
            
            # People features
            'team_size': metrics.team_size_full_time,
            'founder_experience_years': metrics.years_experience_avg,
            'founder_previous_exits': metrics.prior_successful_exits_count,
            'technical_team_ratio': 0.5,  # Default 50% technical
            'advisor_count': metrics.advisors_count,
            'board_size': 5,  # Default board size
            'employee_growth_rate': metrics.user_growth_rate_percent / 100,
            'leadership_stability_score': 0.8,  # Default
            'diversity_score': metrics.team_diversity_percent / 100,
            'has_technical_cofounder': 1,  # Default yes
            'founder_domain_expertise': 1 if metrics.domain_expertise_years_avg > 5 else 0
        }
        
        # Generate explanation
        explanation_result = app.state.explainer.explain_prediction(
            feature_mapping, 
            include_plots=True
        )
        
        # Also get the regular prediction for context
        prediction_result = await predict(request, metrics)
        
        return {
            "prediction": prediction_result.dict(),
            "explanation": explanation_result,
            "feature_mapping": feature_mapping
        }
        
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test_response")
async def test_response():
    """Test endpoint to verify response structure"""
    return {
        "success_probability": 0.75,
        "confidence_interval": {
            "lower": 0.65,
            "upper": 0.85
        },
        "risk_level": "Low Risk",
        "key_insights": [
            "✅ Strong team with previous exit experience",
            "🌍 Large addressable market (>$10B TAM)",
            "⭐ Excellent product retention metrics"
        ],
        "pillar_scores": {
            "capital": 0.68,
            "advantage": 0.72,
            "market": 0.65,
            "people": 0.78
        },
        "recommendation": "Strong position for growth. Focus on maintaining team quality.",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/features")
async def get_features():
    """Get feature definitions and requirements"""
    return {
        "capital": CAPITAL_FEATURES,
        "advantage": ADVANTAGE_FEATURES,
        "market": MARKET_FEATURES,
        "people": PEOPLE_FEATURES,
        "total_features": len(ALL_FEATURES),
        "categorical_features": ["funding_stage", "investor_tier_primary", "product_stage", "sector"]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Set start time for uptime tracking
    app.state.start_time = datetime.now().timestamp()
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )