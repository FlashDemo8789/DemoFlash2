"""
DNA Pattern Analysis for FLASH
Revolutionary pattern recognition system for startup growth trajectories
Identifies and predicts success based on growth DNA patterns
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import logging
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class StartupDNAAnalyzer:
    """
    Analyzes startup growth patterns and creates DNA signatures
    that capture the essence of successful growth trajectories
    """
    
    def __init__(self):
        self.pattern_library = {}
        self.pattern_clusters = None
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        self.success_patterns = []
        self.failure_patterns = []
        
        # Key DNA components
        self.dna_components = {
            'growth_velocity': ['revenue_growth_rate_percent', 'user_growth_rate_percent', 'team_growth_rate'],
            'efficiency_genes': ['burn_multiple', 'ltv_cac_ratio', 'gross_margin_percent'],
            'market_dominance': ['market_share', 'customer_concentration_percent', 'net_dollar_retention_percent'],
            'founder_dna': ['years_experience_avg', 'prior_successful_exits_count', 'domain_expertise_years_avg'],
            'product_evolution': ['product_stage', 'product_retention_30d', 'dau_mau_ratio'],
            'capital_metabolism': ['capital_efficiency', 'runway_months', 'funding_velocity']
        }
        
        # Pattern types
        self.pattern_types = {
            'rocket_ship': {'growth': 0.9, 'efficiency': 0.7, 'retention': 0.8},
            'slow_burn': {'growth': 0.4, 'efficiency': 0.9, 'retention': 0.9},
            'blitzscale': {'growth': 0.95, 'efficiency': 0.3, 'retention': 0.6},
            'sustainable': {'growth': 0.6, 'efficiency': 0.8, 'retention': 0.85},
            'pivot_master': {'growth': 0.5, 'efficiency': 0.6, 'retention': 0.7},
            'category_creator': {'growth': 0.7, 'efficiency': 0.5, 'retention': 0.75}
        }
        
    def extract_dna_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract DNA-like features that capture growth patterns"""
        dna_features = pd.DataFrame(index=df.index)
        
        # Growth Velocity Genes
        if 'revenue_growth_rate_percent' in df.columns:
            dna_features['growth_velocity'] = df['revenue_growth_rate_percent'] / 100
        else:
            dna_features['growth_velocity'] = 0
            
        if 'user_growth_rate_percent' in df.columns:
            dna_features['user_velocity'] = df['user_growth_rate_percent'] / 100
        else:
            dna_features['user_velocity'] = 0
        
        # Team scaling pattern
        if 'team_size_full_time' in df.columns and 'founding_year' in df.columns:
            current_year = datetime.now().year
            company_age = current_year - df['founding_year']
            dna_features['team_growth_rate'] = df['team_size_full_time'] / (company_age + 1)
        else:
            dna_features['team_growth_rate'] = df.get('team_size_full_time', 0) / 3
        
        # Efficiency Genes
        if 'burn_multiple' in df.columns:
            # Invert burn multiple - lower is better
            dna_features['capital_efficiency'] = 1 / (df['burn_multiple'] + 1)
        else:
            dna_features['capital_efficiency'] = 0.5
            
        if 'ltv_cac_ratio' in df.columns:
            dna_features['customer_efficiency'] = np.minimum(df['ltv_cac_ratio'] / 5, 1)
        else:
            dna_features['customer_efficiency'] = 0.5
            
        # Product-Market Fit DNA
        if 'product_retention_30d' in df.columns:
            dna_features['pmf_strength'] = df['product_retention_30d']
        else:
            dna_features['pmf_strength'] = 0.5
            
        if 'net_dollar_retention_percent' in df.columns:
            dna_features['expansion_dna'] = df['net_dollar_retention_percent'] / 150
        else:
            dna_features['expansion_dna'] = 0.7
        
        # Founder DNA
        if 'prior_successful_exits_count' in df.columns:
            dna_features['founder_success_gene'] = np.minimum(df['prior_successful_exits_count'] / 2, 1)
        else:
            dna_features['founder_success_gene'] = 0
            
        if 'domain_expertise_years_avg' in df.columns:
            dna_features['domain_mastery'] = np.minimum(df['domain_expertise_years_avg'] / 15, 1)
        else:
            dna_features['domain_mastery'] = 0.5
        
        # Market Positioning DNA
        if 'tam_size_usd' in df.columns and 'som_size_usd' in df.columns:
            dna_features['market_capture_potential'] = df['som_size_usd'] / (df['tam_size_usd'] + 1)
        else:
            dna_features['market_capture_potential'] = 0.001
            
        # Innovation DNA
        if 'patent_count' in df.columns:
            dna_features['innovation_gene'] = np.minimum(df['patent_count'] / 10, 1)
        else:
            dna_features['innovation_gene'] = 0
            
        if 'tech_differentiation_score' in df.columns:
            dna_features['differentiation_dna'] = df['tech_differentiation_score'] / 5
        else:
            dna_features['differentiation_dna'] = 0.5
        
        # Network Effects DNA
        if 'network_effects_present' in df.columns:
            dna_features['network_dna'] = df['network_effects_present'].astype(float)
        else:
            dna_features['network_dna'] = 0
        
        # Funding Velocity (how fast they raise)
        if 'total_capital_raised_usd' in df.columns and 'funding_rounds_count' in df.columns:
            dna_features['funding_velocity'] = df['total_capital_raised_usd'] / (df['funding_rounds_count'] + 1)
        else:
            dna_features['funding_velocity'] = 1000000
        
        return dna_features
    
    def identify_growth_patterns(self, dna_features: pd.DataFrame, labels: pd.Series) -> Dict:
        """Identify common growth patterns in successful startups"""
        # Normalize features
        dna_normalized = self.scaler.fit_transform(dna_features)
        
        # Reduce dimensions for pattern identification
        dna_reduced = self.pca.fit_transform(dna_normalized)
        
        # Separate success and failure patterns
        success_mask = labels == 1
        success_dna = dna_reduced[success_mask]
        failure_dna = dna_reduced[~success_mask]
        
        # Cluster successful patterns
        n_patterns = min(6, len(success_dna) // 100)
        if n_patterns > 1:
            kmeans = KMeans(n_clusters=n_patterns, random_state=42, n_init=10)
            success_clusters = kmeans.fit_predict(success_dna)
            self.pattern_clusters = kmeans
            
            # Analyze each cluster
            patterns = {}
            for i in range(n_patterns):
                cluster_mask = success_clusters == i
                cluster_features = dna_features[success_mask][cluster_mask]
                
                # Calculate cluster characteristics
                pattern_profile = {
                    'size': cluster_mask.sum(),
                    'avg_growth': cluster_features['growth_velocity'].mean(),
                    'avg_efficiency': cluster_features['capital_efficiency'].mean(),
                    'avg_retention': cluster_features.get('pmf_strength', pd.Series([0.5])).mean(),
                    'dominant_features': self._get_dominant_features(cluster_features)
                }
                
                # Match to known pattern types
                pattern_name = self._match_pattern_type(pattern_profile)
                patterns[pattern_name] = pattern_profile
                
            return patterns
        
        return {}
    
    def _get_dominant_features(self, cluster_features: pd.DataFrame) -> List[str]:
        """Identify the most dominant features in a cluster"""
        feature_means = cluster_features.mean()
        top_features = feature_means.nlargest(3).index.tolist()
        return top_features
    
    def _match_pattern_type(self, profile: Dict) -> str:
        """Match a cluster profile to known pattern types"""
        best_match = 'unknown'
        best_score = 0
        
        for pattern_name, pattern_chars in self.pattern_types.items():
            score = 0
            score += 1 - abs(profile['avg_growth'] - pattern_chars['growth'])
            score += 1 - abs(profile['avg_efficiency'] - pattern_chars['efficiency'])
            score += 1 - abs(profile['avg_retention'] - pattern_chars['retention'])
            
            if score > best_score:
                best_score = score
                best_match = pattern_name
                
        return best_match
    
    def calculate_dna_similarity(self, startup_dna: np.ndarray, pattern_dna: np.ndarray) -> float:
        """Calculate similarity between a startup's DNA and a success pattern"""
        return cosine_similarity(startup_dna.reshape(1, -1), pattern_dna.reshape(1, -1))[0, 0]
    
    def predict_growth_trajectory(self, startup_features: pd.DataFrame) -> Dict:
        """Predict the likely growth trajectory based on DNA analysis"""
        # Extract DNA features
        dna = self.extract_dna_features(startup_features)
        
        # Normalize
        dna_normalized = self.scaler.transform(dna)
        dna_reduced = self.pca.transform(dna_normalized)
        
        # Find closest pattern
        if self.pattern_clusters is not None:
            closest_pattern = self.pattern_clusters.predict(dna_reduced)[0]
            pattern_distance = np.min(self.pattern_clusters.transform(dna_reduced))
            
            # Calculate success probability based on pattern matching
            pattern_confidence = 1 / (1 + pattern_distance)
            
            # Identify growth trajectory characteristics
            pattern_names = list(self.pattern_library.keys())
            pattern_type = pattern_names[closest_pattern] if closest_pattern < len(pattern_names) else 'unknown'
            
            trajectory = {
                'pattern_type': pattern_type,
                'confidence': float(pattern_confidence),
                'growth_prediction': self._predict_growth_rate(dna),
                'risk_factors': self._identify_risk_factors(dna),
                'success_indicators': self._identify_success_indicators(dna)
            }
        else:
            trajectory = {
                'pattern_type': 'unknown',
                'confidence': 0.5,
                'growth_prediction': 'moderate',
                'risk_factors': [],
                'success_indicators': []
            }
            
        return trajectory
    
    def _predict_growth_rate(self, dna: pd.DataFrame) -> str:
        """Predict growth rate category based on DNA"""
        growth_score = dna['growth_velocity'].mean() * 0.4 + dna['user_velocity'].mean() * 0.3 + dna['team_growth_rate'].mean() * 0.3
        
        if growth_score > 0.8:
            return 'hypergrowth'
        elif growth_score > 0.6:
            return 'rapid'
        elif growth_score > 0.4:
            return 'steady'
        else:
            return 'slow'
    
    def _identify_risk_factors(self, dna: pd.DataFrame) -> List[str]:
        """Identify risk factors from DNA analysis"""
        risks = []
        
        if dna['capital_efficiency'].mean() < 0.3:
            risks.append('High burn rate relative to growth')
        if dna['pmf_strength'].mean() < 0.4:
            risks.append('Weak product-market fit signals')
        if dna['founder_success_gene'].mean() < 0.1:
            risks.append('Limited founder track record')
        if dna['customer_efficiency'].mean() < 0.2:
            risks.append('Poor unit economics')
            
        return risks
    
    def _identify_success_indicators(self, dna: pd.DataFrame) -> List[str]:
        """Identify positive indicators from DNA analysis"""
        indicators = []
        
        if dna['growth_velocity'].mean() > 0.7:
            indicators.append('Strong revenue growth momentum')
        if dna['capital_efficiency'].mean() > 0.7:
            indicators.append('Excellent capital efficiency')
        if dna['pmf_strength'].mean() > 0.7:
            indicators.append('Strong product-market fit')
        if dna['founder_success_gene'].mean() > 0.5:
            indicators.append('Experienced founding team')
        if dna['network_dna'].mean() > 0.5:
            indicators.append('Network effects present')
            
        return indicators
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train the DNA pattern analyzer"""
        logger.info("Training DNA Pattern Analyzer...")
        
        # Extract DNA features
        dna_features = self.extract_dna_features(X_train)
        
        # Identify patterns
        self.pattern_library = self.identify_growth_patterns(dna_features, y_train)
        
        # Store successful patterns for comparison
        success_mask = y_train == 1
        self.success_patterns = dna_features[success_mask].values
        self.failure_patterns = dna_features[~success_mask].values
        
        logger.info(f"Identified {len(self.pattern_library)} growth patterns")
        for pattern, profile in self.pattern_library.items():
            logger.info(f"  {pattern}: {profile['size']} companies, "
                       f"avg_growth={profile['avg_growth']:.2f}")
    
    def save(self, path: Path) -> None:
        """Save the DNA analyzer"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save models
        joblib.dump(self.scaler, path / 'dna_scaler.pkl')
        joblib.dump(self.pca, path / 'dna_pca.pkl')
        if self.pattern_clusters:
            joblib.dump(self.pattern_clusters, path / 'dna_clusters.pkl')
        
        # Save patterns
        joblib.dump(self.pattern_library, path / 'pattern_library.pkl')
        joblib.dump(self.success_patterns, path / 'success_patterns.pkl')
        joblib.dump(self.failure_patterns, path / 'failure_patterns.pkl')
        
        # Save configuration
        config = {
            'dna_components': self.dna_components,
            'pattern_types': self.pattern_types
        }
        with open(path / 'dna_config.json', 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"DNA analyzer saved to {path}")
    
    def load(self, path: Path) -> None:
        """Load the DNA analyzer"""
        path = Path(path)
        
        # Load models
        self.scaler = joblib.load(path / 'dna_scaler.pkl')
        self.pca = joblib.load(path / 'dna_pca.pkl')
        if (path / 'dna_clusters.pkl').exists():
            self.pattern_clusters = joblib.load(path / 'dna_clusters.pkl')
        
        # Load patterns
        self.pattern_library = joblib.load(path / 'pattern_library.pkl')
        self.success_patterns = joblib.load(path / 'success_patterns.pkl')
        self.failure_patterns = joblib.load(path / 'failure_patterns.pkl')
        
        # Load configuration
        with open(path / 'dna_config.json', 'r') as f:
            config = json.load(f)
            self.dna_components = config['dna_components']
            self.pattern_types = config['pattern_types']
            
        logger.info(f"DNA analyzer loaded from {path}")


def train_dna_analyzer():
    """Train the DNA pattern analyzer on the dataset"""
    logger.info("Starting DNA Pattern Analysis Training")
    
    # Load data
    df = pd.read_csv("data/final_100k_dataset_45features.csv")
    
    # Prepare features
    exclude_cols = ['success', 'startup_id', 'startup_name']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols]
    y = df['success']
    
    # Train DNA analyzer
    analyzer = StartupDNAAnalyzer()
    analyzer.train(X, y)
    
    # Save analyzer
    analyzer.save(Path("models/dna_analyzer"))
    
    # Test on a few examples
    sample = X.sample(5)
    for idx, row in sample.iterrows():
        trajectory = analyzer.predict_growth_trajectory(pd.DataFrame([row]))
        logger.info(f"\nSample {idx}:")
        logger.info(f"  Pattern: {trajectory['pattern_type']}")
        logger.info(f"  Growth: {trajectory['growth_prediction']}")
        logger.info(f"  Risks: {trajectory['risk_factors']}")
        logger.info(f"  Strengths: {trajectory['success_indicators']}")
    
    return analyzer


if __name__ == "__main__":
    train_dna_analyzer()