import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { AdvancedAnalysisModal } from './AdvancedAnalysisModal';
import { FullAnalysisView } from './FullAnalysisView';
import './EnhancedResults.css';

interface EnhancedResultsProps {
  data: any;
}

export const EnhancedResults: React.FC<EnhancedResultsProps> = ({ data }) => {
  const [showAdvancedModal, setShowAdvancedModal] = useState(false);
  const [showFullAnalysis, setShowFullAnalysis] = useState(false);
  if (!data || !data.pillar_scores) {
    return (
      <div className="enhanced-results error">
        <p>Unable to display results. Please try again.</p>
      </div>
    );
  }

  // Helper functions
  const getScoreColor = (score: number) => {
    if (score >= 0.8) return '#10b981'; // green
    if (score >= 0.6) return '#3b82f6'; // blue
    if (score >= 0.4) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  const getVerdictClass = (verdict: string) => {
    const verdictMap: Record<string, string> = {
      'STRONG PASS': 'strong-pass',
      'PASS': 'pass',
      'CONDITIONAL PASS': 'conditional',
      'FAIL': 'fail',
      'STRONG FAIL': 'strong-fail'
    };
    return verdictMap[verdict] || 'pending';
  };

  const getVerdictExplanation = (verdict: string) => {
    const explanations: Record<string, { title: string; description: string }> = {
      'STRONG PASS': {
        title: 'Exceptional Investment Opportunity',
        description: 'This startup demonstrates outstanding metrics across all key dimensions. Strong recommendation for investment.'
      },
      'PASS': {
        title: 'Solid Investment Candidate',
        description: 'Above-average performance with good fundamentals. Worth serious consideration with minor improvements.'
      },
      'CONDITIONAL PASS': {
        title: 'Borderline Case - Proceed with Caution',
        description: 'Mixed signals with both strengths and weaknesses. Success depends on addressing specific issues.'
      },
      'FAIL': {
        title: 'Not Investment Ready',
        description: 'Significant gaps in key areas. Substantial improvements needed before investment consideration.'
      },
      'STRONG FAIL': {
        title: 'Critical Issues Identified',
        description: 'Multiple red flags across core metrics. Not suitable for investment at this stage.'
      }
    };
    return explanations[verdict] || { title: 'Assessment Complete', description: 'Review the detailed metrics below.' };
  };

  const getPillarIcon = (pillar: string) => {
    const icons: Record<string, string> = {
      capital: '💰',
      advantage: '🛡️',
      market: '📈',
      people: '👥'
    };
    return icons[pillar] || '📊';
  };

  const getPillarDetails = (pillar: string) => {
    const details: Record<string, { name: string; description: string; factors: string[] }> = {
      capital: {
        name: 'Capital Efficiency',
        description: 'Financial health and funding metrics',
        factors: ['Burn rate', 'Runway', 'Revenue growth', 'Unit economics']
      },
      advantage: {
        name: 'Competitive Advantage',
        description: 'Moat strength and differentiation',
        factors: ['Technology IP', 'Network effects', 'Brand strength', 'Switching costs']
      },
      market: {
        name: 'Market Opportunity',
        description: 'Market size and dynamics',
        factors: ['TAM/SAM/SOM', 'Growth rate', 'Competition', 'Market timing']
      },
      people: {
        name: 'Team Quality',
        description: 'Leadership and execution capability',
        factors: ['Experience', 'Domain expertise', 'Track record', 'Team composition']
      }
    };
    return details[pillar] || { name: pillar, description: '', factors: [] };
  };

  const getScoreInterpretation = (score: number) => {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    if (score >= 0.2) return 'Poor';
    return 'Critical';
  };

  const verdict = getVerdictExplanation(data.verdict);
  const hasAdvancedFeatures = !!(data.dna_pattern || data.temporal_predictions);

  return (
    <motion.div 
      className="enhanced-results"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      {/* Header Section */}
      <div className={`results-header ${getVerdictClass(data.verdict)}`}>
        <motion.div 
          className="score-display"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="score-ring">
            <svg viewBox="0 0 200 200">
              <circle cx="100" cy="100" r="90" fill="none" stroke="#e5e7eb" strokeWidth="20"/>
              <circle 
                cx="100" 
                cy="100" 
                r="90" 
                fill="none" 
                stroke={getScoreColor(data.success_probability)}
                strokeWidth="20"
                strokeDasharray={`${data.success_probability * 565.48} 565.48`}
                strokeLinecap="round"
                transform="rotate(-90 100 100)"
              />
            </svg>
            <div className="score-content">
              <h1 className="score-value">
                {Math.round(data.success_probability * 100)}
                <span className="percentage-symbol">%</span>
              </h1>
              <p className="score-label">Success Rate</p>
            </div>
          </div>
        </motion.div>

        <div className="verdict-info">
          <h2 className={`verdict-badge ${getVerdictClass(data.verdict)}`}>
            {data.verdict}
          </h2>
          <h3 className="verdict-title">{verdict.title}</h3>
          <p className="verdict-description">{verdict.description}</p>
          
          {data.confidence_score && (
            <div className="confidence-info">
              <div className="confidence-meter">
                <div 
                  className="confidence-fill"
                  style={{ width: `${data.confidence_score * 100}%` }}
                />
              </div>
              <p className="confidence-text">
                Model confidence: {Math.round(data.confidence_score * 100)}%
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Advanced Features Section */}
      {hasAdvancedFeatures && (
        <div className="advanced-features">
          {data.dna_pattern && (
            <motion.div 
              className="dna-card"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div className="dna-header">
                <span className="dna-icon">🧬</span>
                <h3>Startup DNA Pattern</h3>
              </div>
              <h4 className="dna-type">{data.dna_pattern.pattern_type?.toUpperCase()}</h4>
              <p className="dna-description">
                {data.dna_pattern.pattern_type === 'blitzscale' 
                  ? 'Rapid expansion prioritizing growth over efficiency - typical of unicorn trajectories'
                  : 'Growth pattern identified based on key metrics'}
              </p>
            </motion.div>
          )}

          {data.temporal_predictions && (
            <motion.div 
              className="temporal-card"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <h3>Success Probability Over Time</h3>
              <div className="temporal-timeline">
                <div className="timeline-item">
                  <span className="timeline-period">6 months</span>
                  <span 
                    className="timeline-value"
                    style={{ color: getScoreColor(data.temporal_predictions.short_term || 0.5) }}
                  >
                    {Math.round((data.temporal_predictions.short_term || 0.5) * 100)}%
                  </span>
                </div>
                <div className="timeline-connector" />
                <div className="timeline-item featured">
                  <span className="timeline-period">12 months</span>
                  <span 
                    className="timeline-value"
                    style={{ color: getScoreColor(data.temporal_predictions.medium_term || 0.5) }}
                  >
                    {Math.round((data.temporal_predictions.medium_term || 0.5) * 100)}%
                  </span>
                </div>
                <div className="timeline-connector" />
                <div className="timeline-item">
                  <span className="timeline-period">18+ months</span>
                  <span 
                    className="timeline-value"
                    style={{ color: getScoreColor(data.temporal_predictions.long_term || 0.5) }}
                  >
                    {Math.round((data.temporal_predictions.long_term || 0.5) * 100)}%
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* CAMP Metrics Section - Moved to Full Analysis View */}
      {/* <div className="camp-section">
        <h2 className="section-header">
          <span className="section-title">CAMP Framework Analysis</span>
          <span className="section-subtitle">Four pillars of startup success</span>
        </h2>

        <div className="camp-grid">
          {Object.entries(data.pillar_scores).map(([pillar, score], index) => {
            const details = getPillarDetails(pillar);
            const scoreValue = score as number;
            const interpretation = getScoreInterpretation(scoreValue);
            const isBelowThreshold = data.below_threshold?.includes(pillar);

            return (
              <motion.div 
                key={pillar}
                className={`camp-card ${isBelowThreshold ? 'warning' : ''}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
              >
                <div className="camp-card-header">
                  <span className="camp-icon">{getPillarIcon(pillar)}</span>
                  <h3 className="camp-name">{details.name}</h3>
                </div>

                <div className="camp-score-section">
                  <div className="camp-score-value" style={{ color: getScoreColor(scoreValue) }}>
                    {Math.round(scoreValue * 100)}
                  </div>
                  <div className="camp-score-label">{interpretation}</div>
                </div>

                <p className="camp-description">{details.description}</p>

                <div className="camp-progress">
                  <div 
                    className="camp-progress-fill"
                    style={{ 
                      width: `${scoreValue * 100}%`,
                      backgroundColor: getScoreColor(scoreValue)
                    }}
                  />
                </div>

                <div className="camp-factors">
                  {details.factors.map((factor, i) => (
                    <span key={i} className="camp-factor">{factor}</span>
                  ))}
                </div>

                {isBelowThreshold && (
                  <div className="threshold-warning">
                    ⚠️ Below investment threshold
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>
      </div> */}

      {/* Key Insights Section - Moved to Full Analysis View */}
      {/* {data.key_insights && data.key_insights.length > 0 && (
        <div className="insights-section">
          <h2 className="section-header">
            <span className="section-title">Key Insights</span>
            <span className="section-subtitle">Critical findings from the analysis</span>
          </h2>
          
          <div className="insights-grid">
            {data.key_insights.map((insight: string, index: number) => {
              const isPositive = insight.toLowerCase().includes('strong') || 
                               insight.toLowerCase().includes('excellent') ||
                               insight.toLowerCase().includes('growth');
              const isNegative = insight.toLowerCase().includes('critical') || 
                               insight.toLowerCase().includes('risk') ||
                               insight.toLowerCase().includes('concern');
              
              return (
                <motion.div 
                  key={index}
                  className={`insight-card ${isPositive ? 'positive' : isNegative ? 'negative' : 'neutral'}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7 + index * 0.1 }}
                >
                  <span className="insight-icon">
                    {isPositive ? '✅' : isNegative ? '⚠️' : '💡'}
                  </span>
                  <p className="insight-text">
                    {insight.replace(/[📊🚀💰👥⚠️✅🎯💎📈💸🚨🛡️]/g, '').trim()}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      )} */}

      {/* Quick Summary */}
      <div className="quick-summary">
        <p className="summary-text">
          Your startup has been thoroughly analyzed. Click below to explore detailed insights, benchmarks, and recommendations.
        </p>
      </div>

      {/* Action Buttons */}
      <div className="action-section">
        <button 
          className="action-button primary"
          onClick={() => {
            // Create a detailed report
            const report = {
              timestamp: new Date().toISOString(),
              verdict: data.verdict,
              success_probability: data.success_probability,
              pillar_scores: data.pillar_scores,
              key_insights: data.key_insights,
              dna_pattern: data.dna_pattern,
              temporal_predictions: data.temporal_predictions,
              recommendations: data.recommendations
            };
            
            // Download as JSON
            const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `flash-analysis-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
          }}
        >
          <span className="button-icon">📄</span>
          Export Detailed Report
        </button>
        <button 
          className="action-button secondary"
          onClick={() => setShowFullAnalysis(true)}
        >
          <span className="button-icon">📊</span>
          View Full Analysis
        </button>
        {hasAdvancedFeatures && (
          <button 
            className="advanced-badge"
            onClick={() => setShowAdvancedModal(true)}
            style={{ cursor: 'pointer' }}
          >
            ✨ Advanced Analysis
          </button>
        )}
      </div>

      {/* Advanced Analysis Modal */}
      <AdvancedAnalysisModal 
        isOpen={showAdvancedModal}
        onClose={() => setShowAdvancedModal(false)}
        data={data}
      />
      
      {/* Full Analysis View */}
      <FullAnalysisView
        isOpen={showFullAnalysis}
        onClose={() => setShowFullAnalysis(false)}
        data={data}
        fundingStage={data.funding_stage || 'seed'}
        startupData={data}
      />
    </motion.div>
  );
};