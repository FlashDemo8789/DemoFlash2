#!/usr/bin/env python3
"""
SHAP Explainability Module for FLASH 2.0
Provides interpretable AI insights for startup predictions
"""

import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from typing import Dict, List, Tuple, Optional
import pickle
from pathlib import Path
import seaborn as sns

# Configure matplotlib for better quality
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (10, 6)

class FLASHExplainer:
    """SHAP-based explainability for FLASH predictions"""
    
    def __init__(self, models_dir: str = "models/v2"):
        self.models_dir = Path(models_dir)
        self.models = self._load_models()
        self.explainers = self._create_explainers()
        self.feature_names = self._get_feature_names()
        
    def _load_models(self) -> Dict:
        """Load all trained models"""
        models = {}
        
        # Load pillar models
        for pillar in ['capital', 'advantage', 'market', 'people']:
            model_path = self.models_dir / f"{pillar}_model.pkl"
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    models[pillar] = pickle.load(f)
                    
        # Load meta model
        meta_path = self.models_dir / "meta_model.pkl"
        if meta_path.exists():
            with open(meta_path, 'rb') as f:
                models['meta'] = pickle.load(f)
                
        return models
    
    def _create_explainers(self) -> Dict:
        """Create SHAP explainers for each model"""
        explainers = {}
        
        for name, model in self.models.items():
            # Use TreeExplainer for tree-based models
            explainers[name] = shap.TreeExplainer(model)
            
        return explainers
    
    def _get_feature_names(self) -> Dict[str, List[str]]:
        """Get feature names for each pillar"""
        return {
            'capital': [
                'funding_total_usd', 'funding_rounds', 'last_funding_amount_usd',
                'burn_rate', 'runway_months', 'revenue_growth_rate',
                'gross_margin', 'revenue_per_employee', 'customer_acquisition_cost',
                'lifetime_value', 'ltv_cac_ratio'
            ],
            'advantage': [
                'has_patent', 'tech_stack_complexity', 'product_market_fit_score',
                'competitive_advantage_score', 'time_to_market_days',
                'nps_score', 'is_b2b', 'is_saas'
            ],
            'market': [
                'market_size_billions', 'market_growth_rate', 'market_maturity_score',
                'competitor_count', 'market_share', 'market_concentration',
                'is_emerging_market', 'regulatory_complexity_score'
            ],
            'people': [
                'team_size', 'founder_experience_years', 'founder_previous_exits',
                'technical_team_ratio', 'advisor_count', 'board_size',
                'employee_growth_rate', 'leadership_stability_score',
                'diversity_score', 'has_technical_cofounder', 'founder_domain_expertise'
            ]
        }
    
    def explain_prediction(self, features: Dict[str, float], 
                         include_plots: bool = True) -> Dict:
        """Generate comprehensive explanation for a prediction"""
        
        # Prepare data for each pillar
        pillar_explanations = {}
        pillar_predictions = {}
        
        for pillar, feature_list in self.feature_names.items():
            if pillar in self.models:
                # Extract relevant features
                X = np.array([[features.get(f, 0) for f in feature_list]])
                
                # Get prediction
                pred = self.models[pillar].predict_proba(X)[0, 1]
                pillar_predictions[pillar] = pred
                
                # Get SHAP values
                shap_values = self.explainers[pillar].shap_values(X)
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]  # For binary classification
                
                # Create explanation
                pillar_explanations[pillar] = {
                    'prediction': float(pred),
                    'shap_values': shap_values[0].tolist(),
                    'feature_names': feature_list,
                    'feature_values': [features.get(f, 0) for f in feature_list]
                }
        
        # Get meta model explanation if we have pillar predictions
        meta_explanation = None
        if 'meta' in self.models and len(pillar_predictions) == 4:
            meta_features = np.array([[
                pillar_predictions['capital'],
                pillar_predictions['advantage'],
                pillar_predictions['market'],
                pillar_predictions['people']
            ]])
            
            meta_pred = self.models['meta'].predict_proba(meta_features)[0, 1]
            meta_shap = self.explainers['meta'].shap_values(meta_features)
            if isinstance(meta_shap, list):
                meta_shap = meta_shap[1]
            
            meta_explanation = {
                'prediction': float(meta_pred),
                'shap_values': meta_shap[0].tolist(),
                'feature_names': ['Capital Score', 'Advantage Score', 
                                'Market Score', 'People Score'],
                'feature_values': list(pillar_predictions.values())
            }
        
        # Generate plots if requested
        plots = {}
        if include_plots:
            plots = self._generate_plots(pillar_explanations, meta_explanation)
        
        # Generate insights
        insights = self._generate_insights(pillar_explanations, meta_explanation)
        
        return {
            'pillar_explanations': pillar_explanations,
            'meta_explanation': meta_explanation,
            'plots': plots,
            'insights': insights
        }
    
    def _generate_plots(self, pillar_explanations: Dict, 
                       meta_explanation: Optional[Dict]) -> Dict[str, str]:
        """Generate visualization plots"""
        plots = {}
        
        # 1. Meta model waterfall plot
        if meta_explanation:
            fig, ax = plt.subplots(figsize=(8, 4))
            
            # Create waterfall data
            values = meta_explanation['shap_values']
            features = meta_explanation['feature_names']
            feature_values = meta_explanation['feature_values']
            
            # Sort by absolute impact
            sorted_idx = np.argsort(np.abs(values))[::-1]
            
            # Create bar chart
            y_pos = np.arange(len(values))
            colors = ['#e74c3c' if v < 0 else '#2ecc71' for v in values]
            
            bars = ax.barh(y_pos, [values[i] for i in sorted_idx], 
                          color=[colors[i] for i in sorted_idx])
            
            # Customize
            ax.set_yticks(y_pos)
            ax.set_yticklabels([f"{features[i]}\n({feature_values[i]:.2f})" 
                              for i in sorted_idx])
            ax.set_xlabel('Impact on Success Probability')
            ax.set_title('CAMP Pillar Contributions')
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
            
            # Add value labels
            for i, (bar, idx) in enumerate(zip(bars, sorted_idx)):
                width = bar.get_width()
                ax.text(width + 0.01 if width > 0 else width - 0.01, 
                       bar.get_y() + bar.get_height()/2,
                       f'{values[idx]:.3f}', 
                       ha='left' if width > 0 else 'right', 
                       va='center', fontsize=9)
            
            plt.tight_layout()
            plots['meta_waterfall'] = self._fig_to_base64(fig)
            plt.close(fig)
        
        # 2. Top features across all pillars
        all_features = []
        all_values = []
        all_impacts = []
        
        for pillar, exp in pillar_explanations.items():
            for i, (feat, val, impact) in enumerate(zip(
                exp['feature_names'], 
                exp['feature_values'], 
                exp['shap_values']
            )):
                all_features.append(f"{feat}")
                all_values.append(val)
                all_impacts.append(impact)
        
        # Get top 15 by absolute impact
        top_idx = np.argsort(np.abs(all_impacts))[-15:][::-1]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        y_pos = np.arange(len(top_idx))
        impacts = [all_impacts[i] for i in top_idx]
        colors = ['#e74c3c' if v < 0 else '#2ecc71' for v in impacts]
        
        bars = ax.barh(y_pos, impacts, color=colors)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{all_features[i]}\n(={all_values[i]:.2f})" 
                           for i in top_idx], fontsize=9)
        ax.set_xlabel('Impact on Success Probability')
        ax.set_title('Top 15 Feature Contributions')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        # Add value labels
        for bar, impact in zip(bars, impacts):
            width = bar.get_width()
            ax.text(width + 0.001 if width > 0 else width - 0.001, 
                   bar.get_y() + bar.get_height()/2,
                   f'{impact:.3f}', 
                   ha='left' if width > 0 else 'right', 
                   va='center', fontsize=8)
        
        plt.tight_layout()
        plots['top_features'] = self._fig_to_base64(fig)
        plt.close(fig)
        
        # 3. Pillar breakdown radar chart
        pillar_predictions = {p: e['prediction'] for p, e in pillar_explanations.items()}
        if len(pillar_predictions) == 4:
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            categories = list(pillar_predictions.keys())
            values = list(pillar_predictions.values())
            
            # Number of variables
            num_vars = len(categories)
            
            # Compute angle for each axis
            angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
            values += values[:1]  # Complete the circle
            angles += angles[:1]
            
            # Plot
            ax.plot(angles, values, 'o-', linewidth=2, color='#3498db')
            ax.fill(angles, values, alpha=0.25, color='#3498db')
            
            # Labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels([c.upper() for c in categories])
            ax.set_ylim(0, 1)
            ax.set_yticks([0.2, 0.4, 0.6, 0.8])
            ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8'])
            ax.set_title('CAMP Pillar Scores', y=1.08)
            
            # Add value labels
            for angle, value, cat in zip(angles[:-1], values[:-1], categories):
                ax.text(angle, value + 0.05, f'{value:.2f}', 
                       ha='center', va='center', fontsize=10, 
                       bbox=dict(boxstyle='round,pad=0.3', 
                                facecolor='white', edgecolor='gray'))
            
            plt.tight_layout()
            plots['pillar_radar'] = self._fig_to_base64(fig)
            plt.close(fig)
        
        return plots
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        return f"data:image/png;base64,{image_base64}"
    
    def _generate_insights(self, pillar_explanations: Dict, 
                          meta_explanation: Optional[Dict]) -> Dict:
        """Generate human-readable insights"""
        insights = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'key_drivers': []
        }
        
        # Analyze each pillar
        for pillar, exp in pillar_explanations.items():
            pillar_score = exp['prediction']
            
            # Find top positive and negative factors
            shap_values = np.array(exp['shap_values'])
            feature_names = exp['feature_names']
            feature_values = exp['feature_values']
            
            # Top positive impacts
            pos_idx = np.where(shap_values > 0.02)[0]
            if len(pos_idx) > 0:
                top_pos = pos_idx[np.argsort(shap_values[pos_idx])[-1]]
                insights['strengths'].append(
                    f"{pillar.capitalize()}: Strong {feature_names[top_pos]} "
                    f"({feature_values[top_pos]:.2f}) contributing +{shap_values[top_pos]:.3f}"
                )
            
            # Top negative impacts
            neg_idx = np.where(shap_values < -0.02)[0]
            if len(neg_idx) > 0:
                top_neg = neg_idx[np.argsort(shap_values[neg_idx])[0]]
                insights['weaknesses'].append(
                    f"{pillar.capitalize()}: Weak {feature_names[top_neg]} "
                    f"({feature_values[top_neg]:.2f}) contributing {shap_values[top_neg]:.3f}"
                )
        
        # Overall assessment
        if meta_explanation:
            final_score = meta_explanation['prediction']
            
            if final_score > 0.7:
                insights['opportunities'].append(
                    "High success probability - consider aggressive growth strategies"
                )
            elif final_score > 0.5:
                insights['opportunities'].append(
                    "Moderate success probability - focus on strengthening weak pillars"
                )
            else:
                insights['opportunities'].append(
                    "Low success probability - consider pivoting or addressing fundamental issues"
                )
        
        # Key drivers (top 3 absolute impacts across all features)
        all_impacts = []
        for pillar, exp in pillar_explanations.items():
            for feat, val, impact in zip(exp['feature_names'], 
                                        exp['feature_values'], 
                                        exp['shap_values']):
                all_impacts.append((feat, val, impact, abs(impact)))
        
        all_impacts.sort(key=lambda x: x[3], reverse=True)
        
        for feat, val, impact, _ in all_impacts[:3]:
            direction = "increasing" if impact > 0 else "decreasing"
            insights['key_drivers'].append(
                f"{feat} (current: {val:.2f}) is {direction} success probability by {abs(impact):.3f}"
            )
        
        return insights
    
    def generate_report_data(self, features: Dict[str, float]) -> Dict:
        """Generate complete report data for PDF generation"""
        explanation = self.explain_prediction(features, include_plots=True)
        
        # Add summary statistics
        summary = {
            'final_prediction': None,
            'pillar_scores': {},
            'top_strengths': [],
            'top_weaknesses': [],
            'improvement_areas': []
        }
        
        # Extract final prediction
        if explanation['meta_explanation']:
            summary['final_prediction'] = explanation['meta_explanation']['prediction']
        
        # Extract pillar scores
        for pillar, exp in explanation['pillar_explanations'].items():
            summary['pillar_scores'][pillar] = exp['prediction']
        
        # Identify improvement areas
        for pillar, score in summary['pillar_scores'].items():
            if score < 0.5:
                summary['improvement_areas'].append({
                    'pillar': pillar,
                    'current_score': score,
                    'target_score': 0.7,
                    'priority': 'high' if score < 0.3 else 'medium'
                })
        
        return {
            'summary': summary,
            'detailed_explanation': explanation,
            'timestamp': pd.Timestamp.now().isoformat()
        }


