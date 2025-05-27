import React from 'react';
import { motion } from 'framer-motion';
import './AdvancedResultsPage.css';

interface AdvancedResultsPageProps {
  results: any;
}

const AdvancedResultsPage: React.FC<AdvancedResultsPageProps> = ({ results }) => {
  
  // Extract advanced model predictions
  const {
    success_probability,
    confidence_score,
    pillar_scores,
    stage_prediction,
    dna_pattern,
    temporal_predictions,
    industry_insights,
    trajectory,
    recommendations,
    verdict,
    strength,
    weighted_score
  } = results;

  // Color coding for scores
  const getScoreColor = (score: number) => {
    if (score >= 0.8) return '#00ff88';
    if (score >= 0.6) return '#ffbb00';
    if (score >= 0.4) return '#ff8800';
    return '#ff0055';
  };

  const getTrajectoryIcon = (trajectory: string) => {
    const icons: Record<string, string> = {
      'strong_growth': '🚀',
      'steady_progress': '📈',
      'early_peak': '⚡',
      'late_bloomer': '🌱',
      'immediate_risk': '⚠️'
    };
    return icons[trajectory] || '📊';
  };

  const getDNAPatternDescription = (pattern: string) => {
    const descriptions: Record<string, string> = {
      'rocket_ship': 'Hypergrowth trajectory with strong fundamentals',
      'slow_burn': 'Sustainable growth with excellent efficiency',
      'blitzscale': 'Rapid expansion prioritizing growth over efficiency',
      'sustainable': 'Balanced growth with strong unit economics',
      'pivot_master': 'Adaptable with potential for breakthrough',
      'category_creator': 'Innovative with market-defining potential'
    };
    return descriptions[pattern] || 'Unique growth pattern';
  };

  return (
    <div className="advanced-results-page">
      <motion.div 
        className="results-container"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header with Overall Score */}
        <div className="results-header">
          <motion.div 
            className="score-circle"
            style={{ borderColor: getScoreColor(success_probability) }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="score-value">{(success_probability * 100).toFixed(0)}%</div>
            <div className="score-label">Success Probability</div>
          </motion.div>
          
          <div className="verdict-section">
            <h1 className={`verdict ${verdict?.toLowerCase().replace(' ', '-')}`}>
              {verdict || 'ASSESSMENT COMPLETE'}
            </h1>
            <div className={`strength-badge ${strength?.toLowerCase()}`}>
              {strength || 'ANALYZED'}
            </div>
            <div className="confidence">
              Confidence: {(confidence_score * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        {/* Trajectory and DNA Pattern */}
        {(trajectory || dna_pattern) && (
          <motion.div 
            className="insights-section"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {trajectory && (
              <div className="trajectory-card">
                <div className="trajectory-icon">{getTrajectoryIcon(trajectory)}</div>
                <div className="trajectory-info">
                  <h3>Growth Trajectory</h3>
                  <p className="trajectory-type">{trajectory.replace(/_/g, ' ').toUpperCase()}</p>
                </div>
              </div>
            )}
            
            {dna_pattern && (
              <div className="dna-pattern-card">
                <div className="dna-icon">🧬</div>
                <div className="dna-info">
                  <h3>Startup DNA Pattern</h3>
                  <p className="pattern-type">{dna_pattern.pattern_type?.toUpperCase()}</p>
                  <p className="pattern-description">
                    {getDNAPatternDescription(dna_pattern.pattern_type)}
                  </p>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Temporal Predictions */}
        {temporal_predictions && (
          <motion.div 
            className="temporal-section"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <h2>Success Probability Over Time</h2>
            <div className="temporal-cards">
              <div className="temporal-card">
                <div className="time-period">0-6 months</div>
                <div 
                  className="temporal-score"
                  style={{ color: getScoreColor(temporal_predictions.short_term || 0.5) }}
                >
                  {((temporal_predictions.short_term || 0.5) * 100).toFixed(0)}%
                </div>
                <div className="time-label">Short Term</div>
              </div>
              
              <div className="temporal-card featured">
                <div className="time-period">6-18 months</div>
                <div 
                  className="temporal-score"
                  style={{ color: getScoreColor(temporal_predictions.medium_term || 0.5) }}
                >
                  {((temporal_predictions.medium_term || 0.5) * 100).toFixed(0)}%
                </div>
                <div className="time-label">Medium Term</div>
              </div>
              
              <div className="temporal-card">
                <div className="time-period">18+ months</div>
                <div 
                  className="temporal-score"
                  style={{ color: getScoreColor(temporal_predictions.long_term || 0.5) }}
                >
                  {((temporal_predictions.long_term || 0.5) * 100).toFixed(0)}%
                </div>
                <div className="time-label">Long Term</div>
              </div>
            </div>
          </motion.div>
        )}

        {/* CAMP Scores */}
        <motion.div 
          className="camp-scores-section"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <h2>CAMP Analysis</h2>
          <div className="camp-grid">
            {Object.entries(pillar_scores).map(([pillar, score], index) => {
              const scoreValue = typeof score === 'number' ? score : 0;
              return (
                <motion.div 
                  key={pillar}
                  className="camp-card"
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                >
                  <div className="camp-header">
                    <h3>{pillar.charAt(0).toUpperCase() + pillar.slice(1)}</h3>
                    <div 
                      className="camp-score"
                      style={{ color: getScoreColor(scoreValue) }}
                    >
                      {(scoreValue * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="score-bar">
                    <motion.div 
                      className="score-fill"
                      style={{ backgroundColor: getScoreColor(scoreValue) }}
                      initial={{ width: 0 }}
                      animate={{ width: `${scoreValue * 100}%` }}
                      transition={{ duration: 0.8, delay: 0.8 + index * 0.1 }}
                    />
                  </div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Industry Insights */}
        {industry_insights && (
          <motion.div 
            className="industry-section"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            <h2>Industry-Specific Analysis</h2>
            <div className="industry-card">
              <div className="industry-metrics">
                <div className="metric">
                  <span className="metric-label">Industry Success Rate</span>
                  <span className="metric-value">
                    {(industry_insights.industry_success_rate * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Sample Size</span>
                  <span className="metric-value">
                    {industry_insights.sample_size?.toLocaleString() || 'N/A'}
                  </span>
                </div>
              </div>
              {industry_insights.key_success_factors && (
                <div className="key-factors">
                  <h4>Key Success Factors</h4>
                  <ul>
                    {industry_insights.key_success_factors.map((factor: string, i: number) => (
                      <li key={i}>{factor.replace(/_/g, ' ')}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <motion.div 
            className="recommendations-section"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            <h2>AI Recommendations</h2>
            <div className="recommendations-list">
              {recommendations.map((rec: string, index: number) => (
                <motion.div 
                  key={index}
                  className="recommendation-item"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.9 + index * 0.1 }}
                >
                  <span className="rec-icon">💡</span>
                  <span className="rec-text">{rec}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Action Buttons */}
        <motion.div 
          className="actions-section"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <button 
            className="action-button primary"
            onClick={() => window.print()}
          >
            Download Report
          </button>
          <button 
            className="action-button secondary"
            onClick={() => window.location.reload()}
          >
            New Analysis
          </button>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default AdvancedResultsPage;