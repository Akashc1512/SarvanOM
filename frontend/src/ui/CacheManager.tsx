"use client";

import { useState, useEffect } from "react";
import { Database, Clock, Zap, RefreshCw, Trash2 } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { useToast } from "@/hooks/useToast";

interface CacheEntry {
  id: string;
  query: string;
  answer: string;
  timestamp: Date;
  confidence: number;
  processingTime: number;
  citations?: any[];
}

interface CacheManagerProps {
  onCacheHit: (entry: CacheEntry) => void;
  className?: string;
}

export function CacheManager({ onCacheHit, className = "" }: CacheManagerProps) {
  const [cacheEntries, setCacheEntries] = useState<CacheEntry[]>([]);
  const [isVisible, setIsVisible] = useState(false);
  const { toast } = useToast();

  // Load cache from localStorage on mount
  useEffect(() => {
    const savedCache = localStorage.getItem("sarvanom-cache");
    if (savedCache) {
      try {
        const parsed = JSON.parse(savedCache);
        setCacheEntries(parsed.map((entry: any) => ({
          ...entry,
          timestamp: new Date(entry.timestamp),
        })));
      } catch (error) {
        console.error("Failed to load cache:", error);
      }
    }
  }, []);

  // Save cache to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("sarvanom-cache", JSON.stringify(cacheEntries));
  }, [cacheEntries]);

  const addToCache = (entry: CacheEntry) => {
    setCacheEntries(prev => {
      // Remove duplicate if exists
      const filtered = prev.filter(e => e.id !== entry.id);
      // Add new entry at the beginning
      return [entry, ...filtered].slice(0, 50); // Keep only last 50 entries
    });
  };

  const removeFromCache = (id: string) => {
    setCacheEntries(prev => prev.filter(entry => entry.id !== id));
    toast({
      title: "Cache Cleared",
      description: "Entry removed from cache",
    });
  };

  const clearAllCache = () => {
    setCacheEntries([]);
    toast({
      title: "Cache Cleared",
      description: "All cached entries have been removed",
    });
  };

  const searchCache = (query: string): CacheEntry | null => {
    const normalizedQuery = query.toLowerCase().trim();
    return cacheEntries.find(entry => 
      entry.query.toLowerCase().trim() === normalizedQuery
    ) || null;
  };

  const getCacheStats = () => {
    const totalEntries = cacheEntries.length;
    const totalSize = new Blob([JSON.stringify(cacheEntries)]).size;
    const avgConfidence = cacheEntries.length > 0 
      ? cacheEntries.reduce((sum, entry) => sum + entry.confidence, 0) / cacheEntries.length
      : 0;
    
    return { totalEntries, totalSize, avgConfidence };
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return "Just now";
  };

  const stats = getCacheStats();

  return (
    <>
      {/* Cache Toggle Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsVisible(!isVisible)}
        className="fixed bottom-4 right-4 z-40 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50"
      >
        <Database className="h-4 w-4 mr-2" />
        Cache ({stats.totalEntries})
      </Button>

      {/* Cache Panel */}
      {isVisible && (
        <div className="fixed bottom-16 right-4 z-50 w-80">
          <Card className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 shadow-xl">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Query Cache
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    {stats.totalEntries} entries
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearAllCache}
                    className="h-6 w-6 p-0"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Cache Stats */}
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="text-center p-2 bg-gray-50 dark:bg-slate-700/50 rounded">
                  <div className="font-medium">{stats.totalEntries}</div>
                  <div className="text-gray-500 dark:text-gray-400">Entries</div>
                </div>
                <div className="text-center p-2 bg-gray-50 dark:bg-slate-700/50 rounded">
                  <div className="font-medium">{(stats.totalSize / 1024).toFixed(1)}KB</div>
                  <div className="text-gray-500 dark:text-gray-400">Size</div>
                </div>
                <div className="text-center p-2 bg-gray-50 dark:bg-slate-700/50 rounded">
                  <div className="font-medium">{Math.round(stats.avgConfidence * 100)}%</div>
                  <div className="text-gray-500 dark:text-gray-400">Avg Confidence</div>
                </div>
              </div>

              {/* Recent Entries */}
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {cacheEntries.slice(0, 5).map((entry) => (
                  <div
                    key={entry.id}
                    className="p-2 rounded border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
                    onClick={() => onCacheHit(entry)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {entry.query}
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {formatTimeAgo(entry.timestamp)}
                          </span>
                          <Badge variant="outline" className="text-xs">
                            {Math.round(entry.confidence * 100)}%
                          </Badge>
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFromCache(entry.id);
                        }}
                        className="h-6 w-6 p-0 ml-2"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Cache Info */}
              <div className="text-xs text-gray-500 dark:text-gray-400 text-center pt-2 border-t border-gray-200 dark:border-slate-700">
                <div className="flex items-center justify-center space-x-1 mb-1">
                  <Zap className="h-3 w-3" />
                  <span>Fast repeat queries</span>
                </div>
                <p>Click on any entry to load cached result</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
}

// Hook for cache management
export function useCacheManager() {
  const [cacheEntries, setCacheEntries] = useState<CacheEntry[]>([]);

  const addToCache = (entry: CacheEntry) => {
    setCacheEntries(prev => {
      const filtered = prev.filter(e => e.id !== entry.id);
      return [entry, ...filtered].slice(0, 50);
    });
  };

  const searchCache = (query: string): CacheEntry | null => {
    const normalizedQuery = query.toLowerCase().trim();
    return cacheEntries.find(entry => 
      entry.query.toLowerCase().trim() === normalizedQuery
    ) || null;
  };

  return {
    addToCache,
    searchCache,
  };
}
