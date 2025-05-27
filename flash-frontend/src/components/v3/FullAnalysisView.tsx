import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { WeightageExplanation } from './WeightageExplanation';
import './FullAnalysisView.css';

interface FullAnalysisViewProps {
  isOpen: boolean;
  onClose: () => void;
  data: any;
  fundingStage: string;
  startupData: any;
}

export const FullAnalysisView: React.FC<FullAnalysisViewProps> = ({ 
  isOpen, 
  onClose, 
  data, 
  fundingStage,
  startupData 
}) => {
  const [activeTab, setActiveTab] = useState('weightage');

  if (!data || !isOpen) return null;

  const tabs = [
    { id: 'weightage', label: 'Score Breakdown', icon: '📊' },
    { id: 'detailed', label: 'Detailed Insights', icon: '🔍' },
    { id: 'benchmarks', label: 'Stage Benchmarks', icon: '📈' },
    { id: 'recommendations', label: 'Next Steps', icon: '🎯' }
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="full-analysis-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="full-analysis-container"
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          >
            {/* Header */}
            <div className="full-analysis-header">
              <h2>Full Analysis Report</h2>
              <button className="close-analysis-button" onClick={onClose}>
                <span>Done</span>
              </button>
            </div>

            {/* Tabs */}
            <div className="analysis-tabs">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <span className="tab-icon">{tab.icon}</span>
                  <span className="tab-label">{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="tab-content">
              <AnimatePresence mode="wait">
                {activeTab === 'weightage' && (
                  <motion.div
                    key="weightage"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
                    <WeightageExplanation 
                      currentStage={fundingStage}
                      pillarScores={data.pillar_scores}
                    />
                  </motion.div>
                )}

                {activeTab === 'detailed' && (
                  <motion.div
                    key="detailed"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="detailed-insights-tab"
                  >
                    <h3>Comprehensive Analysis</h3>
                    
                    {/* Strengths */}
                    <section className="analysis-section">
                      <h4>Key Strengths</h4>
                      <div className="strength-cards">
                        {Object.entries(data.pillar_scores)
                          .filter(([_, score]) => (score as number) >= 0.6)
                          .map(([pillar, score]: [string, any]) => (
                            <div key={pillar} className="strength-card">
                              <div className="strength-score">{Math.round((score as number) * 100)}%</div>
                              <h5>{pillar.charAt(0).toUpperCase() + pillar.slice(1)}</h5>
                              <p>{getStrengthDescription(pillar, score as number)}</p>
                            </div>
                          ))}
                      </div>
                    </section>

                    {/* Risk Factors */}
                    <section className="analysis-section">
                      <h4>Risk Factors & Improvements</h4>
                      <div className="risk-grid">
                        {data.below_threshold?.map((pillar: string, i: number) => (
                          <div key={i} className="risk-card">
                            <div className="risk-header">
                              <span className="risk-icon">⚠️</span>
                              <h5>{pillar.charAt(0).toUpperCase() + pillar.slice(1)}</h5>
                            </div>
                            <p>{getRiskDescription(pillar, fundingStage)}</p>
                            <div className="improvement-actions">
                              {getImprovementActions(pillar).map((action, j) => (
                                <div key={j} className="action-item">
                                  <span className="action-bullet">→</span>
                                  {action}
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>

                    {/* Market Position */}
                    <section className="analysis-section">
                      <h4>Market Position Analysis</h4>
                      <div className="market-analysis">
                        <div className="metric-row">
                          <span className="metric-label">TAM Coverage</span>
                          <span className="metric-value">
                            ${((startupData?.tam_size_usd || 0) / 1e9).toFixed(1)}B market
                          </span>
                        </div>
                        <div className="metric-row">
                          <span className="metric-label">Growth Rate</span>
                          <span className="metric-value">
                            {startupData?.market_growth_rate_percent || 0}% annually
                          </span>
                        </div>
                        <div className="metric-row">
                          <span className="metric-label">Competitive Intensity</span>
                          <span className="metric-value">
                            {getCompetitionLevel(startupData?.competition_intensity)}
                          </span>
                        </div>
                      </div>
                    </section>
                  </motion.div>
                )}

                {activeTab === 'benchmarks' && (
                  <motion.div
                    key="benchmarks"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="benchmarks-tab"
                  >
                    <h3>How You Compare</h3>
                    
                    <div className="benchmark-overview">
                      <p>Your startup is being evaluated against <strong>{fundingStage.replace(/_/g, ' ').toUpperCase()}</strong> stage criteria.</p>
                    </div>

                    <div className="benchmark-grid">
                      {Object.entries(data.stage_thresholds || {}).map(([pillar, threshold]: [string, any]) => {
                        const score = data.pillar_scores[pillar] || 0;
                        const isAbove = score >= (threshold as number);
                        
                        return (
                          <div key={pillar} className="benchmark-card">
                            <h5>{pillar.charAt(0).toUpperCase() + pillar.slice(1)}</h5>
                            <div className="benchmark-comparison">
                              <div className="benchmark-bar">
                                <div 
                                  className="threshold-line"
                                  style={{ left: `${(threshold as number) * 100}%` }}
                                >
                                  <span className="threshold-label">
                                    {Math.round((threshold as number) * 100)}%
                                  </span>
                                </div>
                                <div 
                                  className={`score-bar ${isAbove ? 'above' : 'below'}`}
                                  style={{ width: `${score * 100}%` }}
                                >
                                  <span className="score-label">
                                    {Math.round(score * 100)}%
                                  </span>
                                </div>
                              </div>
                              <p className={`benchmark-status ${isAbove ? 'pass' : 'fail'}`}>
                                {isAbove ? '✓ Above threshold' : '✗ Below threshold'}
                              </p>
                            </div>
                            <p className="benchmark-insight">
                              {getBenchmarkInsight(pillar, score, threshold as number, fundingStage)}
                            </p>
                          </div>
                        );
                      })}
                    </div>

                    <div className="peer-comparison">
                      <h4>Peer Comparison</h4>
                      <p>Based on {fundingStage.replace(/_/g, ' ')} stage startups in similar sectors:</p>
                      <div className="percentile-display">
                        <div className="percentile-bar">
                          <div 
                            className="percentile-marker"
                            style={{ left: `${data.success_probability * 100}%` }}
                          >
                            <span className="percentile-value">
                              {Math.round(data.success_probability * 100)}th percentile
                            </span>
                          </div>
                        </div>
                        <div className="percentile-labels">
                          <span>Bottom 25%</span>
                          <span>Median</span>
                          <span>Top 25%</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}

                {activeTab === 'recommendations' && (
                  <motion.div
                    key="recommendations"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="recommendations-tab"
                  >
                    <h3>Strategic Roadmap</h3>
                    
                    <div className="timeline-section">
                      <h4>Next 90 Days</h4>
                      <div className="recommendation-cards">
                        {getShortTermRecommendations(data, fundingStage).map((rec: any, i: number) => (
                          <div key={i} className="recommendation-card urgent">
                            <div className="rec-header">
                              <span className="priority-badge">High Priority</span>
                              <span className="timeline">0-3 months</span>
                            </div>
                            <h5>{rec.title}</h5>
                            <p>{rec.description}</p>
                            <div className="action-steps">
                              {rec.steps.map((step: string, j: number) => (
                                <div key={j} className="step">
                                  <span className="step-number">{j + 1}</span>
                                  {step}
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="timeline-section">
                      <h4>6-Month Goals</h4>
                      <div className="recommendation-cards">
                        {getMediumTermRecommendations(data, fundingStage).map((rec: any, i: number) => (
                          <div key={i} className="recommendation-card medium">
                            <div className="rec-header">
                              <span className="priority-badge">Medium Priority</span>
                              <span className="timeline">3-6 months</span>
                            </div>
                            <h5>{rec.title}</h5>
                            <p>{rec.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="success-metrics">
                      <h4>Success Metrics to Track</h4>
                      <div className="metrics-grid">
                        {getKeyMetrics(fundingStage).map((metric: any, i: number) => (
                          <div key={i} className="metric-card">
                            <span className="metric-icon">{metric.icon}</span>
                            <h5>{metric.name}</h5>
                            <p>{metric.target}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// Helper functions
function getStrengthDescription(pillar: string, score: number): string {
  const descriptions: Record<string, Record<string, string>> = {
    capital: {
      high: "Excellent financial management with strong unit economics",
      good: "Solid financial foundation with room for optimization"
    },
    advantage: {
      high: "Strong competitive moat and differentiation",
      good: "Good product differentiation with defensible position"
    },
    market: {
      high: "Large addressable market with strong growth dynamics",
      good: "Attractive market opportunity with proven demand"
    },
    people: {
      high: "World-class team with proven execution capability",
      good: "Strong team with relevant experience"
    }
  };
  
  const level = score >= 0.8 ? 'high' : 'good';
  return descriptions[pillar]?.[level] || "Strong performance in this area";
}

function getRiskDescription(pillar: string, stage: string): string {
  const descriptions: Record<string, string> = {
    capital: "Financial metrics below investor expectations for this stage",
    advantage: "Insufficient differentiation or competitive moat",
    market: "Market dynamics or size concerns",
    people: "Team gaps that need to be addressed"
  };
  return descriptions[pillar] || "Performance below stage requirements";
}

function getImprovementActions(pillar: string): string[] {
  const actions: Record<string, string[]> = {
    capital: [
      "Extend runway to 18+ months",
      "Improve gross margins by 10-15%",
      "Reduce CAC by optimizing channels"
    ],
    advantage: [
      "File provisional patents for core IP",
      "Increase switching costs",
      "Build network effects into product"
    ],
    market: [
      "Validate TAM with bottom-up analysis",
      "Reduce customer concentration below 30%",
      "Expand to adjacent segments"
    ],
    people: [
      "Hire senior technical talent",
      "Add industry advisors",
      "Strengthen board composition"
    ]
  };
  return actions[pillar] || ["Develop improvement plan"];
}

function getCompetitionLevel(intensity?: number): string {
  if (!intensity) return "Unknown";
  if (intensity <= 3) return "Low - Blue ocean opportunity";
  if (intensity <= 5) return "Moderate - Some competition";
  if (intensity <= 7) return "High - Crowded market";
  return "Very High - Consolidation phase";
}

function getBenchmarkInsight(pillar: string, score: number, threshold: number, stage: string): string {
  const gap = (threshold - score) * 100;
  if (score >= threshold) {
    return `Exceeds ${stage.replace(/_/g, ' ')} requirements by ${Math.abs(gap).toFixed(0)}%`;
  }
  return `Needs ${gap.toFixed(0)}% improvement to meet ${stage.replace(/_/g, ' ')} standards`;
}

function getShortTermRecommendations(data: any, stage: string): any[] {
  const recs = [];
  
  if (data.pillar_scores.capital < 0.4) {
    recs.push({
      title: "Secure Bridge Funding",
      description: "Critical capital needs must be addressed immediately",
      steps: [
        "Calculate exact runway with conservative estimates",
        "Prepare investor update with clear milestones",
        "Start conversations with existing investors"
      ]
    });
  }
  
  if (data.pillar_scores.advantage < 0.5) {
    recs.push({
      title: "Strengthen Competitive Position",
      description: "Build defensibility to attract investors",
      steps: [
        "Document unique technology advantages",
        "File IP protection where applicable",
        "Increase customer switching costs"
      ]
    });
  }
  
  return recs;
}

function getMediumTermRecommendations(data: any, stage: string): any[] {
  return [
    {
      title: "Scale Revenue Operations",
      description: "Build repeatable sales and marketing processes"
    },
    {
      title: "Strengthen Team",
      description: "Fill key roles and add strategic advisors"
    }
  ];
}

function getKeyMetrics(stage: string): any[] {
  const baseMetrics = [
    { icon: "📈", name: "MRR Growth", target: "15-20% MoM" },
    { icon: "💰", name: "Burn Multiple", target: "< 2x" },
    { icon: "🎯", name: "NPS Score", target: "> 50" }
  ];
  
  if (stage === 'series_a' || stage === 'series_b') {
    baseMetrics.push({ icon: "📊", name: "Net Revenue Retention", target: "> 120%" });
  }
  
  return baseMetrics;
}