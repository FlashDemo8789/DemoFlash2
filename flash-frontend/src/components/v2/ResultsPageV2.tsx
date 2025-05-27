import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion';
import { PredictionResult } from '../../types';
import './ResultsPageV2.css';

interface ResultsPageV2Props {
  results: PredictionResult;
  onBack: () => void;
  isDarkMode: boolean;
}

// Animated Success Meter
const SuccessMeter: React.FC<{ probability: number }> = ({ probability }) => {
  const percentage = Math.round(probability * 100);
  const rotation = useMotionValue(0);
  const scale = useTransform(rotation, [0, 360], [1, 1.2]);
  
  useEffect(() => {
    rotation.set(percentage * 3.6);
  }, [percentage, rotation]);
  
  return (
    <div className="success-meter">
      <svg viewBox="0 0 200 200" className="meter-svg">
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#667eea" />
            <stop offset="100%" stopColor="#764ba2" />
          </linearGradient>
        </defs>
        
        <circle
          cx="100"
          cy="100"
          r="90"
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth="20"
        />
        
        <motion.circle
          cx="100"
          cy="100"
          r="90"
          fill="none"
          stroke="url(#gradient)"
          strokeWidth="20"
          strokeLinecap="round"
          strokeDasharray={`${percentage * 5.65} 565`}
          initial={{ strokeDashoffset: 565 }}
          animate={{ strokeDashoffset: 0 }}
          transition={{ duration: 2, ease: "easeInOut" }}
          style={{ transform: 'rotate(-90deg)', transformOrigin: 'center' }}
        />
      </svg>
      
      <motion.div 
        className="meter-content"
        style={{ scale }}
      >
        <motion.div
          className="percentage-display"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <span className="percentage-value">{percentage}</span>
          <span className="percentage-symbol">%</span>
        </motion.div>
        <motion.p
          className="success-label"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          Success Probability
        </motion.p>
      </motion.div>
    </div>
  );
};

// CAMP Pillar Card with Animation
const PillarCard: React.FC<{
  name: string;
  score: number;
  icon: string;
  color: string;
  delay: number;
  threshold?: number;
}> = ({ name, score, icon, color, delay, threshold = 0.5 }) => {
  const percentage = Math.round(score * 100);
  const thresholdPercent = Math.round(threshold * 100);
  
  return (
    <motion.div
      className="pillar-card-v2"
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      whileHover={{ y: -10, boxShadow: `0 20px 40px ${color}33` }}
    >
      <div className="pillar-header-v2">
        <span className="pillar-icon-v2">{icon}</span>
        <h3>{name}</h3>
      </div>
      
      <div className="pillar-score-v2">
        <motion.div
          className="score-ring"
          style={{ borderColor: color }}
        >
          <motion.div
            className="score-fill"
            style={{ background: color }}
            initial={{ height: 0 }}
            animate={{ height: `${percentage}%` }}
            transition={{ delay: delay + 0.3, duration: 1, ease: "easeOut" }}
          />
          <span className="score-text">{percentage}%</span>
        </motion.div>
      </div>
      
      <div className="pillar-insight">
        {percentage >= 70 ? '✅ Strong' : percentage >= thresholdPercent ? '⚠️ Moderate' : '🚨 Critical'}
      </div>
      
      {/* Stage threshold indicator */}
      <div className="threshold-info">
        Stage threshold: {thresholdPercent}%
      </div>
      
      {/* Pass/Fail indicator based on stage threshold */}
      <div className={`pillar-status ${score >= threshold ? 'pass' : 'fail'}`}>
        {score >= threshold ? 'PASS' : 'NEEDS WORK'}
      </div>
    </motion.div>
  );
};

// Insights Panel with Typewriter Effect
const InsightsPanel: React.FC<{ insights: string[] }> = ({ insights }) => {
  const [visibleInsights, setVisibleInsights] = useState<string[]>([]);
  
  useEffect(() => {
    insights.forEach((insight, index) => {
      setTimeout(() => {
        setVisibleInsights(prev => [...prev, insight]);
      }, index * 500);
    });
  }, [insights]);
  
  return (
    <motion.div
      className="insights-panel-v2"
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 1 }}
    >
      <h2>
        <span className="insights-icon">💡</span>
        Key Insights
      </h2>
      <AnimatePresence>
        {visibleInsights.map((insight, index) => (
          <motion.div
            key={index}
            className="insight-item-v2"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <span className="insight-bullet">→</span>
            <span className="insight-text">{insight}</span>
          </motion.div>
        ))}
      </AnimatePresence>
    </motion.div>
  );
};

// Risk Level Badge
const RiskBadge: React.FC<{ level: string }> = ({ level }) => {
  const getColor = () => {
    switch (level) {
      case 'Low Risk': return '#10b981';
      case 'Medium Risk': return '#f59e0b';
      case 'High Risk': return '#ef4444';
      default: return '#6b7280';
    }
  };
  
  return (
    <motion.div
      className="risk-badge-v2"
      style={{ borderColor: getColor(), color: getColor() }}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ delay: 0.8, type: "spring" }}
    >
      <span className="risk-icon">⚡</span>
      {level}
    </motion.div>
  );
};

