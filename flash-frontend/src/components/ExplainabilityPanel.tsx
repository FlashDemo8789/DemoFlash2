import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart3,
  Info,
  Lightbulb,
  TrendingUp,
  TrendingDown,
  AlertTriangle
} from 'lucide-react';

interface ExplainabilityPanelProps {
  startupData: any;
  isDarkMode: boolean;
}

interface ExplanationData {
  prediction: any;
  explanation: {
    pillar_explanations: Record<string, any>;
    meta_explanation: any;
    plots: {
      meta_waterfall?: string;
      top_features?: string;
      pillar_radar?: string;
    };
    insights: {
      strengths: string[];
      weaknesses: string[];
      opportunities: string[];
      key_drivers: string[];
    };
  };
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({
  startupData,
  isDarkMode
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [explanation, setExplanation] = useState<ExplanationData | null>(null);
  const [activeTab, setActiveTab] = useState<'insights' | 'features' | 'pillars'>('insights');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (startupData) {
      fetchExplanation();
    }
  }, [startupData]);

  const fetchExplanation = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/explain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(startupData),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch explanation');
      }

      const data = await response.json();
      setExplanation(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const renderInsightsTab = () => {
    if (!explanation) return null;

    const { insights } = explanation.explanation;

    return (
      <div className="space-y-6">
        {/* Strengths */}
        {insights.strengths.length > 0 && (
          <div>
            <h3 className={`text-lg font-semibold mb-3 flex items-center gap-2 ${
              isDarkMode ? 'text-green-400' : 'text-green-600'
            }`}>
              <TrendingUp className="w-5 h-5" />
              Key Strengths
            </h3>
            <div className="space-y-2">
              {insights.strengths.map((strength, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className={`p-3 rounded-lg ${
                    isDarkMode ? 'bg-green-900/20 border border-green-800' : 'bg-green-50 border border-green-200'
                  }`}
                >
                  <p className={isDarkMode ? 'text-gray-200' : 'text-gray-700'}>
                    {strength}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Weaknesses */}
        {insights.weaknesses.length > 0 && (
          <div>
            <h3 className={`text-lg font-semibold mb-3 flex items-center gap-2 ${
              isDarkMode ? 'text-red-400' : 'text-red-600'
            }`}>
              <TrendingDown className="w-5 h-5" />
              Areas for Improvement
            </h3>
            <div className="space-y-2">
              {insights.weaknesses.map((weakness, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className={`p-3 rounded-lg ${
                    isDarkMode ? 'bg-red-900/20 border border-red-800' : 'bg-red-50 border border-red-200'
                  }`}
                >
                  <p className={isDarkMode ? 'text-gray-200' : 'text-gray-700'}>
                    {weakness}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Opportunities */}
        {insights.opportunities.length > 0 && (
          <div>
            <h3 className={`text-lg font-semibold mb-3 flex items-center gap-2 ${
              isDarkMode ? 'text-blue-400' : 'text-blue-600'
            }`}>
              <Lightbulb className="w-5 h-5" />
              Strategic Opportunities
            </h3>
            <div className="space-y-2">
              {insights.opportunities.map((opportunity, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className={`p-3 rounded-lg ${
                    isDarkMode ? 'bg-blue-900/20 border border-blue-800' : 'bg-blue-50 border border-blue-200'
                  }`}
                >
                  <p className={isDarkMode ? 'text-gray-200' : 'text-gray-700'}>
                    {opportunity}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Key Drivers */}
        {insights.key_drivers.length > 0 && (
          <div>
            <h3 className={`text-lg font-semibold mb-3 flex items-center gap-2 ${
              isDarkMode ? 'text-purple-400' : 'text-purple-600'
            }`}>
              <AlertTriangle className="w-5 h-5" />
              Key Decision Drivers
            </h3>
            <div className="space-y-2">
              {insights.key_drivers.map((driver, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className={`p-3 rounded-lg ${
                    isDarkMode ? 'bg-purple-900/20 border border-purple-800' : 'bg-purple-50 border border-purple-200'
                  }`}
                >
                  <p className={isDarkMode ? 'text-gray-200' : 'text-gray-700'}>
                    {driver}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderFeaturesTab = () => {
    if (!explanation || !explanation.explanation.plots.top_features) return null;

    return (
      <div className="space-y-6">
        <div>
          <h3 className={`text-lg font-semibold mb-3 ${
            isDarkMode ? 'text-gray-200' : 'text-gray-800'
          }`}>
            Top Feature Contributions
          </h3>
          <p className={`mb-4 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            This chart shows which features had the biggest impact on the prediction.
            Green bars increase success probability, red bars decrease it.
          </p>
          <div className={`p-4 rounded-xl ${
            isDarkMode ? 'bg-gray-800' : 'bg-gray-50'
          }`}>
            <img 
              src={explanation.explanation.plots.top_features} 
              alt="Top Features"
              className="w-full h-auto rounded-lg"
            />
          </div>
        </div>
      </div>
    );
  };

  const renderPillarsTab = () => {
    if (!explanation) return null;

    const { plots } = explanation.explanation;

    return (
      <div className="space-y-6">
        {plots.meta_waterfall && (
          <div>
            <h3 className={`text-lg font-semibold mb-3 ${
              isDarkMode ? 'text-gray-200' : 'text-gray-800'
            }`}>
              CAMP Pillar Contributions
            </h3>
            <p className={`mb-4 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              How each CAMP pillar contributes to the final prediction.
            </p>
            <div className={`p-4 rounded-xl ${
              isDarkMode ? 'bg-gray-800' : 'bg-gray-50'
            }`}>
              <img 
                src={plots.meta_waterfall} 
                alt="CAMP Waterfall"
                className="w-full h-auto rounded-lg"
              />
            </div>
          </div>
        )}

        {plots.pillar_radar && (
          <div>
            <h3 className={`text-lg font-semibold mb-3 ${
              isDarkMode ? 'text-gray-200' : 'text-gray-800'
            }`}>
              CAMP Pillar Scores
            </h3>
            <p className={`mb-4 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              Radar chart showing the relative strength of each pillar.
            </p>
            <div className={`p-4 rounded-xl ${
              isDarkMode ? 'bg-gray-800' : 'bg-gray-50'
            }`}>
              <img 
                src={plots.pillar_radar} 
                alt="CAMP Radar"
                className="w-full h-auto rounded-lg"
              />
            </div>
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 rounded-lg ${
        isDarkMode ? 'bg-red-900/20 text-red-400' : 'bg-red-50 text-red-600'
      }`}>
        <p>Error loading explanation: {error}</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-2xl p-6 ${
        isDarkMode ? 'bg-gray-800/50' : 'bg-white'
      } backdrop-blur-sm shadow-xl`}
    >
      <div className="flex items-center gap-2 mb-6">
        <BarChart3 className="w-6 h-6 text-blue-500" />
        <h2 className={`text-2xl font-bold ${
          isDarkMode ? 'text-white' : 'text-gray-900'
        }`}>
          AI Explanation
        </h2>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6">
        {[
          { id: 'insights', label: 'Insights', icon: Lightbulb },
          { id: 'features', label: 'Feature Impact', icon: BarChart3 },
          { id: 'pillars', label: 'CAMP Analysis', icon: Info },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab.id
                ? isDarkMode
                  ? 'bg-blue-600 text-white'
                  : 'bg-blue-500 text-white'
                : isDarkMode
                ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'insights' && renderInsightsTab()}
          {activeTab === 'features' && renderFeaturesTab()}
          {activeTab === 'pillars' && renderPillarsTab()}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
};