"""
Industry-Specific Models for FLASH
Specialized models for different verticals with industry-specific success factors
Supports: SaaS, FinTech, HealthTech, E-commerce, AI/ML, BioTech, etc.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import catboost as cb
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
import joblib
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class IndustrySpecificModel:
    """
    Models trained on industry-specific success factors
    Each industry has unique KPIs and success patterns
    """
    
    def __init__(self):
        self.industry_models = {}
        self.industry_configs = {}
        
        # Industry-specific feature weights and thresholds
        self.industry_profiles = {
            'SaaS': {
                'key_metrics': ['net_dollar_retention_percent', 'ltv_cac_ratio', 'gross_margin_percent'],
                'success_thresholds': {
                    'net_dollar_retention_percent': 110,
                    'ltv_cac_ratio': 3,
                    'gross_margin_percent': 70,
                    'monthly_recurring_revenue': 100000,
                    'churn_rate': 5  # max acceptable churn
                },
                'feature_weights': {
                    'recurring_revenue': 0.35,
                    'unit_economics': 0.30,
                    'growth_efficiency': 0.20,
                    'market_position': 0.15
                }
            },
            'FinTech': {
                'key_metrics': ['regulatory_advantage_present', 'has_data_moat', 'gross_margin_percent'],
                'success_thresholds': {
                    'regulatory_compliance': 1,
                    'security_score': 0.8,
                    'transaction_volume': 1000000,
                    'fraud_rate': 0.1  # max acceptable
                },
                'feature_weights': {
                    'regulatory_position': 0.30,
                    'trust_security': 0.25,
                    'scale_efficiency': 0.25,
                    'partnerships': 0.20
                }
            },
            'HealthTech': {
                'key_metrics': ['regulatory_advantage_present', 'patent_count', 'years_experience_avg'],
                'success_thresholds': {
                    'regulatory_approval': 1,
                    'clinical_validation': 0.8,
                    'provider_adoption': 0.3,
                    'patient_outcomes': 0.7
                },
                'feature_weights': {
                    'clinical_evidence': 0.35,
                    'regulatory_pathway': 0.30,
                    'provider_network': 0.20,
                    'patient_engagement': 0.15
                }
            },
            'E-commerce': {
                'key_metrics': ['customer_count', 'ltv_cac_ratio', 'gross_margin_percent'],
                'success_thresholds': {
                    'customer_count': 10000,
                    'repeat_purchase_rate': 0.3,
                    'gross_margin_percent': 40,
                    'inventory_turnover': 6
                },
                'feature_weights': {
                    'customer_acquisition': 0.30,
                    'operational_efficiency': 0.25,
                    'brand_strength': 0.25,
                    'supply_chain': 0.20
                }
            },
            'AI/ML': {
                'key_metrics': ['tech_differentiation_score', 'patent_count', 'has_data_moat'],
                'success_thresholds': {
                    'model_accuracy': 0.85,
                    'data_advantage': 1,
                    'compute_efficiency': 0.7,
                    'api_adoption': 0.4
                },
                'feature_weights': {
                    'technical_moat': 0.40,
                    'data_advantage': 0.30,
                    'market_application': 0.20,
                    'team_expertise': 0.10
                }
            },
            'BioTech': {
                'key_metrics': ['patent_count', 'years_experience_avg', 'total_capital_raised_usd'],
                'success_thresholds': {
                    'patent_count': 5,
                    'clinical_pipeline': 3,
                    'fda_interactions': 1,
                    'partnership_value': 10000000
                },
                'feature_weights': {
                    'ip_portfolio': 0.35,
                    'clinical_progress': 0.30,
                    'team_credentials': 0.20,
                    'capital_efficiency': 0.15
                }
            }
        }
        
        # Default profile for other industries
        self.default_profile = {
            'key_metrics': ['revenue_growth_rate_percent', 'gross_margin_percent', 'burn_multiple'],
            'success_thresholds': {
                'revenue_growth_rate_percent': 100,
                'gross_margin_percent': 50,
                'burn_multiple': 2
            },
            'feature_weights': {
                'growth': 0.30,
                'efficiency': 0.30,
                'market': 0.20,
                'team': 0.20
            }
        }
    
    def create_industry_features(self, df: pd.DataFrame, industry: str) -> pd.DataFrame:
        """Create industry-specific features"""
        features = pd.DataFrame(index=df.index)
        profile = self.industry_profiles.get(industry, self.default_profile)
        
        if industry == 'SaaS':
            # SaaS-specific metrics
            features['mrr_per_customer'] = (
                df.get('annual_revenue_run_rate', 0) / 12 / 
                (df.get('customer_count', 1) + 1)
            )
            features['expansion_revenue'] = np.maximum(
                (df.get('net_dollar_retention_percent', 100) - 100) / 100, 0
            )
            features['saas_quick_ratio'] = (
                df.get('user_growth_rate_percent', 0) / 
                (100 - df.get('product_retention_30d', 0.7) * 100 + 1)
            )
            features['rule_of_40'] = (
                df.get('revenue_growth_rate_percent', 0) + 
                df.get('gross_margin_percent', 0) - 100
            )
            
        elif industry == 'FinTech':
            # FinTech-specific metrics
            features['regulatory_readiness'] = (
                df.get('regulatory_advantage_present', 0) * 0.5 +
                (df.get('years_experience_avg', 0) > 10).astype(float) * 0.5
            )
            features['trust_score'] = (
                df.get('brand_strength_score', 0) / 5 * 0.4 +
                df.get('has_data_moat', 0) * 0.3 +
                (df.get('advisors_count', 0) > 5).astype(float) * 0.3
            )
            features['transaction_scale'] = np.log1p(
                df.get('customer_count', 0) * df.get('annual_revenue_run_rate', 0) / 1000
            ) / 20
            
        elif industry == 'HealthTech':
            # HealthTech-specific metrics
            features['clinical_credibility'] = (
                (df.get('patent_count', 0) > 0).astype(float) * 0.3 +
                np.minimum(df.get('years_experience_avg', 0) / 20, 1) * 0.4 +
                (df.get('advisors_count', 0) > 10).astype(float) * 0.3
            )
            features['regulatory_pathway_clear'] = df.get('regulatory_advantage_present', 0)
            features['provider_readiness'] = (
                df.get('customer_count', 0) / 100 * 0.5 +
                df.get('product_retention_90d', 0.5) * 0.5
            )
            
        elif industry == 'E-commerce':
            # E-commerce-specific metrics
            features['customer_acquisition_cost'] = 1 / (df.get('ltv_cac_ratio', 1) + 1)
            features['inventory_efficiency'] = (
                df.get('gross_margin_percent', 0) / 100 * 0.5 +
                (1 - df.get('burn_multiple', 5) / 10) * 0.5
            )
            features['brand_power'] = (
                df.get('brand_strength_score', 0) / 5 * 0.6 +
                np.minimum(df.get('customer_count', 0) / 50000, 1) * 0.4
            )
            
        elif industry == 'AI/ML':
            # AI/ML-specific metrics
            features['technical_advantage'] = (
                df.get('tech_differentiation_score', 0) / 5 * 0.4 +
                np.minimum(df.get('patent_count', 0) / 5, 1) * 0.3 +
                df.get('has_data_moat', 0) * 0.3
            )
            features['model_deployment_scale'] = np.log1p(df.get('customer_count', 0)) / 10
            features['ai_team_strength'] = (
                np.minimum(df.get('domain_expertise_years_avg', 0) / 10, 1) * 0.5 +
                (df.get('team_size_full_time', 0) > 20).astype(float) * 0.5
            )
            
        elif industry == 'BioTech':
            # BioTech-specific metrics
            features['ip_strength'] = np.minimum(df.get('patent_count', 0) / 20, 1)
            features['clinical_stage'] = self._infer_clinical_stage(df)
            features['capital_efficiency_biotech'] = (
                df.get('total_capital_raised_usd', 0) / 
                (df.get('founding_year', 2020) - 2015 + 1) / 10000000
            )
            features['team_pedigree'] = (
                np.minimum(df.get('years_experience_avg', 0) / 25, 1) * 0.5 +
                (df.get('prior_successful_exits_count', 0) > 0).astype(float) * 0.5
            )
        
        else:
            # Generic industry features
            features['market_position'] = (
                df.get('customer_count', 0) / 10000 * 0.3 +
                df.get('market_growth_rate_percent', 0) / 100 * 0.3 +
                df.get('tech_differentiation_score', 0) / 5 * 0.4
            )
            features['operational_excellence'] = (
                df.get('gross_margin_percent', 0) / 100 * 0.4 +
                (1 - df.get('burn_multiple', 5) / 10) * 0.3 +
                df.get('team_diversity_percent', 0) / 100 * 0.3
            )
        
        # Common cross-industry features
        features['funding_efficiency'] = (
            df.get('annual_revenue_run_rate', 0) / 
            (df.get('total_capital_raised_usd', 1) + 1)
        )
        features['team_industry_fit'] = (
            np.minimum(df.get('domain_expertise_years_avg', 0) / 15, 1)
        )
        
        return features
    
    def _infer_clinical_stage(self, df: pd.DataFrame) -> pd.Series:
        """Infer clinical stage for biotech companies"""
        stage_score = pd.Series(0.1, index=df.index)
        
        # Use proxies to infer stage
        if 'total_capital_raised_usd' in df.columns:
            capital = df['total_capital_raised_usd']
            stage_score[capital > 50000000] = 0.7  # Likely Phase II+
            stage_score[capital > 100000000] = 0.9  # Likely Phase III
            stage_score[capital < 10000000] = 0.3   # Likely preclinical
        
        return stage_score
    
    def train_industry_models(self, X: pd.DataFrame, y: pd.Series) -> None:
        """Train separate models for each industry"""
        logger.info("Training industry-specific models...")
        
        if 'sector' not in X.columns:
            logger.warning("No sector column found, cannot train industry models")
            return
        
        industries = X['sector'].value_counts()
        
        for industry in industries.index:
            if industries[industry] < 100:  # Skip industries with too few samples
                logger.warning(f"Skipping {industry} - insufficient data ({industries[industry]} samples)")
                continue
            
            logger.info(f"Training model for {industry}...")
            
            # Filter data for this industry
            industry_mask = X['sector'] == industry
            X_industry = X[industry_mask].copy()
            y_industry = y[industry_mask]
            
            # Create industry-specific features
            industry_features = self.create_industry_features(X_industry, industry)
            
            # Select relevant base features
            base_features = self._select_industry_features(X_industry, industry)
            
            # Combine features
            combined_features = pd.concat([base_features, industry_features], axis=1)
            combined_features = combined_features.fillna(0)
            
            # Handle any infinity values
            combined_features = combined_features.replace([np.inf, -np.inf], 0)
            
            # Remove sector column if present
            if 'sector' in combined_features.columns:
                combined_features = combined_features.drop('sector', axis=1)
            
            # Train ensemble for this industry
            if industry in ['SaaS', 'FinTech']:
                # Use CatBoost for these industries
                model = cb.CatBoostClassifier(
                    iterations=200,
                    learning_rate=0.05,
                    depth=5,
                    verbose=False,
                    thread_count=-1
                )
            elif industry in ['BioTech', 'HealthTech']:
                # Use Random Forest for high-variance industries
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=6,
                    random_state=42,
                    n_jobs=-1
                )
            else:
                # Use XGBoost for others
                model = xgb.XGBClassifier(
                    n_estimators=150,
                    learning_rate=0.05,
                    max_depth=5,
                    random_state=42,
                    n_jobs=-1,
                    verbosity=0
                )
            
            model.fit(combined_features, y_industry)
            self.industry_models[industry] = model
            
            # Store feature importance
            if hasattr(model, 'feature_importances_'):
                importance = pd.DataFrame({
                    'feature': combined_features.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                self.industry_configs[industry] = {
                    'top_features': importance.head(10).to_dict(),
                    'sample_count': len(y_industry),
                    'success_rate': y_industry.mean()
                }
            
            logger.info(f"Completed training for {industry}")
    
    def _select_industry_features(self, df: pd.DataFrame, industry: str) -> pd.DataFrame:
        """Select relevant features for each industry"""
        # Common important features
        common_features = [
            'total_capital_raised_usd', 'annual_revenue_run_rate',
            'team_size_full_time', 'runway_months', 'funding_rounds_count'
        ]
        
        # Industry-specific feature selection
        industry_features = {
            'SaaS': [
                'net_dollar_retention_percent', 'ltv_cac_ratio', 'gross_margin_percent',
                'customer_count', 'product_retention_30d', 'product_retention_90d',
                'dau_mau_ratio', 'burn_multiple', 'revenue_growth_rate_percent'
            ],
            'FinTech': [
                'regulatory_advantage_present', 'has_data_moat', 'brand_strength_score',
                'years_experience_avg', 'gross_margin_percent', 'customer_concentration_percent',
                'switching_cost_score', 'network_effects_present'
            ],
            'HealthTech': [
                'regulatory_advantage_present', 'patent_count', 'years_experience_avg',
                'domain_expertise_years_avg', 'advisors_count', 'customer_count',
                'product_retention_90d', 'tech_differentiation_score'
            ],
            'E-commerce': [
                'customer_count', 'ltv_cac_ratio', 'gross_margin_percent',
                'brand_strength_score', 'user_growth_rate_percent', 'burn_multiple',
                'customer_concentration_percent', 'scalability_score'
            ],
            'AI/ML': [
                'tech_differentiation_score', 'patent_count', 'has_data_moat',
                'scalability_score', 'domain_expertise_years_avg', 'network_effects_present',
                'switching_cost_score', 'customer_count'
            ],
            'BioTech': [
                'patent_count', 'years_experience_avg', 'domain_expertise_years_avg',
                'prior_successful_exits_count', 'total_capital_raised_usd',
                'advisors_count', 'team_diversity_percent', 'founding_year'
            ]
        }
        
        # Get features for this industry
        selected = common_features + industry_features.get(
            industry, 
            ['revenue_growth_rate_percent', 'gross_margin_percent', 'burn_multiple']
        )
        
        # Only include columns that exist
        available_features = [col for col in selected if col in df.columns]
        return df[available_features]
    
    def predict_industry(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions using industry-specific models"""
        predictions = np.zeros(len(X))
        
        if 'sector' not in X.columns:
            logger.warning("No sector column, using default prediction")
            return np.full(len(X), 0.5)
        
        for industry in X['sector'].unique():
            if industry in self.industry_models:
                # Get rows for this industry
                industry_mask = X['sector'] == industry
                X_industry = X[industry_mask].copy()
                
                # Create features
                industry_features = self.create_industry_features(X_industry, industry)
                base_features = self._select_industry_features(X_industry, industry)
                combined_features = pd.concat([base_features, industry_features], axis=1)
                combined_features = combined_features.fillna(0)
                
                # Remove sector column
                if 'sector' in combined_features.columns:
                    combined_features = combined_features.drop('sector', axis=1)
                
                # Predict
                model = self.industry_models[industry]
                if hasattr(model, 'predict_proba'):
                    industry_pred = model.predict_proba(combined_features)[:, 1]
                else:
                    industry_pred = model.predict(combined_features)
                
                predictions[industry_mask] = industry_pred
            else:
                # Use default prediction for unknown industries
                predictions[X['sector'] == industry] = 0.5
        
        return predictions
    
    def get_industry_insights(self, industry: str) -> Dict:
        """Get insights for a specific industry"""
        profile = self.industry_profiles.get(industry, self.default_profile)
        config = self.industry_configs.get(industry, {})
        
        return {
            'key_success_factors': profile['key_metrics'],
            'thresholds': profile['success_thresholds'],
            'top_features': config.get('top_features', {}),
            'industry_success_rate': config.get('success_rate', 0.4),
            'sample_size': config.get('sample_count', 0)
        }
    
    def save(self, path: Path) -> None:
        """Save industry models"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save each industry model
        for industry, model in self.industry_models.items():
            safe_name = industry.replace('/', '_').replace(' ', '_')
            if hasattr(model, 'save_model'):  # CatBoost
                model.save_model(str(path / f'industry_{safe_name}.cbm'))
            else:  # sklearn models
                joblib.dump(model, path / f'industry_{safe_name}.pkl')
        
        # Save configurations
        with open(path / 'industry_profiles.json', 'w') as f:
            json.dump(self.industry_profiles, f, indent=2)
        
        with open(path / 'industry_configs.json', 'w') as f:
            json.dump(self.industry_configs, f, indent=2)
        
        logger.info(f"Industry models saved to {path}")
    
    def load(self, path: Path) -> None:
        """Load industry models"""
        path = Path(path)
        
        # Load configurations
        with open(path / 'industry_profiles.json', 'r') as f:
            self.industry_profiles = json.load(f)
        
        if (path / 'industry_configs.json').exists():
            with open(path / 'industry_configs.json', 'r') as f:
                self.industry_configs = json.load(f)
        
        # Load models
        for model_file in path.glob('industry_*'):
            if model_file.suffix == '.cbm':
                industry = model_file.stem.replace('industry_', '').replace('_', '/')
                model = cb.CatBoostClassifier()
                model.load_model(str(model_file))
                self.industry_models[industry] = model
            elif model_file.suffix == '.pkl':
                industry = model_file.stem.replace('industry_', '').replace('_', ' ')
                self.industry_models[industry] = joblib.load(model_file)
        
        logger.info(f"Industry models loaded from {path}")


def train_industry_models():
    """Train industry-specific models"""
    logger.info("Starting Industry-Specific Model Training")
    
    # Load data
    df = pd.read_csv("data/final_100k_dataset_45features.csv")
    
    # Prepare features
    exclude_cols = ['success', 'startup_id', 'startup_name']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols]
    y = df['success']
    
    # Train industry models
    industry_model = IndustrySpecificModel()
    industry_model.train_industry_models(X, y)
    
    # Save models
    industry_model.save(Path("models/industry_specific"))
    
    # Test predictions and insights
    logger.info("\nIndustry Insights:")
    for industry in ['SaaS', 'FinTech', 'AI/ML']:
        insights = industry_model.get_industry_insights(industry)
        logger.info(f"\n{industry}:")
        logger.info(f"  Success Rate: {insights['industry_success_rate']:.2%}")
        logger.info(f"  Sample Size: {insights['sample_size']}")
        logger.info(f"  Key Factors: {insights['key_success_factors']}")
    
    return industry_model


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    train_industry_models()