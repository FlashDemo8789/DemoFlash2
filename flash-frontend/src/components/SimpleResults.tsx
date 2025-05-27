import React from 'react';

interface SimpleResultsProps {
  results: any;
}

const SimpleResults: React.FC<SimpleResultsProps> = ({ results }) => {
  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0', margin: '20px', borderRadius: '8px' }}>
      <h2>Simple Results Component</h2>
      <div style={{ backgroundColor: 'white', padding: '10px', borderRadius: '4px', marginBottom: '10px' }}>
        <h3>Raw Results Object:</h3>
        <pre>{JSON.stringify(results, null, 2)}</pre>
      </div>
      
      {results && results.pillar_scores && (
        <div style={{ backgroundColor: 'white', padding: '10px', borderRadius: '4px' }}>
          <h3>CAMP Scores:</h3>
          <ul>
            <li>Capital: {(results.pillar_scores.capital * 100).toFixed(1)}%</li>
            <li>Advantage: {(results.pillar_scores.advantage * 100).toFixed(1)}%</li>
            <li>Market: {(results.pillar_scores.market * 100).toFixed(1)}%</li>
            <li>People: {(results.pillar_scores.people * 100).toFixed(1)}%</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default SimpleResults;