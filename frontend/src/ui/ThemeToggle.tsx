"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/ui/ui/button";
import { 
  Sun, 
  Moon, 
  Monitor, 
  Palette,
  Check,
  Contrast,
  Accessibility
} from "lucide-react";
import { cn } from "@/lib/utils";

type Theme = "light" | "dark" | "system";

interface ThemeToggleProps {
  className?: string;
  showLabels?: boolean;
  size?: "sm" | "md" | "lg";
  variant?: "default" | "outline" | "ghost";
}

export function ThemeToggle({ 
  className,
  showLabels = false,
  size = "md",
  variant = "default"
}: ThemeToggleProps) {
  const [theme, setTheme] = useState<Theme>("system");
  const [mounted, setMounted] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);

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

  useEffect(() => {
    setMounted(true);
    
    // Load saved theme or default to system
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
      setTheme(savedTheme);
    } else {
      setTheme('system');
    }
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const root = document.documentElement;
    
    // Remove existing theme classes
    root.classList.remove('light', 'dark');
    
    // Apply theme
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
    
    // Save to localStorage
    localStorage.setItem('theme', theme);
    
    // Update CSS custom properties for cosmic theme
    updateCosmicTheme(theme);
  }, [theme, mounted]);

  const updateCosmicTheme = (currentTheme: Theme) => {
    const root = document.documentElement;
    const isDark = currentTheme === 'dark' || (currentTheme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    
    if (isDark) {
      // Dark cosmic theme
      root.style.setProperty('--cosmos-bg', '#0b1020');
      root.style.setProperty('--cosmos-fg', '#e2e8f0');
      root.style.setProperty('--cosmos-card', '#1a2332');
      root.style.setProperty('--cosmos-accent', '#3b82f6');
      root.style.setProperty('--cosmos-accent-hover', '#2563eb');
      root.style.setProperty('--cosmos-border', '#334155');
      root.style.setProperty('--cosmos-muted', '#64748b');
    } else {
      // Light cosmic theme
      root.style.setProperty('--cosmos-bg', '#f8fafc');
      root.style.setProperty('--cosmos-fg', '#1e293b');
      root.style.setProperty('--cosmos-card', '#ffffff');
      root.style.setProperty('--cosmos-accent', '#3b82f6');
      root.style.setProperty('--cosmos-accent-hover', '#2563eb');
      root.style.setProperty('--cosmos-border', '#e2e8f0');
      root.style.setProperty('--cosmos-muted', '#64748b');
    }
  };

  const cycleTheme = () => {
    const themes: Theme[] = ['light', 'dark', 'system'];
    const currentIndex = themes.indexOf(theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    setTheme(themes[nextIndex]);
  };

  const getThemeIcon = () => {
    switch (theme) {
      case 'light':
        return <Sun className="h-4 w-4" />;
      case 'dark':
        return <Moon className="h-4 w-4" />;
      case 'system':
        return <Monitor className="h-4 w-4" />;
      default:
        return <Monitor className="h-4 w-4" />;
    }
  };

  const getThemeLabel = () => {
    switch (theme) {
      case 'light':
        return 'Light mode';
      case 'dark':
        return 'Dark mode';
      case 'system':
        return 'System theme';
      default:
        return 'System theme';
    }
  };

  const sizeClasses = {
    sm: "h-8 w-8",
    md: "h-10 w-10",
    lg: "h-12 w-12"
  };

  const iconSizes = {
    sm: "h-3 w-3",
    md: "h-4 w-4",
    lg: "h-5 w-5"
  };

  if (!mounted) {
    return (
      <Button
        variant={variant}
        size={size}
        className={cn(sizeClasses[size], className)}
        disabled
        aria-label="Loading theme toggle"
      >
        <div className={cn("animate-spin", iconSizes[size])}>
          <Palette />
        </div>
      </Button>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <Button
        variant={variant}
        size={size}
        onClick={cycleTheme}
        className={cn(
          sizeClasses[size],
          "relative overflow-hidden",
          highContrast && "border-2 border-[var(--accent)]",
          className
        )}
        aria-label={`Switch to ${getThemeLabel()}`}
        title={`Current: ${getThemeLabel()}. Click to cycle themes.`}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={theme}
            initial={{ opacity: 0, rotate: -90 }}
            animate={{ opacity: 1, rotate: 0 }}
            exit={{ opacity: 0, rotate: 90 }}
            transition={{ 
              duration: reducedMotion ? 0 : 0.2,
              ease: "easeInOut"
            }}
            className="flex items-center justify-center"
          >
            {getThemeIcon()}
          </motion.div>
        </AnimatePresence>
      </Button>
      
      {showLabels && (
        <span className="text-sm text-[var(--fg)]/70">
          {getThemeLabel()}
        </span>
      )}
      
      {/* Accessibility indicators */}
      <div className="flex items-center gap-1">
        {highContrast && (
          <Contrast 
            className="h-3 w-3 text-[var(--accent)]" 
            title="High contrast mode active"
            aria-label="High contrast mode active"
          />
        )}
        {reducedMotion && (
          <Accessibility 
            className="h-3 w-3 text-[var(--accent)]" 
            title="Reduced motion mode active"
            aria-label="Reduced motion mode active"
          />
        )}
      </div>
    </div>
  );
}

// Theme provider hook
export function useTheme() {
  const [theme, setTheme] = useState<Theme>("system");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
      setTheme(savedTheme);
    }
  }, []);

  const updateTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  return {
    theme,
    setTheme: updateTheme,
    mounted,
    isDark: theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  };
}