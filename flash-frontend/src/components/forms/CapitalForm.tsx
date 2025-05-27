import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { StartupData } from '../../types';
import './Forms.css';

interface CapitalFormProps {
  data: Partial<StartupData>;
  onUpdate: (data: Partial<StartupData>) => void;
}

const CapitalForm: React.FC<CapitalFormProps> = ({ data, onUpdate }) => {
  const [formData, setFormData] = useState({
    funding_stage: data.funding_stage || 'Seed',
    total_capital_raised_usd: data.total_capital_raised_usd || 0,
    cash_on_hand_usd: data.cash_on_hand_usd || 0,
    monthly_burn_usd: data.monthly_burn_usd || 0,
    annual_revenue_run_rate: data.annual_revenue_run_rate || 0,
    revenue_growth_rate_percent: data.revenue_growth_rate_percent || 0,
    gross_margin_percent: data.gross_margin_percent || 0,
    ltv_cac_ratio: data.ltv_cac_ratio || 0,
    investor_tier_primary: data.investor_tier_primary || 'Tier2',
    has_debt: data.has_debt || false,
  });

  // Calculate derived fields
  const runway_months = formData.monthly_burn_usd > 0 
    ? Math.min(formData.cash_on_hand_usd / formData.monthly_burn_usd, 60)
    : 60;

  useEffect(() => {
    // Don't include calculated fields in the data sent to API
    const { ...dataForApi } = formData;
    onUpdate(dataForApi);
  }, [formData, onUpdate]);

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

  return (
    <motion.div
      className="form-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="form-grid">
        {/* Funding Stage */}
        <div className="form-group">
          <label htmlFor="funding_stage">Funding Stage</label>
          <select
            id="funding_stage"
            name="funding_stage"
            value={formData.funding_stage}
            onChange={handleChange}
            className="input"
          >
            <option value="Pre-seed">Pre-seed</option>
            <option value="Seed">Seed</option>
            <option value="Series A">Series A</option>
            <option value="Series B">Series B</option>
            <option value="Series C+">Series C+</option>
          </select>
        </div>

        {/* Total Capital Raised */}
        <div className="form-group">
          <label htmlFor="total_capital_raised_usd">Total Capital Raised (USD)</label>
          <input
            type="number"
            id="total_capital_raised_usd"
            name="total_capital_raised_usd"
            value={formData.total_capital_raised_usd}
            onChange={handleChange}
            className="input"
            min="0"
            step="100000"
          />
        </div>

        {/* Cash on Hand */}
        <div className="form-group">
          <label htmlFor="cash_on_hand_usd">Cash on Hand (USD)</label>
          <input
            type="number"
            id="cash_on_hand_usd"
            name="cash_on_hand_usd"
            value={formData.cash_on_hand_usd}
            onChange={handleChange}
            className="input"
            min="0"
            step="10000"
          />
        </div>

        {/* Monthly Burn */}
        <div className="form-group">
          <label htmlFor="monthly_burn_usd">Monthly Burn Rate (USD)</label>
          <input
            type="number"
            id="monthly_burn_usd"
            name="monthly_burn_usd"
            value={formData.monthly_burn_usd}
            onChange={handleChange}
            className="input"
            min="0"
            step="10000"
          />
        </div>

        {/* Annual Revenue */}
        <div className="form-group">
          <label htmlFor="annual_revenue_run_rate">Annual Revenue Run Rate (USD)</label>
          <input
            type="number"
            id="annual_revenue_run_rate"
            name="annual_revenue_run_rate"
            value={formData.annual_revenue_run_rate}
            onChange={handleChange}
            className="input"
            min="0"
            step="100000"
          />
        </div>

        {/* Revenue Growth */}
        <div className="form-group">
          <label htmlFor="revenue_growth_rate_percent">Revenue Growth Rate (%)</label>
          <input
            type="number"
            id="revenue_growth_rate_percent"
            name="revenue_growth_rate_percent"
            value={formData.revenue_growth_rate_percent}
            onChange={handleChange}
            className="input"
            min="-100"
            max="1000"
            step="10"
          />
        </div>

        {/* Gross Margin */}
        <div className="form-group">
          <label htmlFor="gross_margin_percent">Gross Margin (%)</label>
          <input
            type="number"
            id="gross_margin_percent"
            name="gross_margin_percent"
            value={formData.gross_margin_percent}
            onChange={handleChange}
            className="input"
            min="-100"
            max="100"
            step="5"
          />
        </div>

        {/* LTV/CAC Ratio */}
        <div className="form-group">
          <label htmlFor="ltv_cac_ratio">LTV/CAC Ratio</label>
          <input
            type="number"
            id="ltv_cac_ratio"
            name="ltv_cac_ratio"
            value={formData.ltv_cac_ratio}
            onChange={handleChange}
            className="input"
            min="0"
            max="10"
            step="0.1"
          />
          <span className="input-hint">Industry average: 3.0</span>
        </div>

        {/* Investor Tier */}
        <div className="form-group">
          <label htmlFor="investor_tier_primary">Primary Investor Tier</label>
          <select
            id="investor_tier_primary"
            name="investor_tier_primary"
            value={formData.investor_tier_primary}
            onChange={handleChange}
            className="input"
          >
            <option value="Unknown">Unknown</option>
            <option value="Angel">Angel</option>
            <option value="Tier2">Tier 2 VC</option>
            <option value="Tier1">Tier 1 VC</option>
          </select>
        </div>

        {/* Has Debt */}
        <div className="form-group form-group-full">
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="has_debt"
              checked={formData.has_debt}
              onChange={handleChange}
              className="checkbox"
            />
            <span>Company has debt financing</span>
          </label>
        </div>
      </div>

      {/* Calculated Metrics (Display Only - Computed by API) */}
      <div className="calculated-metrics">
        <div className="metric-card">
          <span className="metric-label">Runway:</span>
          <span className="metric-value">{runway_months.toFixed(0)} months</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Cash Efficiency:</span>
          <span className="metric-value">
            {formData.annual_revenue_run_rate > 0 && formData.monthly_burn_usd > 0
              ? `${(formData.annual_revenue_run_rate / (formData.monthly_burn_usd * 12)).toFixed(1)}x`
              : 'Pre-revenue'}
          </span>
        </div>
      </div>
    </motion.div>
  );
};

export default CapitalForm;