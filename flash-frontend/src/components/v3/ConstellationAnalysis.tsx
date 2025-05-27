import React, { useEffect, useRef } from 'react';
import { motion, useAnimationFrame } from 'framer-motion';

interface Star {
  x: number;
  y: number;
  size: number;
  opacity: number;
  pulseOffset: number;
  pillar?: string;
}

interface Connection {
  from: number;
  to: number;
  strength: number;
  active: boolean;
}

export const ConstellationAnalysis: React.FC<{ 
  isAnalyzing: boolean;
  pillarProgress?: { [key: string]: number };
}> = ({ isAnalyzing, pillarProgress }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const starsRef = useRef<Star[]>([]);
  const connectionsRef = useRef<Connection[]>([]);
  const timeRef = useRef(0);

  // Initialize constellation
  useEffect(() => {
    const centerX = 400;
    const centerY = 300;
    
    // Create constellation pattern based on CAMP pillars
    const pillars = ['capital', 'advantage', 'market', 'people'];
    const stars: Star[] = [];
    
    // Center star (the startup)
    stars.push({
      x: centerX,
      y: centerY,
      size: 8,
      opacity: 1,
      pulseOffset: 0
    });
    
    // Pillar constellations
    pillars.forEach((pillar, i) => {
      const angle = (i / 4) * Math.PI * 2 - Math.PI / 2;
      const distance = 120;
      
      // Main pillar star
      const mainX = centerX + Math.cos(angle) * distance;
      const mainY = centerY + Math.sin(angle) * distance;
      
      stars.push({
        x: mainX,
        y: mainY,
        size: 6,
        opacity: 0.8,
        pulseOffset: i * 0.5,
        pillar
      });
      
      // Satellite stars around each pillar
      for (let j = 0; j < 3; j++) {
        const subAngle = angle + (j - 1) * 0.3;
        const subDistance = distance + 40;
        
        stars.push({
          x: centerX + Math.cos(subAngle) * subDistance,
          y: centerY + Math.sin(subAngle) * subDistance,
          size: 3,
          opacity: 0.4,
          pulseOffset: i * 0.5 + j * 0.2,
          pillar
        });
      }
    });
    
    starsRef.current = stars;
    
    // Create connections
    const connections: Connection[] = [];
    
    // Connect center to main pillars
    for (let i = 1; i <= 4; i++) {
      connections.push({
        from: 0,
        to: i,
        strength: 0,
        active: false
      });
    }
    
    // Connect pillars to their satellites
    let starIndex = 5;
    for (let i = 1; i <= 4; i++) {
      for (let j = 0; j < 3; j++) {
        connections.push({
          from: i,
          to: starIndex++,
          strength: 0,
          active: false
        });
      }
    }
    
    connectionsRef.current = connections;
  }, []);

  useAnimationFrame((time, delta) => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    timeRef.current += delta * 0.001;
    
    // Clear with fade effect
    ctx.fillStyle = 'rgba(255, 255, 255, 0.98)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Update connections based on analysis progress
    if (isAnalyzing) {
      connectionsRef.current.forEach((conn, i) => {
        if (i < 4) {
          // Main connections activate based on overall progress
          conn.active = true;
          conn.strength = Math.min(1, conn.strength + 0.01);
        } else {
          // Satellite connections activate later
          conn.active = timeRef.current > 2;
          if (conn.active) {
            conn.strength = Math.min(1, conn.strength + 0.005);
          }
        }
      });
    }
    
    // Draw connections
    connectionsRef.current.forEach(conn => {
      if (conn.strength > 0) {
        const fromStar = starsRef.current[conn.from];
        const toStar = starsRef.current[conn.to];
        
        ctx.beginPath();
        ctx.moveTo(fromStar.x, fromStar.y);
        ctx.lineTo(toStar.x, toStar.y);
        
        const gradient = ctx.createLinearGradient(
          fromStar.x, fromStar.y, toStar.x, toStar.y
        );
        gradient.addColorStop(0, `rgba(59, 130, 246, ${conn.strength * 0.3})`);
        gradient.addColorStop(1, `rgba(59, 130, 246, ${conn.strength * 0.1})`);
        
        ctx.strokeStyle = gradient;
        ctx.lineWidth = conn.strength * 2;
        ctx.stroke();
      }
    });
    
    // Draw stars
    starsRef.current.forEach((star, i) => {
      const pulse = Math.sin(timeRef.current * 2 + star.pulseOffset) * 0.3 + 0.7;
      const opacity = star.opacity * (isAnalyzing ? pulse : 1);
      
      // Glow effect
      const glowSize = star.size * 3;
      const glowGradient = ctx.createRadialGradient(
        star.x, star.y, 0,
        star.x, star.y, glowSize
      );
      glowGradient.addColorStop(0, `rgba(59, 130, 246, ${opacity * 0.3})`);
      glowGradient.addColorStop(1, 'rgba(59, 130, 246, 0)');
      
      ctx.fillStyle = glowGradient;
      ctx.beginPath();
      ctx.arc(star.x, star.y, glowSize, 0, Math.PI * 2);
      ctx.fill();
      
      // Star core
      ctx.fillStyle = `rgba(59, 130, 246, ${opacity})`;
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
      ctx.fill();
      
      // Inner bright spot
      ctx.fillStyle = `rgba(255, 255, 255, ${opacity * 0.8})`;
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.size * 0.3, 0, Math.PI * 2);
      ctx.fill();
    });
    
    // Draw data flow particles
    if (isAnalyzing) {
      const particleCount = 20;
      for (let i = 0; i < particleCount; i++) {
        const progress = ((timeRef.current * 0.2 + i / particleCount) % 1);
        
        connectionsRef.current.slice(0, 4).forEach(conn => {
          const fromStar = starsRef.current[conn.from];
          const toStar = starsRef.current[conn.to];
          
          const x = fromStar.x + (toStar.x - fromStar.x) * progress;
          const y = fromStar.y + (toStar.y - fromStar.y) * progress;
          
          ctx.fillStyle = `rgba(59, 130, 246, ${0.6 * (1 - progress)})`;
          ctx.beginPath();
          ctx.arc(x, y, 1.5, 0, Math.PI * 2);
          ctx.fill();
        });
      }
    }
  });

  return (
    <div className="constellation-container">
      <canvas
        ref={canvasRef}
        width={800}
        height={600}
        className="constellation-canvas"
      />
      
      <div className="constellation-labels">
        <div className="label capital" style={{ top: '20%', left: '50%' }}>Capital</div>
        <div className="label advantage" style={{ top: '50%', right: '15%' }}>Advantage</div>
        <div className="label market" style={{ bottom: '20%', left: '50%' }}>Market</div>
        <div className="label people" style={{ top: '50%', left: '15%' }}>People</div>
      </div>
    </div>
  );
};