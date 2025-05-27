import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { StartupData } from '../../types';
import { generateTestStartupData, testScenarios } from '../../utils/testDataGenerator';
import './DataCollectionCAMP.css';

interface DataCollectionCAMPProps {
  onSubmit: (data: StartupData) => void;
  onBack: () => void;
}

const CAMP_PILLARS = {
  capital: {
    name: 'Capital',
    icon: 'C',
    description: 'Financial health, funding efficiency, and runway',
    fields: [
      'funding_stage',
      'total_capital_raised_usd',
      'cash_on_hand_usd',
      'monthly_burn_usd',
      'annual_revenue_run_rate',
      'revenue_growth_rate_percent',
      'gross_margin_percent',
      'ltv_cac_ratio',
      'investor_tier_primary',
      'has_debt'
    ]
  },
  advantage: {
    name: 'Advantage',
    icon: 'A',
    description: 'Competitive moat, technology, and differentiation',
    fields: [
      'patent_count',
      'network_effects_present',
      'has_data_moat',
      'regulatory_advantage_present',
      'tech_differentiation_score',
      'switching_cost_score',
      'brand_strength_score',
      'scalability_score',
      'product_stage',
      'product_retention_30d',
      'product_retention_90d'
    ]
  },
  market: {
    name: 'Market',
    icon: 'M',
    description: 'Market size, growth, and customer dynamics',
    fields: [
      'sector',
      'tam_size_usd',
      'sam_size_usd',
      'som_size_usd',
      'market_growth_rate_percent',
      'customer_count',
      'customer_concentration_percent',
      'user_growth_rate_percent',
      'net_dollar_retention_percent',
      'competition_intensity',
      'competitors_named_count',
      'dau_mau_ratio'
    ]
  },
  people: {
    name: 'People',
    icon: 'P',
    description: 'Team experience, composition, and leadership',
    fields: [
      'founders_count',
      'team_size_full_time',
      'years_experience_avg',
      'domain_expertise_years_avg',
      'prior_startup_experience_count',
      'prior_successful_exits_count',
      'board_advisor_experience_score',
      'advisors_count',
      'team_diversity_percent',
      'key_person_dependency'
    ]
  }
};

