"""
Stage-Based Hierarchical Models for FLASH
Implements stage-specific models for improved accuracy (5-10% improvement expected)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.model_selection import train_test_split
import catboost as cb
import xgboost as xgb
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
import joblib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StageHierarchicalModel:
    """
    Hierarchical model that uses stage-specific sub-models for better predictions.
    Different funding stages have different success factors and thresholds.
    """
    
    def __init__(self, base_model_path: Path = Path("models/v2_enhanced")):
        self.base_model_path = base_model_path
        self.stage_models = {}
        self.meta_model = None
        self.feature_importance = {}
        
        # Stage-specific feature weights
        self.stage_feature_weights = {
            'pre_seed': {
                'people': 0.40,  # Team is crucial early
                'advantage': 0.30,  # Product vision matters
                'market': 0.20,  # Market validation
                'capital': 0.10   # Less critical early
            },
            'seed': {
                'people': 0.30,
                'advantage': 0.30,  # Product-market fit
                'market': 0.25,
                'capital': 0.15
            },
            'series_a': {
                'market': 0.30,    # Growth metrics matter
                'advantage': 0.25,
                'capital': 0.25,   # Efficiency crucial
                'people': 0.20
            },
            'series_b': {
                'market': 0.35,    # Market domination
                'capital': 0.30,   # Unit economics
                'advantage': 0.20,
                'people': 0.15
            },
            'series_c': {
                'capital': 0.40,   # Path to profitability
                'market': 0.30,
                'advantage': 0.20,
                'people': 0.10
            },
            'growth': {
                'capital': 0.45,   # Financial metrics dominate
                'market': 0.35,
                'advantage': 0.15,
                'people': 0.05
            }
        }
        
        # Stage-specific success thresholds
        self.stage_thresholds = {
            'pre_seed': {
                'min_team_size': 2,
                'min_experience_years': 3,
                'min_retention_30d': 0.3,
                'max_burn_multiple': 10,
                'min_runway_months': 6
            },
            'seed': {
                'min_team_size': 5,
                'min_experience_years': 5,
                'min_retention_30d': 0.4,
                'max_burn_multiple': 7,
                'min_runway_months': 12,
                'min_revenue': 100000
            },
            'series_a': {
                'min_team_size': 15,
                'min_experience_years': 7,
                'min_retention_30d': 0.5,
                'max_burn_multiple': 5,
                'min_runway_months': 18,
                'min_revenue': 1000000,
                'min_growth_rate': 0.5
            },
            'series_b': {
                'min_team_size': 30,
                'min_retention_30d': 0.6,
                'max_burn_multiple': 3,
                'min_runway_months': 18,
                'min_revenue': 5000000,
                'min_growth_rate': 0.7,
                'min_ndr': 110
            },
            'series_c': {
                'min_team_size': 75,
                'min_retention_30d': 0.7,
                'max_burn_multiple': 2,
                'min_runway_months': 24,
                'min_revenue': 20000000,
                'min_growth_rate': 0.5,
                'min_ndr': 120,
                'min_gross_margin': 0.7
            },
            'growth': {
                'min_retention_30d': 0.75,
                'max_burn_multiple': 1.5,
                'min_runway_months': 36,
                'min_revenue': 50000000,
                'min_growth_rate': 0.3,
                'min_ndr': 125,
                'min_gross_margin': 0.75
            }
        }
    
    def create_stage_specific_features(self, df: pd.DataFrame, stage: str) -> pd.DataFrame:
        """Create features specific to each funding stage"""
        df_copy = df.copy()
        
        if stage == 'pre_seed':
            # Focus on team and vision
            df_copy['founder_quality_score'] = (
                df_copy['years_experience_avg'] / 20 * 0.3 +
                df_copy['domain_expertise_years_avg'] / 15 * 0.4 +
                (df_copy['prior_startup_experience_count'] > 0).astype(int) * 0.3
            )
            df_copy['vision_clarity_score'] = (
                df_copy['tech_differentiation_score'] / 5 * 0.5 +
                (df_copy['patent_count'] > 0).astype(int) * 0.3 +
                df_copy['brand_strength_score'] / 5 * 0.2
            )
            
        elif stage == 'seed':
            # Focus on early traction
            df_copy['early_traction_score'] = (
                df_copy['customer_count'] / 100 * 0.3 +
                df_copy['product_retention_30d'] * 0.4 +
                (df_copy['annual_revenue_run_rate'] > 100000).astype(int) * 0.3
            )
            if 'product_stage' in df_copy.columns:
                # Map product stages to readiness scores
                stage_scores = {'Concept': 0.2, 'Beta': 0.6, 'GA': 1.0}
                df_copy['product_stage_score'] = df_copy['product_stage'].map(stage_scores).fillna(0.5)
                df_copy['product_readiness'] = (
                    df_copy['product_stage_score'] * 0.5 +
                    df_copy.get('scalability_score', 0) * 0.5
                )
            else:
                df_copy['product_readiness'] = df_copy.get('scalability_score', 0)
            
        elif stage == 'series_a':
            # Focus on product-market fit
            df_copy['pmf_score'] = (
                df_copy['product_retention_30d'] * 0.3 +
                df_copy['net_dollar_retention_percent'] / 150 * 0.3 +
                df_copy['user_growth_rate_percent'] / 100 * 0.2 +
                (df_copy['dau_mau_ratio'] > 0.3).astype(int) * 0.2
            )
            df_copy['growth_efficiency'] = (
                np.minimum(df_copy['ltv_cac_ratio'] / 3, 1) * 0.4 +
                (1 - np.minimum(df_copy['burn_multiple'] / 5, 1)) * 0.3 +
                df_copy['gross_margin_percent'] / 100 * 0.3
            )
            
        elif stage in ['series_b', 'series_c', 'growth']:
            # Focus on scalability and economics
            scale_components = []
            if 'annual_revenue_run_rate' in df_copy.columns:
                scale_components.append(np.log1p(df_copy['annual_revenue_run_rate']) / 20 * 0.3)
            if 'customer_count' in df_copy.columns:
                scale_components.append(np.minimum(df_copy['customer_count'] / 10000, 1) * 0.3)
            if 'market_share' in df_copy.columns:
                scale_components.append(df_copy['market_share'] * 0.2)
            elif 'som_size_usd' in df_copy.columns and 'sam_size_usd' in df_copy.columns:
                scale_components.append((df_copy['som_size_usd'] / df_copy['sam_size_usd'].replace(0, 1)) * 0.2)
            
            if scale_components:
                df_copy['scale_score'] = sum(scale_components) / len(scale_components)
            else:
                df_copy['scale_score'] = 0.5
            unit_econ_components = []
            if 'gross_margin_percent' in df_copy.columns:
                unit_econ_components.append(df_copy['gross_margin_percent'] / 100 * 0.3)
            if 'ltv_cac_ratio' in df_copy.columns:
                unit_econ_components.append(np.minimum(df_copy['ltv_cac_ratio'] / 5, 1) * 0.3)
            if 'burn_multiple' in df_copy.columns:
                unit_econ_components.append((1 - np.minimum(df_copy['burn_multiple'] / 3, 1)) * 0.2)
            if 'net_dollar_retention_percent' in df_copy.columns:
                unit_econ_components.append(df_copy['net_dollar_retention_percent'] / 150 * 0.2)
            
            if unit_econ_components:
                df_copy['unit_economics_score'] = sum(unit_econ_components) / len(unit_econ_components)
            else:
                df_copy['unit_economics_score'] = 0.5
            
        return df_copy
    
    def train_stage_models(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train individual models for each funding stage"""
        stages = ['pre_seed', 'seed', 'series_a', 'series_b', 'series_c', 'growth']
        
        for stage in stages:
            logger.info(f"Training model for {stage} stage...")
            
            # Filter data for this stage
            stage_mask = X_train['funding_stage'] == stage
            if stage_mask.sum() < 50:  # Not enough data
                logger.warning(f"Insufficient data for {stage} stage ({stage_mask.sum()} samples)")
                continue
            
            X_stage = X_train[stage_mask].copy()
            y_stage = y_train[stage_mask]
            
            # Create stage-specific features
            X_stage = self.create_stage_specific_features(X_stage, stage)
            
            # Drop non-feature columns
            feature_cols = [col for col in X_stage.columns if col != 'funding_stage']
            X_stage_features = X_stage[feature_cols]
            
            # Train ensemble for this stage
            models = {
                'catboost': cb.CatBoostClassifier(
                    iterations=500,
                    learning_rate=0.05,
                    depth=6,
                    l2_leaf_reg=3,
                    verbose=False,
                    thread_count=-1
                ),
                'xgboost': xgb.XGBClassifier(
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=5,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    verbosity=0,
                    n_jobs=-1
                ),
                'lightgbm': lgb.LGBMClassifier(
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=5,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    verbose=-1,
                    n_jobs=-1
                )
            }
            
            # Train models
            stage_ensemble = {}
            for name, model in models.items():
                model.fit(X_stage_features, y_stage)
                stage_ensemble[name] = model
                
            self.stage_models[stage] = stage_ensemble
            
            # Calculate feature importance
            feature_imp = pd.DataFrame()
            for name, model in stage_ensemble.items():
                if hasattr(model, 'feature_importances_'):
                    imp_df = pd.DataFrame({
                        'feature': feature_cols,
                        f'importance_{name}': model.feature_importances_
                    })
                    if feature_imp.empty:
                        feature_imp = imp_df
                    else:
                        feature_imp = feature_imp.merge(imp_df, on='feature')
            
            feature_imp['importance_mean'] = feature_imp[[col for col in feature_imp.columns if 'importance_' in col]].mean(axis=1)
            self.feature_importance[stage] = feature_imp.nlargest(10, 'importance_mean')
            
            logger.info(f"Completed training for {stage} stage")
    
    def train_meta_model(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train meta-model that combines stage-specific predictions"""
        logger.info("Training meta-model...")
        
        # Get predictions from each stage model
        meta_features = []
        
        for index, row in X_train.iterrows():
            stage = row['funding_stage']
            features = []
            
            if stage in self.stage_models:
                # Get stage-specific features
                row_df = pd.DataFrame([row])
                row_features = self.create_stage_specific_features(row_df, stage)
                feature_cols = [col for col in row_features.columns if col != 'funding_stage']
                
                # Get predictions from each model in ensemble
                for name, model in self.stage_models[stage].items():
                    pred_proba = model.predict_proba(row_features[feature_cols])[0, 1]
                    features.append(pred_proba)
                
                # Add stage weights
                weights = self.stage_feature_weights[stage]
                features.extend(list(weights.values()))
            else:
                # Default features if no stage model
                features = [0.5] * 3 + [0.25] * 4
            
            meta_features.append(features)
        
        meta_features = np.array(meta_features)
        
        # Train meta-model
        self.meta_model = LogisticRegression(
            C=1.0,
            class_weight='balanced',
            max_iter=1000
        )
        self.meta_model.fit(meta_features, y_train)
        
        logger.info("Meta-model training complete")
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions using the hierarchical model"""
        predictions = []
        
        for index, row in X.iterrows():
            stage = row['funding_stage']
            
            if stage in self.stage_models:
                # Get stage-specific features
                row_df = pd.DataFrame([row])
                row_features = self.create_stage_specific_features(row_df, stage)
                feature_cols = [col for col in row_features.columns if col != 'funding_stage']
                
                # Get predictions from ensemble
                stage_preds = []
                for name, model in self.stage_models[stage].items():
                    pred_proba = model.predict_proba(row_features[feature_cols])[0, 1]
                    stage_preds.append(pred_proba)
                
                # Apply stage-specific adjustments
                base_pred = np.mean(stage_preds)
                adjusted_pred = self.apply_stage_adjustments(base_pred, row, stage)
                
                # Meta-model features
                meta_features = stage_preds + list(self.stage_feature_weights[stage].values())
                meta_pred = self.meta_model.predict_proba(np.array(meta_features).reshape(1, -1))[0, 1]
                
                # Combine predictions
                final_pred = 0.7 * adjusted_pred + 0.3 * meta_pred
                predictions.append([1 - final_pred, final_pred])
            else:
                # Fallback for unknown stages
                predictions.append([0.5, 0.5])
        
        return np.array(predictions)
    
    def apply_stage_adjustments(self, base_pred: float, row: pd.Series, stage: str) -> float:
        """Apply stage-specific threshold adjustments"""
        adjusted_pred = base_pred
        thresholds = self.stage_thresholds.get(stage, {})
        
        # Check each threshold
        penalties = []
        
        if 'min_team_size' in thresholds and row.get('team_size_full_time', 0) < thresholds['min_team_size']:
            penalties.append(0.05)
            
        if 'min_retention_30d' in thresholds and row.get('product_retention_30d', 0) < thresholds['min_retention_30d']:
            penalties.append(0.08)
            
        if 'max_burn_multiple' in thresholds and row.get('burn_multiple', 999) > thresholds['max_burn_multiple']:
            penalties.append(0.07)
            
        if 'min_runway_months' in thresholds and row.get('runway_months', 0) < thresholds['min_runway_months']:
            penalties.append(0.06)
            
        if 'min_revenue' in thresholds and row.get('annual_revenue_run_rate', 0) < thresholds['min_revenue']:
            penalties.append(0.05)
            
        if 'min_growth_rate' in thresholds and row.get('revenue_growth_rate_percent', 0) / 100 < thresholds['min_growth_rate']:
            penalties.append(0.04)
            
        # Apply penalties
        total_penalty = min(sum(penalties), 0.3)  # Cap at 30% penalty
        adjusted_pred = adjusted_pred * (1 - total_penalty)
        
        return adjusted_pred
    
    def save_models(self, path: Path) -> None:
        """Save all stage models and meta model"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save stage models
        for stage, models in self.stage_models.items():
            stage_path = path / f"stage_{stage}"
            stage_path.mkdir(exist_ok=True)
            for name, model in models.items():
                joblib.dump(model, stage_path / f"{name}.pkl")
        
        # Save meta model
        joblib.dump(self.meta_model, path / "meta_model.pkl")
        
        # Save configuration
        config = {
            'stage_feature_weights': self.stage_feature_weights,
            'stage_thresholds': self.stage_thresholds,
            'feature_importance': {k: v.to_dict() for k, v in self.feature_importance.items()}
        }
        joblib.dump(config, path / "config.pkl")
        
        logger.info(f"Models saved to {path}")
    
    def load_models(self, path: Path) -> None:
        """Load all stage models and meta model"""
        path = Path(path)
        
        # Load stage models
        self.stage_models = {}
        for stage_dir in path.glob("stage_*"):
            stage = stage_dir.name.replace("stage_", "")
            self.stage_models[stage] = {}
            for model_file in stage_dir.glob("*.pkl"):
                name = model_file.stem
                self.stage_models[stage][name] = joblib.load(model_file)
        
        # Load meta model
        self.meta_model = joblib.load(path / "meta_model.pkl")
        
        # Load configuration
        config = joblib.load(path / "config.pkl")
        self.stage_feature_weights = config['stage_feature_weights']
        self.stage_thresholds = config['stage_thresholds']
        self.feature_importance = {k: pd.DataFrame(v) for k, v in config['feature_importance'].items()}
        
        logger.info(f"Models loaded from {path}")


def integrate_with_api(api_server_path: str = "api_server.py") -> None:
    """Generate code to integrate stage models with the API"""
    integration_code = '''
# Add to api_server.py after model loading section

# Load stage-based hierarchical models
from stage_hierarchical_models import StageHierarchicalModel

STAGE_MODEL = None

def load_stage_models():
    """Load stage-based hierarchical models"""
    global STAGE_MODEL
    try:
        stage_model_path = Path("models/stage_hierarchical")
        if stage_model_path.exists():
            STAGE_MODEL = StageHierarchicalModel()
            STAGE_MODEL.load_models(stage_model_path)
            logger.info("Stage-based hierarchical models loaded successfully")
        else:
            logger.warning("Stage-based models not found, using base models only")
    except Exception as e:
        logger.error(f"Error loading stage models: {e}")
        STAGE_MODEL = None

# Add to startup_event function
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    load_models()
    load_stage_models()  # Add this line

# Modify predict function to use stage models
@app.post("/predict", response_model=PredictionResponse)
@rate_limit(max_requests=100, window=3600)
async def predict(request: Request, metrics: StartupMetrics):
    """Main prediction endpoint with stage-based models"""
    try:
        # ... existing code ...
        
        # Use stage-based model if available
        if STAGE_MODEL is not None:
            # Prepare data for stage model
            stage_data = pd.DataFrame([metrics.dict()])
            stage_proba = STAGE_MODEL.predict_proba(stage_data)[0, 1]
            
            # Blend with base model predictions
            base_proba = probability  # From existing prediction
            probability = 0.6 * stage_proba + 0.4 * base_proba
            
            logger.info(f"Stage model prediction: {stage_proba:.3f}, Base: {base_proba:.3f}, Final: {probability:.3f}")
        
        # ... rest of existing code ...
'''
    
    print("Integration code generated. Add the above code to api_server.py")
    return integration_code


if __name__ == "__main__":
    # Example usage for training stage models
    logger.info("Stage-based hierarchical model trainer")
    print("This module should be imported and used with training data")
    print("Example usage:")
    print("  from stage_hierarchical_models import StageHierarchicalModel")
    print("  model = StageHierarchicalModel()")
    print("  model.train_stage_models(X_train, y_train)")
    print("  model.train_meta_model(X_train, y_train)")
    print("  model.save_models(Path('models/stage_hierarchical'))")