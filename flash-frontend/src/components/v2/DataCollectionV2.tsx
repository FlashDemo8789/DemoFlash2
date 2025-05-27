import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import { Box, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { StartupData } from '../../types';
import { generateTestStartupData, testScenarios } from '../../utils/testDataGenerator';
import './DataCollectionV2.css';

interface DataCollectionV2Props {
  onSubmit: (data: StartupData) => void;
  onBack: () => void;
  isDarkMode: boolean;
}

// 3D Cube representing CAMP pillars
const CampCube: React.FC<{ activePillar: string }> = ({ activePillar }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useEffect(() => {
    if (meshRef.current) {
      const rotations: Record<string, [number, number, number]> = {
        capital: [0, 0, 0],
        advantage: [0, Math.PI / 2, 0],
        market: [0, Math.PI, 0],
        people: [0, -Math.PI / 2, 0]
      };
      
      const target = rotations[activePillar] || [0, 0, 0];
      meshRef.current.rotation.y = target[1];
    }
  }, [activePillar]);
  
  return (
    <Box ref={meshRef} args={[2, 2, 2]}>
      <meshStandardMaterial color="#8B5CF6" />
    </Box>
  );
};

// Interactive slider with visual feedback
const InteractiveSlider: React.FC<{
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  unit?: string;
  icon?: string;
}> = ({ label, value, onChange, min, max, unit = '', icon }) => {
  const [isDragging, setIsDragging] = useState(false);
  const percentage = ((value - min) / (max - min)) * 100;
  
  return (
    <motion.div 
      className="interactive-slider"
      whileHover={{ scale: 1.02 }}
      animate={{ scale: isDragging ? 1.05 : 1 }}
    >
      <div className="slider-header">
        {icon && <span className="slider-icon">{icon}</span>}
        <span className="slider-label">{label}</span>
        <span className="slider-value">{value.toLocaleString()}{unit}</span>
      </div>
      <div className="slider-track">
        <motion.div 
          className="slider-fill"
          style={{ width: `${percentage}%` }}
          animate={{ 
            backgroundColor: percentage > 70 ? '#10b981' : percentage > 30 ? '#f59e0b' : '#ef4444'
          }}
        />
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          onMouseDown={() => setIsDragging(true)}
          onMouseUp={() => setIsDragging(false)}
          className="slider-input"
        />
      </div>
    </motion.div>
  );
};

// Smart input with AI suggestions
const SmartInput: React.FC<{
  label: string;
  value: string | number;
  onChange: (value: any) => void;
  type?: string;
  placeholder?: string;
  suggestions?: string[];
  icon?: string;
}> = ({ label, value, onChange, type = 'text', placeholder, suggestions = [], icon }) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  
  return (
    <motion.div 
      className="smart-input"
      animate={{ scale: isFocused ? 1.02 : 1 }}
    >
      <label>
        {icon && <span className="input-icon">{icon}</span>}
        {label}
      </label>
      <div className="input-wrapper">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(type === 'number' ? Number(e.target.value) : e.target.value)}
          onFocus={() => {
            setIsFocused(true);
            setShowSuggestions(true);
          }}
          onBlur={() => {
            setIsFocused(false);
            setTimeout(() => setShowSuggestions(false), 200);
          }}
          placeholder={placeholder}
          className="smart-input-field"
        />
        <AnimatePresence>
          {showSuggestions && suggestions.length > 0 && (
            <motion.div
              className="suggestions-dropdown"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              {suggestions.map((suggestion, index) => (
                <motion.div
                  key={index}
                  className="suggestion-item"
                  whileHover={{ backgroundColor: 'rgba(139, 92, 246, 0.1)' }}
                  onClick={() => onChange(suggestion)}
                >
                  {suggestion}
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

// Progress ring component
const ProgressRing: React.FC<{ progress: number }> = ({ progress }) => {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progress / 100) * circumference;
  
  return (
    <svg width="100" height="100" className="progress-ring">
      <circle
        cx="50"
        cy="50"
        r={radius}
        stroke="rgba(139, 92, 246, 0.2)"
        strokeWidth="8"
        fill="none"
      />
      <motion.circle
        cx="50"
        cy="50"
        r={radius}
        stroke="#8B5CF6"
        strokeWidth="8"
        fill="none"
        strokeLinecap="round"
        strokeDasharray={circumference}
        animate={{ strokeDashoffset }}
        transition={{ duration: 0.5 }}
      />
      <text x="50" y="50" textAnchor="middle" dy="0.3em" className="progress-text">
        {Math.round(progress)}%
      </text>
    </svg>
  );
};

const DataCollectionV2: React.FC<DataCollectionV2Props> = ({ onSubmit, onBack, isDarkMode }) => {
  const [activePillar, setActivePillar] = useState('capital');
  const [formData, setFormData] = useState<Partial<StartupData>>({});
  const [completedPillars, setCompletedPillars] = useState(new Set<string>());
  
  const pillars = [
    { id: 'capital', name: 'Capital', icon: '💰', color: '#10b981' },
    { id: 'advantage', name: 'Advantage', icon: '🚀', color: '#3b82f6' },
    { id: 'market', name: 'Market', icon: '🌍', color: '#f59e0b' },
    { id: 'people', name: 'People', icon: '👥', color: '#8b5cf6' }
  ];
  
  const progress = (completedPillars.size / pillars.length) * 100;
  
  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };
  
  const markPillarComplete = () => {
    setCompletedPillars(prev => new Set(prev).add(activePillar));
    
    // Auto-navigate to next incomplete pillar
    const currentIndex = pillars.findIndex(p => p.id === activePillar);
    const nextIncomplete = pillars.slice(currentIndex + 1).find(p => !completedPillars.has(p.id));
    if (nextIncomplete) {
      setTimeout(() => setActivePillar(nextIncomplete.id), 300);
    }
  };
  
  // Check if current pillar has minimum required fields
  const isPillarValid = () => {
    switch (activePillar) {
      case 'capital':
        return formData.funding_stage && formData.total_capital_raised_usd !== undefined && 
               formData.annual_revenue_run_rate !== undefined;
      case 'advantage':
        return formData.tech_differentiation_score !== undefined && formData.product_stage;
      case 'market':
        return formData.sector && formData.tam_size_usd !== undefined;
      case 'people':
        return formData.founders_count !== undefined && formData.team_size_full_time !== undefined;
      default:
        return false;
    }
  };
  
  const renderPillarContent = () => {
    switch (activePillar) {
      case 'capital':
        return (
          <motion.div className="pillar-content" key="capital">
            <h2>💰 Capital & Financial Health</h2>
            <div className="form-grid-v2">
              <SmartInput
                label="Funding Stage"
                value={formData.funding_stage || ''}
                onChange={(val) => updateField('funding_stage', val)}
                placeholder="e.g., Series A"
                suggestions={['Pre-seed', 'Seed', 'Series A', 'Series B', 'Series C']}
                icon="📊"
              />
              
              <InteractiveSlider
                label="Total Capital Raised"
                value={formData.total_capital_raised_usd || 0}
                onChange={(val) => updateField('total_capital_raised_usd', val)}
                min={0}
                max={50000000}
                unit="$"
                icon="💵"
              />
              
              <InteractiveSlider
                label="Cash on Hand"
                value={formData.cash_on_hand_usd || 0}
                onChange={(val) => updateField('cash_on_hand_usd', val)}
                min={0}
                max={10000000}
                unit="$"
                icon="💰"
              />
              
              <InteractiveSlider
                label="Monthly Burn Rate"
                value={formData.monthly_burn_usd || 0}
                onChange={(val) => updateField('monthly_burn_usd', val)}
                min={0}
                max={1000000}
                unit="$"
                icon="🔥"
              />
              
              <InteractiveSlider
                label="Annual Revenue Run Rate"
                value={formData.annual_revenue_run_rate || 0}
                onChange={(val) => updateField('annual_revenue_run_rate', val)}
                min={0}
                max={10000000}
                unit="$"
                icon="📈"
              />
              
              <InteractiveSlider
                label="Revenue Growth Rate"
                value={formData.revenue_growth_rate_percent || 0}
                onChange={(val) => updateField('revenue_growth_rate_percent', val)}
                min={-50}
                max={500}
                unit="%"
                icon="📊"
              />
              
              <InteractiveSlider
                label="Gross Margin"
                value={formData.gross_margin_percent || 0}
                onChange={(val) => updateField('gross_margin_percent', val)}
                min={0}
                max={100}
                unit="%"
                icon="💹"
              />
              
              <InteractiveSlider
                label="LTV/CAC Ratio"
                value={formData.ltv_cac_ratio || 1}
                onChange={(val) => updateField('ltv_cac_ratio', val)}
                min={0}
                max={10}
                icon="🎯"
              />
              
              <SmartInput
                label="Primary Investor Tier"
                value={formData.investor_tier_primary || ''}
                onChange={(val) => updateField('investor_tier_primary', val)}
                placeholder="e.g., Tier 1"
                suggestions={['Tier 1', 'Tier 2', 'Tier 3', 'Strategic', 'Angel']}
                icon="🏆"
              />
              
              <div className="toggle-group">
                <label className="toggle-label">
                  <input
                    type="checkbox"
                    checked={formData.has_debt || false}
                    onChange={(e) => updateField('has_debt', e.target.checked)}
                  />
                  <span className="toggle-switch"></span>
                  <span className="toggle-text">Has Debt Financing</span>
                </label>
              </div>
            </div>
          </motion.div>
        );
        
      case 'advantage':
        return (
          <motion.div className="pillar-content" key="advantage">
            <h2>🚀 Competitive Advantage</h2>
            <div className="form-grid-v2">
              <InteractiveSlider
                label="Patent Count"
                value={formData.patent_count || 0}
                onChange={(val) => updateField('patent_count', val)}
                min={0}
                max={50}
                icon="📜"
              />
              
              <InteractiveSlider
                label="Tech Differentiation Score"
                value={formData.tech_differentiation_score || 1}
                onChange={(val) => updateField('tech_differentiation_score', val)}
                min={1}
                max={5}
                icon="⚡"
              />
              
              <InteractiveSlider
                label="Switching Cost Score"
                value={formData.switching_cost_score || 1}
                onChange={(val) => updateField('switching_cost_score', val)}
                min={1}
                max={5}
                icon="🔒"
              />
              
              <InteractiveSlider
                label="Brand Strength Score"
                value={formData.brand_strength_score || 1}
                onChange={(val) => updateField('brand_strength_score', val)}
                min={1}
                max={5}
                icon="⭐"
              />
              
              <InteractiveSlider
                label="Scalability Score"
                value={formData.scalability_score || 1}
                onChange={(val) => updateField('scalability_score', val)}
                min={1}
                max={5}
                icon="📏"
              />
              
              <SmartInput
                label="Product Stage"
                value={formData.product_stage || ''}
                onChange={(val) => updateField('product_stage', val)}
                placeholder="e.g., GA"
                suggestions={['MVP', 'Beta', 'GA', 'Mature', 'Growth']}
                icon="🎯"
              />
              
              <InteractiveSlider
                label="30-Day Retention"
                value={formData.product_retention_30d || 0}
                onChange={(val) => updateField('product_retention_30d', val)}
                min={0}
                max={100}
                unit="%"
                icon="📊"
              />
              
              <InteractiveSlider
                label="90-Day Retention"
                value={formData.product_retention_90d || 0}
                onChange={(val) => updateField('product_retention_90d', val)}
                min={0}
                max={100}
                unit="%"
                icon="📈"
              />
              
              <div className="toggle-group">
                <label className="toggle-label">
                  <input
                    type="checkbox"
                    checked={formData.network_effects_present || false}
                    onChange={(e) => updateField('network_effects_present', e.target.checked)}
                  />
                  <span className="toggle-switch"></span>
                  <span className="toggle-text">Network Effects Present</span>
                </label>
                
                <label className="toggle-label">
                  <input
                    type="checkbox"
                    checked={formData.has_data_moat || false}
                    onChange={(e) => updateField('has_data_moat', e.target.checked)}
                  />
                  <span className="toggle-switch"></span>
                  <span className="toggle-text">Has Data Moat</span>
                </label>
                
                <label className="toggle-label">
                  <input
                    type="checkbox"
                    checked={formData.regulatory_advantage_present || false}
                    onChange={(e) => updateField('regulatory_advantage_present', e.target.checked)}
                  />
                  <span className="toggle-switch"></span>
                  <span className="toggle-text">Regulatory Advantage</span>
                </label>
              </div>
            </div>
          </motion.div>
        );
        
      case 'market':
        return (
          <motion.div className="pillar-content" key="market">
            <h2>🌍 Market Opportunity</h2>
            <div className="form-grid-v2">
              <SmartInput
                label="Sector"
                value={formData.sector || ''}
                onChange={(val) => updateField('sector', val)}
                placeholder="e.g., SaaS"
                suggestions={['SaaS', 'Fintech', 'Healthcare', 'E-commerce', 'AI/ML', 'Marketplace']}
                icon="🏢"
              />
              
              <InteractiveSlider
                label="TAM Size (Total Addressable Market)"
                value={formData.tam_size_usd || 0}
                onChange={(val) => updateField('tam_size_usd', val)}
                min={0}
                max={100000000000}
                unit="$"
                icon="🌐"
              />
              
              <InteractiveSlider
                label="SAM Size (Serviceable Addressable Market)"
                value={formData.sam_size_usd || 0}
                onChange={(val) => updateField('sam_size_usd', val)}
                min={0}
                max={10000000000}
                unit="$"
                icon="🎯"
              />
              
              <InteractiveSlider
                label="SOM Size (Serviceable Obtainable Market)"
                value={formData.som_size_usd || 0}
                onChange={(val) => updateField('som_size_usd', val)}
                min={0}
                max={1000000000}
                unit="$"
                icon="📊"
              />
              
              <InteractiveSlider
                label="Market Growth Rate"
                value={formData.market_growth_rate_percent || 0}
                onChange={(val) => updateField('market_growth_rate_percent', val)}
                min={0}
                max={100}
                unit="%"
                icon="📈"
              />
              
              <InteractiveSlider
                label="Customer Count"
                value={formData.customer_count || 0}
                onChange={(val) => updateField('customer_count', val)}
                min={0}
                max={100000}
                icon="👥"
              />
              
              <InteractiveSlider
                label="Customer Concentration"
                value={formData.customer_concentration_percent || 0}
                onChange={(val) => updateField('customer_concentration_percent', val)}
                min={0}
                max={100}
                unit="%"
                icon="⚖️"
              />
              
              <InteractiveSlider
                label="User Growth Rate"
                value={formData.user_growth_rate_percent || 0}
                onChange={(val) => updateField('user_growth_rate_percent', val)}
                min={0}
                max={500}
                unit="%"
                icon="🚀"
              />
              
              <InteractiveSlider
                label="Net Dollar Retention"
                value={formData.net_dollar_retention_percent || 100}
                onChange={(val) => updateField('net_dollar_retention_percent', val)}
                min={0}
                max={200}
                unit="%"
                icon="💹"
              />
              
              <InteractiveSlider
                label="Competition Intensity"
                value={formData.competition_intensity || 1}
                onChange={(val) => updateField('competition_intensity', val)}
                min={1}
                max={5}
                icon="⚔️"
              />
              
              <InteractiveSlider
                label="Named Competitors Count"
                value={formData.competitors_named_count || 0}
                onChange={(val) => updateField('competitors_named_count', val)}
                min={0}
                max={20}
                icon="🏁"
              />
              
              <InteractiveSlider
                label="DAU/MAU Ratio"
                value={formData.dau_mau_ratio || 0}
                onChange={(val) => updateField('dau_mau_ratio', val)}
                min={0}
                max={1}
                icon="📱"
              />
            </div>
          </motion.div>
        );
        
      case 'people':
        return (
          <motion.div className="pillar-content" key="people">
            <h2>👥 Team & Leadership</h2>
            <div className="form-grid-v2">
              <InteractiveSlider
                label="Number of Founders"
                value={formData.founders_count || 1}
                onChange={(val) => updateField('founders_count', val)}
                min={1}
                max={5}
                icon="👨‍💼"
              />
              
              <InteractiveSlider
                label="Full-Time Team Size"
                value={formData.team_size_full_time || 1}
                onChange={(val) => updateField('team_size_full_time', val)}
                min={1}
                max={500}
                icon="👥"
              />
              
              <InteractiveSlider
                label="Average Years Experience"
                value={formData.years_experience_avg || 0}
                onChange={(val) => updateField('years_experience_avg', val)}
                min={0}
                max={30}
                unit=" years"
                icon="📅"
              />
              
              <InteractiveSlider
                label="Domain Expertise Years"
                value={formData.domain_expertise_years_avg || 0}
                onChange={(val) => updateField('domain_expertise_years_avg', val)}
                min={0}
                max={20}
                unit=" years"
                icon="🎓"
              />
              
              <InteractiveSlider
                label="Prior Startup Experience"
                value={formData.prior_startup_experience_count || 0}
                onChange={(val) => updateField('prior_startup_experience_count', val)}
                min={0}
                max={10}
                icon="🚀"
              />
              
              <InteractiveSlider
                label="Prior Successful Exits"
                value={formData.prior_successful_exits_count || 0}
                onChange={(val) => updateField('prior_successful_exits_count', val)}
                min={0}
                max={5}
                icon="💰"
              />
              
              <InteractiveSlider
                label="Board/Advisor Experience Score"
                value={formData.board_advisor_experience_score || 1}
                onChange={(val) => updateField('board_advisor_experience_score', val)}
                min={1}
                max={5}
                icon="🏛️"
              />
              
              <InteractiveSlider
                label="Team Cohesion Score"
                value={formData.team_cohesion_score || 1}
                onChange={(val) => updateField('team_cohesion_score', val)}
                min={1}
                max={5}
                icon="🤝"
              />
              
              <InteractiveSlider
                label="Hiring Velocity Score"
                value={formData.hiring_velocity_score || 1}
                onChange={(val) => updateField('hiring_velocity_score', val)}
                min={1}
                max={5}
                icon="📈"
              />
              
              <InteractiveSlider
                label="Diversity Score"
                value={formData.diversity_score || 1}
                onChange={(val) => updateField('diversity_score', val)}
                min={1}
                max={5}
                icon="🌈"
              />
              
              <InteractiveSlider
                label="Technical Expertise Score"
                value={formData.technical_expertise_score || 1}
                onChange={(val) => updateField('technical_expertise_score', val)}
                min={1}
                max={5}
                icon="💻"
              />
            </div>
          </motion.div>
        );
        
      default:
        return null;
    }
  };
  
  return (
    <div className="data-collection-v2">
      {/* Header */}
      <motion.header 
        className="collection-header-v2"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <button className="back-button-v2" onClick={onBack}>
          ← Back
        </button>
        
        <div className="progress-container">
          <ProgressRing progress={progress} />
          <div className="progress-text">
            {completedPillars.size}/{pillars.length} Complete
          </div>
        </div>
        
        <div className="header-actions">
          <motion.button
            className="test-data-btn"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              const testData = generateTestStartupData();
              setFormData(prev => ({ ...prev, ...testData }));
            }}
            title="Auto-fill with random test data"
          >
            🎲 Test Data
          </motion.button>
          
          <motion.button
            className="save-draft-btn"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Save Draft
          </motion.button>
        </div>
      </motion.header>
      
      {/* 3D Visualization */}
      <div className="visualization-container">
        <Canvas camera={{ position: [3, 3, 3], fov: 75 }} gl={{ alpha: true, antialias: true }}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <CampCube activePillar={activePillar} />
          <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={1} />
        </Canvas>
      </div>
      
      {/* Pillar Navigation */}
      <motion.nav className="pillar-nav-v2">
        {pillars.map((pillar) => (
          <motion.button
            key={pillar.id}
            className={`pillar-tab-v2 ${activePillar === pillar.id ? 'active' : ''} ${completedPillars.has(pillar.id) ? 'completed' : ''}`}
            onClick={() => setActivePillar(pillar.id)}
            whileHover={{ y: -5 }}
            whileTap={{ scale: 0.95 }}
            style={{
              borderColor: activePillar === pillar.id ? pillar.color : completedPillars.has(pillar.id) ? `${pillar.color}50` : 'transparent'
            }}
          >
            <span className="pillar-icon">{pillar.icon}</span>
            <span className="pillar-name">{pillar.name}</span>
            {completedPillars.has(pillar.id) && (
              <motion.span 
                className="checkmark"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
              >
                ✓
              </motion.span>
            )}
          </motion.button>
        ))}
      </motion.nav>
      
      {/* Navigation Tip */}
      {completedPillars.size === 0 && (
        <motion.div 
          className="nav-tip"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.7 }}
        >
          💡 Click on any pillar tab above or complete them in order
        </motion.div>
      )}
      
      {/* Content Area */}
      <AnimatePresence mode="wait">
        <motion.div
          className="content-area-v2"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          {renderPillarContent()}
          
          <div className="action-buttons-v2">
            {!completedPillars.has(activePillar) && isPillarValid() && (
              <motion.button
                className="complete-pillar-btn"
                onClick={markPillarComplete}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                ✓ Complete {pillars.find(p => p.id === activePillar)?.name}
              </motion.button>
            )}
            
            {completedPillars.has(activePillar) && (
              <>
                <motion.div
                  className="pillar-completed-message"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  ✅ {pillars.find(p => p.id === activePillar)?.name} Completed
                </motion.div>
                
                {/* Next Pillar Button */}
                {activePillar !== 'people' && (
                  <motion.button
                    className="next-pillar-btn"
                    onClick={() => {
                      const currentIndex = pillars.findIndex(p => p.id === activePillar);
                      const nextPillar = pillars[currentIndex + 1];
                      if (nextPillar) {
                        setActivePillar(nextPillar.id);
                      }
                    }}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Next: {pillars[pillars.findIndex(p => p.id === activePillar) + 1]?.name} →
                  </motion.button>
                )}
              </>
            )}
            
            {completedPillars.size === pillars.length && (
              <motion.button
                className="submit-btn-v2 pulse-animation"
                onClick={() => {
                  console.log('Submitting data:', formData);
                  // Map frontend fields to API fields with proper defaults
                  const apiData: any = {
                    // Capital fields
                    funding_stage: formData.funding_stage || 'Seed',
                    total_capital_raised_usd: formData.total_capital_raised_usd || 0,
                    cash_on_hand_usd: formData.cash_on_hand_usd || 0,
                    monthly_burn_usd: formData.monthly_burn_usd || 0,
                    annual_revenue_run_rate: formData.annual_revenue_run_rate || 0,
                    revenue_growth_rate_percent: formData.revenue_growth_rate_percent || 0,
                    gross_margin_percent: formData.gross_margin_percent || 0,
                    ltv_cac_ratio: formData.ltv_cac_ratio || 1,
                    investor_tier_primary: formData.investor_tier_primary || 'Tier 3',
                    has_debt: formData.has_debt || false,
                    
                    // Advantage fields
                    patent_count: formData.patent_count || 0,
                    network_effects_present: formData.network_effects_present || false,
                    has_data_moat: formData.has_data_moat || false,
                    regulatory_advantage_present: formData.regulatory_advantage_present || false,
                    tech_differentiation_score: formData.tech_differentiation_score || 1,
                    switching_cost_score: formData.switching_cost_score || 1,
                    brand_strength_score: formData.brand_strength_score || 1,
                    scalability_score: (formData.scalability_score || 1) / 5, // Convert 1-5 to 0-1
                    product_stage: formData.product_stage || 'MVP',
                    product_retention_30d: (formData.product_retention_30d || 0) / 100, // Convert % to decimal
                    product_retention_90d: (formData.product_retention_90d || 0) / 100, // Convert % to decimal
                    
                    // Market fields
                    sector: formData.sector || 'SaaS',
                    tam_size_usd: formData.tam_size_usd || 1000000000,
                    sam_size_usd: formData.sam_size_usd || 100000000,
                    som_size_usd: formData.som_size_usd || 10000000,
                    market_growth_rate_percent: formData.market_growth_rate_percent || 10,
                    customer_count: formData.customer_count || 0,
                    customer_concentration_percent: formData.customer_concentration_percent || 0,
                    user_growth_rate_percent: formData.user_growth_rate_percent || 0,
                    net_dollar_retention_percent: formData.net_dollar_retention_percent || 100,
                    competition_intensity: formData.competition_intensity || 3,
                    competitors_named_count: formData.competitors_named_count || 0,
                    dau_mau_ratio: formData.dau_mau_ratio || 0.1,
                    
                    // People fields
                    founders_count: formData.founders_count || 1,
                    team_size_full_time: formData.team_size_full_time || 1,
                    years_experience_avg: formData.years_experience_avg || 0,
                    domain_expertise_years_avg: formData.domain_expertise_years_avg || 0,
                    prior_startup_experience_count: formData.prior_startup_experience_count || 0,
                    prior_successful_exits_count: formData.prior_successful_exits_count || 0,
                    board_advisor_experience_score: formData.board_advisor_experience_score || 1,
                    advisors_count: formData.board_advisor_experience_score ? Math.floor((formData.board_advisor_experience_score - 1) * 2.5) : 0,
                    team_diversity_percent: (formData.diversity_score || 1) * 20,
                    key_person_dependency: false
                  };
                  
                  console.log('API data:', apiData);
                  onSubmit(apiData as StartupData);
                }}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                🚀 Analyze Startup →
              </motion.button>
            )}
            
            {!isPillarValid() && !completedPillars.has(activePillar) && (
              <motion.div
                className="validation-hint"
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.7 }}
              >
                Please fill in required fields to continue
              </motion.div>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default DataCollectionV2;