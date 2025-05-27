import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import * as Tabs from '@radix-ui/react-tabs';
import { ArrowLeft, ArrowRight, Check } from 'lucide-react';
import { StartupData, Pillar, PILLAR_NAMES, PILLAR_DESCRIPTIONS } from '../types';
import CapitalForm from './forms/CapitalForm';
import AdvantageForm from './forms/AdvantageForm';
import MarketForm from './forms/MarketForm';
import PeopleForm from './forms/PeopleForm';
import './DataCollection.css';

interface DataCollectionProps {
  onSubmit: (data: StartupData) => void;
  onBack: () => void;
}

const DataCollection: React.FC<DataCollectionProps> = ({ onSubmit, onBack }) => {
  const [activeTab, setActiveTab] = useState<Pillar>('capital');
  const [formData, setFormData] = useState<Partial<StartupData>>({});
  const [completedPillars, setCompletedPillars] = useState<Set<Pillar>>(new Set());

  const pillars: Pillar[] = ['capital', 'advantage', 'market', 'people'];
  const currentIndex = pillars.indexOf(activeTab);
  const progress = ((completedPillars.size / pillars.length) * 100);

  const updateFormData = (pillar: Pillar, data: Partial<StartupData>) => {
    setFormData(prev => ({ ...prev, ...data }));
    setCompletedPillars(prev => {
      const newSet = new Set(prev);
      newSet.add(pillar);
      return newSet;
    });
  };

  const handleNext = () => {
    if (currentIndex < pillars.length - 1) {
      setActiveTab(pillars[currentIndex + 1]);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setActiveTab(pillars[currentIndex - 1]);
    }
  };

  const handleSubmit = () => {
    // Validate all required fields are filled
    if (completedPillars.size === pillars.length) {
      console.log('Submitting form data:', formData);
      console.log('Data being sent to API:', JSON.stringify(formData, null, 2));
      onSubmit(formData as StartupData);
    }
  };

  const isLastPillar = currentIndex === pillars.length - 1;
  const isFirstPillar = currentIndex === 0;

  return (
    <div className="collection-container">
      <div className="collection-header">
        <button className="back-button" onClick={onBack}>
          <ArrowLeft size={20} />
          Back
        </button>
        
        <div className="progress-indicator">
          <div className="progress-bar">
            <motion.div 
              className="progress-bar-fill"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
          <span className="progress-text">{Math.round(progress)}% Complete</span>
        </div>
      </div>

      <div className="collection-content">
        <h1 className="collection-title">Tell us about your startup</h1>
        
        <Tabs.Root value={activeTab} onValueChange={(value) => setActiveTab(value as Pillar)}>
          <Tabs.List className="tabs-list">
            {pillars.map((pillar) => (
              <Tabs.Trigger
                key={pillar}
                value={pillar}
                className={`tab-trigger ${completedPillars.has(pillar) ? 'completed' : ''}`}
              >
                <span className="tab-letter">{PILLAR_NAMES[pillar][0]}</span>
                <span className="tab-name">{PILLAR_NAMES[pillar]}</span>
                {completedPillars.has(pillar) && (
                  <Check size={16} className="tab-check" />
                )}
              </Tabs.Trigger>
            ))}
          </Tabs.List>

          <div className="tab-content-wrapper">
            <AnimatePresence mode="wait">
              <Tabs.Content value="capital" key="capital">
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="pillar-description">
                    {PILLAR_DESCRIPTIONS.capital}
                  </div>
                  <CapitalForm
                    data={formData}
                    onUpdate={(data) => updateFormData('capital', data)}
                  />
                </motion.div>
              </Tabs.Content>

              <Tabs.Content value="advantage" key="advantage">
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="pillar-description">
                    {PILLAR_DESCRIPTIONS.advantage}
                  </div>
                  <AdvantageForm
                    data={formData}
                    onUpdate={(data) => updateFormData('advantage', data)}
                  />
                </motion.div>
              </Tabs.Content>

              <Tabs.Content value="market" key="market">
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="pillar-description">
                    {PILLAR_DESCRIPTIONS.market}
                  </div>
                  <MarketForm
                    data={formData}
                    onUpdate={(data) => updateFormData('market', data)}
                  />
                </motion.div>
              </Tabs.Content>

              <Tabs.Content value="people" key="people">
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="pillar-description">
                    {PILLAR_DESCRIPTIONS.people}
                  </div>
                  <PeopleForm
                    data={formData}
                    onUpdate={(data) => updateFormData('people', data)}
                  />
                </motion.div>
              </Tabs.Content>
            </AnimatePresence>
          </div>
        </Tabs.Root>

        <div className="navigation-buttons">
          <button
            className="button button-secondary"
            onClick={handlePrevious}
            disabled={isFirstPillar}
          >
            <ArrowLeft size={20} />
            Previous
          </button>

          {!isLastPillar ? (
            <button
              className="button button-primary"
              onClick={handleNext}
            >
              Next
              <ArrowRight size={20} />
            </button>
          ) : (
            <button
              className="button button-primary"
              onClick={handleSubmit}
              disabled={completedPillars.size < pillars.length}
            >
              Analyze Startup
              <Check size={20} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataCollection;