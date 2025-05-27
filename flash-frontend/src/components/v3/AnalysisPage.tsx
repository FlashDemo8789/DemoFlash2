import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnalysisOrb } from './AnalysisOrb';
import { WorldClassResults } from './WorldClassResults';
import './AnalysisPage.css';

interface AnalysisPageProps {
  startupData: any;
  onComplete: (results: any) => void;
  onBack: () => void;
  useAdvancedAPI?: boolean;
}

export const AnalysisPage: React.FC<AnalysisPageProps> = ({ 
  startupData, 
  onComplete,
  onBack,
  useAdvancedAPI = false 
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(true);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<any>(null);
  const [currentPhase, setCurrentPhase] = useState('Initializing');

  const phases = [
    'Sequencing startup DNA',
    'Analyzing capital genes',
    'Mapping market chromosomes',
    'Decoding team genetics',
    'Computing growth patterns',
    'Synthesizing insights',
    'Finalizing genome analysis'
  ];

  useEffect(() => {
    // Simulate analysis process
    let currentProgress = 0;
    let phaseIndex = 0;

    const progressInterval = setInterval(() => {
      currentProgress += 2;
      setProgress(currentProgress);

      // Update phase
      const newPhaseIndex = Math.floor((currentProgress / 100) * phases.length);
      if (newPhaseIndex !== phaseIndex && newPhaseIndex < phases.length) {
        phaseIndex = newPhaseIndex;
        setCurrentPhase(phases[phaseIndex]);
      }

      if (currentProgress >= 100) {
        clearInterval(progressInterval);
        performAnalysis();
      }
    }, 100);

    return () => clearInterval(progressInterval);
  }, []);

  const transformDataForAPI = (data: any) => {
    const transformed = { ...data };
    
    // Transform funding_stage
    if (transformed.funding_stage) {
      transformed.funding_stage = transformed.funding_stage
        .toLowerCase()
        .replace(/-/g, '_')
        .replace(/\s+/g, '_')
        .replace('series_a+', 'series_c')
        .replace('series_b+', 'series_c')
        .replace('series_c+', 'series_c');
    }
    
    // Transform investor_tier_primary
    if (transformed.investor_tier_primary) {
      const tierMap: Record<string, string> = {
        'angel': 'none',
        'tier 1': 'tier_1',
        'tier 2': 'tier_2',
        'tier 3': 'tier_3',
        'none': 'none'
      };
      transformed.investor_tier_primary = tierMap[transformed.investor_tier_primary.toLowerCase()] || 'none';
    }
    
    // Transform scalability_score from 0-1 to 1-5
    if (typeof transformed.scalability_score === 'number' && transformed.scalability_score <= 1) {
      transformed.scalability_score = 1 + (transformed.scalability_score * 4);
    }
    
    // Transform product_stage
    if (transformed.product_stage) {
      transformed.product_stage = transformed.product_stage.toLowerCase();
    }
    
    return transformed;
  };

  const performAnalysis = async () => {
    try {
      const apiData = transformDataForAPI(startupData);
      console.log('Sending data to API:', apiData);
      
      const endpoint = useAdvancedAPI ? 'http://localhost:8000/predict_advanced' : 'http://localhost:8000/predict';
      console.log(`Using ${useAdvancedAPI ? 'advanced' : 'standard'} API endpoint`);
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(apiData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', response.status, errorData);
        throw new Error(`API Error: ${response.status} - ${JSON.stringify(errorData)}`);
      }
      
      const data = await response.json();
      console.log('API Response:', data);
      
      setTimeout(() => {
        setIsAnalyzing(false);
        setResults(data);
        onComplete(data);
      }, 500);
    } catch (error) {
      console.error('Analysis error:', error);
      setIsAnalyzing(false);
      // Show error state instead of crashing
      setResults(null);
    }
  };

  return (
    <div className="analysis-page">
      <AnimatePresence mode="wait">
        {isAnalyzing ? (
          <motion.div
            key="analyzing"
            className="analysis-container"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <AnalysisOrb 
              isAnalyzing={true} 
              progress={progress}
            />
            
            <motion.div 
              className="phase-indicator"
              key={currentPhase}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              {currentPhase}
            </motion.div>
          </motion.div>
        ) : results ? (
          <motion.div
            key="results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <WorldClassResults data={results} />
          </motion.div>
        ) : (
          <motion.div
            key="error"
            className="error-state"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <p>Unable to complete analysis</p>
            <button onClick={onBack}>Try Again</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};