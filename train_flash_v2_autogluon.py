#!/usr/bin/env python3
"""
FLASH 2.0 AutoGluon - State-of-the-art AutoML ensemble
Combines multiple algorithms for superior performance
"""
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns

# AutoGluon imports
from autogluon.tabular import TabularDataset, TabularPredictor

# Feature definitions (same as before)
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


class FLASHAutoGluonPipeline:
    """AutoGluon-powered ML pipeline for startup success prediction."""
    
    def __init__(self, output_dir="models/v2_autogluon"):
        self.output_dir = output_dir
        self.predictors = {}
        self.performance_metrics = {}
        os.makedirs(output_dir, exist_ok=True)
        
    def prepare_data(self, df):
        """Prepare data with feature engineering."""
        print("Preparing data with advanced feature engineering...")
        
        # Handle boolean columns
        bool_columns = ['has_debt', 'network_effects_present', 'has_data_moat', 
                       'regulatory_advantage_present', 'key_person_dependency']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].astype(int)
        
        # Create interaction features
        df['capital_efficiency'] = df['annual_revenue_run_rate'] / (df['total_capital_raised_usd'] + 1)
        df['team_experience_score'] = (df['years_experience_avg'] + df['domain_expertise_years_avg']) / 2
        df['market_opportunity_score'] = np.log1p(df['tam_size_usd']) * df['market_growth_rate_percent'] / 100
        
        # Create ratio features
        df['revenue_per_employee'] = df['annual_revenue_run_rate'] / (df['team_size_full_time'] + 1)
        df['burn_revenue_ratio'] = df['monthly_burn_usd'] / (df['annual_revenue_run_rate'] / 12 + 1)
        df['market_penetration'] = df['som_size_usd'] / (df['tam_size_usd'] + 1)
        
        # Create growth momentum features
        df['growth_efficiency'] = df['user_growth_rate_percent'] / (df['burn_multiple'] + 1)
        df['retention_score'] = (df['product_retention_30d'] + df['product_retention_90d']) / 2
        
        # Stage-based features
        stage_order = {'Pre-seed': 0, 'Seed': 1, 'Series A': 2, 'Series B': 3, 'Series C+': 4}
        df['stage_numeric'] = df['funding_stage'].map(stage_order)
        
        # Competitive advantage score
        df['moat_score'] = (
            df['patent_count'].clip(0, 10) / 10 * 0.2 +
            df['network_effects_present'] * 0.3 +
            df['has_data_moat'] * 0.2 +
            df['tech_differentiation_score'] / 5 * 0.3
        )
        
        # Financial health score
        df['financial_health'] = (
            df['runway_months'].clip(0, 24) / 24 * 0.3 +
            df['gross_margin_percent'] / 100 * 0.3 +
            (1 / (df['burn_multiple'] + 1)) * 0.2 +
            df['ltv_cac_ratio'].clip(0, 5) / 5 * 0.2
        )
        
        return df
    
    def train_pillar_predictor(self, train_data, val_data, pillar_name, features):
        """Train AutoGluon predictor for a specific pillar."""
        print(f"\nTraining {pillar_name} AutoGluon ensemble...")
        
        # Prepare datasets
        train_df = train_data[features + ['success']].copy()
        val_df = val_data[features + ['success']].copy()
        
        # Configure AutoGluon
        predictor = TabularPredictor(
            label='success',
            path=f"{self.output_dir}/{pillar_name}_predictor",
            problem_type='binary',
            eval_metric='roc_auc',
            verbosity=2
        )
        
        # Train with different presets for ensemble diversity
        predictor.fit(
            train_data=train_df,
            tuning_data=val_df,
            time_limit=300,  # 5 minutes per pillar
            presets=['best_quality'],
            # Include various algorithms
            hyperparameters={
                'GBM': {},
                'CAT': {},
                'XGB': {},
                'RF': {},
                'NN_TORCH': {},  # Neural network
                'FASTAI': {},    # Deep learning
            },
            num_bag_folds=5,  # Bagging for better generalization
            num_stack_levels=2,  # Stacking levels
        )
        
        # Get predictions
        train_pred = predictor.predict_proba(train_data[features])
        val_pred = predictor.predict_proba(val_data[features])
        
        # Calculate metrics
        train_auc = roc_auc_score(train_data['success'], train_pred.iloc[:, 1])
        val_auc = roc_auc_score(val_data['success'], val_pred.iloc[:, 1])
        
        print(f"{pillar_name} - Train AUC: {train_auc:.4f}, Val AUC: {val_auc:.4f}")
        
        # Get model leaderboard
        leaderboard = predictor.leaderboard(val_data[features + ['success']], silent=True)
        print(f"\n{pillar_name} Model Leaderboard:")
        print(leaderboard[['model', 'score_val', 'pred_time_val', 'fit_time']].head(10))
        
        return predictor, train_pred.iloc[:, 1].values, val_pred.iloc[:, 1].values
    
    def train_meta_ensemble(self, pillar_predictions_train, y_train, pillar_predictions_val, y_val):
        """Train meta-ensemble combining all pillars."""
        print("\nTraining meta-ensemble...")
        
        # Create meta features
        meta_train = pd.DataFrame(pillar_predictions_train)
        meta_train['success'] = y_train.values
        
        meta_val = pd.DataFrame(pillar_predictions_val)
        meta_val['success'] = y_val.values
        
        # Add polynomial features
        for col1 in ['capital', 'advantage', 'market', 'people']:
            for col2 in ['capital', 'advantage', 'market', 'people']:
                if col1 < col2:  # Avoid duplicates
                    meta_train[f'{col1}_x_{col2}'] = meta_train[col1] * meta_train[col2]
                    meta_val[f'{col1}_x_{col2}'] = meta_val[col1] * meta_val[col2]
        
        # Add min/max/std features
        pillar_cols = ['capital', 'advantage', 'market', 'people']
        meta_train['pillar_min'] = meta_train[pillar_cols].min(axis=1)
        meta_train['pillar_max'] = meta_train[pillar_cols].max(axis=1)
        meta_train['pillar_std'] = meta_train[pillar_cols].std(axis=1)
        meta_train['pillar_mean'] = meta_train[pillar_cols].mean(axis=1)
        
        meta_val['pillar_min'] = meta_val[pillar_cols].min(axis=1)
        meta_val['pillar_max'] = meta_val[pillar_cols].max(axis=1)
        meta_val['pillar_std'] = meta_val[pillar_cols].std(axis=1)
        meta_val['pillar_mean'] = meta_val[pillar_cols].mean(axis=1)
        
        # Train meta predictor
        meta_predictor = TabularPredictor(
            label='success',
            path=f"{self.output_dir}/meta_predictor",
            problem_type='binary',
            eval_metric='roc_auc',
            verbosity=2
        )
        
        # Use best_quality preset for meta model
        meta_predictor.fit(
            train_data=meta_train,
            tuning_data=meta_val,
            time_limit=600,  # 10 minutes for meta model
            presets=['best_quality'],
            hyperparameters={
                'GBM': {'num_boost_round': 200},
                'CAT': {'iterations': 1000},
                'XGB': {'n_estimators': 200},
                'NN_TORCH': {'num_epochs': 50},
                'FASTAI': {'epochs': 50},
            },
            num_bag_folds=10,
            num_stack_levels=2,
        )
        
        # Get final predictions
        final_train_pred = meta_predictor.predict_proba(meta_train.drop('success', axis=1))
        final_val_pred = meta_predictor.predict_proba(meta_val.drop('success', axis=1))
        
        # Calculate metrics
        train_auc = roc_auc_score(y_train, final_train_pred.iloc[:, 1])
        val_auc = roc_auc_score(y_val, final_val_pred.iloc[:, 1])
        
        print(f"\nMeta-ensemble - Train AUC: {train_auc:.4f}, Val AUC: {val_auc:.4f}")
        
        # Show meta model leaderboard
        leaderboard = meta_predictor.leaderboard(meta_val, silent=True)
        print("\nMeta Model Leaderboard:")
        print(leaderboard[['model', 'score_val', 'pred_time_val', 'fit_time']].head(10))
        
        return meta_predictor, final_train_pred.iloc[:, 1].values, final_val_pred.iloc[:, 1].values
    
    def train_full_pipeline(self, data_path):
        """Train the complete AutoGluon pipeline."""
        print("="*60)
        print("FLASH 2.0 AutoGluon Pipeline")
        print("="*60)
        
        # Load and prepare data
        print(f"\nLoading data from {data_path}")
        df = pd.read_csv(data_path)
        df = self.prepare_data(df)
        
        # Get all features including engineered ones
        engineered_features = [
            'capital_efficiency', 'team_experience_score', 'market_opportunity_score',
            'revenue_per_employee', 'burn_revenue_ratio', 'market_penetration',
            'growth_efficiency', 'retention_score', 'stage_numeric',
            'moat_score', 'financial_health'
        ]
        
        all_features_extended = ALL_FEATURES + engineered_features
        
        # Split data
        X = df[all_features_extended + ['success']]
        train_data, test_data = train_test_split(X, test_size=0.2, random_state=42, stratify=X['success'])
        train_data, val_data = train_test_split(train_data, test_size=0.2, random_state=42, stratify=train_data['success'])
        
        print(f"\nDataset splits:")
        print(f"  Train: {len(train_data)} samples")
        print(f"  Val: {len(val_data)} samples")
        print(f"  Test: {len(test_data)} samples")
        
        # Train pillar predictors
        pillar_configs = {
            'capital': CAPITAL_FEATURES + ['capital_efficiency', 'revenue_per_employee', 'financial_health'],
            'advantage': ADVANTAGE_FEATURES + ['moat_score', 'retention_score'],
            'market': MARKET_FEATURES + ['market_opportunity_score', 'market_penetration', 'growth_efficiency'],
            'people': PEOPLE_FEATURES + ['team_experience_score', 'stage_numeric']
        }
        
        pillar_predictions_train = {}
        pillar_predictions_val = {}
        pillar_predictions_test = {}
        
        for pillar, features in pillar_configs.items():
            predictor, train_pred, val_pred = self.train_pillar_predictor(
                train_data, val_data, pillar, features
            )
            
            self.predictors[pillar] = predictor
            pillar_predictions_train[pillar] = train_pred
            pillar_predictions_val[pillar] = val_pred
            pillar_predictions_test[pillar] = predictor.predict_proba(test_data[features]).iloc[:, 1].values
        
        # Train meta ensemble
        meta_predictor, final_train_pred, final_val_pred = self.train_meta_ensemble(
            pillar_predictions_train, train_data['success'],
            pillar_predictions_val, val_data['success']
        )
        
        self.predictors['meta'] = meta_predictor
        
        # Evaluate on test set
        meta_test = pd.DataFrame(pillar_predictions_test)
        
        # Add polynomial features for test
        for col1 in ['capital', 'advantage', 'market', 'people']:
            for col2 in ['capital', 'advantage', 'market', 'people']:
                if col1 < col2:
                    meta_test[f'{col1}_x_{col2}'] = meta_test[col1] * meta_test[col2]
        
        # Add aggregation features
        pillar_cols = ['capital', 'advantage', 'market', 'people']
        meta_test['pillar_min'] = meta_test[pillar_cols].min(axis=1)
        meta_test['pillar_max'] = meta_test[pillar_cols].max(axis=1)
        meta_test['pillar_std'] = meta_test[pillar_cols].std(axis=1)
        meta_test['pillar_mean'] = meta_test[pillar_cols].mean(axis=1)
        
        final_test_pred = meta_predictor.predict_proba(meta_test)
        
        # Calculate final metrics
        print("\n" + "="*40)
        print("FINAL TEST SET PERFORMANCE")
        print("="*40)
        
        test_auc = roc_auc_score(test_data['success'], final_test_pred.iloc[:, 1])
        test_pred_binary = (final_test_pred.iloc[:, 1] > 0.5).astype(int)
        test_accuracy = accuracy_score(test_data['success'], test_pred_binary)
        test_f1 = f1_score(test_data['success'], test_pred_binary)
        
        print(f"AUC: {test_auc:.4f}")
        print(f"Accuracy: {test_accuracy:.4f}")
        print(f"F1-Score: {test_f1:.4f}")
        
        # Feature importance
        print("\nFeature Importance Summary:")
        for pillar in ['capital', 'advantage', 'market', 'people']:
            importance = self.predictors[pillar].feature_importance()
            print(f"\n{pillar.capitalize()} - Top 5 Features:")
            print(importance.head())
        
        # Save results
        self.performance_metrics = {
            'test_auc': test_auc,
            'test_accuracy': test_accuracy,
            'test_f1': test_f1,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save metadata
        metadata = {
            'version': '2.0-AutoGluon',
            'performance_metrics': self.performance_metrics,
            'feature_sets': pillar_configs,
            'engineered_features': engineered_features
        }
        
        with open(f"{self.output_dir}/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\nModels saved to: {self.output_dir}")
        
        return self

def main():
    """Run the AutoGluon training pipeline."""
    data_path = "/Users/sf/Desktop/FLASH/data/final_100k_dataset_45features.csv"
    
    print("Starting FLASH 2.0 AutoGluon Pipeline...")
    print("This will take approximately 30-40 minutes for full training.")
    
    pipeline = FLASHAutoGluonPipeline()
    pipeline.train_full_pipeline(data_path)
    
    print("\n" + "="*60)
    print("FLASH 2.0 AutoGluon Training Complete!")
    print("="*60)

if __name__ == "__main__":
    main()