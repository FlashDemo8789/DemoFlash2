"""
Train Stage-Based Hierarchical Models for FLASH
This script trains stage-specific models using the existing dataset
Expected improvement: 5-10% accuracy increase
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import logging
import json
from datetime import datetime
from stage_hierarchical_models import StageHierarchicalModel

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_and_prepare_data():
    """Load the hybrid dataset and prepare for training"""
    logger.info("Loading dataset...")
    
    # Load the main dataset
    df = pd.read_csv("data/final_100k_dataset_45features.csv")
    logger.info(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Map existing funding stages to our standard stages
    stage_mapping = {
        'Pre-seed': 'pre_seed',
        'Seed': 'seed',
        'Series A': 'series_a',
        'Series B': 'series_b',
        'Series C+': 'series_c'
    }
    
    # Add funding stage if not present or map existing ones
    if 'funding_stage' in df.columns:
        df['funding_stage'] = df['funding_stage'].map(stage_mapping).fillna('series_c')
    else:
        # Infer funding stage from various features
        df['funding_stage'] = df.apply(lambda row: infer_funding_stage(row), axis=1)
    
    # Prepare features and target
    # Exclude non-numeric columns and target
    exclude_cols = ['success', 'company_id', 'funding_stage']
    if 'company_name' in df.columns:
        exclude_cols.append('company_name')
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    # Remove any remaining non-numeric columns
    numeric_cols = []
    for col in feature_cols:
        if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
            numeric_cols.append(col)
    
    feature_cols = numeric_cols
    X = df[feature_cols + ['funding_stage']]
    y = df['success']
    
    # Log stage distribution
    stage_dist = df['funding_stage'].value_counts()
    logger.info(f"Stage distribution:\n{stage_dist}")
    
    return X, y, feature_cols


def infer_funding_stage(row):
    """Infer funding stage based on company metrics"""
    total_funding = row.get('total_capital_raised_usd', 0)
    revenue = row.get('annual_revenue_run_rate', 0)
    team_size = row.get('team_size_full_time', 0)
    rounds = row.get('funding_rounds_count', 0)
    
    # Rule-based stage inference
    if total_funding < 500000 and team_size < 5:
        return 'pre_seed'
    elif total_funding < 2000000 and team_size < 15:
        return 'seed'
    elif total_funding < 10000000 and revenue < 5000000:
        return 'series_a'
    elif total_funding < 30000000 and revenue < 20000000:
        return 'series_b'
    elif total_funding < 100000000:
        return 'series_c'
    else:
        return 'growth'


def evaluate_models(model, X_test, y_test):
    """Evaluate the stage-based model performance"""
    logger.info("Evaluating stage-based models...")
    
    # Get predictions
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }
    
    # Evaluate by stage
    stage_metrics = {}
    for stage in X_test['funding_stage'].unique():
        stage_mask = X_test['funding_stage'] == stage
        if stage_mask.sum() > 10:  # Only evaluate if enough samples
            stage_metrics[stage] = {
                'accuracy': accuracy_score(y_test[stage_mask], y_pred[stage_mask]),
                'precision': precision_score(y_test[stage_mask], y_pred[stage_mask]),
                'recall': recall_score(y_test[stage_mask], y_pred[stage_mask]),
                'samples': stage_mask.sum()
            }
    
    return metrics, stage_metrics


def compare_with_baseline(X_test, y_test):
    """Load and compare with existing base models"""
    try:
        import joblib
        
        # Load existing meta model for comparison
        base_model_path = Path("models/v2_enhanced/meta_catboost_meta.cbm")
        if base_model_path.exists():
            import catboost as cb
            base_model = cb.CatBoostClassifier()
            base_model.load_model(str(base_model_path))
            
            # Prepare features for base model (without funding_stage)
            X_base = X_test.drop('funding_stage', axis=1)
            base_pred = base_model.predict_proba(X_base)[:, 1]
            base_accuracy = accuracy_score(y_test, (base_pred > 0.5).astype(int))
            base_auc = roc_auc_score(y_test, base_pred)
            
            logger.info(f"Baseline model - Accuracy: {base_accuracy:.3f}, AUC: {base_auc:.3f}")
            return base_accuracy, base_auc
    except Exception as e:
        logger.warning(f"Could not load baseline model: {e}")
        return None, None


def main():
    """Main training pipeline"""
    logger.info("Starting Stage-Based Hierarchical Model Training")
    
    # Load data
    X, y, feature_cols = load_and_prepare_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # Initialize and train stage models
    stage_model = StageHierarchicalModel()
    
    # Train stage-specific models
    logger.info("Training stage-specific models...")
    stage_model.train_stage_models(X_train, y_train)
    
    # Train meta model
    logger.info("Training meta model...")
    stage_model.train_meta_model(X_train, y_train)
    
    # Save models
    model_path = Path("models/stage_hierarchical")
    stage_model.save_models(model_path)
    
    # Evaluate performance
    metrics, stage_metrics = evaluate_models(stage_model, X_test, y_test)
    
    logger.info("Overall Performance:")
    for metric, value in metrics.items():
        logger.info(f"  {metric}: {value:.3f}")
    
    logger.info("\nPerformance by Stage:")
    for stage, stage_perf in stage_metrics.items():
        logger.info(f"  {stage}: Accuracy={stage_perf['accuracy']:.3f}, "
                   f"Precision={stage_perf['precision']:.3f}, "
                   f"Recall={stage_perf['recall']:.3f}, "
                   f"Samples={stage_perf['samples']}")
    
    # Compare with baseline
    base_accuracy, base_auc = compare_with_baseline(X_test, y_test)
    improvement = None
    if base_accuracy:
        improvement = ((metrics['accuracy'] - base_accuracy) / base_accuracy) * 100
        logger.info(f"\nImprovement over baseline: {improvement:.1f}%")
    
    # Convert numpy types to Python types for JSON serialization
    def convert_to_python_types(obj):
        if isinstance(obj, dict):
            return {k: convert_to_python_types(v) for k, v in obj.items()}
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'overall_metrics': convert_to_python_types(metrics),
        'stage_metrics': convert_to_python_types(stage_metrics),
        'baseline_comparison': {
            'baseline_accuracy': float(base_accuracy) if base_accuracy else None,
            'baseline_auc': float(base_auc) if base_auc else None,
            'improvement_percent': float(improvement) if improvement else None
        },
        'model_info': {
            'type': 'stage_hierarchical',
            'stages': list(stage_model.stage_models.keys()),
            'total_models': sum(len(models) for models in stage_model.stage_models.values()) + 1
        }
    }
    
    with open(model_path / 'training_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\nTraining complete! Models saved to {model_path}")
    logger.info("Next step: Update api_server.py to use stage-based models")
    
    # Generate feature importance report
    logger.info("\nTop Features by Stage:")
    for stage, importance_df in stage_model.feature_importance.items():
        logger.info(f"\n{stage.upper()} Stage:")
        if not importance_df.empty:
            for _, row in importance_df.head(5).iterrows():
                logger.info(f"  - {row['feature']}: {row['importance_mean']:.3f}")


if __name__ == "__main__":
    main()