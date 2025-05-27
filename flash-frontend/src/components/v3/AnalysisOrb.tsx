import React, { useEffect, useRef } from 'react';
import { motion, useAnimationFrame } from 'framer-motion';
import './AnalysisOrb.css';

interface AnalysisOrbProps {
  isAnalyzing: boolean;
  progress?: number;
  pillarData?: {
    capital: number;
    advantage: number;
    market: number;
    people: number;
  };
}

export const AnalysisOrb: React.FC<AnalysisOrbProps> = ({ 
  isAnalyzing, 
  progress = 0,
  pillarData 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const timeRef = useRef(0);
  const dataPointsRef = useRef<number[]>([]);

  useAnimationFrame((time, delta) => {
    if (!canvasRef.current || !isAnalyzing) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Update time
    timeRef.current += delta * 0.001;
    
    // Draw the analysis visualization
    drawAnalysisPattern(ctx, canvas.width, canvas.height, timeRef.current, pillarData);
  });

  const drawAnalysisPattern = (
    ctx: CanvasRenderingContext2D, 
    width: number, 
    height: number, 
    time: number,
    data?: any
  ) => {
    const centerX = width / 2;
    const centerY = height / 2;
    
    // DNA Helix parameters
    const helixHeight = 200;
    const helixWidth = 60;
    const numPoints = 30;
    const rotationSpeed = time * 0.5;
    
    // Clear with subtle glow effect
    const glowGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 120);
    glowGradient.addColorStop(0, 'rgba(59, 130, 246, 0.03)');
    glowGradient.addColorStop(1, 'rgba(59, 130, 246, 0)');
    ctx.fillStyle = glowGradient;
    ctx.fillRect(0, 0, width, height);
    
    // Draw DNA double helix
    for (let strand = 0; strand < 2; strand++) {
      const phaseShift = strand * Math.PI;
      
      ctx.beginPath();
      for (let i = 0; i <= numPoints; i++) {
        const t = i / numPoints;
        const y = centerY - helixHeight/2 + t * helixHeight;
        const angle = rotationSpeed + t * Math.PI * 4 + phaseShift;
        const x = centerX + Math.cos(angle) * helixWidth;
        const z = Math.sin(angle);
        
        // Apply perspective (closer points are larger)
        const scale = 0.8 + z * 0.2;
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      
      // Gradient for depth
      const strandGradient = ctx.createLinearGradient(centerX - helixWidth, 0, centerX + helixWidth, 0);
      strandGradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
      strandGradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.6)');
      strandGradient.addColorStop(1, 'rgba(59, 130, 246, 0.3)');
      
      ctx.strokeStyle = strandGradient;
      ctx.lineWidth = 3;
      ctx.stroke();
    }
    
    // Draw connecting base pairs
    const basePairCount = 8;
    for (let i = 0; i < basePairCount; i++) {
      const t = (i + 0.5) / basePairCount;
      const y = centerY - helixHeight/2 + t * helixHeight;
      const angle1 = rotationSpeed + t * Math.PI * 4;
      const angle2 = angle1 + Math.PI;
      
      const x1 = centerX + Math.cos(angle1) * helixWidth;
      const x2 = centerX + Math.cos(angle2) * helixWidth;
      const z = Math.sin(angle1);
      
      // Only draw front-facing base pairs
      if (z > -0.3) {
        ctx.beginPath();
        ctx.moveTo(x1, y);
        ctx.lineTo(x2, y);
        
        // Fade based on depth
        const alpha = 0.2 + z * 0.3;
        ctx.strokeStyle = `rgba(59, 130, 246, ${alpha})`;
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Draw nucleotide points
        const nucleotideSize = 3 + z * 1;
        ctx.fillStyle = `rgba(59, 130, 246, ${0.6 + z * 0.4})`;
        
        ctx.beginPath();
        ctx.arc(x1, y, nucleotideSize, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(x2, y, nucleotideSize, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    
    // Add flowing data particles along the helix
    const particleCount = 15;
    for (let i = 0; i < particleCount; i++) {
      const particleTime = (time * 0.8 + i * 0.4) % 1;
      const y = centerY - helixHeight/2 + particleTime * helixHeight;
      const angle = rotationSpeed + particleTime * Math.PI * 4;
      const x = centerX + Math.cos(angle) * (helixWidth + 10);
      
      const particleAlpha = 0.8 * (1 - Math.abs(particleTime - 0.5) * 2);
      ctx.fillStyle = `rgba(59, 130, 246, ${particleAlpha})`;
      ctx.beginPath();
      ctx.arc(x, y, 2, 0, Math.PI * 2);
      ctx.fill();
    }
  };

  return (
    <div className="analysis-orb-container">
      <canvas
        ref={canvasRef}
        width={300}
        height={350}
        className="analysis-canvas"
      />
      
      {isAnalyzing && (
        <motion.div 
          className="analysis-status"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <div className="status-text">Analyzing startup DNA</div>
          {progress > 0 && (
            <div className="progress-indicator">
              <div 
                className="progress-bar" 
                style={{ width: `${progress}%` }}
              />
            </div>
          )}
        </motion.div>
      )}
      
      {pillarData && !isAnalyzing && (
        <motion.div 
          className="analysis-complete"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="complete-icon">✓</div>
          <div className="complete-text">Analysis complete</div>
        </motion.div>
      )}
    </div>
  );
};

// Enhanced result display component with advanced features
export const MinimalResults: React.FC<{ data: any }> = ({ data }) => {
  if (!data || !data.pillar_scores) {
    return (
      <div className="minimal-results error">
        <p>Unable to display results. Please try again.</p>
      </div>
    );
  }

  // Check if this is an advanced response
  const hasAdvancedFeatures = !!(
    data.stage_prediction || 
    data.dna_pattern || 
    data.temporal_predictions || 
    data.industry_insights
  );

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return '#00ff88';
    if (score >= 0.6) return '#ffbb00';
    if (score >= 0.4) return '#ff8800';
    return '#ff0055';
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
    <motion.div 
      className="minimal-results"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* Primary verdict */}
      <div className="verdict-section">
        <h1 className="probability" style={{ color: getScoreColor(data.success_probability || 0) }}>
          {Math.round((data.success_probability || 0) * 100)}%
        </h1>
        <p className="verdict-text">{data.verdict || 'PENDING'}</p>
        {data.confidence_score && (
          <p className="confidence-score">Confidence: {Math.round(data.confidence_score * 100)}%</p>
        )}
      </div>
      
      {/* DNA Pattern if available */}
      {data.dna_pattern && (
        <div className="dna-section">
          <div className="dna-label">Startup DNA: {data.dna_pattern.pattern_type?.toUpperCase()}</div>
          <p className="dna-description">{getDNAPatternDescription(data.dna_pattern.pattern_type)}</p>
        </div>
      )}

      {/* Temporal predictions if available */}
      {data.temporal_predictions && (
        <div className="temporal-grid">
          <div className="temporal-item">
            <span className="temporal-label">6 months:</span>
            <span className="temporal-value" style={{ color: getScoreColor(data.temporal_predictions.short_term || 0.5) }}>
              {Math.round((data.temporal_predictions.short_term || 0.5) * 100)}%
            </span>
          </div>
          <div className="temporal-item">
            <span className="temporal-label">12 months:</span>
            <span className="temporal-value" style={{ color: getScoreColor(data.temporal_predictions.medium_term || 0.5) }}>
              {Math.round((data.temporal_predictions.medium_term || 0.5) * 100)}%
            </span>
          </div>
          <div className="temporal-item">
            <span className="temporal-label">18+ months:</span>
            <span className="temporal-value" style={{ color: getScoreColor(data.temporal_predictions.long_term || 0.5) }}>
              {Math.round((data.temporal_predictions.long_term || 0.5) * 100)}%
            </span>
          </div>
        </div>
      )}
      
      {/* Key metrics in clean grid */}
      <div className="metrics-grid">
        {data.pillar_scores && Object.entries(data.pillar_scores).map(([key, value]) => (
          <div key={key} className="metric">
            <div className="metric-value" style={{ color: getScoreColor(value as number) }}>
              {((value as number) * 100).toFixed(0)}
            </div>
            <div className="metric-label">{key}</div>
            <div className="metric-indicator">
              <div 
                className="indicator-fill" 
                style={{ 
                  width: `${(value as number) * 100}%`,
                  backgroundColor: getScoreColor(value as number)
                }}
              />
            </div>
          </div>
        ))}
      </div>
      
      {/* Insights as clean prose */}
      {data.key_insights && data.key_insights.length > 0 && (
        <div className="insights-section">
          {data.key_insights.slice(0, 3).map((insight: string, i: number) => (
            <p key={i} className="insight">{insight.replace(/[📊🚀💰👥⚠️✅🎯]/g, '')}</p>
          ))}
        </div>
      )}

      {/* Industry insights if available */}
      {data.industry_insights && data.industry_insights.relative_performance && (
        <div className="industry-section">
          <p className="industry-performance">
            Industry Performance: <strong>{data.industry_insights.relative_performance}</strong>
          </p>
        </div>
      )}
      
      {/* Actions with advanced mode indicator */}
      <div className="action-section">
        <button className="primary-action">
          Export Analysis
        </button>
        <button className="secondary-action">
          View Details
        </button>
        {hasAdvancedFeatures && (
          <span className="advanced-badge">Advanced Analysis</span>
        )}
      </div>
    </motion.div>
  );
};