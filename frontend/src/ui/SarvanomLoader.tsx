"use client";

import React from "react";

// Loader for Sarvanom - Enhanced Cosmic Galaxy
// 200 individual particles with vibrant cosmic colors rotating around a central star

interface SarvanomLoaderProps {
  size?: number;
  className?: string;
}

export const SarvanomLoader: React.FC<SarvanomLoaderProps> = ({ size = 120, className = "" }) => (
  <div 
    className={`flex items-center justify-center ${className}`}
    style={{
      minHeight: '240px',
      width: '100%',
      background: 'transparent'
    }}
  >
    <div className="relative" style={{ width: size, height: size }}>
      {/* 200 individual particles with enhanced cosmic colors */}
      {[...Array(200)].map((_, i) => {
        const particleTypes = [
          { color: 'from-cyan-300 to-blue-400', size: 2.5 }, // Blue stars
          { color: 'from-purple-300 to-pink-400', size: 2 }, // Purple stars
          { color: 'from-yellow-300 to-orange-400', size: 1.8 }, // Yellow stars
          { color: 'from-green-300 to-emerald-400', size: 1.5 }, // Green stars
          { color: 'from-red-300 to-pink-400', size: 2.2 }, // Red giants
          { color: 'from-indigo-300 to-purple-400', size: 1.6 }, // Indigo stars
          { color: 'from-teal-300 to-cyan-400', size: 1.9 }, // Teal stars
          { color: 'from-amber-300 to-yellow-400', size: 2.1 }, // Amber stars
        ];
        const particleType = particleTypes[i % particleTypes.length];
        
        return (
          <div
            key={i}
            className={`absolute top-1/2 left-1/2 bg-gradient-to-r ${particleType.color} rounded-full`}
            style={{
              width: `${Math.random() * particleType.size + 0.5}px`,
              height: `${Math.random() * particleType.size + 0.5}px`,
              transform: `rotate(${i * 18}deg) translate(${Math.random() * (size * 0.45) + size * 0.08}px)`,
              animationDelay: `${-i * 0.1}s`,
              opacity: `${Math.random() * 0.9 + 0.1}`,
              zIndex: Math.floor(Math.random() * 15),
              filter: 'drop-shadow(0 0 2px currentColor)',
              animation: 'spin-slow 120s linear infinite',
            }}
          />
        );
      })}

      {/* Central star with enhanced glow */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div 
          className="w-6 h-6 bg-gradient-to-br from-yellow-300 via-orange-400 to-red-500 rounded-full animate-pulse"
          style={{
            boxShadow: '0 0 20px rgba(251, 191, 36, 0.8), 0 0 30px rgba(251, 146, 60, 0.6), 0 0 40px rgba(239, 68, 68, 0.4), 0 0 50px rgba(220, 38, 38, 0.2)'
          }}
        />
        {/* Inner core */}
        <div 
          className="absolute w-3 h-3 bg-gradient-to-br from-white to-yellow-200 rounded-full animate-pulse"
          style={{
            animationDelay: '0.5s',
            boxShadow: '0 0 10px rgba(255, 255, 255, 0.9), 0 0 20px rgba(251, 191, 36, 0.7)'
          }}
        />
      </div>

      {/* Orbital rings for depth */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div 
          className="w-16 h-16 border border-cyan-300/20 rounded-full" 
          style={{ 
            animation: 'spin-slow 180s linear infinite'
          }} 
        />
        <div 
          className="w-24 h-24 border border-purple-300/15 rounded-full" 
          style={{ 
            animation: 'spin-slow 240s linear infinite reverse'
          }} 
        />
        <div 
          className="w-32 h-32 border border-pink-300/10 rounded-full" 
          style={{ 
            animation: 'spin-slow 300s linear infinite'
          }} 
        />
      </div>
    </div>
  </div>
);

export function SarvanomLoaderFullScreen() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900 flex items-center justify-center">
      <div className="text-center">
        <SarvanomLoader size={120} />
        <p className="mt-6 text-cyan-300 text-lg font-medium">Loading SarvanOM...</p>
        <p className="mt-2 text-purple-300 text-sm">Cosmic knowledge awaits</p>
      </div>
    </div>
  );
}

export function SarvanomLoaderInline({ size = 40 }: { size?: number }) {
  return (
    <div className="flex items-center justify-center p-4">
      <SarvanomLoader size={size} />
    </div>
  );
}

export default SarvanomLoader; 