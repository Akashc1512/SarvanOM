"use client";

import { useState, useEffect } from "react";
import { Moon, Sun, Sparkles } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { cn } from "@/lib/utils";

interface ThemeToggleProps {
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function ThemeToggle({ className, size = "md" }: ThemeToggleProps) {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Check for saved theme preference or default to light
    const savedTheme = localStorage.getItem("sarvanom-theme") as "light" | "dark" | null;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.classList.toggle("dark", savedTheme === "dark");
    } else if (prefersDark) {
      setTheme("dark");
      document.documentElement.classList.add("dark");
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("sarvanom-theme", newTheme);
    document.documentElement.classList.toggle("dark");
  };

  // Prevent hydration mismatch
  if (!mounted) {
    return (
      <Button
        variant="outline"
        size={size}
        className={cn(
          "relative overflow-hidden transition-all duration-300",
          "bg-gradient-to-r from-purple-500/10 to-blue-500/10",
          "border-purple-200/50 dark:border-purple-800/50",
          "hover:from-purple-500/20 hover:to-blue-500/20",
          "animate-pulse",
          className
        )}
        disabled
      >
        <div className="w-4 h-4 bg-gray-300 dark:bg-gray-600 rounded-full" />
      </Button>
    );
  }

  return (
    <Button
      variant="outline"
      size={size}
      onClick={toggleTheme}
      className={cn(
        "relative overflow-hidden transition-all duration-500",
        "bg-gradient-to-r from-purple-500/10 to-blue-500/10",
        "border-purple-200/50 dark:border-purple-800/50",
        "hover:from-purple-500/20 hover:to-blue-500/20",
        "hover:scale-105 active:scale-95",
        "group",
        className
      )}
      aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
    >
      {/* Cosmic background effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      {/* Floating particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1 left-2 w-1 h-1 bg-purple-400/60 rounded-full animate-pulse" />
        <div className="absolute top-3 right-1 w-0.5 h-0.5 bg-blue-400/60 rounded-full animate-pulse delay-100" />
        <div className="absolute bottom-2 left-3 w-0.5 h-0.5 bg-purple-300/60 rounded-full animate-pulse delay-200" />
      </div>

      {/* Icon with smooth transition */}
      <div className="relative z-10 transition-transform duration-300 group-hover:rotate-12">
        {theme === "light" ? (
          <Moon className="h-4 w-4 text-purple-600 dark:text-purple-400" />
        ) : (
          <Sun className="h-4 w-4 text-yellow-500 dark:text-yellow-400" />
        )}
      </div>

      {/* Sparkle effect on hover */}
      <Sparkles className="absolute -top-1 -right-1 h-3 w-3 text-purple-400 opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:animate-pulse" />
    </Button>
  );
}
