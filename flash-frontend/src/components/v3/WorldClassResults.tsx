import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FullAnalysisView } from './FullAnalysisView';
import { AdvancedAnalysisModal } from './AdvancedAnalysisModal';
import './WorldClassResults.css';

interface WorldClassResultsProps {
  data: any;
}

export const WorldClassResults: React.FC<WorldClassResultsProps> = ({ data }) => {
  const [showFullAnalysis, setShowFullAnalysis] = useState(false);
  const [showAdvancedModal, setShowAdvancedModal] = useState(false);
  const [activeMetric, setActiveMetric] = useState<string | null>(null);

  if (!data || !data.pillar_scores) {
    return (
      <div className="wc-results error">
        <p>Unable to display results. Please try again.</p>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return '#00C851';
    if (score >= 0.6) return '#33B5E5';
    if (score >= 0.4) return '#FF8800';
    return '#FF4444';
  };

  const getVerdictIcon = (verdict: string) => {
    const icons: Record<string, string> = {
      'STRONG PASS': '🚀',
      'PASS': '✅',
      'CONDITIONAL PASS': '⚡',
      'FAIL': '⚠️',
      'STRONG FAIL': '🔴'
    };
    return icons[verdict] || '📊';
  };

  const getVerdictClass = (verdict: string) => {
    const classMap: Record<string, string> = {
      'STRONG PASS': 'strong-pass',
      'PASS': 'pass',
      'CONDITIONAL PASS': 'conditional',
      'FAIL': 'fail',
      'STRONG FAIL': 'strong-fail'
    };
    return classMap[verdict] || 'neutral';
  };

  const getMetricIcon = (metric: string) => {
    const icons: Record<string, string> = {
      capital: '💰',
      advantage: '🏆',
      market: '📈',
      people: '👥'
    };
    return icons[metric] || '📊';
  };

  const getMetricDescription = (metric: string) => {
    const descriptions: Record<string, string> = {
      capital: 'Financial Health & Unit Economics',
      advantage: 'Competitive Moat & Differentiation',
      market: 'TAM Size & Growth Dynamics',
      people: 'Team Strength & Experience'
    };
    return descriptions[metric] || metric;
  };

  const verdict = getVerdictDetails(data.verdict);
  const hasAdvancedFeatures = !!(data.dna_pattern || data.temporal_predictions || data.industry_insights);

  return (
    <>
      <motion.div 
        className="wc-results"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        {/* Hero Section */}
        <section className="wc-hero">
          <motion.div 
            className="wc-score-card"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "spring", stiffness: 100, delay: 0.2 }}
          >
            <div className="wc-score-visual">
              <svg className="wc-score-ring" viewBox="0 0 260 260">
                <defs>
                  <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%%" y2="100%">
                    <stop offset="0%" stopColor={getScoreColor(data.success_probability)} />
                    <stop offset="100%" stopColor={getScoreColor(data.success_probability)} stopOpacity="0.6" />
                  </linearGradient>
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                
                {/* Background ring */}
                <circle
                  cx="130"
                  cy="130"
                  r="120"
                  fill="none"
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="2"
                />
                
                {/* Progress ring */}
                <circle
                  cx="130"
                  cy="130"
                  r="120"
                  fill="none"
                  stroke="url(#scoreGradient)"
                  strokeWidth="4"
                  strokeDasharray={`${data.success_probability * 754} 754`}
                  strokeLinecap="round"
                  transform="rotate(-90 130 130)"
                  filter="url(#glow)"
                  className="wc-score-progress"
                />
              </svg>
              
              <div className="wc-score-content">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <h1 className="wc-score-number">
                    <span className="wc-score-digits">{Math.round(data.success_probability * 100)}</span>
                    <span className="wc-score-percent">%</span>
                  </h1>
                  <p className="wc-score-label">Success Probability</p>
                </motion.div>
              </div>
            </div>
            
            <motion.div 
              className="wc-verdict-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <div className={`wc-verdict-badge ${getVerdictClass(data.verdict)}`}>
                <span className="wc-verdict-icon">{getVerdictIcon(data.verdict)}</span>
                <span className="wc-verdict-text">{data.verdict}</span>
              </div>
              
              <h2 className="wc-verdict-headline">{verdict.title}</h2>
              <p className="wc-verdict-description">{verdict.description}</p>
              
              {data.confidence_score && (
                <div className="wc-confidence">
                  <div className="wc-confidence-bar">
                    <motion.div 
                      className="wc-confidence-fill"
                      initial={{ width: 0 }}
                      animate={{ width: `${data.confidence_score * 100}%` }}
                      transition={{ delay: 0.8, duration: 0.8 }}
                    />
                  </div>
                  <span className="wc-confidence-text">
                    Model Confidence: {Math.round(data.confidence_score * 100)}%
                  </span>
                </div>
              )}
            </motion.div>
          </motion.div>
        </section>

        {/* CAMP Metrics Section */}
        <section className="wc-metrics">
          <motion.h3 
            className="wc-section-title"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            CAMP Framework Analysis
          </motion.h3>
          
          <div className="wc-metrics-grid">
            {Object.entries(data.pillar_scores).map(([metric, score], index) => {
              const isActive = activeMetric === metric;
              const isBelowThreshold = data.below_threshold?.includes(metric);
              
              return (
                <motion.div
                  key={metric}
                  className={`wc-metric-card ${isActive ? 'active' : ''} ${isBelowThreshold ? 'warning' : ''}`}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 + index * 0.1 }}
                  onHoverStart={() => setActiveMetric(metric)}
                  onHoverEnd={() => setActiveMetric(null)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="wc-metric-header">
                    <span className="wc-metric-icon">{getMetricIcon(metric)}</span>
                    <h4 className="wc-metric-name">{metric.toUpperCase()}</h4>
                  </div>
                  
                  <div className="wc-metric-score">
                    <span className="wc-metric-value" style={{ color: getScoreColor(score as number) }}>
                      {Math.round((score as number) * 100)}
                    </span>
                    <span className="wc-metric-unit">%</span>
                  </div>
                  
                  <div className="wc-metric-bar">
                    <motion.div 
                      className="wc-metric-fill"
                      style={{ backgroundColor: getScoreColor(score as number) }}
                      initial={{ width: 0 }}
                      animate={{ width: `${(score as number) * 100}%` }}
                      transition={{ delay: 0.9 + index * 0.1, duration: 0.6 }}
                    />
                  </div>
                  
                  <p className="wc-metric-description">{getMetricDescription(metric)}</p>
                  
                  {isBelowThreshold && (
                    <div className="wc-metric-warning">
                      Below investment threshold
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </section>

        {/* Advanced Insights */}
        {hasAdvancedFeatures && (
          <section className="wc-advanced">
            <motion.div 
              className="wc-advanced-grid"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
            >
              {data.dna_pattern && (
                <div className="wc-insight-card dna">
                  <div className="wc-insight-header">
                    <span className="wc-insight-icon">🧬</span>
                    <h4>Startup DNA</h4>
                  </div>
                  <p className="wc-insight-value">{data.dna_pattern.pattern_type?.toUpperCase()}</p>
                  <p className="wc-insight-description">
                    {getDNADescription(data.dna_pattern.pattern_type)}
                  </p>
                </div>
              )}
              
              {data.temporal_predictions && (
                <div className="wc-insight-card temporal">
                  <div className="wc-insight-header">
                    <span className="wc-insight-icon">📅</span>
                    <h4>Growth Trajectory</h4>
                  </div>
                  <div className="wc-timeline">
                    <div className="wc-timeline-item">
                      <span className="wc-timeline-label">6 months</span>
                      <span className="wc-timeline-value" style={{ color: getScoreColor(data.temporal_predictions.short_term || 0.5) }}>
                        {Math.round((data.temporal_predictions.short_term || 0.5) * 100)}%
                      </span>
                    </div>
                    <div className="wc-timeline-item">
                      <span className="wc-timeline-label">12 months</span>
                      <span className="wc-timeline-value" style={{ color: getScoreColor(data.temporal_predictions.medium_term || 0.5) }}>
                        {Math.round((data.temporal_predictions.medium_term || 0.5) * 100)}%
                      </span>
                    </div>
                    <div className="wc-timeline-item">
                      <span className="wc-timeline-label">18+ months</span>
                      <span className="wc-timeline-value" style={{ color: getScoreColor(data.temporal_predictions.long_term || 0.5) }}>
                        {Math.round((data.temporal_predictions.long_term || 0.5) * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </section>
        )}

        {/* Actions */}
        <section className="wc-actions">
          <motion.button 
            className="wc-button primary"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowFullAnalysis(true)}
          >
            <span className="wc-button-icon">📊</span>
            View Full Analysis
          </motion.button>
          
          <motion.button 
            className="wc-button secondary"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              const report = {
                timestamp: new Date().toISOString(),
                verdict: data.verdict,
                success_probability: data.success_probability,
                pillar_scores: data.pillar_scores,
                key_insights: data.key_insights,
                dna_pattern: data.dna_pattern,
                temporal_predictions: data.temporal_predictions
              };
              
              const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `flash-analysis-${new Date().toISOString().split('T')[0]}.json`;
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            <span className="wc-button-icon">💾</span>
            Export Report
          </motion.button>
          
          {hasAdvancedFeatures && (
            <motion.button 
              className="wc-button gradient"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowAdvancedModal(true)}
            >
              <span className="wc-button-icon">✨</span>
              Advanced Insights
            </motion.button>
          )}
        </section>
      </motion.div>

      {/* Modals */}
      <FullAnalysisView
        isOpen={showFullAnalysis}
        onClose={() => setShowFullAnalysis(false)}
        data={data}
        fundingStage={data.funding_stage || 'seed'}
        startupData={data}
      />
      
      {showAdvancedModal && hasAdvancedFeatures && (
        <AdvancedAnalysisModal
          isOpen={showAdvancedModal}
          onClose={() => setShowAdvancedModal(false)}
          data={data}
        />
      )}
    </>
  );
};

// Helper functions
function getVerdictDetails(verdict: string) {
  const details: Record<string, { title: string; description: string }> = {
    'STRONG PASS': {
      title: 'Exceptional Investment Opportunity',
      description: 'This startup demonstrates outstanding potential across all key metrics.'
    },
    'PASS': {
      title: 'Solid Investment Candidate',
      description: 'Strong fundamentals with good growth potential and manageable risks.'
    },
    'CONDITIONAL PASS': {
      title: 'Promising with Conditions',
      description: 'Shows potential but requires specific improvements before investment.'
    },
    'FAIL': {
      title: 'Not Investment Ready',
      description: 'Significant gaps need to be addressed before seeking investment.'
    },
    'STRONG FAIL': {
      title: 'Major Concerns Identified',
      description: 'Fundamental issues require substantial restructuring.'
    }
  };
  
  return details[verdict] || {
    title: 'Analysis Complete',
    description: 'Review the detailed metrics below for insights.'
  };
}

function getDNADescription(pattern: string) {
  const descriptions: Record<string, string> = {
    'rocket_ship': 'Hypergrowth trajectory with exceptional fundamentals',
    'slow_burn': 'Sustainable growth with excellent efficiency metrics',
    'blitzscale': 'Rapid expansion prioritizing growth over profitability',
    'sustainable': 'Balanced approach with strong unit economics',
    'pivot_master': 'Highly adaptable with breakthrough potential',
    'category_creator': 'Innovative leader defining new markets'
  };
  return descriptions[pattern] || 'Unique growth characteristics identified';
}