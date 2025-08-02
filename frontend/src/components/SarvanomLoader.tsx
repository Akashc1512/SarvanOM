import React from "react";

// Loader for Sarvanom - Universal Knowledge Hub
// All ellipses (edges) and all nodes revolve; center node pulses.

interface SarvanomLoaderProps {
  size?: number;
  className?: string;
}

export const SarvanomLoader: React.FC<SarvanomLoaderProps> = ({ size = 100, className = "" }) => (
  <div 
    className={`flex items-center justify-center ${className}`}
    style={{
      minHeight: '240px',
      width: '100%',
      background: 'transparent'
    }}
  >
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      style={{ display: "block" }}
    >
      {/* Outer blue circle */}
      <circle cx="32" cy="32" r="30" fill="#2563eb" />

      {/* Rotating group: all ellipses and orbiting nodes */}
      <g style={{
        transformOrigin: "32px 32px",
        animation: "sarvanom-spin 4s linear infinite"
      }}>
        {/* Globe ellipses (edges) */}
        <ellipse
          cx="32"
          cy="32"
          rx="20"
          ry="10"
          stroke="#fff"
          strokeWidth={2.5}
          fill="none"
        />
        <ellipse
          cx="32"
          cy="32"
          rx="10"
          ry="20"
          stroke="#fff"
          strokeWidth={2.5}
          fill="none"
          transform="rotate(45 32 32)"
        />
        <ellipse
          cx="32"
          cy="32"
          rx="10"
          ry="20"
          stroke="#fff"
          strokeWidth={2.5}
          fill="none"
          transform="rotate(-45 32 32)"
        />
        {/* Animated orbiting nodes */}
        {/* Top node */}
        <circle
          cx="32"
          cy="12"
          r="3"
          fill="#fff"
          style={{
            transformOrigin: "32px 32px",
            animation: "sarvanom-orbit1 2.5s linear infinite"
          }}
        />
        {/* Left node */}
        <circle
          cx="12"
          cy="32"
          r="3"
          fill="#fff"
          style={{
            transformOrigin: "32px 32px",
            animation: "sarvanom-orbit2 2.5s linear infinite"
          }}
        />
        {/* Right node */}
        <circle
          cx="52"
          cy="32"
          r="3"
          fill="#fff"
          style={{
            transformOrigin: "32px 32px",
            animation: "sarvanom-orbit3 2.5s linear infinite"
          }}
        />
      </g>
      {/* Pulsing + rotating center node */}
      <circle
        cx="32"
        cy="32"
        r="2"
        fill="#fff"
        style={{
          animation: "sarvanom-pulse 1.6s ease-in-out infinite, sarvanom-spin 4s linear infinite"
        }}
      />
      <style>
        {`
        @keyframes sarvanom-spin {
          100% { transform: rotate(360deg); }
        }
        @keyframes sarvanom-orbit1 {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg);}
        }
        @keyframes sarvanom-orbit2 {
          0% { transform: rotate(120deg);}
          100% { transform: rotate(480deg);}
        }
        @keyframes sarvanom-orbit3 {
          0% { transform: rotate(240deg);}
          100% { transform: rotate(600deg);}
        }
        @keyframes sarvanom-pulse {
          0%,100% { r: 2px; opacity: 1; }
          50% { r: 4px; opacity: 0.65;}
        }
        `}
      </style>
    </svg>
  </div>
);

export function SarvanomLoaderFullScreen() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <SarvanomLoader size={120} />
        <p className="mt-4 text-gray-600 text-lg font-medium">Loading SarvanOM...</p>
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