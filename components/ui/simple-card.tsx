import React, { useEffect, useRef, useCallback, useState } from "react";

interface SimpleCardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

const SimpleCard: React.FC<SimpleCardProps> = ({ children, className = "", onClick }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);
  const [mouseX, setMouseX] = useState(50);
  const [mouseY, setMouseY] = useState(50);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;

    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateXValue = (y - centerY) / 10;
    const rotateYValue = (centerX - x) / 10;
    
    const mouseXPercent = (x / rect.width) * 100;
    const mouseYPercent = (y / rect.height) * 100;
    
    setRotateX(rotateXValue);
    setRotateY(rotateYValue);
    setMouseX(mouseXPercent);
    setMouseY(mouseYPercent);
  }, []);

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
    setRotateX(0);
    setRotateY(0);
    setMouseX(50);
    setMouseY(50);
  }, []);

  const cardStyle: React.CSSProperties = {
    position: 'relative',
    width: '100%',
    height: '100%',
    borderRadius: '16px',
    overflow: 'hidden',
    cursor: 'pointer',
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) ${isHovered ? 'scale(1.02)' : 'scale(1)'}`,
    transition: isHovered ? 'none' : 'transform 0.5s ease-out',
    boxShadow: isHovered 
      ? '0 20px 40px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1)'
      : '0 4px 8px rgba(0, 0, 0, 0.1)',
  };

  const shineStyle: React.CSSProperties = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `radial-gradient(circle at ${mouseX}% ${mouseY}%, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.1) 20%, transparent 50%)`,
    opacity: isHovered ? 1 : 0,
    transition: 'opacity 0.3s ease',
    pointerEvents: 'none',
    borderRadius: 'inherit',
    zIndex: 2,
  };

  const glareStyle: React.CSSProperties = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(135deg, transparent 40%, rgba(255, 255, 255, 0.1) 50%, transparent 60%)',
    opacity: isHovered ? 1 : 0,
    transform: isHovered ? 'translateX(100%)' : 'translateX(-100%)',
    transition: 'opacity 0.3s ease, transform 0.6s ease',
    pointerEvents: 'none',
    borderRadius: 'inherit',
    zIndex: 3,
  };

  return (
    <div
      ref={cardRef}
      className={className}
      style={cardStyle}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
    >
      <div style={shineStyle} />
      <div style={glareStyle} />
      <div style={{ position: 'relative', zIndex: 4, width: '100%', height: '100%' }}>
        {children}
      </div>
    </div>
  );
};

export default SimpleCard; 