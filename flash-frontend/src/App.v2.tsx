import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './styles/theme.v2.css';
import './App.v2.css';
import LandingPageV2 from './components/v2/LandingPageV2';
import DataCollectionV2 from './components/v2/DataCollectionV2';
import ResultsPageV2 from './components/v2/ResultsPageV2';
import { StartupData, PredictionResult } from './types';

type AppState = 'landing' | 'collection' | 'analyzing' | 'results';

function AppV2() {
  const [appState, setAppState] = useState<AppState>('landing');
  const [startupData, setStartupData] = useState<Partial<StartupData>>({});
  const [results, setResults] = useState<PredictionResult | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark'); // Default to dark for revolutionary feel

  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const handleStartAnalysis = () => {
    setAppState('collection');
  };

  const handleDataSubmit = async (data: StartupData) => {
    setStartupData(data);
    setAppState('analyzing');
    
    try {
      console.log('Sending data to API:', data);
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', errorData);
        throw new Error(`Prediction failed: ${JSON.stringify(errorData)}`);
      }

      const result = await response.json();
      setResults(result);
      
      // Smooth transition to results
      setTimeout(() => {
        setAppState('results');
      }, 2000);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to analyze startup. Please check console for details.');
      setAppState('collection');
    }
  };

  const handleBackToHome = () => {
    setAppState('landing');
    setStartupData({});
    setResults(null);
  };

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <div className="app-v2">
      {/* Theme Toggle */}
      <motion.button
        className="theme-toggle-v2"
        onClick={toggleTheme}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        {theme === 'light' ? '🌙' : '☀️'}
      </motion.button>

      <AnimatePresence mode="wait">
        {appState === 'landing' && (
          <motion.div
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <LandingPageV2 
              onStart={handleStartAnalysis}
              isDarkMode={theme === 'dark'}
            />
          </motion.div>
        )}

        {appState === 'collection' && (
          <motion.div
            key="collection"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <DataCollectionV2
              onSubmit={handleDataSubmit}
              onBack={handleBackToHome}
              isDarkMode={theme === 'dark'}
            />
          </motion.div>
        )}

        {appState === 'analyzing' && (
          <motion.div
            key="analyzing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="analyzing-container-v2"
          >
            <div className="analyzing-content-v2">
              <motion.div className="ai-brain">
                <motion.div
                  className="brain-wave wave-1"
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                <motion.div
                  className="brain-wave wave-2"
                  animate={{ scale: [1, 1.8, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
                />
                <motion.div
                  className="brain-wave wave-3"
                  animate={{ scale: [1, 2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
                />
                <div className="brain-core">🧠</div>
              </motion.div>
              
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                AI is analyzing your startup...
              </motion.h2>
              
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7 }}
              >
                Processing 45 key metrics across 4 pillars
              </motion.p>
              
              <motion.div
                className="processing-steps"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
              >
                <motion.div
                  className="step"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  Evaluating Capital Health...
                </motion.div>
                <motion.div
                  className="step"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity, delay: 0.3 }}
                >
                  Analyzing Competitive Advantage...
                </motion.div>
                <motion.div
                  className="step"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity, delay: 0.6 }}
                >
                  Assessing Market Opportunity...
                </motion.div>
                <motion.div
                  className="step"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity, delay: 0.9 }}
                >
                  Reviewing Team Strength...
                </motion.div>
              </motion.div>
            </div>
          </motion.div>
        )}

        {appState === 'results' && results && (
          <motion.div
            key="results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <ResultsPageV2 
              results={results}
              onBack={handleBackToHome}
              isDarkMode={theme === 'dark'}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default AppV2;