import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { StartupData } from '../../types';
import './Forms.css';

interface AdvantageFormProps {
  data: Partial<StartupData>;
  onUpdate: (data: Partial<StartupData>) => void;
}

const AdvantageForm: React.FC<AdvantageFormProps> = ({ data, onUpdate }) => {
  const [formData, setFormData] = useState({
    patent_count: data.patent_count || 0,
    network_effects_present: data.network_effects_present || false,
    has_data_moat: data.has_data_moat || false,
    regulatory_advantage_present: data.regulatory_advantage_present || false,
    tech_differentiation_score: data.tech_differentiation_score || 3,
    switching_cost_score: data.switching_cost_score || 3,
    brand_strength_score: data.brand_strength_score || 3,
    scalability_score: data.scalability_score || 0.5,
    product_stage: data.product_stage || 'Beta',
    product_retention_30d: data.product_retention_30d || 0.5,
    product_retention_90d: data.product_retention_90d || 0.3,
  });

  useEffect(() => {
    onUpdate(formData);
  }, [formData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' 
        ? (e.target as HTMLInputElement).checked 
        : type === 'number' 
        ? parseFloat(value) || 0
        : value
    }));
  };

  const handleRangeChange = (name: string, value: number) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <motion.div
      className="form-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="form-grid">
        {/* Patent Count */}
        <div className="form-group">
          <label htmlFor="patent_count">Patent Count</label>
          <input
            type="number"
            id="patent_count"
            name="patent_count"
            value={formData.patent_count}
            onChange={handleChange}
            className="input"
            min="0"
            max="100"
          />
        </div>

        {/* Product Stage */}
        <div className="form-group">
          <label htmlFor="product_stage">Product Stage</label>
          <select
            id="product_stage"
            name="product_stage"
            value={formData.product_stage}
            onChange={handleChange}
            className="input"
          >
            <option value="Concept">Concept</option>
            <option value="Beta">Beta</option>
            <option value="GA">General Availability</option>
          </select>
        </div>

        {/* Tech Differentiation Score */}
        <div className="form-group form-group-full">
          <label htmlFor="tech_differentiation_score">
            Tech Differentiation Score: {formData.tech_differentiation_score.toFixed(1)}
          </label>
          <input
            type="range"
            id="tech_differentiation_score"
            name="tech_differentiation_score"
            value={formData.tech_differentiation_score}
            onChange={(e) => handleRangeChange('tech_differentiation_score', parseFloat(e.target.value))}
            className="range-slider"
            min="1"
            max="5"
            step="0.1"
          />
          <div className="range-value">
            <span>Low</span>
            <span>High</span>
          </div>
        </div>

        {/* Switching Cost Score */}
        <div className="form-group form-group-full">
          <label htmlFor="switching_cost_score">
            Switching Cost Score: {formData.switching_cost_score.toFixed(1)}
          </label>
          <input
            type="range"
            id="switching_cost_score"
            name="switching_cost_score"
            value={formData.switching_cost_score}
            onChange={(e) => handleRangeChange('switching_cost_score', parseFloat(e.target.value))}
            className="range-slider"
            min="1"
            max="5"
            step="0.1"
          />
          <div className="range-value">
            <span>Low</span>
            <span>High</span>
          </div>
        </div>

        {/* Brand Strength Score */}
        <div className="form-group form-group-full">
          <label htmlFor="brand_strength_score">
            Brand Strength Score: {formData.brand_strength_score.toFixed(1)}
          </label>
          <input
            type="range"
            id="brand_strength_score"
            name="brand_strength_score"
            value={formData.brand_strength_score}
            onChange={(e) => handleRangeChange('brand_strength_score', parseFloat(e.target.value))}
            className="range-slider"
            min="1"
            max="5"
            step="0.1"
          />
          <div className="range-value">
            <span>Weak</span>
            <span>Strong</span>
          </div>
        </div>

        {/* Scalability Score */}
        <div className="form-group form-group-full">
          <label htmlFor="scalability_score">
            Scalability Score: {(formData.scalability_score * 100).toFixed(0)}%
          </label>
          <input
            type="range"
            id="scalability_score"
            name="scalability_score"
            value={formData.scalability_score}
            onChange={(e) => handleRangeChange('scalability_score', parseFloat(e.target.value))}
            className="range-slider"
            min="0"
            max="1"
            step="0.01"
          />
          <div className="range-value">
            <span>Low</span>
            <span>High</span>
          </div>
        </div>

        {/* Product Retention 30d */}
        <div className="form-group">
          <label htmlFor="product_retention_30d">
            30-Day Retention: {(formData.product_retention_30d * 100).toFixed(0)}%
          </label>
          <input
            type="range"
            id="product_retention_30d"
            name="product_retention_30d"
            value={formData.product_retention_30d}
            onChange={(e) => handleRangeChange('product_retention_30d', parseFloat(e.target.value))}
            className="range-slider"
            min="0"
            max="1"
            step="0.01"
          />
        </div>

        {/* Product Retention 90d */}
        <div className="form-group">
          <label htmlFor="product_retention_90d">
            90-Day Retention: {(formData.product_retention_90d * 100).toFixed(0)}%
          </label>
          <input
            type="range"
            id="product_retention_90d"
            name="product_retention_90d"
            value={formData.product_retention_90d}
            onChange={(e) => handleRangeChange('product_retention_90d', parseFloat(e.target.value))}
            className="range-slider"
            min="0"
            max="1"
            step="0.01"
          />
        </div>

        {/* Competitive Advantages */}
        <div className="form-group form-group-full">
          <label>Competitive Advantages</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="network_effects_present"
                checked={formData.network_effects_present}
                onChange={handleChange}
                className="checkbox"
              />
              <span>Network Effects Present</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="has_data_moat"
                checked={formData.has_data_moat}
                onChange={handleChange}
                className="checkbox"
              />
              <span>Has Data Moat</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="regulatory_advantage_present"
                checked={formData.regulatory_advantage_present}
                onChange={handleChange}
                className="checkbox"
              />
              <span>Regulatory Advantage</span>
            </label>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default AdvantageForm;