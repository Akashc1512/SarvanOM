"use client";

import { useState } from "react";
import { Card, CardContent } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { Button } from "@/ui/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/ui/ui/dialog";
import { ScrollArea } from "@/ui/ui/ScrollArea";
import { 
  ExternalLink, 
  Copy, 
  Globe, 
  FileText, 
  Database, 
  Star, 
  CheckCircle, 
  AlertCircle,
  Calendar,
  User,
  Eye,
  BookOpen,
  Video,
  Image
} from "lucide-react";
import { useToast } from "@/hooks/useToast";

interface SourceCardProps {
  source: {
    marker?: string;
    title: string;
    url: string;
    snippet?: string;
    domain: string;
    provider: string;
    relevance_score?: number;
    credibility_score?: number;
    source_type?: string;
    metadata?: {
      published_date?: string;
      author?: string;
      views?: number;
      duration?: string;
      thumbnail?: string;
      media_type?: "image" | "video" | "document";
    };
  };
  showMarker?: boolean;
  compact?: boolean;
}

export function SourceCard({ source, showMarker = true, compact = false }: SourceCardProps) {
  const { toast } = useToast();
  const [showDetails, setShowDetails] = useState(false);

  const getSourceIcon = (sourceType?: string, provider?: string) => {
    if (provider?.toLowerCase().includes("youtube")) return <Video className="h-4 w-4" />;
    if (provider?.toLowerCase().includes("github")) return <Database className="h-4 w-4" />;
    if (provider?.toLowerCase().includes("arxiv")) return <FileText className="h-4 w-4" />;
    if (provider?.toLowerCase().includes("stack")) return <Globe className="h-4 w-4" />;
    if (provider?.toLowerCase().includes("mdn")) return <BookOpen className="h-4 w-4" />;
    
    switch (sourceType?.toLowerCase()) {
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

  const getRelevanceColor = (score?: number) => {
    if (!score) return "text-gray-500";
    if (score >= 0.8) return "text-green-600 dark:text-green-400";
    if (score >= 0.6) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  const getCredibilityColor = (score?: number) => {
    if (!score) return "text-gray-500";
    if (score >= 0.8) return "text-green-600 dark:text-green-400";
    if (score >= 0.6) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  const handleCopyUrl = async () => {
    try {
      await navigator.clipboard.writeText(source.url);
      toast({
        title: "URL copied",
        description: "Source URL copied to clipboard",
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy URL to clipboard",
        variant: "destructive",
      });
    }
  };

  const handleOpenSource = () => {
    window.open(source.url, '_blank', 'noopener,noreferrer');
  };

  const formatDomain = (domain: string) => {
    return domain.replace(/^www\./, '').replace(/\.com$/, '');
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    try {
      return new Date(dateString).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return null;
    }
  };

  if (compact) {
    return (
      <div className="p-3 rounded-lg bg-gray-50 dark:bg-slate-700/50 border border-gray-200 dark:border-slate-600 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              {showMarker && source.marker && (
                <Badge variant="outline" className="text-xs">
                  {source.marker}
                </Badge>
              )}
              {getSourceIcon(source.source_type, source.provider)}
              <h4 className="font-medium text-gray-900 dark:text-white text-sm truncate">
                {source.title}
              </h4>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {formatDomain(source.domain)}
              </span>
              <div className="flex items-center space-x-1">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopyUrl}
                  className="h-6 w-6 p-0"
                >
                  <Copy className="h-3 w-3" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleOpenSource}
                  className="h-6 w-6 p-0"
                >
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 hover:bg-white/90 dark:hover:bg-slate-800/90 transition-all duration-200">
        <CardContent className="p-4">
          <div className="space-y-3">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-2 flex-1 min-w-0">
                {showMarker && source.marker && (
                  <Badge variant="outline" className="text-xs">
                    {source.marker}
                  </Badge>
                )}
                {getSourceIcon(source.source_type, source.provider)}
                <h4 className="font-medium text-gray-900 dark:text-white text-sm line-clamp-2">
                  {source.title}
                </h4>
              </div>
              <Badge variant="outline" className="text-xs ml-2">
                {source.provider}
              </Badge>
            </div>

            {/* Snippet */}
            {source.snippet && (
              <p className="text-xs text-gray-600 dark:text-gray-300 line-clamp-2">
                {source.snippet}
              </p>
            )}

            {/* Metadata */}
            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <div className="flex items-center space-x-4">
                <span>{formatDomain(source.domain)}</span>
                {source.metadata?.published_date && (
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-3 w-3" />
                    <span>{formatDate(source.metadata.published_date)}</span>
                  </div>
                )}
                {source.metadata?.author && (
                  <div className="flex items-center space-x-1">
                    <User className="h-3 w-3" />
                    <span>{source.metadata.author}</span>
                  </div>
                )}
                {source.metadata?.views && (
                  <div className="flex items-center space-x-1">
                    <Eye className="h-3 w-3" />
                    <span>{source.metadata.views.toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Scores */}
            <div className="flex items-center space-x-4 text-xs">
              {source.relevance_score && (
                <div className="flex items-center space-x-1">
                  <Star className="h-3 w-3" />
                  <span className={getRelevanceColor(source.relevance_score)}>
                    Relevance: {(source.relevance_score * 100).toFixed(0)}%
                  </span>
                </div>
              )}
              {source.credibility_score && (
                <div className="flex items-center space-x-1">
                  <CheckCircle className="h-3 w-3" />
                  <span className={getCredibilityColor(source.credibility_score)}>
                    Credibility: {(source.credibility_score * 100).toFixed(0)}%
                  </span>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-slate-600">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDetails(true)}
                className="text-xs"
              >
                View Details
              </Button>
              <div className="flex items-center space-x-1">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopyUrl}
                  className="h-7 w-7 p-0"
                >
                  <Copy className="h-3 w-3" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleOpenSource}
                  className="h-7 w-7 p-0"
                >
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {getSourceIcon(source.source_type, source.provider)}
              {source.title}
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="max-h-96">
            <div className="space-y-4">
              {/* Thumbnail */}
              {source.metadata?.thumbnail && (
                <div className="relative">
                  <img
                    src={source.metadata.thumbnail}
                    alt={source.title}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  {source.metadata.media_type && (
                    <Badge className="absolute top-2 right-2">
                      {source.metadata.media_type === "video" ? (
                        <Video className="h-3 w-3 mr-1" />
                      ) : (
                        <Image className="h-3 w-3 mr-1" />
                      )}
                      {source.metadata.media_type}
                    </Badge>
                  )}
                </div>
              )}

              {/* Content */}
              {source.snippet && (
                <div>
                  <h4 className="font-medium mb-2">Content</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    {source.snippet}
                  </p>
                </div>
              )}

              {/* URL */}
              <div>
                <h4 className="font-medium mb-2">URL</h4>
                <p className="text-sm text-blue-600 dark:text-blue-400 break-all">
                  {source.url}
                </p>
              </div>

              {/* Metadata Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-1">Domain</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    {formatDomain(source.domain)}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-1">Provider</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    {source.provider}
                  </p>
                </div>
                {source.relevance_score && (
                  <div>
                    <h4 className="font-medium mb-1">Relevance Score</h4>
                    <p className={`text-sm ${getRelevanceColor(source.relevance_score)}`}>
                      {(source.relevance_score * 100).toFixed(1)}%
                    </p>
                  </div>
                )}
                {source.credibility_score && (
                  <div>
                    <h4 className="font-medium mb-1">Credibility Score</h4>
                    <p className={`text-sm ${getCredibilityColor(source.credibility_score)}`}>
                      {(source.credibility_score * 100).toFixed(1)}%
                    </p>
                  </div>
                )}
                {source.metadata?.published_date && (
                  <div>
                    <h4 className="font-medium mb-1">Published</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {formatDate(source.metadata.published_date)}
                    </p>
                  </div>
                )}
                {source.metadata?.author && (
                  <div>
                    <h4 className="font-medium mb-1">Author</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {source.metadata.author}
                    </p>
                  </div>
                )}
                {source.metadata?.duration && (
                  <div>
                    <h4 className="font-medium mb-1">Duration</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {source.metadata.duration}
                    </p>
                  </div>
                )}
                {source.metadata?.views && (
                  <div>
                    <h4 className="font-medium mb-1">Views</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {source.metadata.views.toLocaleString()}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </>
  );
}
