import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { StartupData } from '../../types';
import './Forms.css';

interface PeopleFormProps {
  data: Partial<StartupData>;
  onUpdate: (data: Partial<StartupData>) => void;
}

const PeopleForm: React.FC<PeopleFormProps> = ({ data, onUpdate }) => {
  const [formData, setFormData] = useState({
    founders_count: data.founders_count || 2,
    team_size_full_time: data.team_size_full_time || 10,
    years_experience_avg: data.years_experience_avg || 10,
    domain_expertise_years_avg: data.domain_expertise_years_avg || 5,
    prior_startup_experience_count: data.prior_startup_experience_count || 1,
    prior_successful_exits_count: data.prior_successful_exits_count || 0,
    board_advisor_experience_score: data.board_advisor_experience_score || 3,
    advisors_count: data.advisors_count || 3,
    team_diversity_percent: data.team_diversity_percent || 40,
    key_person_dependency: data.key_person_dependency || false,
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

  return (
    <motion.div
      className="form-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="founders_count">Number of Founders</label>
          <input
            type="number"
            id="founders_count"
            name="founders_count"
            value={formData.founders_count}
            onChange={handleChange}
            className="input"
            min="1"
            max="10"
          />
        </div>

        <div className="form-group">
          <label htmlFor="team_size_full_time">Full-Time Team Size</label>
          <input
            type="number"
            id="team_size_full_time"
            name="team_size_full_time"
            value={formData.team_size_full_time}
            onChange={handleChange}
            className="input"
            min="0"
          />
        </div>

        <div className="form-group">
          <label htmlFor="years_experience_avg">Average Years Experience</label>
          <input
            type="number"
            id="years_experience_avg"
            name="years_experience_avg"
            value={formData.years_experience_avg}
            onChange={handleChange}
            className="input"
            min="0"
            max="50"
          />
        </div>

        <div className="form-group">
          <label htmlFor="prior_successful_exits_count">Prior Successful Exits</label>
          <input
            type="number"
            id="prior_successful_exits_count"
            name="prior_successful_exits_count"
            value={formData.prior_successful_exits_count}
            onChange={handleChange}
            className="input"
            min="0"
            max="10"
          />
        </div>

        <div className="form-group form-group-full">
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="key_person_dependency"
              checked={formData.key_person_dependency}
              onChange={handleChange}
              className="checkbox"
            />
            <span>Key Person Dependency Risk</span>
          </label>
        </div>
      </div>
    </motion.div>
  );
};

export default PeopleForm;