import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './AdvancedAnalysisModal.css';

interface AdvancedAnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: any;
}

export const AdvancedAnalysisModal: React.FC<AdvancedAnalysisModalProps> = ({ isOpen, onClose, data }) => {
  if (!data) return null;

  const getTrajectoryDescription = (trajectory: string) => {
    const descriptions: Record<string, string> = {
      'strong_growth': 'Your startup shows signs of exponential growth with strong market validation.',
      'steady_progress': 'Consistent growth trajectory with good fundamentals in place.',
      'early_peak': 'Rapid initial traction that may require careful management to sustain.',
      'late_bloomer': 'Building strong foundations now for future acceleration.',
      'immediate_risk': 'Critical issues require immediate attention to avoid failure.'
    };
    return descriptions[trajectory] || 'Growth pattern analysis in progress.';
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="modal-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="modal-container"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
          >
            <div className="modal-header">
              <h2>Advanced Analysis</h2>
              <button className="close-button" onClick={onClose}>×</button>
            </div>

            <div className="modal-content">
              {/* DNA Pattern Deep Dive */}
              {data.dna_pattern && (
                <section className="analysis-section">
                  <h3>🧬 Startup DNA Pattern Analysis</h3>
                  <div className="dna-details">
                    <div className="pattern-badge">
                      {data.dna_pattern.pattern_type?.toUpperCase()}
                    </div>
                    <p className="pattern-description">
                      {data.dna_pattern.pattern_type === 'blitzscale' 
                        ? 'Your startup exhibits a blitzscaling pattern - rapid expansion prioritizing growth over efficiency. This is characteristic of unicorn trajectories but requires careful capital management.'
                        : data.dna_pattern.pattern_type === 'slow_burn'
                        ? 'Your startup follows a slow-burn pattern - sustainable growth with excellent capital efficiency. This approach builds lasting value with lower risk.'
                        : 'Your growth pattern has been identified and analyzed for optimization opportunities.'}
                    </p>
                    
                    {data.dna_pattern.success_indicators && (
                      <div className="indicators-list">
                        <h4>Success Indicators</h4>
                        <ul>
                          {data.dna_pattern.success_indicators.map((indicator: string, i: number) => (
                            <li key={i}>{indicator}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {data.dna_pattern.risk_factors && (
                      <div className="risk-list">
                        <h4>Risk Factors</h4>
                        <ul>
                          {data.dna_pattern.risk_factors.map((risk: string, i: number) => (
                            <li key={i}>{risk}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </section>
              )}

              {/* Temporal Analysis */}
              {data.temporal_predictions && (
                <section className="analysis-section">
                  <h3>📈 Time-Based Success Projections</h3>
                  <div className="temporal-analysis">
                    <div className="projection-grid">
                      <div className="projection-card">
                        <h4>Short Term (0-6 months)</h4>
                        <div className="projection-value">
                          {Math.round((data.temporal_predictions.short_term || 0.5) * 100)}%
                        </div>
                        <p>Focus on product-market fit and early traction metrics.</p>
                      </div>
                      <div className="projection-card">
                        <h4>Medium Term (6-18 months)</h4>
                        <div className="projection-value">
                          {Math.round((data.temporal_predictions.medium_term || 0.5) * 100)}%
                        </div>
                        <p>Scale operations and prove unit economics.</p>
                      </div>
                      <div className="projection-card">
                        <h4>Long Term (18+ months)</h4>
                        <div className="projection-value">
                          {Math.round((data.temporal_predictions.long_term || 0.5) * 100)}%
                        </div>
                        <p>Achieve market leadership and sustainable growth.</p>
                      </div>
                    </div>
                    
                    {data.trajectory && (
                      <div className="trajectory-insight">
                        <h4>Growth Trajectory: {data.trajectory.replace(/_/g, ' ').toUpperCase()}</h4>
                        <p>{getTrajectoryDescription(data.trajectory)}</p>
                      </div>
                    )}
                  </div>
                </section>
              )}

              {/* Industry Insights */}
              {data.industry_insights && (
                <section className="analysis-section">
                  <h3>🏭 Industry-Specific Analysis</h3>
                  <div className="industry-details">
                    <p className="industry-performance">
                      Relative Performance: <strong>{data.industry_insights.relative_performance}</strong>
                    </p>
                    {data.industry_insights.benchmarks && (
                      <div className="industry-benchmarks">
                        <h4>Industry Benchmarks</h4>
                        <ul>
                          {Object.entries(data.industry_insights.benchmarks).map(([metric, value]) => (
                            <li key={metric}>
                              {`${metric.replace(/_/g, ' ')}: ${value}`}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </section>
              )}

              {/* Recommendations */}
              {data.recommendations && data.recommendations.length > 0 && (
                <section className="analysis-section">
                  <h3>🎯 Strategic Recommendations</h3>
                  <div className="recommendations-list">
                    {data.recommendations.map((rec: string, i: number) => (
                      <div key={i} className="recommendation-item">
                        <span className="rec-number">{i + 1}</span>
                        <p>{rec}</p>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Critical Factors */}
              {data.critical_factors && data.critical_factors.length > 0 && (
                <section className="analysis-section">
                  <h3>⚠️ Critical Success Factors</h3>
                  <div className="factors-grid">
                    {data.critical_factors.map((factor: string, i: number) => (
                      <div key={i} className="factor-card">
                        {factor}
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </div>

            <div className="modal-footer">
              <button className="action-button secondary" onClick={onClose}>
                Close
              </button>
              <button 
                className="action-button primary"
                onClick={() => {
                  // Export advanced analysis
                  const advancedReport = {
                    timestamp: new Date().toISOString(),
                    analysis_type: 'advanced',
                    ...data
                  };
                  const blob = new Blob([JSON.stringify(advancedReport, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `flash-advanced-analysis-${new Date().toISOString().split('T')[0]}.json`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
              >
                Export Advanced Report
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};