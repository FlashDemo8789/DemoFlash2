import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { StartupData } from '../../types';
import './Forms.css';

interface MarketFormProps {
  data: Partial<StartupData>;
  onUpdate: (data: Partial<StartupData>) => void;
}

const MarketForm: React.FC<MarketFormProps> = ({ data, onUpdate }) => {
  const [formData, setFormData] = useState({
    sector: data.sector || 'SaaS',
    tam_size_usd: data.tam_size_usd || 1000000000,
    sam_size_usd: data.sam_size_usd || 100000000,
    som_size_usd: data.som_size_usd || 10000000,
    market_growth_rate_percent: data.market_growth_rate_percent || 20,
    customer_count: data.customer_count || 100,
    customer_concentration_percent: data.customer_concentration_percent || 20,
    user_growth_rate_percent: data.user_growth_rate_percent || 100,
    net_dollar_retention_percent: data.net_dollar_retention_percent || 110,
    competition_intensity: data.competition_intensity || 3,
    competitors_named_count: data.competitors_named_count || 5,
    dau_mau_ratio: data.dau_mau_ratio || 0.3,
  });

  useEffect(() => {
    onUpdate(formData);
  }, [formData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
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
        <div className="form-group">
          <label htmlFor="sector">Sector</label>
          <select
            id="sector"
            name="sector"
            value={formData.sector}
            onChange={handleChange}
            className="input"
          >
            <option value="SaaS">SaaS</option>
            <option value="FinTech">FinTech</option>
            <option value="HealthTech">HealthTech</option>
            <option value="E-commerce">E-commerce</option>
            <option value="AI/ML">AI/ML</option>
            <option value="EdTech">EdTech</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="tam_size_usd">TAM Size (USD)</label>
          <input
            type="number"
            id="tam_size_usd"
            name="tam_size_usd"
            value={formData.tam_size_usd}
            onChange={handleChange}
            className="input"
            min="0"
            step="1000000"
          />
        </div>

        <div className="form-group">
          <label htmlFor="customer_count">Customer Count</label>
          <input
            type="number"
            id="customer_count"
            name="customer_count"
            value={formData.customer_count}
            onChange={handleChange}
            className="input"
            min="0"
          />
        </div>

        <div className="form-group">
          <label htmlFor="market_growth_rate_percent">Market Growth Rate (%)</label>
          <input
            type="number"
            id="market_growth_rate_percent"
            name="market_growth_rate_percent"
            value={formData.market_growth_rate_percent}
            onChange={handleChange}
            className="input"
            min="0"
            max="200"
          />
        </div>
      </div>
    </motion.div>
  );
};

export default MarketForm;