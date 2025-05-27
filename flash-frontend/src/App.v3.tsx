import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import LandingPageV2 from './components/v2/LandingPageV2';
import DataCollectionV2 from './components/v2/DataCollectionV2';
import ResultsRouter from './components/ResultsRouter';
import { AnalysisOrb } from './components/v3/AnalysisOrb';
import './App.v2.css';

type AppState = 'landing' | 'collection' | 'analyzing' | 'results';

const AppV3: React.FC = () => {
  const [appState, setAppState] = useState<AppState>('landing');
  const [startupData, setStartupData] = useState<any>({});
  const [results, setResults] = useState<any>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [useAdvancedAPI, setUseAdvancedAPI] = useState(true); // Toggle for advanced API

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const handleStartAnalysis = () => {
    setAppState('collection');
  };

  const handleDataSubmit = async (data: any) => {
    setStartupData(data);
    setAppState('analyzing');
    
    try {
      console.log('Sending data to API:', data);
      
      // Choose endpoint based on toggle or check if advanced endpoint exists
      const endpoint = useAdvancedAPI ? 
        'http://localhost:8000/predict_advanced' : 
        'http://localhost:8000/predict';
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        // Fallback to standard endpoint if advanced fails
        if (useAdvancedAPI && response.status === 404) {
          console.log('Advanced endpoint not found, falling back to standard');
          const standardResponse = await fetch('http://localhost:8000/predict', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          });
          
          if (!standardResponse.ok) {
            const errorData = await standardResponse.json();
            throw new Error(`Prediction failed: ${JSON.stringify(errorData)}`);
          }
          
          const result = await standardResponse.json();
          setResults(result);
        } else {
          const errorData = await response.json();
          console.error('API Error:', errorData);
          throw new Error(`Prediction failed: ${JSON.stringify(errorData)}`);
        }
      } else {
        const result = await response.json();
        setResults(result);
      }
      
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

  const toggleAdvancedAPI = () => {
    setUseAdvancedAPI(prev => !prev);
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

      {/* Advanced API Toggle (for development) */}
      {process.env.NODE_ENV === 'development' && (
        <motion.button
          className="api-toggle"
          onClick={toggleAdvancedAPI}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            padding: '10px 20px',
            borderRadius: '20px',
            background: useAdvancedAPI ? '#00ff88' : '#888',
            color: '#000',
            border: 'none',
            cursor: 'pointer',
            fontSize: '0.9rem',
            fontWeight: 600,
            zIndex: 1000
          }}
        >
          {useAdvancedAPI ? 'Advanced API' : 'Standard API'}
        </motion.button>
      )}

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
              <AnalysisOrb isAnalyzing={true} />
              <motion.h2
                className="analyzing-text-v2"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                Analyzing your startup...
              </motion.h2>
              <motion.p
                className="analyzing-subtext-v2"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                {useAdvancedAPI ? 
                  'Running advanced AI models including DNA pattern analysis...' :
                  'Our AI is evaluating 45 key metrics across 4 pillars'
                }
              </motion.p>
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
            <ResultsRouter results={results} onBack={handleBackToHome} isDarkMode={theme === 'dark'} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AppV3;