const FIELD_CONFIG: { [key: string]: { label: string; type: string; placeholder?: string; options?: string[]; min?: number; max?: number; step?: number } } = {
  // Capital fields
  funding_stage: { label: 'Funding Stage', type: 'select', options: ['Pre-seed', 'Seed', 'Series A', 'Series B', 'Series C'] },
  total_capital_raised_usd: { label: 'Total Capital Raised ($)', type: 'number', placeholder: '1000000', min: 0 },
  cash_on_hand_usd: { label: 'Cash on Hand ($)', type: 'number', placeholder: '500000', min: 0 },
  monthly_burn_usd: { label: 'Monthly Burn Rate ($)', type: 'number', placeholder: '50000', min: 0 },
  annual_revenue_run_rate: { label: 'Annual Revenue Run Rate ($)', type: 'number', placeholder: '1000000', min: 0 },
  revenue_growth_rate_percent: { label: 'Revenue Growth Rate (%)', type: 'number', placeholder: '100', min: -100, max: 1000 },
  gross_margin_percent: { label: 'Gross Margin (%)', type: 'number', placeholder: '70', min: -100, max: 100 },
  ltv_cac_ratio: { label: 'LTV/CAC Ratio', type: 'number', placeholder: '3', min: 0, max: 100, step: 0.1 },
  investor_tier_primary: { label: 'Primary Investor Tier', type: 'select', options: ['Tier 1', 'Tier 2', 'Tier 3', 'Angel'] },
  has_debt: { label: 'Has Debt Financing', type: 'boolean' },
  
  // Advantage fields
  patent_count: { label: 'Patent Count', type: 'number', placeholder: '0', min: 0 },
  network_effects_present: { label: 'Network Effects Present', type: 'boolean' },
  has_data_moat: { label: 'Has Data Moat', type: 'boolean' },
  regulatory_advantage_present: { label: 'Regulatory Advantage', type: 'boolean' },
  tech_differentiation_score: { label: 'Tech Differentiation (1-5)', type: 'number', placeholder: '3', min: 1, max: 5 },
  switching_cost_score: { label: 'Switching Cost (1-5)', type: 'number', placeholder: '3', min: 1, max: 5 },
  brand_strength_score: { label: 'Brand Strength (1-5)', type: 'number', placeholder: '3', min: 1, max: 5 },
  scalability_score: { label: 'Scalability Score (%)', type: 'number', placeholder: '70', min: 0, max: 100 },
  product_stage: { label: 'Product Stage', type: 'select', options: ['MVP', 'Beta', 'GA', 'Mature'] },
  product_retention_30d: { label: '30-Day Retention (%)', type: 'number', placeholder: '60', min: 0, max: 100 },
  product_retention_90d: { label: '90-Day Retention (%)', type: 'number', placeholder: '40', min: 0, max: 100 },
  
  // Market fields
  sector: { label: 'Industry Sector', type: 'text', placeholder: 'SaaS, Fintech, etc.' },
  tam_size_usd: { label: 'Total Addressable Market ($)', type: 'number', placeholder: '1000000000', min: 0 },
  sam_size_usd: { label: 'Serviceable Addressable Market ($)', type: 'number', placeholder: '100000000', min: 0 },
  som_size_usd: { label: 'Serviceable Obtainable Market ($)', type: 'number', placeholder: '10000000', min: 0 },
  market_growth_rate_percent: { label: 'Market Growth Rate (%)', type: 'number', placeholder: '20', min: -50, max: 200 },
  customer_count: { label: 'Customer Count', type: 'number', placeholder: '100', min: 0 },
  customer_concentration_percent: { label: 'Customer Concentration (%)', type: 'number', placeholder: '20', min: 0, max: 100 },
  user_growth_rate_percent: { label: 'User Growth Rate (%)', type: 'number', placeholder: '50', min: -100, max: 1000 },
  net_dollar_retention_percent: { label: 'Net Dollar Retention (%)', type: 'number', placeholder: '110', min: 0, max: 300 },
  competition_intensity: { label: 'Competition Intensity (1-5)', type: 'number', placeholder: '3', min: 1, max: 5 },
  competitors_named_count: { label: 'Number of Competitors', type: 'number', placeholder: '5', min: 0 },
  dau_mau_ratio: { label: 'DAU/MAU Ratio', type: 'number', placeholder: '0.5', min: 0, max: 1, step: 0.1 },
  
  // People fields
  founders_count: { label: 'Number of Founders', type: 'number', placeholder: '2', min: 1, max: 10 },
  team_size_full_time: { label: 'Full-Time Team Size', type: 'number', placeholder: '10', min: 0 },
  years_experience_avg: { label: 'Avg Years Experience', type: 'number', placeholder: '8', min: 0, max: 50 },
  domain_expertise_years_avg: { label: 'Avg Domain Expertise (years)', type: 'number', placeholder: '5', min: 0, max: 50 },
  prior_startup_experience_count: { label: 'Prior Startup Experience', type: 'number', placeholder: '1', min: 0 },
  prior_successful_exits_count: { label: 'Prior Successful Exits', type: 'number', placeholder: '0', min: 0 },
  board_advisor_experience_score: { label: 'Board/Advisor Experience (1-5)', type: 'number', placeholder: '3', min: 1, max: 5 },
  advisors_count: { label: 'Number of Advisors', type: 'number', placeholder: '3', min: 0 },
  team_diversity_percent: { label: 'Team Diversity (%)', type: 'number', placeholder: '40', min: 0, max: 100 },
  key_person_dependency: { label: 'Key Person Dependency', type: 'boolean' }
};

