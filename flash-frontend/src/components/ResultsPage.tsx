import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Download, TrendingUp, AlertCircle } from 'lucide-react';
import { PredictionResult, PILLAR_NAMES } from '../types';
import { ExplainabilityPanel } from './ExplainabilityPanel';
import './ResultsPage.css';

interface ResultsPageProps {
  results: PredictionResult;
  startupData?: any;
  onBack: () => void;
  isDarkMode?: boolean;
}

const ResultsPage: React.FC<ResultsPageProps> = ({ results, startupData, onBack, isDarkMode = false }) => {
  console.log('ResultsPage received results:', results);
  console.log('Pillar scores in results:', results.pillar_scores);
  const successPercentage = Math.round(results.success_probability * 100);
  const isHighProbability = successPercentage >= 70;
  
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'Low Risk': return 'var(--color-success)';
      case 'Medium Risk': return 'var(--color-warning)';
      case 'High Risk': return 'var(--color-danger)';
      default: return 'var(--color-danger)';
    }
  };

  const handleDownloadReport = () => {
    // TODO: Implement PDF download
    console.log('Download report');
  };

  return (
    <div className="results-container">
      <div className="results-header">
        <button className="back-button" onClick={onBack}>
          <ArrowLeft size={20} />
          Back to Home
        </button>
      </div>

      <motion.div 
        className="results-content"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Success Probability */}
        <div className="probability-section">
          <h1 className="results-title">Your Startup Analysis</h1>
          
          <motion.div 
            className="probability-circle"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <svg width="200" height="200" viewBox="0 0 200 200">
              <circle
                cx="100"
                cy="100"
                r="90"
                fill="none"
                stroke="var(--color-surface)"
                strokeWidth="10"
              />
              <motion.circle
                cx="100"
                cy="100"
                r="90"
                fill="none"
                stroke={isHighProbability ? 'var(--color-success)' : 'var(--color-primary)'}
                strokeWidth="10"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 90}`}
                strokeDashoffset={`${2 * Math.PI * 90 * (1 - results.success_probability)}`}
                transform="rotate(-90 100 100)"
                initial={{ strokeDashoffset: `${2 * Math.PI * 90}` }}
                animate={{ strokeDashoffset: `${2 * Math.PI * 90 * (1 - results.success_probability)}` }}
                transition={{ duration: 1.5, delay: 0.3, ease: 'easeOut' }}
              />
            </svg>
            <div className="probability-text">
              <span className="probability-number">{successPercentage}%</span>
              <span className="probability-label">Success Probability</span>
            </div>
          </motion.div>

          <div className="confidence-interval">
            Confidence Interval: {Math.round(results.confidence_interval.lower * 100)}% - {Math.round(results.confidence_interval.upper * 100)}%
          </div>

          <div className="risk-badge" style={{ color: getRiskColor(results.risk_level) }}>
            <AlertCircle size={20} />
            {results.risk_level}
          </div>
        </div>

        {/* AI Insights */}
        <motion.div 
          className="insights-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <h2>AI Insights</h2>
          <p className="recommendation">{results.recommendation}</p>
          
          <div className="key-insights">
            <h3>Key Findings</h3>
            <ul>
              {results.key_insights.map((insight, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                >
                  {insight}
                </motion.li>
              ))}
            </ul>
          </div>
        </motion.div>

        {/* Pillar Scores */}
        <motion.div 
          className="pillars-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <h2>CAMP Analysis</h2>
          <div className="pillar-scores">
            {results && results.pillar_scores && Object.keys(results.pillar_scores).length > 0 ? (
              Object.entries(results.pillar_scores).map(([pillar, score], index) => (
              <motion.div
                key={pillar}
                className="pillar-score"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.7 + index * 0.1 }}
              >
                <div className="pillar-header">
                  <span className="pillar-name">{PILLAR_NAMES[pillar as keyof typeof PILLAR_NAMES]}</span>
                  <span className="pillar-value">{Math.round(score * 100)}%</span>
                </div>
                <div className="pillar-bar">
                  <motion.div
                    className="pillar-bar-fill"
                    style={{ backgroundColor: score >= 0.7 ? 'var(--color-success)' : score >= 0.5 ? 'var(--color-warning)' : 'var(--color-danger)' }}
                    initial={{ width: 0 }}
                    animate={{ width: `${score * 100}%` }}
                    transition={{ duration: 0.8, delay: 0.8 + index * 0.1 }}
                  />
                </div>
              </motion.div>
            ))
            ) : (
              <div style={{padding: '20px', textAlign: 'center', color: '#666'}}>
                <p>No pillar scores available</p>
                <p style={{fontSize: '12px', marginTop: '10px'}}>
                  Results object: {results ? 'exists' : 'null'}<br/>
                  Pillar scores: {results?.pillar_scores ? 'exists' : 'null'}<br/>
                  Keys: {results?.pillar_scores ? Object.keys(results.pillar_scores).join(', ') : 'none'}
                </p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Explainability Panel */}
        {startupData && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 1.2 }}
          >
            <ExplainabilityPanel 
              startupData={startupData} 
              isDarkMode={isDarkMode} 
            />
          </motion.div>
        )}

        {/* Action Buttons */}
        <motion.div 
          className="action-buttons"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 1 }}
        >
          <button className="button button-secondary" onClick={onBack}>
            <TrendingUp size={20} />
            Analyze Another
          </button>
          <button className="button button-primary" onClick={handleDownloadReport}>
            <Download size={20} />
            Download Report
          </button>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default ResultsPage;