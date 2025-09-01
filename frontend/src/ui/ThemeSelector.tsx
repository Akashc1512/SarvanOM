"use client";

import { useState, useEffect } from "react";
import { Palette, Sparkles, Moon, Sun, Zap, Star, Globe } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { cn } from "@/lib/utils";

interface CosmicTheme {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
  };
  gradients: {
    background: string;
    surface: string;
    accent: string;
  };
  particles: {
    count: number;
    speed: number;
    theme: "purple" | "blue" | "mixed";
  };
}

const cosmicThemes: CosmicTheme[] = [
  {
    id: "cosmic-purple",
    name: "Cosmic Purple",
    description: "Deep space with purple nebulas and star clusters",
    icon: <Sparkles className="h-5 w-5" />,
    colors: {
      primary: "#8b5cf6",
      secondary: "#a855f7",
      accent: "#c084fc",
      background: "from-slate-900 via-purple-900 to-slate-900",
      surface: "bg-slate-800/80"
    },
    gradients: {
      background: "bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900",
      surface: "bg-slate-800/80",
      accent: "from-purple-600 to-purple-700"
    },
    particles: {
      count: 60,
      speed: 0.8,
      theme: "purple"
    }
  },
  {
    id: "nebula-blue",
    name: "Nebula Blue",
    description: "Ethereal blue nebulas with cosmic dust",
    icon: <Globe className="h-5 w-5" />,
    colors: {
      primary: "#3b82f6",
      secondary: "#60a5fa",
      accent: "#93c5fd",
      background: "from-slate-900 via-blue-900 to-slate-900",
      surface: "bg-slate-800/80"
    },
    gradients: {
      background: "bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900",
      surface: "bg-slate-800/80",
      accent: "from-blue-600 to-blue-700"
    },
    particles: {
      count: 80,
      speed: 0.6,
      theme: "blue"
    }
  },
  {
    id: "aurora-borealis",
    name: "Aurora Borealis",
    description: "Northern lights with green and purple auroras",
    icon: <Zap className="h-5 w-5" />,
    colors: {
      primary: "#10b981",
      secondary: "#8b5cf6",
      accent: "#06b6d4",
      background: "from-slate-900 via-emerald-900 to-purple-900",
      surface: "bg-slate-800/80"
    },
    gradients: {
      background: "bg-gradient-to-br from-slate-900 via-emerald-900 to-purple-900",
      surface: "bg-slate-800/80",
      accent: "from-emerald-600 to-purple-600"
    },
    particles: {
      count: 100,
      speed: 0.4,
      theme: "mixed"
    }
  },
  {
    id: "solar-flare",
    name: "Solar Flare",
    description: "Intense solar activity with orange and yellow bursts",
    icon: <Sun className="h-5 w-5" />,
    colors: {
      primary: "#f59e0b",
      secondary: "#f97316",
      accent: "#ef4444",
      background: "from-slate-900 via-orange-900 to-red-900",
      surface: "bg-slate-800/80"
    },
    gradients: {
      background: "bg-gradient-to-br from-slate-900 via-orange-900 to-red-900",
      surface: "bg-slate-800/80",
      accent: "from-orange-600 to-red-600"
    },
    particles: {
      count: 120,
      speed: 1.2,
      theme: "mixed"
    }
  },
  {
    id: "cosmic-twilight",
    name: "Cosmic Twilight",
    description: "Gentle twilight with soft pinks and purples",
    icon: <Moon className="h-5 w-5" />,
    colors: {
      primary: "#ec4899",
      secondary: "#a855f7",
      accent: "#f472b6",
      background: "from-slate-900 via-pink-900 to-purple-900",
      surface: "bg-slate-800/80"
    },
    gradients: {
      background: "bg-gradient-to-br from-slate-900 via-pink-900 to-purple-900",
      surface: "bg-slate-800/80",
      accent: "from-pink-600 to-purple-600"
    },
    particles: {
      count: 40,
      speed: 0.3,
      theme: "purple"
    }
  },
  {
    id: "stellar-cluster",
    name: "Stellar Cluster",
    description: "Dense star cluster with white and blue stars",
    icon: <Star className="h-5 w-5" />,
    colors: {
      primary: "#f8fafc",
      secondary: "#60a5fa",
      accent: "#cbd5e1",
      background: "from-slate-900 via-slate-800 to-blue-900",
      surface: "bg-slate-800/80"
    },
    gradients: {
      background: "bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900",
      surface: "bg-slate-800/80",
      accent: "from-slate-600 to-blue-600"
    },
    particles: {
      count: 150,
      speed: 0.5,
      theme: "blue"
    }
  }
];

interface ThemeSelectorProps {
  className?: string;
  onThemeChange?: (theme: CosmicTheme) => void;
}

