"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { ExternalLink, Globe } from "lucide-react";
import { type Source } from "@/services/api";

interface SourcesListProps {
  sources: Source[];
  className?: string;
}

export function SourcesList({ sources, className }: SourcesListProps) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleOpenUrl = (url: string) => {
    if (isClient && typeof window !== "undefined") {
      window.open(url, "_blank");
    }
  };

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5" />
          Sources & Citations
        </CardTitle>
        <CardDescription>
          {sources.length} source{sources.length !== 1 ? "s" : ""} used in this research
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ol className="list-decimal ml-4 space-y-2">
          {sources.map((source, idx) => (
            <li key={idx} className="text-sm">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <a 
                    href={source.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                  >
                    {source.title}
                  </a>
                  {source.snippet && (
                    <p className="text-gray-600 mt-1 text-xs">
                      {source.snippet}
                    </p>
                  )}
                  <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                    <span>
                      Relevance: {(source.relevance_score * 100).toFixed(0)}%
                    </span>
                    {source.credibility_score && (
                      <span>
                        Credibility: {(source.credibility_score * 100).toFixed(0)}%
                      </span>
                    )}
                    <span className="capitalize">
                      {source.source_type}
                    </span>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleOpenUrl(source.url)}
                  className="ml-2 flex-shrink-0"
                >
                  <ExternalLink className="h-3 w-3 mr-1" />
                  Visit
                </Button>
              </div>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
} 