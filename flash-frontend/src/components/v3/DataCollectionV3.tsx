import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { StartupData } from '../../types';
import './DataCollectionV3.css';

interface DataCollectionV3Props {
  onSubmit: (data: StartupData) => void;
  onBack: () => void;
}

const SECTIONS = [
  {
    id: 'basics',
    title: 'Basic Information',
    fields: ['funding_stage', 'sector', 'team_size_full_time', 'founders_count']
  },
  {
    id: 'financial',
    title: 'Financial Metrics',
    fields: ['total_capital_raised_usd', 'annual_revenue_run_rate', 'monthly_burn_usd', 'gross_margin_percent']
  },
  {
    id: 'market',
    title: 'Market Position',
    fields: ['tam_size_usd', 'customer_count', 'market_growth_rate_percent', 'net_dollar_retention_percent']
  },
  {
    id: 'product',
    title: 'Product & Team',
    fields: ['product_stage', 'product_retention_30d', 'years_experience_avg', 'tech_differentiation_score']
  }
];

const FIELD_LABELS: { [key: string]: string } = {
  funding_stage: 'Funding Stage',
  sector: 'Industry Sector',
  team_size_full_time: 'Team Size',
  founders_count: 'Number of Founders',
  total_capital_raised_usd: 'Total Capital Raised',
  annual_revenue_run_rate: 'Annual Revenue Run Rate',
  monthly_burn_usd: 'Monthly Burn Rate',
  gross_margin_percent: 'Gross Margin %',
  tam_size_usd: 'Total Addressable Market',
  customer_count: 'Customer Count',
  market_growth_rate_percent: 'Market Growth Rate %',
  net_dollar_retention_percent: 'Net Dollar Retention %',
  product_stage: 'Product Stage',
  product_retention_30d: '30-Day Retention %',
  years_experience_avg: 'Average Years Experience',
  tech_differentiation_score: 'Tech Differentiation (1-5)'
};

