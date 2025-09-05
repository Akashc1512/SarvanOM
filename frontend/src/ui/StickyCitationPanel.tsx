"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { ScrollArea } from "@/ui/ui/ScrollArea";
import { Separator } from "@/ui/ui/separator";
import { type Source } from "@/services/api";
import {
  ExternalLink,
  BookOpen,
  Globe,
  Database,
  FileText,
  Star,
  Calendar,
  User,
  Eye,
  Copy,
  Check,
  X,
  AlertCircle,
  Info,
  Pin,
  PinOff,
  ChevronUp,
  ChevronDown,
  Accessibility,
  Contrast
} from "lucide-react";
import { useToast } from "@/hooks/useToast";
import { CitationSkeleton } from "@/ui/atoms/skeleton";
import { cn } from "@/lib/utils";

interface StickyCitationPanelProps {
  sources: Source[];
  title?: string;
  maxDisplay?: number;
  isLoading?: boolean;
  isSticky?: boolean;
  onToggleSticky?: (sticky: boolean) => void;
  className?: string;
}

export function StickyCitationPanel({ 
  sources, 
  title = "Live Sources & Citations",
  maxDisplay = 5,
  isLoading = false,
  isSticky = true,
  onToggleSticky,
  className
}: StickyCitationPanelProps) {
  const { toast } = useToast();
  const [selectedSource, setSelectedSource] = useState<Source | null>(null);
  const [copiedSource, setCopiedSource] = useState<string | null>(null);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [highContrast, setHighContrast] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

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

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && selectedSource) {
        setSelectedSource(null);
      }
      if (e.key === 'Tab' && e.shiftKey && isSticky) {
        // Focus management for sticky panel
        const focusableElements = panelRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements && focusableElements.length > 0) {
          const firstElement = focusableElements[0] as HTMLElement;
          firstElement.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedSource, isSticky]);

  const handleCopySource = async (source: Source) => {
    try {
      const sourceText = `${source.title}\n${source.url}\n${source.snippet || ''}`;
      await navigator.clipboard.writeText(sourceText);
      setCopiedSource(source.url);
      toast({
        title: "Source copied",
        description: "Source information copied to clipboard",
      });
      setTimeout(() => setCopiedSource(null), 2000);
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy source information",
        variant: "destructive",
      });
    }
  };

  const getSourceIcon = (source: Source) => {
    const domain = new URL(source.url).hostname.toLowerCase();
    if (domain.includes('wikipedia')) return <BookOpen className="h-4 w-4" />;
    if (domain.includes('stackoverflow') || domain.includes('stackexchange')) return <Database className="h-4 w-4" />;
    if (domain.includes('github')) return <FileText className="h-4 w-4" />;
    if (domain.includes('arxiv')) return <FileText className="h-4 w-4" />;
    return <Globe className="h-4 w-4" />;
  };

  const getSourceType = (source: Source) => {
    const domain = new URL(source.url).hostname.toLowerCase();
    if (domain.includes('wikipedia')) return 'Wikipedia';
    if (domain.includes('stackoverflow')) return 'Stack Overflow';
    if (domain.includes('stackexchange')) return 'Stack Exchange';
    if (domain.includes('github')) return 'GitHub';
    if (domain.includes('arxiv')) return 'arXiv';
    if (domain.includes('mdn')) return 'MDN';
    return 'Web';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "bg-green-500/20 text-green-400 border-green-500/30";
    if (confidence >= 0.6) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    return "bg-red-500/20 text-red-400 border-red-500/30";
  };

  const displayedSources = sources.slice(0, maxDisplay);
  const hasMoreSources = sources.length > maxDisplay;

  if (isLoading) {
    return (
      <motion.div
        ref={panelRef}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: reducedMotion ? 0 : 0.3 }}
        className={cn(
          "w-full max-w-md",
          isSticky && "sticky top-4",
          className
        )}
      >
        <Card className={cn(
          "bg-[var(--card)]/90 backdrop-blur-sm border-[var(--border)]",
          highContrast && "border-2 border-[var(--accent)]"
        )}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-[var(--fg)]">
                {title}
              </CardTitle>
              <div className="flex items-center gap-2">
                <Accessibility className="h-4 w-4 text-[var(--fg)]/60" />
                <Contrast className="h-4 w-4 text-[var(--fg)]/60" />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <CitationSkeleton key={i} />
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  if (!sources.length) {
    return null;
  }

  return (
    <motion.div
      ref={panelRef}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: isVisible ? 1 : 0, y: isVisible ? 0 : 20 }}
      transition={{ duration: reducedMotion ? 0 : 0.3 }}
      className={cn(
        "w-full max-w-md",
        isSticky && "sticky top-4",
        className
      )}
      role="complementary"
      aria-label="Sources and citations panel"
    >
      <Card className={cn(
        "bg-[var(--card)]/90 backdrop-blur-sm border-[var(--border)] shadow-lg",
        highContrast && "border-2 border-[var(--accent)]",
        isCollapsed && "overflow-hidden"
      )}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-semibold text-[var(--fg)]">
              {title}
            </CardTitle>
            <div className="flex items-center gap-2">
              {/* Accessibility indicators */}
              {highContrast && (
                <Contrast className="h-4 w-4 text-[var(--accent)]" title="High contrast mode active" />
              )}
              {reducedMotion && (
                <Accessibility className="h-4 w-4 text-[var(--accent)]" title="Reduced motion mode active" />
              )}
              
              {/* Sticky toggle */}
              {onToggleSticky && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onToggleSticky(!isSticky)}
                  className="h-8 w-8 p-0"
                  aria-label={isSticky ? "Unpin panel" : "Pin panel"}
                >
                  {isSticky ? <Pin className="h-4 w-4" /> : <PinOff className="h-4 w-4" />}
                </Button>
              )}
              
              {/* Collapse toggle */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="h-8 w-8 p-0"
                aria-label={isCollapsed ? "Expand panel" : "Collapse panel"}
              >
                {isCollapsed ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
              </Button>
            </div>
          </div>
          <CardDescription className="text-[var(--fg)]/70">
            {sources.length} source{sources.length !== 1 ? 's' : ''} found
            {hasMoreSources && ` (showing ${maxDisplay})`}
          </CardDescription>
        </CardHeader>

        <AnimatePresence>
          {!isCollapsed && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: reducedMotion ? 0 : 0.2 }}
            >
              <CardContent className="pt-0">
                <ScrollArea className="h-[400px] pr-4">
                  <div className="space-y-3">
                    {displayedSources.map((source, index) => (
                      <motion.div
                        key={source.url}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ 
                          duration: reducedMotion ? 0 : 0.2,
                          delay: index * 0.1 
                        }}
                        className="group"
                      >
                        <Card className={cn(
                          "bg-[var(--card)]/50 border-[var(--border)]/50 hover:bg-[var(--card)]/80 transition-all duration-200",
                          highContrast && "border-2 hover:border-[var(--accent)]",
                          "focus-within:ring-2 focus-within:ring-[var(--accent)] focus-within:ring-offset-2"
                        )}>
                          <CardContent className="p-4">
                            <div className="flex items-start gap-3">
                              <div className="flex-shrink-0 mt-1">
                                {getSourceIcon(source)}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-start justify-between gap-2 mb-2">
                                  <h4 className="font-medium text-[var(--fg)] line-clamp-2 group-hover:text-[var(--accent)] transition-colors">
                                    {source.title}
                                  </h4>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleCopySource(source)}
                                    className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                                    aria-label={`Copy source: ${source.title}`}
                                  >
                                    {copiedSource === source.url ? (
                                      <Check className="h-3 w-3 text-green-500" />
                                    ) : (
                                      <Copy className="h-3 w-3" />
                                    )}
                                  </Button>
                                </div>
                                
                                <div className="flex items-center gap-2 mb-2">
                                  <Badge 
                                    variant="outline" 
                                    className={cn(
                                      "text-xs",
                                      getConfidenceColor(source.confidence || 0.8)
                                    )}
                                  >
                                    {getSourceType(source)}
                                  </Badge>
                                  {source.confidence && (
                                    <Badge 
                                      variant="outline"
                                      className="text-xs bg-[var(--accent)]/20 text-[var(--accent)] border-[var(--accent)]/30"
                                    >
                                      {Math.round(source.confidence * 100)}% confidence
                                    </Badge>
                                  )}
                                </div>
                                
                                {source.snippet && (
                                  <p className="text-sm text-[var(--fg)]/70 line-clamp-2 mb-2">
                                    {source.snippet}
                                  </p>
                                )}
                                
                                <div className="flex items-center justify-between">
                                  <a
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1 text-xs text-[var(--accent)] hover:text-[var(--accent-hover)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--accent)] focus:ring-offset-2 rounded"
                                    aria-label={`Open source: ${source.title}`}
                                  >
                                    <ExternalLink className="h-3 w-3" />
                                    View source
                                  </a>
                                  
                                  {source.published_date && (
                                    <span className="text-xs text-[var(--fg)]/50 flex items-center gap-1">
                                      <Calendar className="h-3 w-3" />
                                      {new Date(source.published_date).toLocaleDateString()}
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </motion.div>
                    ))}
                    
                    {hasMoreSources && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: displayedSources.length * 0.1 }}
                        className="text-center py-4"
                      >
                        <p className="text-sm text-[var(--fg)]/60">
                          +{sources.length - maxDisplay} more sources available
                        </p>
                      </motion.div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
}
