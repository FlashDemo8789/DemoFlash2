import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { DataCollectionCAMP } from './components/v3/DataCollectionCAMP';
import { AnalysisPage } from './components/v3/AnalysisPage';
import { WorldClassResults } from './components/v3/WorldClassResults';
import { StartupData, PredictionResult } from './types';
import './AppV3.css';

type AppState = 'landing' | 'collect' | 'analyze' | 'results';

function AppV3() {
  const [appState, setAppState] = useState<AppState>('landing');
  const [startupData, setStartupData] = useState<StartupData | null>(null);
  const [results, setResults] = useState<PredictionResult | null>(null);
  const [useAdvancedAPI, setUseAdvancedAPI] = useState(true);

  const handleDataSubmit = (data: StartupData) => {
    setStartupData(data);
    setAppState('analyze');
  };

  const handleAnalysisComplete = (analysisResults: PredictionResult) => {
    setResults(analysisResults);
    setAppState('results');
  };

  const resetApp = () => {
    setAppState('landing');
    setStartupData(null);
    setResults(null);
  };

  return (
    <div className="app-v3">
      <AnimatePresence mode="wait">
        {appState === 'landing' && (
          <motion.div
            key="landing"
            className="landing-page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="landing-content">
              <h1>FLASH</h1>
              <p className="tagline">Intelligent startup assessment powered by advanced ML</p>
              
              <div className="camp-grid">
                <div className="camp-feature">
                  <div className="camp-letter">C</div>
                  <h3>Capital</h3>
                  <p>Financial health, funding efficiency, and runway metrics</p>
                </div>
                <div className="camp-feature">
                  <div className="camp-letter">A</div>
                  <h3>Advantage</h3>
                  <p>Competitive moat, technology differentiation, and IP</p>
                </div>
                <div className="camp-feature">
                  <div className="camp-letter">M</div>
                  <h3>Market</h3>
                  <p>TAM, growth dynamics, and customer concentration</p>
                </div>
                <div className="camp-feature">
                  <div className="camp-letter">P</div>
                  <h3>People</h3>
                  <p>Team experience, composition, and advisory strength</p>
                </div>
              </div>
              
              <p className="metrics-note">45 data points • 11 ML models • Stage-specific evaluation</p>
              
              <div className="api-toggle">
                <label>
                  <input
                    type="checkbox"
                    checked={useAdvancedAPI}
                    onChange={(e) => setUseAdvancedAPI(e.target.checked)}
                  />
                  Use Advanced Analysis (DNA patterns, temporal predictions, industry insights)
                </label>
              </div>
              
              <button 
                className="start-button"
                onClick={() => setAppState('collect')}
              >
                Begin Assessment
              </button>
              
              <p className="disclaimer">
                For professional use only. Results are probabilistic, not guarantees.
              </p>
            </div>
          </motion.div>
        )}

        {appState === 'collect' && (
          <motion.div
            key="collect"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <DataCollectionCAMP
              onSubmit={handleDataSubmit}
              onBack={resetApp}
            />
          </motion.div>
        )}

        {appState === 'analyze' && startupData && (
          <motion.div
            key="analyze"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <AnalysisPage
              startupData={startupData}
              onComplete={handleAnalysisComplete}
              onBack={() => setAppState('collect')}
              useAdvancedAPI={useAdvancedAPI}
            />
          </motion.div>
        )}

        {appState === 'results' && results && (
          <motion.div
            key="results"
            className="results-page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <header className="results-header">
              <button className="back-button" onClick={resetApp}>
                ← New Analysis
              </button>
              <div className="header-actions">
                <button className="export-button">Export PDF</button>
                <button className="share-button">Share</button>
              </div>
            </header>
            
            <WorldClassResults data={results} />
            
            {/* Weightage Explanation - Moved to Full Analysis View */}
            {/* <WeightageExplanation 
              currentStage={startupData?.funding_stage || 'seed'}
              pillarScores={results.pillar_scores}
            /> */}
            
            {/* Additional insights section - Moved to Full Analysis View */}
            {/* <div className="detailed-insights">
              <h2>Detailed Analysis</h2>
              
              <div className="insight-grid">
                {results.critical_failures && results.critical_failures.length > 0 && (
                  <div className="insight-card critical">
                    <h3>Critical Issues</h3>
                    <ul>
                      {results.critical_failures.map((failure, i) => (
                        <li key={i}>{failure}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div className="insight-card">
                  <h3>Stage Benchmarks</h3>
                  <p>Your startup is being evaluated against {startupData?.funding_stage || 'Seed'} stage criteria.</p>
                  <div className="benchmark-list">
                    {Object.entries(results.stage_thresholds || {}).map(([pillar, threshold]) => (
                      <div key={pillar} className="benchmark-item">
                        <span className="benchmark-label">{pillar}</span>
                        <span className="benchmark-value">{Math.round(threshold * 100)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="insight-card">
                  <h3>Key Strengths</h3>
                  <ul>
                    {Object.entries(results.pillar_scores)
                      .filter(([_, score]) => score >= 0.7)
                      .map(([pillar, score]) => (
                        <li key={pillar}>
                          {pillar.charAt(0).toUpperCase() + pillar.slice(1)}: {Math.round(score * 100)}%
                        </li>
                      ))}
                  </ul>
                </div>
                
                <div className="insight-card">
                  <h3>Improvement Areas</h3>
                  <ul>
                    {results.below_threshold?.map((pillar, i) => (
                      <li key={i}>
                        {pillar.charAt(0).toUpperCase() + pillar.slice(1)} needs attention
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div> */}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default AppV3;