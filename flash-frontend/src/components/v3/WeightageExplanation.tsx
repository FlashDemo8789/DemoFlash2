import React from 'react';
import { motion } from 'framer-motion';
import './WeightageExplanation.css';

interface WeightageExplanationProps {
  currentStage: string;
  pillarScores: Record<string, number>;
}

export const WeightageExplanation: React.FC<WeightageExplanationProps> = ({ 
  currentStage, 
  pillarScores 
}) => {
  // Stage-specific weightings
  const stageWeights: Record<string, Record<string, number>> = {
    pre_seed: {
      people: 0.40,
      advantage: 0.30,
      market: 0.20,
      capital: 0.10
    },
    seed: {
      people: 0.30,
      advantage: 0.30,
      market: 0.25,
      capital: 0.15
    },
    series_a: {
      market: 0.30,
      people: 0.25,
      advantage: 0.25,
      capital: 0.20
    },
    series_b: {
      market: 0.35,
      capital: 0.25,
      advantage: 0.20,
      people: 0.20
    },
    series_c: {
      capital: 0.35,
      market: 0.30,
      people: 0.20,
      advantage: 0.15
    },
    growth: {
      capital: 0.35,
      market: 0.30,
      people: 0.20,
      advantage: 0.15
    }
  };

  const stageExplanations: Record<string, { focus: string; rationale: string; example: string }> = {
    pre_seed: {
      focus: "Team Quality (40%)",
      rationale: "At pre-seed, execution capability is everything. A great team can pivot, adapt, and find product-market fit.",
      example: "Example: Airbnb's founders were rejected by many VCs, but their persistence and execution skills turned a simple idea into a $75B company."
    },
    seed: {
      focus: "Team & Product Advantage (30% each)",
      rationale: "Balance between strong execution and unique product differentiation. Early traction validates the concept.",
      example: "Example: Stripe succeeded because the Collison brothers (team) built dramatically better payment APIs (advantage) than existing solutions."
    },
    series_a: {
      focus: "Market Opportunity (30%)",
      rationale: "Product-market fit must be proven. The market size and growth potential become critical for scaling.",
      example: "Example: Uber raised Series A after proving the ride-sharing market was massive and their model could scale beyond San Francisco."
    },
    series_b: {
      focus: "Market Dominance (35%)",
      rationale: "Focus shifts to capturing significant market share and proving scalable unit economics.",
      example: "Example: DoorDash's Series B focused on their path to market leadership and improving delivery economics."
    },
    series_c: {
      focus: "Capital Efficiency (35%)",
      rationale: "Path to profitability becomes paramount. Investors want to see sustainable business models.",
      example: "Example: Spotify's later rounds focused heavily on improving gross margins and reducing customer acquisition costs."
    },
    growth: {
      focus: "Capital Efficiency (35%)",
      rationale: "Must demonstrate clear path to profitability and efficient capital deployment for expansion.",
      example: "Example: Canva maintained high growth while achieving profitability, making it attractive for growth investors."
    }
  };

  const getPillarDescription = (pillar: string) => {
    const descriptions: Record<string, { title: string; metrics: string[] }> = {
      capital: {
        title: "Capital Efficiency",
        metrics: ["Burn rate vs. growth", "Runway length", "Revenue per dollar spent", "Gross margins", "LTV/CAC ratio"]
      },
      advantage: {
        title: "Competitive Advantage", 
        metrics: ["Patent portfolio", "Network effects", "Brand strength", "Switching costs", "Technical differentiation"]
      },
      market: {
        title: "Market Opportunity",
        metrics: ["TAM/SAM/SOM size", "Market growth rate", "Customer concentration", "Competitive landscape", "Market timing"]
      },
      people: {
        title: "Team Quality",
        metrics: ["Founder experience", "Domain expertise", "Previous exits", "Team completeness", "Advisory board"]
      }
    };
    return descriptions[pillar] || { title: pillar, metrics: [] };
  };

  const currentWeights = stageWeights[currentStage] || stageWeights.seed;
  const stageInfo = stageExplanations[currentStage] || stageExplanations.seed;

  // Calculate weighted score
  const weightedScore = Object.entries(pillarScores).reduce((sum, [pillar, score]) => {
    return sum + (score * (currentWeights[pillar] || 0));
  }, 0);

  return (
    <motion.div 
      className="weightage-explanation"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="explanation-header">
        <h2>How Your Score is Calculated</h2>
        <p className="explanation-subtitle">
          FLASH uses stage-specific weightings because different factors matter at different stages of growth
        </p>
      </div>

      {/* Current Stage Focus */}
      <div className="stage-focus-card">
        <div className="stage-badge">
          {currentStage.replace(/_/g, ' ').toUpperCase()}
        </div>
        <h3>{stageInfo.focus}</h3>
        <p className="stage-rationale">{stageInfo.rationale}</p>
        <div className="stage-example">
          <span className="example-icon">💡</span>
          <p>{stageInfo.example}</p>
        </div>
      </div>

      {/* Weightage Breakdown */}
      <div className="weightage-grid">
        {Object.entries(currentWeights)
          .sort((a, b) => b[1] - a[1])
          .map(([pillar, weight]) => {
            const score = pillarScores[pillar] || 0;
            const contribution = score * weight;
            const pillarInfo = getPillarDescription(pillar);
            
            return (
              <motion.div 
                key={pillar}
                className="weightage-card"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 }}
              >
                <div className="weightage-header">
                  <h4>{pillarInfo.title}</h4>
                  <div className="weight-badge">{Math.round(weight * 100)}% weight</div>
                </div>
                
                <div className="score-calculation">
                  <div className="score-parts">
                    <span className="part-label">Your Score</span>
                    <span className="part-value">{Math.round(score * 100)}%</span>
                  </div>
                  <span className="multiply">×</span>
                  <div className="score-parts">
                    <span className="part-label">Weight</span>
                    <span className="part-value">{Math.round(weight * 100)}%</span>
                  </div>
                  <span className="equals">=</span>
                  <div className="score-parts highlighted">
                    <span className="part-label">Contribution</span>
                    <span className="part-value">{(contribution * 100).toFixed(1)}%</span>
                  </div>
                </div>

                <div className="metrics-measured">
                  <p className="metrics-title">What we measure:</p>
                  <ul>
                    {pillarInfo.metrics.map((metric, i) => (
                      <li key={i}>{metric}</li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            );
          })}
      </div>

      {/* Final Calculation */}
      <div className="final-calculation">
        <h3>Your Final Weighted Score</h3>
        <div className="calculation-display">
          <span className="final-score">{(weightedScore * 100).toFixed(1)}%</span>
          <span className="score-description">
            Combined score across all weighted pillars
          </span>
        </div>
      </div>

      {/* Stage Progression */}
      <div className="stage-progression">
        <h3>How Weightings Change by Stage</h3>
        <div className="progression-chart">
          {Object.entries(stageWeights).map(([stage, weights]) => (
            <div 
              key={stage} 
              className={`stage-column ${stage === currentStage ? 'current' : ''}`}
            >
              <h4>{stage.replace(/_/g, ' ').toUpperCase()}</h4>
              <div className="weight-bars">
                {Object.entries(weights)
                  .sort((a, b) => b[1] - a[1])
                  .map(([pillar, weight]) => (
                    <div key={pillar} className="weight-bar">
                      <span className="pillar-label">
                        {pillar.charAt(0).toUpperCase() + pillar.slice(1)}
                      </span>
                      <div className="bar-container">
                        <div 
                          className="bar-fill"
                          style={{ width: `${weight * 100}%` }}
                        />
                        <span className="weight-label">{Math.round(weight * 100)}%</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Insights */}
      <div className="key-insights">
        <h3>Why This Matters</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <span className="insight-icon">🎯</span>
            <h4>Stage-Appropriate Focus</h4>
            <p>VCs evaluate startups differently at each stage. Our algorithm mirrors these real-world investment criteria.</p>
          </div>
          <div className="insight-card">
            <span className="insight-icon">⚖️</span>
            <h4>Balanced Assessment</h4>
            <p>No single factor determines success. The weightings ensure a holistic view appropriate to your stage.</p>
          </div>
          <div className="insight-card">
            <span className="insight-icon">📈</span>
            <h4>Growth Trajectory</h4>
            <p>Understanding how priorities shift helps you prepare for future funding rounds and scaling challenges.</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};