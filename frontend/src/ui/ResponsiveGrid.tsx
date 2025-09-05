"use client";

import { ReactNode, useRef, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { 
  Grid3X3, 
  LayoutGrid, 
  List, 
  Maximize2,
  Minimize2,
  Accessibility,
  Contrast
} from "lucide-react";
import { Button } from "@/ui/ui/button";

type GridLayout = "grid" | "masonry" | "list" | "fullscreen";

interface ResponsiveGridProps {
  children: ReactNode[];
  className?: string;
  defaultLayout?: GridLayout;
  showLayoutToggle?: boolean;
  showAccessibilityControls?: boolean;
  minItemWidth?: number;
  gap?: number;
  maxColumns?: number;
}

export function ResponsiveGrid({
  children,
  className,
  defaultLayout = "grid",
  showLayoutToggle = true,
  showAccessibilityControls = true,
  minItemWidth = 300,
  gap = 16,
  maxColumns = 4
}: ResponsiveGridProps) {
  const [layout, setLayout] = useState<GridLayout>(defaultLayout);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [containerWidth, setContainerWidth] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Accessibility: Check for user preferences
  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches;
    
    setReducedMotion(prefersReducedMotion);
    setHighContrast(prefersHighContrast);

    // Listen for changes
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const contrastQuery = window.matchMedia('(prefers-contrast: high)');
    
    const handleMotionChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    const handleContrastChange = (e: MediaQueryListEvent) => setHighContrast(e.matches);
    
    motionQuery.addEventListener('change', handleMotionChange);
    contrastQuery.addEventListener('change', handleContrastChange);
    
    return () => {
      motionQuery.removeEventListener('change', handleMotionChange);
      contrastQuery.removeEventListener('change', handleContrastChange);
    };
  }, []);

  // Calculate responsive columns
  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth);
      }
    };

    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  const calculateColumns = () => {
    if (layout === "list") return 1;
    if (layout === "fullscreen") return 1;
    
    const availableWidth = containerWidth - (gap * 2); // Account for padding
    const columns = Math.floor(availableWidth / (minItemWidth + gap));
    return Math.min(Math.max(columns, 1), maxColumns);
  };

  const columns = calculateColumns();

  const getLayoutClasses = () => {
    switch (layout) {
      case "grid":
        return `grid-cols-1 sm:grid-cols-2 lg:grid-cols-${Math.min(columns, 3)} xl:grid-cols-${columns}`;
      case "masonry":
        return "columns-1 sm:columns-2 lg:columns-3 xl:columns-4";
      case "list":
        return "grid-cols-1";
      case "fullscreen":
        return "grid-cols-1";
      default:
        return "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3";
    }
  };

  const getItemClasses = () => {
    switch (layout) {
      case "masonry":
        return "break-inside-avoid mb-4";
      case "list":
        return "w-full";
      case "fullscreen":
        return "w-full h-full";
      default:
        return "w-full";
    }
  };

  const layoutVariants = {
    grid: {
      hidden: { opacity: 0, scale: 0.8 },
      visible: { opacity: 1, scale: 1 },
      exit: { opacity: 0, scale: 0.8 }
    },
    masonry: {
      hidden: { opacity: 0, y: 20 },
      visible: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: -20 }
    },
    list: {
      hidden: { opacity: 0, x: -20 },
      visible: { opacity: 1, x: 0 },
      exit: { opacity: 0, x: 20 }
    },
    fullscreen: {
      hidden: { opacity: 0, scale: 0.9 },
      visible: { opacity: 1, scale: 1 },
      exit: { opacity: 0, scale: 0.9 }
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: reducedMotion ? 0 : 0.1,
        delayChildren: reducedMotion ? 0 : 0.1
      }
    },
    exit: {
      opacity: 0,
      transition: {
        staggerChildren: reducedMotion ? 0 : 0.05,
        staggerDirection: -1
      }
    }
  };

  return (
    <div 
      ref={containerRef}
      className={cn(
        "w-full",
        isFullscreen && "fixed inset-0 z-50 bg-[var(--cosmos-bg)] p-4",
        className
      )}
      role="region"
      aria-label="Responsive content grid"
    >
      {/* Controls */}
      {(showLayoutToggle || showAccessibilityControls) && (
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            {showLayoutToggle && (
              <div className="flex items-center gap-1" role="group" aria-label="Layout options">
                <Button
                  variant={layout === "grid" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setLayout("grid")}
                  aria-label="Grid layout"
                  title="Grid layout"
                >
                  <Grid3X3 className="h-4 w-4" />
                </Button>
                <Button
                  variant={layout === "masonry" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setLayout("masonry")}
                  aria-label="Masonry layout"
                  title="Masonry layout"
                >
                  <LayoutGrid className="h-4 w-4" />
                </Button>
                <Button
                  variant={layout === "list" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setLayout("list")}
                  aria-label="List layout"
                  title="List layout"
                >
                  <List className="h-4 w-4" />
                </Button>
                <Button
                  variant={layout === "fullscreen" ? "default" : "outline"}
                  size="sm"
                  onClick={() => {
                    setLayout("fullscreen");
                    setIsFullscreen(!isFullscreen);
                  }}
                  aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
                  title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
                >
                  {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                </Button>
              </div>
            )}
          </div>
          
          {showAccessibilityControls && (
            <div className="flex items-center gap-2">
              {highContrast && (
                <Contrast 
                  className="h-4 w-4 text-[var(--accent)]" 
                  title="High contrast mode active"
                  aria-label="High contrast mode active"
                />
              )}
              {reducedMotion && (
                <Accessibility 
                  className="h-4 w-4 text-[var(--accent)]" 
                  title="Reduced motion mode active"
                  aria-label="Reduced motion mode active"
                />
              )}
            </div>
          )}
        </div>
      )}

      {/* Grid Container */}
      <AnimatePresence mode="wait">
        <motion.div
          key={layout}
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          className={cn(
            "grid gap-4",
            getLayoutClasses(),
            layout === "masonry" && "columns-1 sm:columns-2 lg:columns-3 xl:columns-4"
          )}
          style={{
            gap: `${gap}px`,
            ...(highContrast && {
              border: `2px solid var(--cosmos-accent)`,
              borderRadius: '8px',
              padding: '8px'
            })
          }}
        >
          {children.map((child, index) => (
            <motion.div
              key={index}
              variants={layoutVariants[layout]}
              className={cn(
                getItemClasses(),
                highContrast && "border-2 border-[var(--cosmos-accent)] rounded-lg p-2"
              )}
              role="article"
              aria-label={`Content item ${index + 1}`}
            >
              {child}
            </motion.div>
          ))}
        </motion.div>
      </AnimatePresence>

      {/* Grid Info */}
      <div className="mt-4 text-sm text-[var(--cosmos-fg)]/60 text-center">
        {layout === "grid" && `${columns} column${columns !== 1 ? 's' : ''} • Grid layout`}
        {layout === "masonry" && "Masonry layout • Responsive columns"}
        {layout === "list" && "List layout • Single column"}
        {layout === "fullscreen" && "Fullscreen layout • Focused view"}
        {highContrast && " • High contrast mode"}
        {reducedMotion && " • Reduced motion"}
      </div>
    </div>
  );
}

// Grid item wrapper for consistent styling
export function GridItem({ 
  children, 
  className,
  ...props 
}: { 
  children: ReactNode; 
  className?: string;
  [key: string]: any;
}) {
  return (
    <div 
      className={cn(
        "bg-[var(--cosmos-card)]/90 backdrop-blur-sm border border-[var(--cosmos-border)] rounded-lg p-4",
        "hover:bg-[var(--cosmos-card)]/95 transition-all duration-200",
        "focus-within:ring-2 focus-within:ring-[var(--cosmos-accent)] focus-within:ring-offset-2",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