export const DataCollectionV3: React.FC<DataCollectionV3Props> = ({ onSubmit, onBack }) => {
  const [currentSection, setCurrentSection] = useState(0);
  const [formData, setFormData] = useState<Partial<StartupData>>({});
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const handleFieldChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateSection = (): boolean => {
    const section = SECTIONS[currentSection];
    const newErrors: { [key: string]: string } = {};
    
    section.fields.forEach(field => {
      if (!formData[field as keyof StartupData]) {
        newErrors[field] = 'This field is required';
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateSection()) {
      if (currentSection < SECTIONS.length - 1) {
        setCurrentSection(prev => prev + 1);
      } else {
        // Submit with all required defaults
        const completeData = {
          ...formData,
          // Add all required fields with defaults
          runway_months: 12,
          burn_multiple: 2,
          ltv_cac_ratio: 3,
          investor_tier_primary: 'Tier 2',
          has_debt: false,
          patent_count: 0,
          network_effects_present: false,
          has_data_moat: false,
          regulatory_advantage_present: false,
          switching_cost_score: 3,
          brand_strength_score: 3,
          scalability_score: 0.7,
          product_retention_90d: (formData.product_retention_30d || 50) * 0.8,
          sam_size_usd: (formData.tam_size_usd || 1000000000) * 0.1,
          som_size_usd: (formData.tam_size_usd || 1000000000) * 0.01,
          customer_concentration_percent: 20,
          user_growth_rate_percent: 50,
          competition_intensity: 3,
          competitors_named_count: 5,
          dau_mau_ratio: 0.5,
          domain_expertise_years_avg: formData.years_experience_avg || 5,
          prior_startup_experience_count: 1,
          prior_successful_exits_count: 0,
          board_advisor_experience_score: 3,
          advisors_count: 3,
          team_diversity_percent: 40,
          key_person_dependency: true,
          cash_on_hand_usd: 1000000,
          revenue_growth_rate_percent: 100
        } as StartupData;
        
        onSubmit(completeData);
      }
    }
  };

  const handlePrevious = () => {
    if (currentSection > 0) {
      setCurrentSection(prev => prev - 1);
    } else {
      onBack();
    }
  };

  const renderField = (field: string) => {
    const rawValue = formData[field as keyof StartupData];
    const value = typeof rawValue === 'boolean' ? rawValue.toString() : rawValue;
    const error = errors[field];
    
    // Special handling for select fields
    if (field === 'funding_stage') {
      return (
        <div className="field-group" key={field}>
          <label htmlFor={field}>{FIELD_LABELS[field]}</label>
          <select
            id={field}
            value={value || ''}
            onChange={(e) => handleFieldChange(field, e.target.value)}
            className={error ? 'error' : ''}
          >
            <option value="">Select stage</option>
            <option value="Pre-seed">Pre-seed</option>
            <option value="Seed">Seed</option>
            <option value="Series A">Series A</option>
            <option value="Series B">Series B</option>
            <option value="Series C">Series C</option>
          </select>
          {error && <span className="error-message">{error}</span>}
        </div>
      );
    }
    
    if (field === 'product_stage') {
      return (
        <div className="field-group" key={field}>
          <label htmlFor={field}>{FIELD_LABELS[field]}</label>
          <select
            id={field}
            value={value || ''}
            onChange={(e) => handleFieldChange(field, e.target.value)}
            className={error ? 'error' : ''}
          >
            <option value="">Select stage</option>
            <option value="MVP">MVP</option>
            <option value="Beta">Beta</option>
            <option value="GA">General Availability</option>
            <option value="Mature">Mature</option>
          </select>
          {error && <span className="error-message">{error}</span>}
        </div>
      );
    }
    
    // Default to input field
    const inputType = field.includes('percent') || field.includes('score') ? 'number' : 
                     field.includes('usd') || field.includes('count') || field.includes('size') ? 'number' : 
                     'text';
    
    return (
      <div className="field-group" key={field}>
        <label htmlFor={field}>{FIELD_LABELS[field]}</label>
        <input
          id={field}
          type={inputType}
          value={value || ''}
          onChange={(e) => {
            const val = inputType === 'number' ? parseFloat(e.target.value) || 0 : e.target.value;
            handleFieldChange(field, val);
          }}
          className={error ? 'error' : ''}
          placeholder={inputType === 'number' ? '0' : ''}
        />
        {error && <span className="error-message">{error}</span>}
      </div>
    );
  };

  const section = SECTIONS[currentSection];
  const progress = ((currentSection + 1) / SECTIONS.length) * 100;

  return (
    <div className="data-collection-v3">
      {/* Clean header */}
      <header className="collection-header">
        <button className="back-button" onClick={handlePrevious}>
          ←
        </button>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress}%` }}
          />
        </div>
      </header>

      {/* Form content */}
      <div className="form-container">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentSection}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="form-section"
          >
            <h2>{section.title}</h2>
            <p className="section-description">
              {currentSection === 0 && "Let's start with some basic information about your startup."}
              {currentSection === 1 && "Help us understand your financial position and runway."}
              {currentSection === 2 && "Tell us about your market opportunity and traction."}
              {currentSection === 3 && "Share details about your product and team."}
            </p>
            
            <div className="fields-grid">
              {section.fields.map(field => renderField(field))}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Actions */}
        <div className="form-actions">
          <button 
            className="secondary-button"
            onClick={handlePrevious}
          >
            {currentSection === 0 ? 'Cancel' : 'Previous'}
          </button>
          <button 
            className="primary-button"
            onClick={handleNext}
          >
            {currentSection === SECTIONS.length - 1 ? 'Analyze' : 'Continue'}
          </button>
        </div>
      </div>

      {/* Section indicators */}
      <div className="section-indicators">
        {SECTIONS.map((_, index) => (
          <div 
            key={index}
            className={`indicator ${index === currentSection ? 'active' : ''} ${index < currentSection ? 'completed' : ''}`}
          />
        ))}
      </div>
    </div>
  );
};