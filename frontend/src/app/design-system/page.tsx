"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { 
  SwatchIcon,
  PaintBrushIcon,
  EyeIcon,
  CodeBracketIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from "@heroicons/react/24/outline";

interface ComponentExample {
  name: string;
  description: string;
  code: string;
  component: React.ReactNode;
  category: string;
}

export default function DesignSystemPage() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [expandedComponents, setExpandedComponents] = useState<Set<string>>(new Set());

  const categories = [
    { id: "all", name: "All Components", icon: SwatchIcon },
    { id: "buttons", name: "Buttons", icon: PaintBrushIcon },
    { id: "cards", name: "Cards", icon: SwatchIcon },
    { id: "inputs", name: "Inputs", icon: CodeBracketIcon },
    { id: "navigation", name: "Navigation", icon: EyeIcon },
    { id: "feedback", name: "Feedback", icon: CheckIcon }
  ];

  const copyToClipboard = async (code: string, componentName: string) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(componentName);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const toggleComponent = (componentName: string) => {
    const newExpanded = new Set(expandedComponents);
    if (newExpanded.has(componentName)) {
      newExpanded.delete(componentName);
    } else {
      newExpanded.add(componentName);
    }
    setExpandedComponents(newExpanded);
  };

  const components: ComponentExample[] = [
    // Buttons
    {
      name: "Primary Button",
      description: "Main call-to-action button with cosmic glow effect",
      category: "buttons",
      code: `<button className="cosmic-btn-primary">
  Primary Action
</button>`,
      component: (
        <button className="cosmic-btn-primary">
          Primary Action
        </button>
      )
    },
    {
      name: "Secondary Button",
      description: "Secondary action button with subtle styling",
      category: "buttons",
      code: `<button className="cosmic-btn-secondary">
  Secondary Action
</button>`,
      component: (
        <button className="cosmic-btn-secondary">
          Secondary Action
        </button>
      )
    },
    {
      name: "Ghost Button",
      description: "Minimal button for subtle actions",
      category: "buttons",
      code: `<button className="cosmic-btn-ghost">
  Ghost Action
</button>`,
      component: (
        <button className="cosmic-btn-ghost">
          Ghost Action
        </button>
      )
    },
    {
      name: "Danger Button",
      description: "Destructive action button with error styling",
      category: "buttons",
      code: `<button className="cosmic-btn-danger">
  Delete Item
</button>`,
      component: (
        <button className="cosmic-btn-danger">
          Delete Item
        </button>
      )
    },

    // Cards
    {
      name: "Basic Card",
      description: "Standard card with cosmic styling and hover effects",
      category: "cards",
      code: `<div className="cosmic-card p-6">
  <h3 className="cosmic-text-primary font-semibold mb-2">Card Title</h3>
  <p className="cosmic-text-secondary">Card content goes here</p>
</div>`,
      component: (
        <div className="cosmic-card p-6">
          <h3 className="cosmic-text-primary font-semibold mb-2">Card Title</h3>
          <p className="cosmic-text-secondary">Card content goes here</p>
        </div>
      )
    },
    {
      name: "Glass Card",
      description: "Glass morphism card with backdrop blur",
      category: "cards",
      code: `<div className="cosmic-card-glass p-6">
  <h3 className="cosmic-text-primary font-semibold mb-2">Glass Card</h3>
  <p className="cosmic-text-secondary">Transparent with blur effect</p>
</div>`,
      component: (
        <div className="cosmic-card-glass p-6">
          <h3 className="cosmic-text-primary font-semibold mb-2">Glass Card</h3>
          <p className="cosmic-text-secondary">Transparent with blur effect</p>
        </div>
      )
    },
    {
      name: "Metric Tile",
      description: "KPI/metric display card with hover lift effect",
      category: "cards",
      code: `<div className="cosmic-tile-metric cosmic-hover-lift p-6">
  <div className="text-2xl font-bold cosmic-text-primary">1,234</div>
  <div className="cosmic-text-secondary">Total Users</div>
</div>`,
      component: (
        <div className="cosmic-tile-metric cosmic-hover-lift p-6">
          <div className="text-2xl font-bold cosmic-text-primary">1,234</div>
          <div className="cosmic-text-secondary">Total Users</div>
        </div>
      )
    },

    // Inputs
    {
      name: "Text Input",
      description: "Standard text input with cosmic styling",
      category: "inputs",
      code: `<input 
  type="text" 
  placeholder="Enter text..." 
  className="cosmic-input"
/>`,
      component: (
        <input 
          type="text" 
          placeholder="Enter text..." 
          className="cosmic-input"
        />
      )
    },
    {
      name: "Search Input",
      description: "Search input with cosmic glow and icon",
      category: "inputs",
      code: `<div className="cosmic-search-container">
  <input 
    type="text" 
    placeholder="Search..." 
    className="cosmic-search-input"
  />
  <button className="cosmic-btn-primary">
    Search
  </button>
</div>`,
      component: (
        <div className="cosmic-search-container">
          <input 
            type="text" 
            placeholder="Search..." 
            className="cosmic-search-input"
          />
          <button className="cosmic-btn-primary">
            Search
          </button>
        </div>
      )
    },
    {
      name: "Textarea",
      description: "Multi-line text input with cosmic styling",
      category: "inputs",
      code: `<textarea 
  placeholder="Enter description..." 
  className="cosmic-input min-h-[100px] resize-none"
/>`,
      component: (
        <textarea 
          placeholder="Enter description..." 
          className="cosmic-input min-h-[100px] resize-none"
        />
      )
    },

    // Navigation
    {
      name: "Nav Item",
      description: "Navigation item with hover effects",
      category: "navigation",
      code: `<a href="#" className="cosmic-nav-item">
  Navigation Item
</a>`,
      component: (
        <a href="#" className="cosmic-nav-item">
          Navigation Item
        </a>
      )
    },
    {
      name: "Breadcrumb",
      description: "Breadcrumb navigation with cosmic styling",
      category: "navigation",
      code: `<nav className="flex items-center space-x-2 text-sm">
  <a href="#" className="cosmic-text-tertiary hover:cosmic-text-primary">
    Home
  </a>
  <span className="cosmic-text-tertiary">/</span>
  <span className="cosmic-text-primary font-medium">Current Page</span>
</nav>`,
      component: (
        <nav className="flex items-center space-x-2 text-sm">
          <a href="#" className="cosmic-text-tertiary hover:cosmic-text-primary">
            Home
          </a>
          <span className="cosmic-text-tertiary">/</span>
          <span className="cosmic-text-primary font-medium">Current Page</span>
        </nav>
      )
    },

    // Feedback
    {
      name: "Success Alert",
      description: "Success message with cosmic success styling",
      category: "feedback",
      code: `<div className="cosmic-card border-cosmic-success/20 bg-cosmic-success/5 p-4">
  <div className="flex items-center gap-2">
    <CheckIcon className="w-5 h-5 text-cosmic-success" />
    <span className="cosmic-text-primary">Operation completed successfully</span>
  </div>
</div>`,
      component: (
        <div className="cosmic-card border-cosmic-success/20 bg-cosmic-success/5 p-4">
          <div className="flex items-center gap-2">
            <CheckIcon className="w-5 h-5 text-cosmic-success" />
            <span className="cosmic-text-primary">Operation completed successfully</span>
          </div>
        </div>
      )
    },
    {
      name: "Error Alert",
      description: "Error message with cosmic error styling",
      category: "feedback",
      code: `<div className="cosmic-card border-cosmic-error/20 bg-cosmic-error/5 p-4">
  <div className="flex items-center gap-2">
    <XMarkIcon className="w-5 h-5 text-cosmic-error" />
    <span className="cosmic-text-primary">An error occurred</span>
  </div>
</div>`,
      component: (
        <div className="cosmic-card border-cosmic-error/20 bg-cosmic-error/5 p-4">
          <div className="flex items-center gap-2">
            <XMarkIcon className="w-5 h-5 text-cosmic-error" />
            <span className="cosmic-text-primary">An error occurred</span>
          </div>
        </div>
      )
    },
    {
      name: "Loading State",
      description: "Loading indicator with cosmic animation",
      category: "feedback",
      code: `<div className="cosmic-card p-6 text-center">
  <div className="cosmic-spinner mx-auto mb-4"></div>
  <p className="cosmic-text-secondary">Loading...</p>
</div>`,
      component: (
        <div className="cosmic-card p-6 text-center">
          <div className="cosmic-spinner mx-auto mb-4"></div>
          <p className="cosmic-text-secondary">Loading...</p>
        </div>
      )
    }
  ];

  const filteredComponents = selectedCategory === "all" 
    ? components 
    : components.filter(comp => comp.category === selectedCategory);

  return (
    <div className="min-h-screen cosmic-bg-primary">
      <div className="cosmic-container cosmic-section">
        {/* Header */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-cosmic-primary-500 to-cosmic-secondary-500 text-white px-4 py-2 rounded-full text-sm font-medium mb-6"
          >
            <SwatchIcon className="w-4 h-4" />
            Design System
          </motion.div>
          <h1 className="text-4xl font-bold cosmic-text-primary mb-4">
            Cosmic Pro Component Library
          </h1>
          <p className="text-lg cosmic-text-secondary max-w-3xl mx-auto">
            A comprehensive collection of reusable UI components built with the Cosmic Pro design system. 
            Each component is designed for consistency, accessibility, and visual excellence.
          </p>
        </div>

        {/* Category Filter */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-wrap gap-2 mb-8 justify-center"
        >
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300 ${
                selectedCategory === category.id
                  ? "cosmic-btn-primary"
                  : "cosmic-btn-secondary"
              }`}
            >
              <category.icon className="w-4 h-4" />
              {category.name}
            </button>
          ))}
        </motion.div>

        {/* Components Grid */}
        <div className="space-y-8">
          {filteredComponents.map((component, index) => (
            <motion.div
              key={component.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="cosmic-card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold cosmic-text-primary mb-1">
                    {component.name}
                  </h3>
                  <p className="cosmic-text-secondary text-sm">
                    {component.description}
                  </p>
                </div>
                <button
                  onClick={() => toggleComponent(component.name)}
                  className="cosmic-btn-ghost p-2"
                >
                  {expandedComponents.has(component.name) ? (
                    <ChevronDownIcon className="w-5 h-5" />
                  ) : (
                    <ChevronRightIcon className="w-5 h-5" />
                  )}
                </button>
              </div>

              {/* Component Preview */}
              <div className="mb-4 p-6 bg-cosmic-bg-secondary rounded-lg border border-cosmic-border-primary">
                {component.component}
              </div>

              {/* Code Section */}
              {expandedComponents.has(component.name) && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <h4 className="cosmic-text-primary font-medium">Code Example</h4>
                    <button
                      onClick={() => copyToClipboard(component.code, component.name)}
                      className="cosmic-btn-secondary flex items-center gap-2 text-sm"
                    >
                      {copiedCode === component.name ? (
                        <>
                          <CheckIcon className="w-4 h-4" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <ClipboardDocumentIcon className="w-4 h-4" />
                          Copy Code
                        </>
                      )}
                    </button>
                  </div>
                  <pre className="bg-cosmic-bg-tertiary p-4 rounded-lg overflow-x-auto">
                    <code className="text-sm cosmic-text-primary">{component.code}</code>
                  </pre>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Design Tokens Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-16 cosmic-card p-8"
        >
          <h2 className="text-2xl font-bold cosmic-text-primary mb-6 text-center">
            Design Tokens
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Colors */}
            <div>
              <h3 className="cosmic-text-primary font-semibold mb-4">Colors</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-cosmic-primary-500 rounded"></div>
                  <span className="cosmic-text-secondary text-sm">cosmic-primary-500</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-cosmic-secondary-500 rounded"></div>
                  <span className="cosmic-text-secondary text-sm">cosmic-secondary-500</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-cosmic-success rounded"></div>
                  <span className="cosmic-text-secondary text-sm">cosmic-success</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-cosmic-warning rounded"></div>
                  <span className="cosmic-text-secondary text-sm">cosmic-warning</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-cosmic-error rounded"></div>
                  <span className="cosmic-text-secondary text-sm">cosmic-error</span>
                </div>
              </div>
            </div>

            {/* Typography */}
            <div>
              <h3 className="cosmic-text-primary font-semibold mb-4">Typography</h3>
              <div className="space-y-3">
                <div>
                  <h1 className="text-2xl font-bold cosmic-text-primary">Heading 1</h1>
                  <p className="cosmic-text-tertiary text-xs">text-2xl font-bold</p>
                </div>
                <div>
                  <h2 className="text-xl font-semibold cosmic-text-primary">Heading 2</h2>
                  <p className="cosmic-text-tertiary text-xs">text-xl font-semibold</p>
                </div>
                <div>
                  <p className="cosmic-text-primary">Body Text</p>
                  <p className="cosmic-text-tertiary text-xs">cosmic-text-primary</p>
                </div>
                <div>
                  <p className="cosmic-text-secondary">Secondary Text</p>
                  <p className="cosmic-text-tertiary text-xs">cosmic-text-secondary</p>
                </div>
              </div>
            </div>

            {/* Spacing */}
            <div>
              <h3 className="cosmic-text-primary font-semibold mb-4">Spacing</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-cosmic-primary-500 rounded"></div>
                  <span className="cosmic-text-secondary text-sm">0.5rem (2)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-4 h-2 bg-cosmic-primary-500 rounded"></div>
                  <span className="cosmic-text-secondary text-sm">1rem (4)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-6 h-2 bg-cosmic-primary-500 rounded"></div>
                  <span className="cosmic-text-secondary text-sm">1.5rem (6)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-2 bg-cosmic-primary-500 rounded"></div>
                  <span className="cosmic-text-secondary text-sm">2rem (8)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-2 bg-cosmic-primary-500 rounded"></div>
                  <span className="cosmic-text-secondary text-sm">3rem (12)</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}