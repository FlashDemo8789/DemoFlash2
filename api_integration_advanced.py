
# Add this code to api_server.py after the existing model loading section

# ========== ADVANCED MODEL IMPORTS ==========
from train_stage_models_quick import SimpleStageModel
from dna_pattern_analysis import StartupDNAAnalyzer
from temporal_models import TemporalPredictionModel
from industry_specific_models import IndustrySpecificModel

# ========== GLOBAL ADVANCED MODELS ==========
STAGE_MODEL = None
DNA_ANALYZER = None
TEMPORAL_MODEL = None
INDUSTRY_MODEL = None

def load_advanced_models():
    """Load all advanced ML models"""
    global STAGE_MODEL, DNA_ANALYZER, TEMPORAL_MODEL, INDUSTRY_MODEL
    
    try:
        # Load Stage-Based Models
        stage_path = Path("models/stage_hierarchical_simple")
        if stage_path.exists():
            STAGE_MODEL = SimpleStageModel()
            # Load individual stage models
            for stage_file in stage_path.glob("stage_*.cbm"):
                stage = stage_file.stem.replace("stage_", "")
                model = cb.CatBoostClassifier()
                model.load_model(str(stage_file))
                STAGE_MODEL.stage_models[stage] = model
            logger.info("Stage-based models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load stage models: {e}")
    
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

# Update the startup event
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    load_models()  # Existing model loading
    load_advanced_models()  # Add advanced models

# ========== ENHANCED PREDICTION RESPONSE ==========
from pydantic import BaseModel
from typing import Dict, List, Optional

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

# ========== ENHANCED PREDICTION ENDPOINT ==========
@app.post("/predict_advanced", response_model=AdvancedPredictionResponse)
async def predict_advanced(request: Request, metrics: StartupMetrics):
    """Advanced prediction endpoint using all models"""
    try:
        # Prepare data
        feature_dict = metrics.dict()
        df = pd.DataFrame([feature_dict])
        
        # Get base prediction (existing logic)
        input_data = prepare_model_input(feature_dict)
        base_proba = META_MODEL.predict_proba(input_data)[0, 1]
        
        # Stage-based prediction
        stage_proba = None
        if STAGE_MODEL and 'funding_stage' in feature_dict:
            # Map funding stage
            stage_map = {
                'pre_seed': 'pre_seed',
                'seed': 'seed', 
                'series_a': 'series_a',
                'series_b': 'series_b',
                'series_c': 'series_c'
            }
            df['funding_stage'] = stage_map.get(feature_dict.get('funding_stage', '').lower(), 'seed')
            stage_proba = float(STAGE_MODEL.predict_proba(df))
        
        # DNA Pattern Analysis
        dna_pattern = None
        if DNA_ANALYZER:
            dna_pattern = DNA_ANALYZER.predict_growth_trajectory(df)
        
        # Temporal Predictions
        temporal_preds = None
        temporal_insights = None
        if TEMPORAL_MODEL:
            temporal_preds = TEMPORAL_MODEL.predict_temporal(df)
            # Convert arrays to floats
            temporal_preds = {
                k: float(v[0]) if isinstance(v, np.ndarray) else float(v)
                for k, v in temporal_preds.items()
            }
            temporal_insights = TEMPORAL_MODEL.get_temporal_insights(temporal_preds)
        
        # Industry-Specific Prediction
        industry_insights = None
        industry_proba = None
        if INDUSTRY_MODEL and 'sector' in feature_dict:
            df['sector'] = feature_dict['sector']
            industry_proba = float(INDUSTRY_MODEL.predict_industry(df)[0])
            industry_insights = INDUSTRY_MODEL.get_industry_insights(feature_dict['sector'])
        
        # Combine all predictions (weighted ensemble)
        final_proba = base_proba
        weight_sum = 1.0
        
        if stage_proba is not None:
            final_proba += stage_proba * 0.2
            weight_sum += 0.2
            
        if industry_proba is not None:
            final_proba += industry_proba * 0.15
            weight_sum += 0.15
            
        if temporal_preds and 'medium_term' in temporal_preds:
            final_proba += temporal_preds['medium_term'] * 0.1
            weight_sum += 0.1
        
        final_proba = final_proba / weight_sum
        
        # Generate consolidated insights
        all_recommendations = []
        critical_factors = []
        
        if dna_pattern:
            all_recommendations.extend(dna_pattern.get('success_indicators', []))
            critical_factors.extend(dna_pattern.get('risk_factors', []))
        
        if temporal_insights:
            all_recommendations.extend(temporal_insights.get('recommendations', []))
            
        # Calculate pillar scores (existing logic)
        pillar_scores = calculate_pillar_scores(feature_dict)
        
        # Build response
        response = AdvancedPredictionResponse(
            success_probability=round(final_proba, 3),
            confidence_score=calculate_confidence(feature_dict),
            risk_factors=identify_risk_factors(feature_dict) + critical_factors[:3],
            growth_indicators=identify_growth_indicators(feature_dict),
            pillar_scores=pillar_scores,
            stage_prediction=stage_proba,
            dna_pattern=dna_pattern,
            temporal_predictions=temporal_preds,
            industry_insights=industry_insights,
            trajectory=temporal_insights.get('trajectory') if temporal_insights else None,
            critical_factors=list(set(critical_factors))[:5],
            recommendations=list(set(all_recommendations))[:5]
        )
        
        logger.info(f"Advanced prediction: {final_proba:.3f} (base: {base_proba:.3f})")
        return response
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== MODEL COMPARISON ENDPOINT ==========
@app.post("/compare_models")
async def compare_models(metrics: StartupMetrics):
    """Compare predictions across all models"""
    try:
        feature_dict = metrics.dict()
        df = pd.DataFrame([feature_dict])
        
        comparisons = {
            "base_model": float(META_MODEL.predict_proba(prepare_model_input(feature_dict))[0, 1])
        }
        
        if STAGE_MODEL and 'funding_stage' in feature_dict:
            df['funding_stage'] = feature_dict.get('funding_stage', 'seed').lower()
            comparisons["stage_model"] = float(STAGE_MODEL.predict_proba(df))
        
        if TEMPORAL_MODEL:
            temp_preds = TEMPORAL_MODEL.predict_temporal(df)
            comparisons["temporal_short"] = float(temp_preds.get('short_term', [0.5])[0])
            comparisons["temporal_medium"] = float(temp_preds.get('medium_term', [0.5])[0])
            comparisons["temporal_long"] = float(temp_preds.get('long_term', [0.5])[0])
        
        if INDUSTRY_MODEL and 'sector' in feature_dict:
            df['sector'] = feature_dict['sector']
            comparisons["industry_model"] = float(INDUSTRY_MODEL.predict_industry(df)[0])
        
        return {
            "predictions": comparisons,
            "consensus": np.mean(list(comparisons.values())),
            "variance": np.var(list(comparisons.values())),
            "recommendation": "high_confidence" if np.var(list(comparisons.values())) < 0.01 else "review_needed"
        }
        
    except Exception as e:
        logger.error(f"Model comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
