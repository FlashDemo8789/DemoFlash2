"""
Temporal Models for FLASH
Predicts startup success over different time horizons
Short-term (0-6 months), Medium-term (6-18 months), Long-term (18+ months)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import catboost as cb
import joblib
import logging
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class TemporalPredictionModel:
    """
    Models that predict success at different time horizons
    Different factors matter for short vs long term success
    """
    
    def __init__(self):
        self.models = {
            'short_term': None,  # 0-6 months
            'medium_term': None,  # 6-18 months
            'long_term': None    # 18+ months
        }
        
        # Feature importance by time horizon
        self.temporal_weights = {
            'short_term': {
                'cash_runway': 0.35,      # Most critical short-term
                'burn_rate': 0.25,
                'revenue_growth': 0.15,
                'product_metrics': 0.15,
                'team_stability': 0.10
            },
            'medium_term': {
                'product_market_fit': 0.30,
                'unit_economics': 0.25,
                'market_dynamics': 0.20,
                'team_growth': 0.15,
                'competitive_position': 0.10
            },
            'long_term': {
                'market_size': 0.25,
                'moat_strength': 0.25,
                'scalability': 0.20,
                'founder_quality': 0.20,
                'network_effects': 0.10
            }
        }
        
        # Time decay factors
        self.decay_factors = {
            'short_term': 0.9,   # Recent data very important
            'medium_term': 0.7,  # Moderate decay
            'long_term': 0.5     # Historical trends matter more
        }
        
    def create_temporal_features(self, df: pd.DataFrame, horizon: str) -> pd.DataFrame:
        """Create features relevant for specific time horizons"""
        features = pd.DataFrame(index=df.index)
        
        if horizon == 'short_term':
            # Short-term survival features
            features['runway_risk'] = (df.get('runway_months', 12) < 6).astype(float)
            features['burn_severity'] = np.minimum(df.get('monthly_burn_usd', 0) / 100000, 1)
            features['cash_position'] = np.log1p(df.get('cash_on_hand_usd', 0)) / 20
            features['immediate_revenue'] = (df.get('annual_revenue_run_rate', 0) > 0).astype(float)
            features['team_stability_score'] = 1 - (df.get('key_person_dependency', 0) / 5)
            
            # Quick wins potential
            features['quick_growth'] = df.get('user_growth_rate_percent', 0) / 100
            features['immediate_traction'] = df.get('customer_count', 0) / 100
            
        elif horizon == 'medium_term':
            # Medium-term growth features
            features['pmf_score'] = (
                df.get('product_retention_30d', 0.5) * 0.4 +
                (df.get('net_dollar_retention_percent', 100) / 150) * 0.3 +
                (df.get('dau_mau_ratio', 0.2) > 0.3).astype(float) * 0.3
            )
            features['unit_economics'] = np.minimum(df.get('ltv_cac_ratio', 0) / 3, 1)
            features['growth_efficiency'] = 1 / (df.get('burn_multiple', 5) + 1)
            features['market_momentum'] = df.get('market_growth_rate_percent', 0) / 100
            features['competitive_advantage'] = df.get('tech_differentiation_score', 0) / 5
            
            # Team scaling ability
            features['team_growth_capability'] = (
                np.minimum(df.get('team_size_full_time', 0) / 50, 1) * 0.5 +
                (df.get('advisors_count', 0) > 3).astype(float) * 0.5
            )
            
        elif horizon == 'long_term':
            # Long-term dominance features
            features['market_opportunity'] = np.log1p(df.get('tam_size_usd', 0)) / 25
            features['moat_strength'] = (
                df.get('patent_count', 0) / 10 * 0.2 +
                df.get('network_effects_present', 0) * 0.3 +
                df.get('has_data_moat', 0) * 0.2 +
                df.get('switching_cost_score', 0) / 5 * 0.3
            )
            features['scalability_potential'] = df.get('scalability_score', 0) / 5
            features['founder_long_term'] = (
                df.get('prior_successful_exits_count', 0) / 2 * 0.4 +
                np.minimum(df.get('domain_expertise_years_avg', 0) / 15, 1) * 0.6
            )
            features['brand_power'] = df.get('brand_strength_score', 0) / 5
            features['regulatory_moat'] = df.get('regulatory_advantage_present', 0)
            
        # Add common temporal indicators
        features['stage_maturity'] = self._calculate_stage_maturity(df)
        features['momentum_score'] = self._calculate_momentum(df, horizon)
        
        return features
    
    def _calculate_stage_maturity(self, df: pd.DataFrame) -> pd.Series:
        """Calculate company maturity based on various factors"""
        maturity_score = pd.Series(0.5, index=df.index)
        
        # Revenue maturity
        if 'annual_revenue_run_rate' in df.columns:
            revenue_maturity = np.minimum(df['annual_revenue_run_rate'] / 10000000, 1)
            maturity_score += revenue_maturity * 0.3
        
        # Team maturity
        if 'team_size_full_time' in df.columns:
            team_maturity = np.minimum(df['team_size_full_time'] / 100, 1)
            maturity_score += team_maturity * 0.2
        
        # Funding maturity
        if 'funding_rounds_count' in df.columns:
            funding_maturity = np.minimum(df['funding_rounds_count'] / 5, 1)
            maturity_score += funding_maturity * 0.2
        
        # Product maturity
        if 'product_stage' in df.columns:
            product_map = {'Concept': 0.2, 'Beta': 0.6, 'GA': 1.0}
            product_maturity = df['product_stage'].map(product_map).fillna(0.5)
            maturity_score += product_maturity * 0.3
        
        return np.minimum(maturity_score, 1.0)
    
    def _calculate_momentum(self, df: pd.DataFrame, horizon: str) -> pd.Series:
        """Calculate momentum score based on growth indicators"""
        momentum = pd.Series(0.5, index=df.index)
        
        # Weight recent metrics more for short-term
        decay = self.decay_factors[horizon]
        
        if 'revenue_growth_rate_percent' in df.columns:
            momentum += (df['revenue_growth_rate_percent'] / 200) * decay
        
        if 'user_growth_rate_percent' in df.columns:
            momentum += (df['user_growth_rate_percent'] / 200) * (decay * 0.8)
        
        if 'customer_count' in df.columns and 'founding_year' in df.columns:
            age = datetime.now().year - df['founding_year']
            customer_velocity = df['customer_count'] / (age + 1)
            momentum += np.minimum(customer_velocity / 1000, 1) * (decay * 0.6)
        
        return np.minimum(momentum, 1.0)
    
    def train_temporal_models(self, X: pd.DataFrame, y: pd.Series) -> None:
        """Train models for different time horizons"""
        logger.info("Training temporal prediction models...")
        
        for horizon in ['short_term', 'medium_term', 'long_term']:
            logger.info(f"Training {horizon} model...")
            
            # Create temporal features
            temporal_features = self.create_temporal_features(X, horizon)
            
            # Combine with original features
            feature_subset = self._select_features_for_horizon(X, horizon)
            combined_features = pd.concat([feature_subset, temporal_features], axis=1)
            
            # Remove any NaN values
            combined_features = combined_features.fillna(0)
            
            # Train model
            if horizon == 'short_term':
                # Use gradient boosting for short-term (captures non-linearities)
                model = GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=4,
                    random_state=42
                )
            elif horizon == 'medium_term':
                # Use CatBoost for medium-term
                model = cb.CatBoostClassifier(
                    iterations=200,
                    learning_rate=0.05,
                    depth=5,
                    verbose=False,
                    thread_count=-1
                )
            else:
                # Use logistic regression for long-term (more stable)
                model = LogisticRegression(
                    C=1.0,
                    max_iter=1000,
                    random_state=42
                )
            
            model.fit(combined_features, y)
            self.models[horizon] = model
            
            logger.info(f"Completed training {horizon} model")
    
    def _select_features_for_horizon(self, df: pd.DataFrame, horizon: str) -> pd.DataFrame:
        """Select relevant features based on time horizon"""
        if horizon == 'short_term':
            # Focus on financial health and immediate metrics
            relevant_cols = [
                'cash_on_hand_usd', 'monthly_burn_usd', 'runway_months',
                'annual_revenue_run_rate', 'customer_count', 'team_size_full_time',
                'product_retention_30d', 'burn_multiple'
            ]
        elif horizon == 'medium_term':
            # Focus on growth and efficiency
            relevant_cols = [
                'revenue_growth_rate_percent', 'user_growth_rate_percent',
                'ltv_cac_ratio', 'gross_margin_percent', 'net_dollar_retention_percent',
                'market_growth_rate_percent', 'tech_differentiation_score',
                'product_retention_90d', 'dau_mau_ratio'
            ]
        else:
            # Focus on strategic position and moats
            relevant_cols = [
                'tam_size_usd', 'sam_size_usd', 'patent_count',
                'network_effects_present', 'has_data_moat', 'switching_cost_score',
                'prior_successful_exits_count', 'domain_expertise_years_avg',
                'brand_strength_score', 'scalability_score'
            ]
        
        # Only include columns that exist
        available_cols = [col for col in relevant_cols if col in df.columns]
        return df[available_cols]
    
    def predict_temporal(self, X: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Make predictions for all time horizons"""
        predictions = {}
        
        for horizon, model in self.models.items():
            if model is not None:
                # Create temporal features
                temporal_features = self.create_temporal_features(X, horizon)
                
                # Combine with original features
                feature_subset = self._select_features_for_horizon(X, horizon)
                combined_features = pd.concat([feature_subset, temporal_features], axis=1)
                combined_features = combined_features.fillna(0)
                
                # Predict
                if hasattr(model, 'predict_proba'):
                    pred_proba = model.predict_proba(combined_features)[:, 1]
                else:
                    pred_proba = model.predict(combined_features)
                
                predictions[horizon] = pred_proba
        
        return predictions
    
    def get_temporal_insights(self, predictions: Dict[str, float]) -> Dict:
        """Generate insights from temporal predictions"""
        insights = {
            'trajectory': self._determine_trajectory(predictions),
            'critical_period': self._identify_critical_period(predictions),
            'recommendations': self._generate_recommendations(predictions)
        }
        return insights
    
    def _determine_trajectory(self, predictions: Dict[str, float]) -> str:
        """Determine overall trajectory based on temporal predictions"""
        short = predictions.get('short_term', 0.5)
        medium = predictions.get('medium_term', 0.5)
        long = predictions.get('long_term', 0.5)
        
        if short > 0.7 and medium > 0.7 and long > 0.7:
            return 'strong_growth'
        elif short > 0.7 and medium > 0.5 and long < 0.5:
            return 'early_peak'
        elif short < 0.5 and medium > 0.6 and long > 0.7:
            return 'late_bloomer'
        elif short < 0.3:
            return 'immediate_risk'
        else:
            return 'steady_progress'
    
    def _identify_critical_period(self, predictions: Dict[str, float]) -> str:
        """Identify the most critical time period for the startup"""
        periods = ['short_term', 'medium_term', 'long_term']
        min_period = min(periods, key=lambda p: predictions.get(p, 0.5))
        
        if predictions.get(min_period, 0.5) < 0.3:
            return min_period
        return 'none'
    
    def _generate_recommendations(self, predictions: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations based on temporal analysis"""
        recommendations = []
        
        short = predictions.get('short_term', 0.5)
        medium = predictions.get('medium_term', 0.5)
        long = predictions.get('long_term', 0.5)
        
        if short < 0.4:
            recommendations.append("Immediate action needed: Focus on runway extension and revenue generation")
        
        if medium < 0.5 and short > 0.6:
            recommendations.append("Prepare for scaling challenges: Strengthen unit economics and team")
        
        if long < 0.5:
            recommendations.append("Build stronger moats: Invest in IP, network effects, or switching costs")
        
        if short > 0.7 and long > 0.7:
            recommendations.append("Maintain momentum: Continue current strategy while preparing for scale")
        
        return recommendations
    
    def save(self, path: Path) -> None:
        """Save temporal models"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        for horizon, model in self.models.items():
            if model is not None:
                joblib.dump(model, path / f'temporal_{horizon}.pkl')
        
        # Save configuration
        config = {
            'temporal_weights': self.temporal_weights,
            'decay_factors': self.decay_factors
        }
        with open(path / 'temporal_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Temporal models saved to {path}")
    
    def load(self, path: Path) -> None:
        """Load temporal models"""
        path = Path(path)
        
        for horizon in ['short_term', 'medium_term', 'long_term']:
            model_path = path / f'temporal_{horizon}.pkl'
            if model_path.exists():
                self.models[horizon] = joblib.load(model_path)
        
        # Load configuration
        with open(path / 'temporal_config.json', 'r') as f:
            config = json.load(f)
            self.temporal_weights = config['temporal_weights']
            self.decay_factors = config['decay_factors']
        
        logger.info(f"Temporal models loaded from {path}")


def train_temporal_models():
    """Train temporal prediction models"""
    logger.info("Starting Temporal Model Training")
    
    # Load data
    df = pd.read_csv("data/final_100k_dataset_45features.csv")
    
    # Prepare features
    exclude_cols = ['success', 'startup_id', 'startup_name']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols]
    y = df['success']
    
    # Train temporal models
    temporal_model = TemporalPredictionModel()
    temporal_model.train_temporal_models(X, y)
    
    # Save models
    temporal_model.save(Path("models/temporal"))
    
    # Test predictions
    sample = X.sample(3)
    for idx, row in sample.iterrows():
        predictions = temporal_model.predict_temporal(pd.DataFrame([row]))
        
        # Convert to single values
        pred_values = {
            horizon: float(pred[0]) if isinstance(pred, np.ndarray) else float(pred)
            for horizon, pred in predictions.items()
        }
        
        insights = temporal_model.get_temporal_insights(pred_values)
        
        logger.info(f"\nSample {idx}:")
        logger.info(f"  Short-term: {pred_values.get('short_term', 0):.3f}")
        logger.info(f"  Medium-term: {pred_values.get('medium_term', 0):.3f}")
        logger.info(f"  Long-term: {pred_values.get('long_term', 0):.3f}")
        logger.info(f"  Trajectory: {insights['trajectory']}")
        logger.info(f"  Critical Period: {insights['critical_period']}")
        logger.info(f"  Recommendations: {insights['recommendations']}")
    
    return temporal_model


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    train_temporal_models()