export function ThemeSelector({ className = "", onThemeChange }: ThemeSelectorProps) {
  const [selectedTheme, setSelectedTheme] = useState<string>("cosmic-purple");
  const [isOpen, setIsOpen] = useState(false);
  const [previewTheme, setPreviewTheme] = useState<CosmicTheme | null>(null);

  useEffect(() => {
    const savedTheme = localStorage.getItem("sarvanom-cosmic-theme");
    if (savedTheme && cosmicThemes.find(t => t.id === savedTheme)) {
      setSelectedTheme(savedTheme);
    }
  }, []);

  const handleThemeSelect = (theme: CosmicTheme) => {
    setSelectedTheme(theme.id);
    localStorage.setItem("sarvanom-cosmic-theme", theme.id);
    onThemeChange?.(theme);
    setIsOpen(false);
  };

  const currentTheme = cosmicThemes.find(t => t.id === selectedTheme) || cosmicThemes[0];

  return (
    <div className={cn("relative", className)}>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "relative overflow-hidden transition-all duration-300",
          "bg-gradient-to-r from-purple-500/10 to-blue-500/10",
          "border-purple-200/50 dark:border-purple-800/50",
          "hover:from-purple-500/20 hover:to-blue-500/20",
          "hover:scale-105 active:scale-95",
          "group"
        )}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        <div className="relative z-10 flex items-center space-x-2">
          <Palette className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          <span className="text-sm font-medium">Theme</span>
        </div>
        <Sparkles className="absolute -top-1 -right-1 h-3 w-3 text-purple-400 opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:animate-pulse" />
      </Button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 z-50 w-80">
          <Card className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 shadow-xl">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Choose Your Cosmic Theme
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 gap-3 max-h-96 overflow-y-auto">
                {cosmicThemes.map((theme) => (
                  <button
                    key={theme.id}
                    onClick={() => handleThemeSelect(theme)}
                    onMouseEnter={() => setPreviewTheme(theme)}
                    onMouseLeave={() => setPreviewTheme(null)}
                    className={cn(
                      "relative p-4 rounded-lg border transition-all duration-200 text-left",
                      "hover:scale-105 active:scale-95",
                      selectedTheme === theme.id
                        ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                        : "border-gray-200 dark:border-slate-700 hover:border-purple-300 dark:hover:border-purple-600"
                    )}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={cn(
                        "p-2 rounded-lg",
                        selectedTheme === theme.id
                          ? "bg-purple-100 dark:bg-purple-800/50"
                          : "bg-gray-100 dark:bg-slate-700/50"
                      )}>
                        {theme.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-semibold text-gray-900 dark:text-white">
                            {theme.name}
                          </h4>
                          {selectedTheme === theme.id && (
                            <Badge variant="outline" className="text-xs">
                              Active
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                          {theme.description}
                        </p>
                        <div className="flex items-center space-x-2">
                          <div className="flex space-x-1">
                            <div 
                              className="w-3 h-3 rounded-full border border-gray-300 dark:border-slate-600"
                              style={{ backgroundColor: theme.colors.primary }}
                            />
                            <div 
                              className="w-3 h-3 rounded-full border border-gray-300 dark:border-slate-600"
                              style={{ backgroundColor: theme.colors.secondary }}
                            />
                            <div 
                              className="w-3 h-3 rounded-full border border-gray-300 dark:border-slate-600"
                              style={{ backgroundColor: theme.colors.accent }}
                            />
                          </div>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {theme.particles.count} particles
                          </span>
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              
              {previewTheme && (
                <div className="mt-4 p-3 rounded-lg bg-gray-50 dark:bg-slate-700/50 border border-gray-200 dark:border-slate-600">
                  <div className="flex items-center space-x-2 mb-2">
                    <Sparkles className="h-4 w-4 text-purple-500 dark:text-purple-400" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Preview: {previewTheme.name}
                    </span>
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    <p>• {previewTheme.particles.count} animated particles</p>
                    <p>• {previewTheme.particles.speed}x animation speed</p>
                    <p>• {previewTheme.particles.theme} color theme</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

export function useCosmicTheme() {
  const [currentTheme, setCurrentTheme] = useState<CosmicTheme>(cosmicThemes[0]);

  useEffect(() => {
    const savedThemeId = localStorage.getItem("sarvanom-cosmic-theme");
    if (savedThemeId) {
      const theme = cosmicThemes.find(t => t.id === savedThemeId);
      if (theme) {
        setCurrentTheme(theme);
      }
    }
  }, []);

  const updateTheme = (theme: CosmicTheme) => {
    setCurrentTheme(theme);
    localStorage.setItem("sarvanom-cosmic-theme", theme.id);
  };

  return { currentTheme, updateTheme, availableThemes: cosmicThemes };
}
