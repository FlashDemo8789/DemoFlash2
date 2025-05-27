import React from 'react';
import ResultsPageV2 from './v2/ResultsPageV2';
import AdvancedResultsPage from './v3/AdvancedResultsPage';

interface ResultsRouterProps {
  results: any;
  onBack?: () => void;
  isDarkMode?: boolean;
}

const ResultsRouter: React.FC<ResultsRouterProps> = ({ results, onBack, isDarkMode = true }) => {
  // Check if results contain advanced model features
  const hasAdvancedFeatures = !!(
    results.dna_pattern || 
    results.temporal_predictions || 
    results.industry_insights ||
    results.stage_prediction ||
    results.trajectory ||
    results.recommendations
  );

  // Use advanced results page if advanced features are present
  if (hasAdvancedFeatures) {
    return <AdvancedResultsPage results={results} />;
  }

  // Otherwise use the existing V2 results page
  return <ResultsPageV2 results={results} onBack={onBack || (() => window.location.reload())} isDarkMode={isDarkMode} />;
};

export default ResultsRouter;