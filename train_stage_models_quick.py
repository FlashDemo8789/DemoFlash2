"""
Quick training script for Stage-Based Hierarchical Models
Simplified version for faster training
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import catboost as cb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleStageModel:
    """Simplified stage-based model for quick training"""
    
    def __init__(self):
        self.stage_models = {}
        self.stage_weights = {
            'pre_seed': {'people': 0.4, 'advantage': 0.3, 'market': 0.2, 'capital': 0.1},
            'seed': {'people': 0.3, 'advantage': 0.3, 'market': 0.25, 'capital': 0.15},
            'series_a': {'market': 0.3, 'advantage': 0.25, 'capital': 0.25, 'people': 0.2},
            'series_b': {'market': 0.35, 'capital': 0.3, 'advantage': 0.2, 'people': 0.15},
            'series_c': {'capital': 0.4, 'market': 0.3, 'advantage': 0.2, 'people': 0.1}
        }
    
    def train(self, X_train, y_train):
        """Train stage-specific models"""
        stages = ['pre_seed', 'seed', 'series_a', 'series_b', 'series_c']
        
        for stage in stages:
            stage_mask = X_train['funding_stage'] == stage
            if stage_mask.sum() < 100:
                logger.warning(f"Skipping {stage} - insufficient data")
                continue
                
            X_stage = X_train[stage_mask].drop('funding_stage', axis=1)
            y_stage = y_train[stage_mask]
            
            # Train a simple CatBoost model
            model = cb.CatBoostClassifier(
                iterations=100,  # Reduced for speed
                learning_rate=0.1,
                depth=4,
                verbose=False,
                thread_count=-1
            )
            
            model.fit(X_stage, y_stage)
            self.stage_models[stage] = model
            logger.info(f"Trained model for {stage} stage ({stage_mask.sum()} samples)")
    
    def predict_proba(self, X):
        """Make predictions using stage-specific models"""
        predictions = []
        
        for idx, row in X.iterrows():
            stage = row['funding_stage']
            if stage in self.stage_models:
                X_row = row.drop('funding_stage').to_frame().T
                pred = self.stage_models[stage].predict_proba(X_row)[0, 1]
            else:
                pred = 0.5  # Default prediction
            predictions.append(pred)
        
        return np.array(predictions)
    
    def save(self, path):
        """Save the models"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        for stage, model in self.stage_models.items():
            model.save_model(str(path / f"stage_{stage}.cbm"))
        
        joblib.dump(self.stage_weights, path / "stage_weights.pkl")
        logger.info(f"Models saved to {path}")


def main():
    """Main training pipeline"""
    logger.info("Starting Quick Stage-Based Model Training")
    
    # Load data
    df = pd.read_csv("data/final_100k_dataset_45features.csv")
    
    # Map funding stages
    stage_mapping = {
        'Pre-seed': 'pre_seed',
        'Seed': 'seed',
        'Series A': 'series_a',
        'Series B': 'series_b',
        'Series C+': 'series_c'
    }
    df['funding_stage'] = df['funding_stage'].map(stage_mapping)
    
    # Prepare features
    exclude_cols = ['success', 'startup_id', 'startup_name', 'funding_stage']
    feature_cols = [col for col in df.columns if col not in exclude_cols and df[col].dtype in ['int64', 'float64']]
    
    X = df[feature_cols + ['funding_stage']]
    y = df['success']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train model
    model = SimpleStageModel()
    model.train(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict_proba(X_test)
    accuracy = accuracy_score(y_test, (y_pred > 0.5).astype(int))
    auc = roc_auc_score(y_test, y_pred)
    
    logger.info(f"Overall Performance - Accuracy: {accuracy:.3f}, AUC: {auc:.3f}")
    
    # Evaluate by stage
    for stage in X_test['funding_stage'].unique():
        if stage in model.stage_models:
            stage_mask = X_test['funding_stage'] == stage
            stage_acc = accuracy_score(y_test[stage_mask], (y_pred[stage_mask] > 0.5).astype(int))
            logger.info(f"{stage}: Accuracy={stage_acc:.3f}, Samples={stage_mask.sum()}")
    
    # Save model
    model_path = Path("models/stage_hierarchical_simple")
    model.save(model_path)
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'accuracy': float(accuracy),
        'auc': float(auc),
        'stages_trained': list(model.stage_models.keys())
    }
    
    with open(model_path / 'training_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Training complete! Models saved to {model_path}")
    
    # Compare with baseline
    try:
        base_model = cb.CatBoostClassifier()
        base_model.load_model("models/v2_enhanced/meta_catboost_meta.cbm")
        base_pred = base_model.predict_proba(X_test.drop('funding_stage', axis=1))[:, 1]
        base_acc = accuracy_score(y_test, (base_pred > 0.5).astype(int))
        
        improvement = ((accuracy - base_acc) / base_acc) * 100
        logger.info(f"\nBaseline accuracy: {base_acc:.3f}")
        logger.info(f"Improvement: {improvement:.1f}%")
    except Exception as e:
        logger.warning(f"Could not compare with baseline: {e}")


if __name__ == "__main__":
    main()