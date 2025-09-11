"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { Button } from "@/ui/ui/button";
import { Card, CardContent } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { 
  Search, 
  Home, 
  ArrowLeft, 
  Compass, 
  AlertTriangle,
  Sparkles,
  Globe,
  BookOpen,
  BarChart3
} from "lucide-react";

export default function NotFound() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleGoBack = () => {
    if (isClient && typeof window !== "undefined") {
      window.history.back();
    }
  };

  const popularPages = [
    { href: "/", label: "Home", icon: Home, description: "Main dashboard" },
    { href: "/search", label: "Search", icon: Search, description: "Knowledge search" },
    { href: "/analytics", label: "Analytics", icon: BarChart3, description: "Platform insights" },
    { href: "/blog", label: "Blog", icon: BookOpen, description: "Latest articles" },
    { href: "/multimodal-demo", label: "Upload", icon: Globe, description: "File upload" }
  ];

  return (
    <div className="cosmic-bg-primary min-h-screen relative overflow-hidden">
      {/* Starfield Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div 
          className="absolute inset-0 opacity-20 animate-starfield cosmic-starfield"
          style={{
            background: `
              radial-gradient(1px 1px at 20% 30%, rgba(59, 130, 246, 0.4) 0, transparent 40%),
              radial-gradient(1px 1px at 80% 20%, rgba(168, 85, 247, 0.3) 0, transparent 40%),
              radial-gradient(1px 1px at 40% 70%, rgba(59, 130, 246, 0.2) 0, transparent 40%),
              radial-gradient(1px 1px at 90% 90%, rgba(168, 85, 247, 0.3) 0, transparent 40%)
            `,
            backgroundSize: '200px 200px, 300px 300px, 150px 150px, 250px 250px'
          }}
        />
      </div>

      <div className="relative z-10 flex items-center justify-center min-h-screen p-6">
        <div className="w-full max-w-2xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            {/* 404 Icon */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="flex items-center justify-center mb-8"
            >
              <div className="relative">
                <div className="w-24 h-24 bg-cosmic-error/20 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-12 h-12 text-cosmic-error" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-cosmic-primary-500 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold cosmic-text-primary">404</span>
                </div>
              </div>
            </motion.div>

            {/* Error Message */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mb-8"
            >
              <h1 className="text-6xl font-bold cosmic-text-primary mb-4">404</h1>
              <h2 className="text-2xl font-semibold cosmic-text-primary mb-4">
                Lost in the Cosmos
              </h2>
              <p className="text-lg cosmic-text-secondary max-w-md mx-auto">
                The page you're looking for seems to have drifted into the void. 
                Don't worry, even the best explorers sometimes take a wrong turn.
              </p>
            </motion.div>

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
            >
              <Button asChild className="cosmic-btn-primary">
                <Link href="/">
                  <Home className="w-4 h-4 mr-2" />
                  Return Home
                </Link>
              </Button>

              <Button variant="outline" asChild className="cosmic-btn-secondary">
                <Link href="/search">
                  <Search className="w-4 h-4 mr-2" />
                  Start Searching
                </Link>
              </Button>

              <Button
                variant="ghost"
                onClick={handleGoBack}
                className="cosmic-btn-secondary"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Go Back
              </Button>
            </motion.div>

            {/* Popular Pages */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Card className="cosmic-card">
                <CardContent className="p-8">
                  <div className="text-center mb-6">
                    <div className="flex items-center justify-center mb-4">
                      <Compass className="w-6 h-6 text-cosmic-primary-500 mr-2" />
                      <h3 className="text-lg font-semibold cosmic-text-primary">
                        Popular Destinations
                      </h3>
                    </div>
                    <p className="cosmic-text-secondary text-sm">
                      Here are some pages you might find interesting
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {popularPages.map((page, index) => (
                      <motion.div
                        key={page.href}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 + index * 0.1 }}
                      >
                        <Link href={page.href}>
                          <div className="cosmic-bg-secondary rounded-lg p-4 border border-cosmic-border-primary hover:border-cosmic-primary-500/50 transition-all duration-200 group">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 bg-cosmic-primary-500/20 rounded-lg flex items-center justify-center group-hover:bg-cosmic-primary-500/30 transition-colors">
                                <page.icon className="w-5 h-5 text-cosmic-primary-500" />
                              </div>
                              <div className="text-left">
                                <h4 className="font-medium cosmic-text-primary group-hover:text-cosmic-primary-400 transition-colors">
                                  {page.label}
                                </h4>
                                <p className="text-xs cosmic-text-tertiary">
                                  {page.description}
                                </p>
                              </div>
                            </div>
                          </div>
                        </Link>
                      </motion.div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Status Badge */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="mt-8"
            >
              <Badge variant="outline" className="border-cosmic-success text-cosmic-success">
                <Sparkles className="w-3 h-3 mr-1" />
                System Operational
              </Badge>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
