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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/ui/ui/dialog";
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
} from "lucide-react";
import { useToast } from "@/hooks/useToast";

interface CitationPanelProps {
  sources: Source[];
  title?: string;
  maxDisplay?: number;
}

export function CitationPanel({ 
  sources, 
  title = "Sources & Citations",
  maxDisplay = 5 
}: CitationPanelProps) {
  const { toast } = useToast();
  const [selectedSource, setSelectedSource] = useState<Source | null>(null);
  const [showAll, setShowAll] = useState(false);

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType) {
      case "web":
        return <Globe className="h-4 w-4" />;
      case "document":
        return <FileText className="h-4 w-4" />;
      case "database":
        return <Database className="h-4 w-4" />;
      case "api":
        return <BookOpen className="h-4 w-4" />;
      default:
        return <BookOpen className="h-4 w-4" />;
    }
  };

  const getSourceTypeLabel = (sourceType: string) => {
    switch (sourceType) {
      case "web":
        return "Web";
      case "document":
        return "Document";
      case "database":
        return "Database";
      case "api":
        return "API";
      default:
        return "Unknown";
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return "bg-green-100 text-green-800";
    if (score >= 0.6) return "bg-yellow-100 text-yellow-800";
    if (score >= 0.4) return "bg-orange-100 text-orange-800";
    return "bg-red-100 text-red-800";
  };

  const getCredibilityColor = (score?: number) => {
    if (!score) return "bg-gray-100 text-gray-800";
    if (score >= 0.8) return "bg-green-100 text-green-800";
    if (score >= 0.6) return "bg-yellow-100 text-yellow-800";
    if (score >= 0.4) return "bg-orange-100 text-orange-800";
    return "bg-red-100 text-red-800";
  };

  const handleCopyUrl = async (url: string) => {
    try {
      await navigator.clipboard.writeText(url);
      toast({
        title: "URL copied",
        description: "Source URL has been copied to clipboard",
      });
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy URL to clipboard",
        variant: "destructive",
      });
    }
  };

  const handleOpenSource = (url: string) => {
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const displayedSources = showAll ? sources : sources.slice(0, maxDisplay);
  const hasMore = sources.length > maxDisplay;

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BookOpen className="h-5 w-5" />
          {title}
          <Badge variant="secondary">{sources.length}</Badge>
        </CardTitle>
        <CardDescription>
          Sources and references used to generate this answer
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {displayedSources.map((source, index) => (
            <div
              key={index}
              className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    {getSourceIcon(source.source_type)}
                    <Badge variant="outline" className="text-xs">
                      {getSourceTypeLabel(source.source_type)}
                    </Badge>
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${getRelevanceColor(source.relevance_score)}`}
                    >
                      Relevance: {(source.relevance_score * 100).toFixed(0)}%
                    </Badge>
                    {source.credibility_score && (
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${getCredibilityColor(source.credibility_score)}`}
                      >
                        Credibility: {(source.credibility_score * 100).toFixed(0)}%
                      </Badge>
                    )}
                  </div>
                  
                  <h4 className="font-medium text-gray-900 mb-2 line-clamp-2">
                    {source.title}
                  </h4>
                  
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {source.snippet}
                  </p>
                  
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Globe className="h-3 w-3" />
                    <span className="truncate">{source.url}</span>
                  </div>
                </div>
                
                <div className="flex items-center gap-1 ml-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedSource(source)}
                    className="h-8 w-8 p-0"
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleOpenSource(source.url)}
                    className="h-8 w-8 p-0"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopyUrl(source.url)}
                    className="h-8 w-8 p-0"
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
          
          {hasMore && (
            <div className="text-center pt-2">
              <Button
                variant="outline"
                onClick={() => setShowAll(!showAll)}
                className="text-sm"
              >
                {showAll ? `Show Less` : `Show ${sources.length - maxDisplay} More Sources`}
              </Button>
            </div>
          )}
        </div>
      </CardContent>

      {/* Source Detail Dialog */}
      <Dialog open={!!selectedSource} onOpenChange={() => setSelectedSource(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {getSourceIcon(selectedSource?.source_type || "web")}
              Source Details
            </DialogTitle>
          </DialogHeader>
          
          {selectedSource && (
            <ScrollArea className="max-h-[60vh]">
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-lg mb-2">{selectedSource.title}</h3>
                  <div className="flex items-center gap-2 mb-3">
                    <Badge variant="outline">
                      {getSourceTypeLabel(selectedSource.source_type)}
                    </Badge>
                    <Badge className={getRelevanceColor(selectedSource.relevance_score)}>
                      Relevance: {(selectedSource.relevance_score * 100).toFixed(0)}%
                    </Badge>
                    {selectedSource.credibility_score && (
                      <Badge className={getCredibilityColor(selectedSource.credibility_score)}>
                        Credibility: {(selectedSource.credibility_score * 100).toFixed(0)}%
                      </Badge>
                    )}
                  </div>
                </div>
                
                <Separator />
                
                <div>
                  <h4 className="font-medium mb-2">Snippet</h4>
                  <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                    {selectedSource.snippet}
                  </p>
                </div>
                
                <Separator />
                
                <div>
                  <h4 className="font-medium mb-2">URL</h4>
                  <div className="flex items-center gap-2">
                    <code className="text-sm bg-gray-100 px-2 py-1 rounded flex-1 break-all">
                      {selectedSource.url}
                    </code>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCopyUrl(selectedSource.url)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleOpenSource(selectedSource.url)}
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                
                <Separator />
                
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleOpenSource(selectedSource.url)}
                    className="flex-1"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Open Source
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleCopyUrl(selectedSource.url)}
                    className="flex-1"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy URL
                  </Button>
                </div>
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>
    </Card>
  );
} 