const ResultsPageV2: React.FC<ResultsPageV2Props> = ({ results, onBack, isDarkMode }) => {
  const [showActions, setShowActions] = useState(false);
  
  useEffect(() => {
    setTimeout(() => setShowActions(true), 2000);
  }, []);
  
  const pillars = [
    { name: 'Capital', score: results.pillar_scores.capital, icon: '💰', color: '#10b981', threshold: results.stage_thresholds?.capital || 0.5 },
    { name: 'Advantage', score: results.pillar_scores.advantage, icon: '🚀', color: '#3b82f6', threshold: results.stage_thresholds?.advantage || 0.5 },
    { name: 'Market', score: results.pillar_scores.market, icon: '🌍', color: '#f59e0b', threshold: results.stage_thresholds?.market || 0.5 },
    { name: 'People', score: results.pillar_scores.people, icon: '👥', color: '#8b5cf6', threshold: results.stage_thresholds?.people || 0.5 }
  ];
  
  return (
    <div className="results-page-v2">
      {/* Animated Background */}
      <div className="animated-bg">
        <div className="gradient-orb orb-1" />
        <div className="gradient-orb orb-2" />
        <div className="gradient-orb orb-3" />
      </div>
      
      {/* Header */}
      <motion.header
        className="results-header-v2"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <button className="back-btn-v2" onClick={onBack}>
          ← Back to Home
        </button>
        
        <motion.div
          className="share-actions"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
        >
          <button className="share-btn">
            <span>📤</span> Share
          </button>
          <button className="download-btn">
            <span>📥</span> Download Report
          </button>
        </motion.div>
      </motion.header>
      
      {/* Main Content */}
      <div className="results-content-v2">
        {/* Success Meter Section */}
        <motion.section
          className="meter-section"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <SuccessMeter probability={results.success_probability} />
          
          {/* Final Pass/Fail Score */}
          <motion.div
            className={`final-verdict ${results.verdict === 'PASS' ? 'pass' : results.verdict === 'CONDITIONAL PASS' ? 'conditional' : 'fail'}`}
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 1.5, type: "spring", stiffness: 200 }}
          >
            <div className="verdict-icon">
              {results.verdict === 'PASS' ? '✅' : results.verdict === 'CONDITIONAL PASS' ? '⚠️' : '❌'}
            </div>
            <div className="verdict-text">
              {results.verdict || 'PENDING'}
            </div>
            <div className="verdict-subtitle">
              {results.verdict === 'PASS' && results.strength === 'STRONG' && 'Excellent position - ready to scale'}
              {results.verdict === 'PASS' && results.strength !== 'STRONG' && 'Good foundation with room to grow'}
              {results.verdict === 'CONDITIONAL PASS' && `${results.below_threshold?.length || 0} pillar(s) below stage threshold`}
              {results.verdict === 'FAIL' && results.critical_failures?.length > 0 && `Critical: ${results.critical_failures[0]}`}
              {results.verdict === 'FAIL' && !results.critical_failures?.length && `${results.below_threshold?.length || 0} pillars need significant improvement`}
            </div>
            {results.weighted_score && (
              <div className="weighted-score">
                Weighted Score: {Math.round(results.weighted_score * 100)}%
              </div>
            )}
          </motion.div>
          
          <RiskBadge level={results.risk_level} />
          
          <motion.div
            className="confidence-range"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
          >
            <span>Confidence Interval:</span>
            <strong>
              {Math.round(results.confidence_interval.lower * 100)}% - 
              {Math.round(results.confidence_interval.upper * 100)}%
            </strong>
          </motion.div>
        </motion.section>
        
        {/* CAMP Pillars Grid */}
        <motion.section className="pillars-grid-v2">
          {pillars.map((pillar, index) => (
            <PillarCard
              key={pillar.name}
              {...pillar}
              delay={0.5 + index * 0.1}
            />
          ))}
        </motion.section>
        
        {/* Insights and Recommendation */}
        <div className="insights-recommendation-grid">
          <InsightsPanel insights={results.key_insights} />
          
          <motion.div
            className="recommendation-panel-v2"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2 }}
          >
            <h2>
              <span className="recommendation-icon">🎯</span>
              AI Recommendation
            </h2>
            <p className="recommendation-text">{results.recommendation}</p>
            
            <AnimatePresence>
              {showActions && (
                <motion.div
                  className="action-items"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <h3>Next Steps:</h3>
                  <ul>
                    <li>Focus on strengthening weak pillars</li>
                    <li>Schedule strategic planning session</li>
                    <li>Connect with advisors in key areas</li>
                  </ul>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
        
        {/* Action Buttons */}
        <AnimatePresence>
          {showActions && (
            <motion.div
              className="results-actions-v2"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 50 }}
            >
              <motion.button
                className="action-btn-v2 secondary"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onBack}
              >
                Analyze Another Startup
              </motion.button>
              
              <motion.button
                className="action-btn-v2 primary"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Get Detailed Report →
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ResultsPageV2;