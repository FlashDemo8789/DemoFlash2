import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './styles/theme.css';
import './App.css';
import LandingPage from './components/LandingPage';
import DataCollection from './components/DataCollection';
import ResultsPage from './components/ResultsPage';
import SimpleResults from './components/SimpleResults';
import { StartupData, PredictionResult } from './types';

type AppState = 'landing' | 'collection' | 'analyzing' | 'results';

function App() {
  const [appState, setAppState] = useState<AppState>('landing');
  const [startupData, setStartupData] = useState<Partial<StartupData>>({});
  const [results, setResults] = useState<PredictionResult | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

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
      // Call the API
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Prediction failed');
      }

      const result = await response.json();
      console.log('API Response:', result);
      console.log('Pillar scores:', result.pillar_scores);
      setResults(result);
      setAppState('results');
    } catch (error) {
      console.error('Error:', error);
      // Handle error - show error state
      setAppState('collection');
    }
  };

  const handleBackToHome = () => {
    setAppState('landing');
    setStartupData({});
    setResults(null);
  };

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <div className="app">
      {/* Theme Toggle */}
      <button 
        className="theme-toggle"
        onClick={toggleTheme}
        aria-label="Toggle theme"
      >
        {theme === 'light' ? '🌙' : '☀️'}
      </button>

      <AnimatePresence mode="wait">
        {appState === 'landing' && (
          <motion.div
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <LandingPage onStart={handleStartAnalysis} />
          </motion.div>
        )}

        {appState === 'collection' && (
          <motion.div
            key="collection"
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.5, ease: 'easeInOut' }}
          >
            <DataCollection 
              onSubmit={handleDataSubmit}
              onBack={handleBackToHome}
            />
          </motion.div>
        )}

        {appState === 'analyzing' && (
          <motion.div
            key="analyzing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="analyzing-container"
          >
            <div className="analyzing-content">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="analyzing-spinner"
              />
              <h2>Analyzing your startup...</h2>
              <p>Our AI is evaluating 45 key metrics across 4 pillars</p>
            </div>
          </motion.div>
        )}

        {appState === 'results' && results && (
          <motion.div
            key="results"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.5 }}
          >
            <>
              {console.log('Rendering ResultsPage with results:', results)}
              <SimpleResults results={results} />
              <ResultsPage 
                results={results}
                startupData={startupData}
                onBack={handleBackToHome}
                isDarkMode={theme === 'dark'}
              />
            </>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;