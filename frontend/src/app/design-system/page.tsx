"use client";

import React from "react";
import { StandardLayout, StandardCard, StandardButton } from "@/components/layout/StandardLayout";
import { motion } from "framer-motion";

export default function DesignSystemPage() {
  return (
    <StandardLayout
      title="Design System Showcase"
      description="Demonstrating the standardized cosmic theme design tokens, layout utilities, and component patterns used throughout SarvanOM."
    >
      <div className="space-y-8">
        {/* Design Tokens Section */}
        <StandardCard
          title="Design Tokens"
          description="CSS custom properties and standardized values for consistent theming"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium text-[var(--fg)]">Colors</h4>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: "var(--bg)" }}></div>
                  <span className="text-sm text-[var(--fg)]/70">--bg</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: "var(--fg)" }}></div>
                  <span className="text-sm text-[var(--fg)]/70">--fg</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: "var(--accent)" }}></div>
                  <span className="text-sm text-[var(--fg)]/70">--accent</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded" style={{ backgroundColor: "var(--card)" }}></div>
                  <span className="text-sm text-[var(--fg)]/70">--card</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium text-[var(--fg)]">Typography</h4>
              <div className="space-y-2">
                <div className="text-title text-[var(--fg)]">Title Text</div>
                <div className="text-body text-[var(--fg)]/80">Body Text</div>
                <div className="text-sm text-[var(--fg)]/60">Small Text</div>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium text-[var(--fg)]">Spacing</h4>
              <div className="space-y-2">
                <div className="text-sm text-[var(--fg)]/70">container-std: max-w-7xl</div>
                <div className="text-sm text-[var(--fg)]/70">section-std: space-y-6 py-6</div>
                <div className="text-sm text-[var(--fg)]/70">Standardized 8px base unit</div>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium text-[var(--fg)]">Components</h4>
              <div className="space-y-2">
                <div className="text-sm text-[var(--fg)]/70">card-std: Rounded cards</div>
                <div className="text-sm text-[var(--fg)]/70">link-std: Accent underlined</div>
                <div className="text-sm text-[var(--fg)]/70">cosmic: Starfield background</div>
              </div>
            </div>
          </div>
        </StandardCard>

        {/* Layout Utilities Section */}
        <StandardCard
          title="Layout Utilities"
          description="Standardized container sizes, spacing, and responsive layouts"
        >
          <div className="space-y-6">
            <div>
              <h4 className="font-medium text-[var(--fg)] mb-3">Container Standards</h4>
              <div className="bg-[var(--card)]/50 p-4 rounded-lg">
                <div className="container-std bg-[var(--accent)]/20 p-4 rounded">
                  <p className="text-[var(--fg)]">container-std: max-w-7xl with responsive padding</p>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-[var(--fg)] mb-3">Section Spacing</h4>
              <div className="section-std bg-[var(--card)]/50 rounded-lg">
                <div className="bg-[var(--accent)]/20 p-4 rounded mb-6">
                  <p className="text-[var(--fg)]">Section with standardized spacing</p>
                </div>
                <div className="bg-[var(--accent)]/20 p-4 rounded">
                  <p className="text-[var(--fg)]">Consistent vertical rhythm</p>
                </div>
              </div>
            </div>
          </div>
        </StandardCard>

        {/* Component Examples Section */}
        <StandardCard
          title="Component Examples"
          description="Standardized button variants and interactive elements"
        >
          <div className="space-y-6">
            <div>
              <h4 className="font-medium text-[var(--fg)] mb-3">Button Variants</h4>
              <div className="flex flex-wrap gap-4">
                <StandardButton variant="primary" size="sm">
                  Primary Small
                </StandardButton>
                <StandardButton variant="primary" size="md">
                  Primary Medium
                </StandardButton>
                <StandardButton variant="primary" size="lg">
                  Primary Large
                </StandardButton>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-[var(--fg)] mb-3">Secondary & Outline</h4>
              <div className="flex flex-wrap gap-4">
                <StandardButton variant="secondary">
                  Secondary Button
                </StandardButton>
                <StandardButton variant="outline">
                  Outline Button
                </StandardButton>
                <StandardButton disabled>
                  Disabled Button
                </StandardButton>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-[var(--fg)] mb-3">Interactive Elements</h4>
              <div className="space-y-3">
                <a href="#" className="link-std">
                  Standard link with accent underline
                </a>
                <div className="card-std p-4 hover:bg-[var(--card)]/80 transition-colors cursor-pointer">
                  <p className="text-[var(--fg)]">Interactive card with hover effects</p>
                </div>
              </div>
            </div>
          </div>
        </StandardCard>

        {/* Cosmic Theme Section */}
        <StandardCard
          title="Cosmic Theme"
          description="Space-inspired background and visual effects"
        >
          <div className="space-y-4">
            <div className="cosmic p-8 rounded-lg text-center">
              <h4 className="text-xl font-semibold text-white mb-2">Cosmic Starfield</h4>
              <p className="text-white/80">
                Performance-optimized radial gradient starfield background
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-[var(--accent)]/20 to-purple-500/20 p-4 rounded-lg">
                <h5 className="font-medium text-[var(--fg)] mb-2">Gradient Cards</h5>
                <p className="text-[var(--fg)]/70 text-sm">
                  Subtle gradients for depth and visual interest
                </p>
              </div>
              <div className="bg-[var(--card)]/50 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                <h5 className="font-medium text-[var(--fg)] mb-2">Glassmorphism</h5>
                <p className="text-[var(--fg)]/70 text-sm">
                  Backdrop blur effects for modern UI aesthetics
                </p>
              </div>
            </div>
          </div>
        </StandardCard>

        {/* Usage Guidelines */}
        <StandardCard
          title="Usage Guidelines"
          description="Best practices for implementing the design system"
        >
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-[var(--fg)] mb-2">CSS Classes</h4>
              <ul className="space-y-1 text-sm text-[var(--fg)]/70">
                <li>• Use <code className="bg-[var(--card)]/50 px-1 rounded">container-std</code> for main content areas</li>
                <li>• Apply <code className="bg-[var(--card)]/50 px-1 rounded">section-std</code> for consistent vertical spacing</li>
                <li>• Use <code className="bg-[var(--card)]/50 px-1 rounded">card-std</code> for content containers</li>
                <li>• Apply <code className="bg-[var(--card)]/50 px-1 rounded">cosmic</code> for starfield backgrounds</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-[var(--fg)] mb-2">Component Usage</h4>
              <ul className="space-y-1 text-sm text-[var(--fg)]/70">
                <li>• Import and use <code className="bg-[var(--card)]/50 px-1 rounded">StandardLayout</code> for page structure</li>
                <li>• Use <code className="bg-[var(--card)]/50 px-1 rounded">StandardCard</code> for content sections</li>
                <li>• Apply <code className="bg-[var(--card)]/50 px-1 rounded">StandardButton</code> for consistent interactions</li>
                <li>• Leverage CSS variables for custom styling: <code className="bg-[var(--card)]/50 px-1 rounded">var(--accent)</code></li>
              </ul>
            </div>
          </div>
        </StandardCard>
      </div>
    </StandardLayout>
  );
}