export const DataCollectionCAMP: React.FC<DataCollectionCAMPProps> = ({ onSubmit, onBack }) => {
  const [activePillar, setActivePillar] = useState<'capital' | 'advantage' | 'market' | 'people'>('capital');
  const [formData, setFormData] = useState<Partial<StartupData>>({});
  const [completedPillars, setCompletedPillars] = useState<Set<string>>(new Set());
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const handleFieldChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validatePillar = (pillar: string): boolean => {
    const fields = CAMP_PILLARS[pillar as keyof typeof CAMP_PILLARS].fields;
    const newErrors: { [key: string]: string } = {};
    
    fields.forEach(field => {
      const config = FIELD_CONFIG[field];
      const value = formData[field as keyof StartupData];
      
      // Required field check
      if (value === undefined || value === null || value === '') {
        newErrors[field] = 'Required';
      } else if (config.type === 'number') {
        const numValue = Number(value);
        if (isNaN(numValue)) {
          newErrors[field] = 'Must be a number';
        } else if (config.min !== undefined && numValue < config.min) {
          newErrors[field] = `Min: ${config.min}`;
        } else if (config.max !== undefined && numValue > config.max) {
          newErrors[field] = `Max: ${config.max}`;
        }
      }
    });
    
    setErrors(prev => ({ ...prev, ...newErrors }));
    return Object.keys(newErrors).length === 0;
  };

  const handlePillarComplete = () => {
    if (validatePillar(activePillar)) {
      setCompletedPillars(prev => new Set(prev).add(activePillar));
      
      // Auto-advance to next pillar
      const pillars = Object.keys(CAMP_PILLARS) as Array<keyof typeof CAMP_PILLARS>;
      const currentIndex = pillars.indexOf(activePillar);
      if (currentIndex < pillars.length - 1) {
        setActivePillar(pillars[currentIndex + 1]);
      }
    }
  };

  const handleSubmit = () => {
    // Validate all pillars
    const allValid = Object.keys(CAMP_PILLARS).every(pillar => validatePillar(pillar));
    
    if (allValid) {
      // Transform data to ensure correct types
      const transformedData: any = {};
      
      // Process each field with proper type conversion
      Object.entries(formData).forEach(([key, value]) => {
        const config = FIELD_CONFIG[key];
        if (config) {
          if (config.type === 'number') {
            let numValue = Number(value) || 0;
            
            // Convert percentage fields to decimals (0-1) for API
            if (key === 'product_retention_30d' || key === 'product_retention_90d' || key === 'scalability_score') {
              numValue = numValue / 100; // Convert percentage to decimal
            }
            
            transformedData[key] = numValue;
          } else if (config.type === 'boolean') {
            transformedData[key] = Boolean(value);
          } else {
            transformedData[key] = value;
          }
        } else {
          transformedData[key] = value;
        }
      });
      
      // Ensure all required fields have values
      const requiredDefaults = {
        // Capital
        revenue_growth_rate_percent: 0,
        ltv_cac_ratio: 0,
        
        // Advantage  
        patent_count: 0,
        
        // Market
        user_growth_rate_percent: 0,
        customer_concentration_percent: 20,
        
        // People
        team_diversity_percent: 40,
        advisors_count: 0
      };
      
      // Add calculated fields and defaults
      const completeData = {
        ...requiredDefaults,
        ...transformedData,
        runway_months: transformedData.cash_on_hand_usd && transformedData.monthly_burn_usd 
          ? Math.min(transformedData.cash_on_hand_usd / transformedData.monthly_burn_usd, 60) 
          : 12,
        burn_multiple: 2 // Will be calculated server-side
      } as StartupData;
      
      console.log('Submitting data:', completeData);
      onSubmit(completeData);
    }
  };

  const handleAutofill = () => {
    const testData = generateTestStartupData();
    setFormData(prev => ({ ...prev, ...testData }));
  };

  const handleScenarioFill = (scenario: 'best' | 'worst') => {
    const data = scenario === 'best' ? testScenarios.bestCase() : testScenarios.worstCase();
    setFormData(prev => ({ ...prev, ...data }));
  };

  const renderField = (fieldName: string) => {
    const config = FIELD_CONFIG[fieldName];
    const rawValue = formData[fieldName as keyof StartupData];
    const value = typeof rawValue === 'boolean' ? String(rawValue) : rawValue;
    const error = errors[fieldName];
    
    if (config.type === 'select') {
      return (
        <div className="field-group" key={fieldName}>
          <label>{config.label}</label>
          <select
            value={value || ''}
            onChange={(e) => handleFieldChange(fieldName, e.target.value)}
            className={error ? 'error' : ''}
          >
            <option value="">Select...</option>
            {config.options?.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
          {error && <span className="error-message">{error}</span>}
        </div>
      );
    }
    
    if (config.type === 'boolean') {
      return (
        <div className="field-group checkbox" key={fieldName}>
          <label>
            <input
              type="checkbox"
              checked={Boolean(rawValue)}
              onChange={(e) => handleFieldChange(fieldName, e.target.checked)}
            />
            {config.label}
          </label>
        </div>
      );
    }
    
    return (
      <div className="field-group" key={fieldName}>
        <label>{config.label}</label>
        <input
          type={config.type}
          value={value || ''}
          onChange={(e) => {
            const val = config.type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value;
            handleFieldChange(fieldName, val);
          }}
          placeholder={config.placeholder}
          min={config.min}
          max={config.max}
          step={config.step}
          className={error ? 'error' : ''}
        />
        {error && <span className="error-message">{error}</span>}
      </div>
    );
  };

  const pillar = CAMP_PILLARS[activePillar];
  const progress = (completedPillars.size / 4) * 100;

  return (
    <div className="data-collection-camp">
      <header className="camp-header">
        <button className="back-button" onClick={onBack}>←</button>
        
        <div className="camp-nav">
          {Object.entries(CAMP_PILLARS).map(([key, p]) => (
            <button
              key={key}
              className={`camp-pill ${activePillar === key ? 'active' : ''} ${completedPillars.has(key) ? 'completed' : ''}`}
              onClick={() => setActivePillar(key as any)}
            >
              <span className="camp-icon">{p.icon}</span>
              <span className="camp-label">{p.name}</span>
              {completedPillars.has(key) && <span className="check">✓</span>}
            </button>
          ))}
        </div>
        
        <div className="header-right">
          <div className="test-actions">
            <button 
              className="test-btn"
              onClick={handleAutofill}
              title="Fill with random test data"
            >
              🎲
            </button>
            <button 
              className="test-btn"
              onClick={() => handleScenarioFill('best')}
              title="Best case scenario"
            >
              ⬆
            </button>
            <button 
              className="test-btn"
              onClick={() => handleScenarioFill('worst')}
              title="Worst case scenario"
            >
              ⬇
            </button>
          </div>
          <div className="progress-indicator">
            {Math.round(progress)}% Complete
          </div>
        </div>
      </header>

      <div className="camp-content">
        <AnimatePresence mode="wait">
          <motion.div
            key={activePillar}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="pillar-section"
          >
            <div className="pillar-header">
              <h2>{pillar.name}</h2>
              <p>{pillar.description}</p>
            </div>
            
            <div className="fields-grid">
              {pillar.fields.map(field => renderField(field))}
            </div>
            
            <div className="pillar-actions">
              {!completedPillars.has(activePillar) ? (
                <button 
                  className="complete-button"
                  onClick={handlePillarComplete}
                >
                  Complete {pillar.name}
                </button>
              ) : (
                <div className="completed-message">
                  ✓ {pillar.name} Complete
                </div>
              )}
              
              {completedPillars.size === 4 && (
                <button 
                  className="analyze-button"
                  onClick={handleSubmit}
                >
                  Analyze Startup
                </button>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};