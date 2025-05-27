import React, { useEffect, useRef, useState } from 'react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Sphere, MeshDistortMaterial } from '@react-three/drei';
import './LandingPageV2.css';

interface LandingPageV2Props {
  onStart: () => void;
  isDarkMode: boolean;
}

// 3D Animated Sphere Component
const AnimatedSphere: React.FC = () => {
  return (
    <Sphere visible args={[1, 100, 200]} scale={2.5}>
      <MeshDistortMaterial
        color="#8B5CF6"
        attach="material"
        distort={0.3}
        speed={1.5}
        roughness={0}
        metalness={0.2}
      />
    </Sphere>
  );
};

// Floating particles background
const ParticleField: React.FC = () => {
  const particlesRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const particles = particlesRef.current;
    if (!particles) return;
    
    const createParticle = () => {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.left = Math.random() * 100 + '%';
      particle.style.animationDelay = Math.random() * 20 + 's';
      particle.style.animationDuration = 20 + Math.random() * 10 + 's';
      particles.appendChild(particle);
      
      setTimeout(() => particle.remove(), 30000);
    };
    
    const interval = setInterval(createParticle, 300);
    
    // Create initial particles
    for (let i = 0; i < 20; i++) {
      createParticle();
    }
    
    return () => clearInterval(interval);
  }, []);
  
  return <div ref={particlesRef} className="particle-field" />;
};

// Animated metrics cards
const MetricCard: React.FC<{ value: string; label: string; delay: number }> = ({ value, label, delay }) => {
  return (
    <motion.div
      className="metric-card-v2"
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ scale: 1.05, y: -5 }}
    >
      <div className="metric-value-v2">{value}</div>
      <div className="metric-label-v2">{label}</div>
    </motion.div>
  );
};

const LandingPageV2: React.FC<LandingPageV2Props> = ({ onStart, isDarkMode }) => {
  const [isLoading, setIsLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  });
  
  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  
  const handleStart = () => {
    setIsLoading(true);
    setTimeout(() => {
      onStart();
    }, 1500);
  };
  
  return (
    <div ref={containerRef} className="landing-v2-container">
      <ParticleField />
      
      {/* Hero Section */}
      <motion.section 
        className="hero-section-v2"
        style={{ y, opacity }}
      >
        <div className="hero-content-v2">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.div 
              className="logo-container-v2"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className="logo-3d-container">
                <Canvas camera={{ position: [0, 0, 5], fov: 75 }} gl={{ alpha: true, antialias: true }}>
                  <ambientLight intensity={0.5} />
                  <directionalLight position={[10, 10, 5]} intensity={1} />
                  <AnimatedSphere />
                  <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={2} />
                </Canvas>
              </div>
            </motion.div>
            
            <motion.h1 
              className="hero-title-v2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              <span className="gradient-text">FLASH</span>
              <span className="subtitle-v2">AI-Powered Startup Intelligence</span>
            </motion.h1>
            
            <motion.p 
              className="hero-description-v2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.8 }}
            >
              Predict success with 77.3% accuracy using advanced ML across 45 key metrics
            </motion.p>
            
            <motion.button
              className="cta-button-v2"
              onClick={handleStart}
              disabled={isLoading}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.7, duration: 0.5 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <AnimatePresence mode="wait">
                {isLoading ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="loading-state"
                  >
                    <div className="spinner" />
                    <span>Initializing...</span>
                  </motion.div>
                ) : (
                  <motion.span
                    key="start"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    Start Analysis
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>
          </motion.div>
          
          {/* Floating Metrics */}
          <div className="floating-metrics-v2">
            <MetricCard value="11" label="AI Models" delay={0.9} />
            <MetricCard value="100K" label="Companies Analyzed" delay={1.1} />
            <MetricCard value="77.3%" label="Accuracy" delay={1.3} />
            <MetricCard value="45" label="Key Metrics" delay={1.5} />
          </div>
        </div>
        
        {/* Scroll Indicator */}
        <motion.div
          className="scroll-indicator-v2"
          animate={{ y: [0, 10, 0] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
        >
          <div className="mouse">
            <div className="wheel"></div>
          </div>
        </motion.div>
      </motion.section>
      
      {/* Features Section */}
      <section className="features-section-v2">
        <div className="features-grid-v2">
          {[
            { 
              icon: "📊", 
              title: "CAMP Framework", 
              desc: "Capital, Advantage, Market, People - comprehensive analysis" 
            },
            { 
              icon: "🧠", 
              title: "Explainable AI", 
              desc: "SHAP-powered insights into every prediction" 
            },
            { 
              icon: "⚡", 
              title: "Real-time Analysis", 
              desc: "Instant predictions as you input data" 
            },
            { 
              icon: "🎯", 
              title: "Actionable Insights", 
              desc: "Clear recommendations for improvement" 
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              className="feature-card-v2"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -10, boxShadow: "0 20px 40px rgba(139, 92, 246, 0.3)" }}
            >
              <div className="feature-icon-v2">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default LandingPageV2;