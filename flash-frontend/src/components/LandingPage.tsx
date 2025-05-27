import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, TrendingUp, Shield, Users } from 'lucide-react';
import './LandingPage.css';

interface LandingPageProps {
  onStart: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onStart }) => {
  const features = [
    {
      icon: <TrendingUp size={24} />,
      title: '77% Accuracy',
      description: 'AI-powered predictions based on 100,000+ startups'
    },
    {
      icon: <Shield size={24} />,
      title: '4 Key Pillars',
      description: 'Comprehensive analysis across Capital, Advantage, Market, People'
    },
    {
      icon: <Users size={24} />,
      title: 'Trusted by VCs',
      description: 'Used by top-tier investors and accelerators worldwide'
    }
  ];

  return (
    <div className="landing-container">
      <motion.div 
        className="landing-content"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      >
        {/* Logo */}
        <motion.div 
          className="logo"
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Sparkles size={48} />
        </motion.div>

        {/* Title */}
        <motion.h1 
          className="landing-title"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          FLASH
        </motion.h1>

        {/* Subtitle */}
        <motion.p 
          className="landing-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          AI-Powered Startup Success Prediction
        </motion.p>

        {/* CTA Button */}
        <motion.button
          className="button button-primary landing-cta"
          onClick={onStart}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Analyze Your Startup
          <ArrowRight size={20} style={{ marginLeft: 8 }} />
        </motion.button>

        {/* Features */}
        <motion.div 
          className="landing-features"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="feature-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7 + index * 0.1 }}
            >
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Trust Badge */}
        <motion.p 
          className="trust-badge"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 1 }}
        >
          🔒 Your data is encrypted and never shared
        </motion.p>
      </motion.div>
    </div>
  );
};

export default LandingPage;