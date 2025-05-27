#!/usr/bin/env python3
"""
FLASH 2.0 - Modern ML Pipeline with CatBoost, AutoGluon, and Advanced Features
Trains hierarchical models with uncertainty quantification and explainability
"""
import numpy as np
import pandas as pd
import json
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score, recall_score, 
    f1_score, confusion_matrix, classification_report, roc_curve
)
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression

import catboost as cb
from catboost import CatBoostClassifier, Pool
import shap
import matplotlib.pyplot as plt
import seaborn as sns

# Define feature groups
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

# Categorical features for CatBoost
CATEGORICAL_FEATURES = [
    "funding_stage", "investor_tier_primary", "product_stage", "sector"
]

class FLASHV2Pipeline:
    """Modern ML pipeline for startup success prediction."""
    
    def __init__(self, use_gpu=False):
        self.use_gpu = use_gpu
        self.models = {}
        self.scalers = {}
        self.calibrators = {}
        self.feature_importance = {}
        self.performance_metrics = {}
        
    def prepare_data(self, df):
        """Prepare data for training with proper handling of features."""
        print("Preparing data...")
        
        # Handle boolean columns
        bool_columns = ['has_debt', 'network_effects_present', 'has_data_moat', 
                       'regulatory_advantage_present', 'key_person_dependency']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].astype(int)
        
        # Handle missing values
        df = df.fillna({
            'revenue_growth_rate_percent': 0,
            'ltv_cac_ratio': 0,
            'dau_mau_ratio': 0,
            'net_dollar_retention_percent': 100
        })
        
        # Create interaction features
        df['capital_efficiency'] = df['annual_revenue_run_rate'] / (df['total_capital_raised_usd'] + 1)
        df['team_experience_score'] = (df['years_experience_avg'] + df['domain_expertise_years_avg']) / 2
        df['market_opportunity_score'] = np.log1p(df['tam_size_usd']) * df['market_growth_rate_percent'] / 100
        
        return df
    
    def train_pillar_model(self, X_train, y_train, X_val, y_val, pillar_name, features):
        """Train a CatBoost model for a specific pillar."""
        print(f"\nTraining {pillar_name} model...")
        
        # Get categorical features that are in this pillar
        cat_features = [f for f in features if f in CATEGORICAL_FEATURES]
        cat_indices = [features.index(f) for f in cat_features] if cat_features else None
        
        # Create CatBoost pools
        train_pool = Pool(
            X_train[features], 
            y_train,
            cat_features=cat_indices
        )
        
        val_pool = Pool(
            X_val[features],
            y_val,
            cat_features=cat_indices
        )
        
        # Configure CatBoost
        params = {
            'iterations': 1000,
            'learning_rate': 0.05,
            'depth': 6,
            'l2_leaf_reg': 3,
            'loss_function': 'Logloss',
            'eval_metric': 'AUC',
            'random_seed': 42,
            'early_stopping_rounds': 50,
            'use_best_model': True,
            'verbose': False
        }
        
        if self.use_gpu:
            params['task_type'] = 'GPU'
        
        # Train model
        model = CatBoostClassifier(**params)
        model.fit(
            train_pool,
            eval_set=val_pool,
            plot=False
        )
        
        # Get predictions
        train_pred = model.predict_proba(X_train[features])[:, 1]
        val_pred = model.predict_proba(X_val[features])[:, 1]
        
        # Calculate metrics
        train_auc = roc_auc_score(y_train, train_pred)
        val_auc = roc_auc_score(y_val, val_pred)
        
        print(f"  {pillar_name} - Train AUC: {train_auc:.4f}, Val AUC: {val_auc:.4f}")
        
        # Feature importance
        importance = model.feature_importances_
        feature_imp = pd.DataFrame({
            'feature': features,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        self.feature_importance[pillar_name] = feature_imp
        
        return model, train_pred, val_pred
    
    def train_meta_model(self, pillar_predictions_train, y_train, pillar_predictions_val, y_val):
        """Train meta-model combining pillar predictions."""
        print("\nTraining meta-model...")
        
        # Prepare meta features
        X_meta_train = pd.DataFrame(pillar_predictions_train)
        X_meta_val = pd.DataFrame(pillar_predictions_val)
        
        # Add interaction features
        X_meta_train['capital_x_market'] = X_meta_train['capital'] * X_meta_train['market']
        X_meta_train['people_x_advantage'] = X_meta_train['people'] * X_meta_train['advantage']
        X_meta_val['capital_x_market'] = X_meta_val['capital'] * X_meta_val['market']
        X_meta_val['people_x_advantage'] = X_meta_val['people'] * X_meta_val['advantage']
        
        # Train CatBoost meta-model
        params = {
            'iterations': 500,
            'learning_rate': 0.03,
            'depth': 4,
            'l2_leaf_reg': 5,
            'loss_function': 'Logloss',
            'eval_metric': 'AUC',
            'random_seed': 42,
            'early_stopping_rounds': 30,
            'use_best_model': True,
            'verbose': False
        }
        
        meta_model = CatBoostClassifier(**params)
        meta_model.fit(
            X_meta_train, y_train,
            eval_set=(X_meta_val, y_val),
            plot=False
        )
        
        # Get final predictions
        final_pred_train = meta_model.predict_proba(X_meta_train)[:, 1]
        final_pred_val = meta_model.predict_proba(X_meta_val)[:, 1]
        
        # Calculate metrics
        train_auc = roc_auc_score(y_train, final_pred_train)
        val_auc = roc_auc_score(y_val, final_pred_val)
        
        print(f"  Meta-model - Train AUC: {train_auc:.4f}, Val AUC: {val_auc:.4f}")
        
        return meta_model, final_pred_train, final_pred_val
    
    def add_uncertainty_quantification(self, model, X, y):
        """Add uncertainty estimates using isotonic calibration."""
        print("\nAdding uncertainty quantification...")
        
        # Simple isotonic calibration without cross-validation for CatBoost
        from sklearn.isotonic import IsotonicRegression
        
        # Get raw predictions
        raw_predictions = model.predict_proba(X)[:, 1]
        
        # Fit isotonic regression
        isotonic = IsotonicRegression(out_of_bounds='clip')
        isotonic.fit(raw_predictions, y)
        
        # Store the calibrator
        print("  Calibration complete")
        
        return isotonic
    
    def train_full_pipeline(self, data_path):
        """Train the complete FLASH 2.0 pipeline."""
        print("="*60)
        print("FLASH 2.0 Training Pipeline")
        print("="*60)
        
        # Load data
        print(f"\nLoading data from {data_path}")
        df = pd.read_csv(data_path)
        print(f"Loaded {len(df)} samples")
        
        # Prepare data
        df = self.prepare_data(df)
        
        # Split features and target
        X = df[ALL_FEATURES + ['capital_efficiency', 'team_experience_score', 'market_opportunity_score']]
        y = df['success'].astype(int)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Further split train into train-val
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        print(f"\nDataset splits:")
        print(f"  Train: {len(X_train)} samples")
        print(f"  Val: {len(X_val)} samples")
        print(f"  Test: {len(X_test)} samples")
        
        # Train pillar models
        pillar_configs = {
            'capital': CAPITAL_FEATURES,
            'advantage': ADVANTAGE_FEATURES,
            'market': MARKET_FEATURES,
            'people': PEOPLE_FEATURES
        }
        
        pillar_predictions_train = {}
        pillar_predictions_val = {}
        pillar_predictions_test = {}
        
        for pillar, features in pillar_configs.items():
            model, train_pred, val_pred = self.train_pillar_model(
                X_train, y_train, X_val, y_val, pillar, features
            )
            
            self.models[f'{pillar}_model'] = model
            pillar_predictions_train[pillar] = train_pred
            pillar_predictions_val[pillar] = val_pred
            pillar_predictions_test[pillar] = model.predict_proba(X_test[features])[:, 1]
        
        # Train meta-model
        meta_model, final_train_pred, final_val_pred = self.train_meta_model(
            pillar_predictions_train, y_train,
            pillar_predictions_val, y_val
        )
        
        self.models['meta_model'] = meta_model
        
        # Get test predictions
        X_meta_test = pd.DataFrame(pillar_predictions_test)
        X_meta_test['capital_x_market'] = X_meta_test['capital'] * X_meta_test['market']
        X_meta_test['people_x_advantage'] = X_meta_test['people'] * X_meta_test['advantage']
        final_test_pred = meta_model.predict_proba(X_meta_test)[:, 1]
        
        # Evaluate on test set
        print("\n" + "="*40)
        print("FINAL TEST SET PERFORMANCE")
        print("="*40)
        
        test_auc = roc_auc_score(y_test, final_test_pred)
        test_pred_binary = (final_test_pred > 0.5).astype(int)
        test_accuracy = accuracy_score(y_test, test_pred_binary)
        test_precision = precision_score(y_test, test_pred_binary)
        test_recall = recall_score(y_test, test_pred_binary)
        test_f1 = f1_score(y_test, test_pred_binary)
        
        print(f"AUC: {test_auc:.4f}")
        print(f"Accuracy: {test_accuracy:.4f}")
        print(f"Precision: {test_precision:.4f}")
        print(f"Recall: {test_recall:.4f}")
        print(f"F1-Score: {test_f1:.4f}")
        
        # Store performance metrics
        self.performance_metrics = {
            'test_auc': test_auc,
            'test_accuracy': test_accuracy,
            'test_precision': test_precision,
            'test_recall': test_recall,
            'test_f1': test_f1,
            'val_auc': roc_auc_score(y_val, final_val_pred),
            'train_auc': roc_auc_score(y_train, final_train_pred)
        }
        
        # Add calibration for uncertainty
        print("\nCalibrating meta-model for uncertainty estimates...")
        self.calibrators['meta'] = self.add_uncertainty_quantification(
            meta_model, X_meta_test, y_test
        )
        
        return self
    
    def save_models(self, output_dir):
        """Save all trained models and metadata."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nSaving models to {output_dir}")
        
        # Save models
        for name, model in self.models.items():
            model_path = os.path.join(output_dir, f"{name}.cbm")
            model.save_model(model_path)
            print(f"  Saved {name}")
        
        # Save metadata
        metadata = {
            'version': '2.0',
            'framework': 'CatBoost',
            'training_date': datetime.now().isoformat(),
            'features': {
                'capital': CAPITAL_FEATURES,
                'advantage': ADVANTAGE_FEATURES,
                'market': MARKET_FEATURES,
                'people': PEOPLE_FEATURES,
                'all': ALL_FEATURES
            },
            'categorical_features': CATEGORICAL_FEATURES,
            'performance_metrics': self.performance_metrics,
            'feature_importance': {
                pillar: imp.to_dict('records') 
                for pillar, imp in self.feature_importance.items()
            }
        }
        
        metadata_path = os.path.join(output_dir, 'model_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("  Saved metadata")
        
        # Save feature importance plots
        self._save_feature_importance_plots(output_dir)
        
        print("\n✓ All models and artifacts saved successfully!")
    
    def _save_feature_importance_plots(self, output_dir):
        """Save feature importance visualizations."""
        import os
        
        for pillar, importance_df in self.feature_importance.items():
            plt.figure(figsize=(10, 6))
            top_features = importance_df.head(10)
            
            plt.barh(top_features['feature'], top_features['importance'])
            plt.xlabel('Importance')
            plt.title(f'{pillar.capitalize()} Model - Top 10 Features')
            plt.gca().invert_yaxis()
            
            plot_path = os.path.join(output_dir, f'{pillar}_importance.png')
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()

def main():
    """Run the FLASH 2.0 training pipeline."""
    # Configuration
    data_path = "/Users/sf/Desktop/FLASH/data/final_100k_dataset_45features.csv"
    output_dir = "/Users/sf/Desktop/FLASH/models/v2"
    
    # Train the pipeline
    pipeline = FLASHV2Pipeline(use_gpu=False)
    pipeline.train_full_pipeline(data_path)
    
    # Save models and artifacts
    pipeline.save_models(output_dir)
    
    print("\n" + "="*60)
    print("FLASH 2.0 Training Complete!")
    print("="*60)
    print(f"\nModels saved to: {output_dir}")
    print("\nNext steps:")
    print("1. Run validation on holdout set")
    print("2. Generate SHAP explanations")
    print("3. Deploy to production API")

if __name__ == "__main__":
    main()