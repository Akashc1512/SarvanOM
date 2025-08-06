"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/ui/ui/dialog";
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
  Info
} from "lucide-react";
import { useToast } from "@/hooks/useToast";
import { CitationSkeleton } from "@/ui/atoms/skeleton";

interface CitationPanelProps {
  sources: Source[];
  title?: string;
  maxDisplay?: number;
  isLoading?: boolean;
}

export function CitationPanel({ 
  sources, 
  title = "Sources & Citations",
  maxDisplay = 5,
  isLoading = false
}: CitationPanelProps) {
  const { toast } = useToast();
  const [selectedSource, setSelectedSource] = useState<Source | null>(null);
  const [showAll, setShowAll] = useState(false);
  const [isClient, setIsClient] = useState(false);

  // Ensure we're on the client side
  useState(() => {
    setIsClient(true);
  });

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType.toLowerCase()) {
      case "web":
        return <Globe className="h-4 w-4" />;
      case "document":
        return <FileText className="h-4 w-4" />;
      case "database":
        return <Database className="h-4 w-4" />;
      default:
        return <Globe className="h-4 w-4" />;
    }
  };

  const getSourceTypeLabel = (sourceType: string) => {
    switch (sourceType.toLowerCase()) {
      case "web":
        return "Web";
      case "document":
        return "Document";
      case "database":
        return "Database";
      default:
        return sourceType;
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return "text-green-600";
    if (score >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const getCredibilityColor = (score?: number) => {
    if (!score) return "text-gray-600";
    if (score >= 0.8) return "text-green-600";
    if (score >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const handleCopyUrl = async (url: string) => {
    try {
      if (isClient && navigator.clipboard) {
        await navigator.clipboard.writeText(url);
        toast({
          title: "URL copied",
          description: "Source URL copied to clipboard",
        });
      }
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy URL to clipboard",
        variant: "destructive",
      });
    }
  };

  const handleOpenSource = (url: string) => {
    if (isClient && typeof window !== "undefined") {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  // Show loading skeleton when loading
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <CitationSkeleton />
        </CardContent>
      </Card>
    );
  }

  // Show empty state if no sources
  if (!sources || sources.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <Info className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-muted-foreground mb-2">
                No sources available
              </h3>
              <p className="text-sm text-muted-foreground">
                No citations or sources were found for this response.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const displayedSources = showAll ? sources : sources.slice(0, maxDisplay);
  const hasMoreSources = sources.length > maxDisplay;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            {title}
          </CardTitle>
          <Badge variant="secondary">
            {sources.length} source{sources.length !== 1 ? 's' : ''}
          </Badge>
        </div>
        <CardDescription>
          References and sources used to generate this response
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {displayedSources.map((source, index) => (
            <div
              key={source.url || index}
              className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    {getSourceIcon(source.source_type)}
                    <span className="text-sm font-medium">
                      {source.title || "Untitled Source"}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      {getSourceTypeLabel(source.source_type)}
                    </Badge>
                  </div>
                  
                  {source.snippet && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {source.snippet}
                    </p>
                  )}
                  
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    {source.relevance_score && (
                      <div className="flex items-center gap-1">
                        <Star className="h-3 w-3" />
                        <span className={getRelevanceColor(source.relevance_score)}>
                          Relevance: {(source.relevance_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                    {source.credibility_score && (
                      <div className="flex items-center gap-1">
                        <Check className="h-3 w-3" />
                        <span className={getCredibilityColor(source.credibility_score)}>
                          Credibility: {(source.credibility_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-1 ml-4">
                  {source.url && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCopyUrl(source.url!)}
                        className="h-8 w-8 p-0"
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleOpenSource(source.url!)}
                        className="h-8 w-8 p-0"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {hasMoreSources && (
            <div className="text-center">
              <Button
                variant="outline"
                onClick={() => setShowAll(!showAll)}
                className="w-full"
              >
                {showAll ? "Show Less" : `Show ${sources.length - maxDisplay} More`}
              </Button>
            </div>
          )}
        </div>

        {/* Source Detail Dialog */}
        {selectedSource && (
          <Dialog open={!!selectedSource} onOpenChange={() => setSelectedSource(null)}>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  {getSourceIcon(selectedSource.source_type)}
                  {selectedSource.title || "Source Details"}
                </DialogTitle>
              </DialogHeader>
              <ScrollArea className="max-h-96">
                <div className="space-y-4">
                  {selectedSource.snippet && (
                    <div>
                      <h4 className="font-medium mb-2">Content</h4>
                      <p className="text-sm text-muted-foreground">
                        {selectedSource.snippet}
                      </p>
                    </div>
                  )}
                  
                  {selectedSource.url && (
                    <div>
                      <h4 className="font-medium mb-2">URL</h4>
                      <p className="text-sm text-blue-600 break-all">
                        {selectedSource.url}
                      </p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 gap-4">
                    {selectedSource.relevance_score && (
                      <div>
                        <h4 className="font-medium mb-1">Relevance Score</h4>
                        <p className={`text-sm ${getRelevanceColor(selectedSource.relevance_score)}`}>
                          {(selectedSource.relevance_score * 100).toFixed(1)}%
                        </p>
                      </div>
                    )}
                    {selectedSource.credibility_score && (
                      <div>
                        <h4 className="font-medium mb-1">Credibility Score</h4>
                        <p className={`text-sm ${getCredibilityColor(selectedSource.credibility_score)}`}>
                          {(selectedSource.credibility_score * 100).toFixed(1)}%
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </ScrollArea>
            </DialogContent>
          </Dialog>
        )}
      </CardContent>
    </Card>
  );
} 