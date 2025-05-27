#!/usr/bin/env python3
"""
FLASH 2.0 Enhanced - Advanced ensemble techniques without AutoGluon
Uses multiple CatBoost models with different configurations for ensemble diversity
"""
import numpy as np
import pandas as pd
import json
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from sklearn.ensemble import VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import catboost as cb
from catboost import CatBoostClassifier, Pool
import matplotlib.pyplot as plt
import seaborn as sns

# Feature groups (same as before)
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
CATEGORICAL_FEATURES = ["funding_stage", "investor_tier_primary", "product_stage", "sector"]


class EnhancedFLASHPipeline:
    """Enhanced ML pipeline with advanced ensemble techniques."""
    
    def __init__(self):
        self.models = {}
        self.ensemble_models = {}
        self.performance_metrics = {}
        
    def create_advanced_features(self, df):
        """Create advanced feature engineering."""
        print("Creating advanced features...")
        
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
    
    def create_model_variants(self):
        """Create different CatBoost configurations for ensemble diversity."""
        variants = {
            'conservative': {
                'iterations': 500,
                'learning_rate': 0.03,
                'depth': 4,
                'l2_leaf_reg': 5,
                'subsample': 0.8,
                'random_strength': 0.5
            },
            'aggressive': {
                'iterations': 1000,
                'learning_rate': 0.05,
                'depth': 7,
                'l2_leaf_reg': 1,
                'subsample': 0.9,
                'random_strength': 0.2
            },
            'balanced': {
                'iterations': 750,
                'learning_rate': 0.04,
                'depth': 6,
                'l2_leaf_reg': 3,
                'subsample': 0.85,
                'random_strength': 0.3
            },
            'deep': {
                'iterations': 600,
                'learning_rate': 0.02,
                'depth': 8,
                'l2_leaf_reg': 2,
                'subsample': 0.7,
                'random_strength': 0.4
            }
        }
        
        # Add common parameters
        for config in variants.values():
            config.update({
                'loss_function': 'Logloss',
                'eval_metric': 'AUC',
                'random_seed': 42,
                'early_stopping_rounds': 50,
                'use_best_model': True,
                'verbose': False
            })
        
        return variants
    
    def train_ensemble_models(self, X_train, y_train, X_val, y_val, features, cat_indices):
        """Train multiple model variants for ensemble."""
        print("\nTraining ensemble models...")
        
        variants = self.create_model_variants()
        ensemble_predictions_train = {}
        ensemble_predictions_val = {}
        
        for name, params in variants.items():
            print(f"  Training {name} variant...")
            
            # Create pools
            train_pool = Pool(X_train[features], y_train, cat_features=cat_indices)
            val_pool = Pool(X_val[features], y_val, cat_features=cat_indices)
            
            # Train model
            model = CatBoostClassifier(**params)
            model.fit(train_pool, eval_set=val_pool, plot=False)
            
            # Get predictions
            train_pred = model.predict_proba(X_train[features])[:, 1]
            val_pred = model.predict_proba(X_val[features])[:, 1]
            
            ensemble_predictions_train[name] = train_pred
            ensemble_predictions_val[name] = val_pred
            
            # Store model
            self.ensemble_models[name] = model
            
            # Evaluate
            val_auc = roc_auc_score(y_val, val_pred)
            print(f"    {name} AUC: {val_auc:.4f}")
        
        return ensemble_predictions_train, ensemble_predictions_val
    
    def train_stacking_meta_learner(self, ensemble_preds_train, y_train, ensemble_preds_val, y_val):
        """Train a meta-learner to combine ensemble predictions."""
        print("\nTraining stacking meta-learner...")
        
        # Convert predictions to DataFrame
        X_meta_train = pd.DataFrame(ensemble_preds_train)
        X_meta_val = pd.DataFrame(ensemble_preds_val)
        
        # Add statistical features
        X_meta_train['mean'] = X_meta_train.mean(axis=1)
        X_meta_train['std'] = X_meta_train.std(axis=1)
        X_meta_train['min'] = X_meta_train.min(axis=1)
        X_meta_train['max'] = X_meta_train.max(axis=1)
        
        X_meta_val['mean'] = X_meta_val.mean(axis=1)
        X_meta_val['std'] = X_meta_val.std(axis=1)
        X_meta_val['min'] = X_meta_val.min(axis=1)
        X_meta_val['max'] = X_meta_val.max(axis=1)
        
        # Train multiple meta-learners
        meta_learners = {
            'logistic': LogisticRegression(C=0.1, random_state=42),
            'nn': MLPClassifier(hidden_layer_sizes=(50, 30), max_iter=1000, random_state=42),
            'catboost_meta': CatBoostClassifier(
                iterations=300, learning_rate=0.03, depth=3,
                verbose=False, random_seed=42
            )
        }
        
        meta_predictions = {}
        
        for name, learner in meta_learners.items():
            print(f"  Training {name} meta-learner...")
            learner.fit(X_meta_train, y_train)
            
            pred_train = learner.predict_proba(X_meta_train)[:, 1]
            pred_val = learner.predict_proba(X_meta_val)[:, 1]
            
            train_auc = roc_auc_score(y_train, pred_train)
            val_auc = roc_auc_score(y_val, pred_val)
            
            print(f"    {name} - Train AUC: {train_auc:.4f}, Val AUC: {val_auc:.4f}")
            
            meta_predictions[name] = (pred_train, pred_val)
            self.models[f'meta_{name}'] = learner
        
        # Blend meta-learner predictions
        final_train_pred = np.mean([pred[0] for pred in meta_predictions.values()], axis=0)
        final_val_pred = np.mean([pred[1] for pred in meta_predictions.values()], axis=0)
        
        return final_train_pred, final_val_pred, X_meta_train, X_meta_val
    
    def train_full_pipeline(self, data_path):
        """Train the complete enhanced pipeline."""
        print("="*60)
        print("FLASH 2.0 Enhanced Pipeline")
        print("="*60)
        
        # Load and prepare data
        print(f"\nLoading data from {data_path}")
        df = pd.read_csv(data_path)
        df = self.create_advanced_features(df)
        
        # Get all features including engineered
        engineered_features = [
            'capital_efficiency', 'burn_efficiency', 'revenue_per_burn',
            'team_quality', 'market_capture', 'growth_potential',
            'moat_strength', 'pmf_score', 'burn_risk', 'concentration_risk',
            'team_risk', 'stage_numeric', 'stage_revenue_fit', 'team_market_fit'
        ]
        
        all_features = ALL_FEATURES + engineered_features
        
        # Get categorical indices
        cat_indices = [i for i, f in enumerate(all_features) if f in CATEGORICAL_FEATURES]
        
        # Split data
        X = df[all_features]
        y = df['success'].astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        print(f"\nDataset splits:")
        print(f"  Train: {len(X_train)} samples")
        print(f"  Val: {len(X_val)} samples")
        print(f"  Test: {len(X_test)} samples")
        
        # Train ensemble models
        ensemble_preds_train, ensemble_preds_val = self.train_ensemble_models(
            X_train, y_train, X_val, y_val, all_features, cat_indices
        )
        
        # Get test predictions from ensemble
        ensemble_preds_test = {}
        for name, model in self.ensemble_models.items():
            ensemble_preds_test[name] = model.predict_proba(X_test[all_features])[:, 1]
        
        # Train stacking meta-learner
        final_train_pred, final_val_pred, X_meta_train, X_meta_val = self.train_stacking_meta_learner(
            ensemble_preds_train, y_train, ensemble_preds_val, y_val
        )
        
        # Get final test predictions
        X_meta_test = pd.DataFrame(ensemble_preds_test)
        X_meta_test['mean'] = X_meta_test.mean(axis=1)
        X_meta_test['std'] = X_meta_test.std(axis=1)
        X_meta_test['min'] = X_meta_test.min(axis=1)
        X_meta_test['max'] = X_meta_test.max(axis=1)
        
        # Blend meta-learner predictions for test
        test_predictions = []
        for name in ['meta_logistic', 'meta_nn', 'meta_catboost_meta']:
            if name in self.models:
                test_predictions.append(
                    self.models[name].predict_proba(X_meta_test)[:, 1]
                )
        
        final_test_pred = np.mean(test_predictions, axis=0)
        
        # Evaluate final performance
        print("\n" + "="*40)
        print("FINAL TEST SET PERFORMANCE")
        print("="*40)
        
        test_auc = roc_auc_score(y_test, final_test_pred)
        test_pred_binary = (final_test_pred > 0.5).astype(int)
        test_accuracy = accuracy_score(y_test, test_pred_binary)
        test_f1 = f1_score(y_test, test_pred_binary)
        
        print(f"AUC: {test_auc:.4f}")
        print(f"Accuracy: {test_accuracy:.4f}")
        print(f"F1-Score: {test_f1:.4f}")
        
        # Compare with individual models
        print("\nIndividual Model Performance:")
        for name, pred in ensemble_preds_test.items():
            auc = roc_auc_score(y_test, pred)
            print(f"  {name}: {auc:.4f}")
        
        # Store metrics
        self.performance_metrics = {
            'test_auc': test_auc,
            'test_accuracy': test_accuracy,
            'test_f1': test_f1,
            'val_auc': roc_auc_score(y_val, final_val_pred),
            'ensemble_models': len(self.ensemble_models),
            'features_used': len(all_features),
            'engineered_features': len(engineered_features)
        }
        
        return self
    
    def save_models(self, output_dir="models/v2_enhanced"):
        """Save all models and metadata."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nSaving models to {output_dir}")
        
        # Save ensemble models
        for name, model in self.ensemble_models.items():
            model.save_model(f"{output_dir}/{name}_model.cbm")
        
        # Save meta-learners
        for name, model in self.models.items():
            if 'catboost' in name:
                model.save_model(f"{output_dir}/{name}.cbm")
            else:
                joblib.dump(model, f"{output_dir}/{name}.pkl")
        
        # Save metadata
        metadata = {
            'version': '2.0-Enhanced',
            'framework': 'CatBoost Ensemble + Stacking',
            'performance_metrics': self.performance_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(f"{output_dir}/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("✓ All models saved successfully!")


def main():
    """Run the enhanced training pipeline."""
    data_path = "/Users/sf/Desktop/FLASH/data/final_100k_dataset_45features.csv"
    
    pipeline = EnhancedFLASHPipeline()
    pipeline.train_full_pipeline(data_path)
    pipeline.save_models()
    
    print("\n" + "="*60)
    print("FLASH 2.0 Enhanced Training Complete!")
    print("="*60)

if __name__ == "__main__":
    main()