if __name__ == "__main__":
    # Test the explainer
    explainer = FLASHExplainer()
    
    # Sample features
    test_features = {
        'funding_total_usd': 5000000,
        'funding_rounds': 2,
        'last_funding_amount_usd': 3000000,
        'burn_rate': 150000,
        'runway_months': 20,
        'revenue_growth_rate': 0.15,
        'gross_margin': 0.65,
        'revenue_per_employee': 120000,
        'customer_acquisition_cost': 500,
        'lifetime_value': 2500,
        'ltv_cac_ratio': 5.0,
        'has_patent': 1,
        'tech_stack_complexity': 7,
        'product_market_fit_score': 0.7,
        'competitive_advantage_score': 0.6,
        'time_to_market_days': 180,
        'nps_score': 45,
        'is_b2b': 1,
        'is_saas': 1,
        'market_size_billions': 50,
        'market_growth_rate': 0.25,
        'market_maturity_score': 0.6,
        'competitor_count': 15,
        'market_share': 0.02,
        'market_concentration': 0.3,
        'is_emerging_market': 0,
        'regulatory_complexity_score': 0.4,
        'team_size': 25,
        'founder_experience_years': 12,
        'founder_previous_exits': 1,
        'technical_team_ratio': 0.6,
        'advisor_count': 4,
        'board_size': 5,
        'employee_growth_rate': 0.5,
        'leadership_stability_score': 0.8,
        'diversity_score': 0.7,
        'has_technical_cofounder': 1,
        'founder_domain_expertise': 1
    }
    
    result = explainer.explain_prediction(test_features)
    print("Explanation generated successfully!")
    print(f"Final prediction: {result['meta_explanation']['prediction']:.2%}")
    print("\nKey insights:")
    for key, items in result['insights'].items():
        if items:
            print(f"\n{key.upper()}:")
            for item in items:
                print(f"  - {item}")