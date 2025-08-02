"use client";

import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import {
  Network,
  Search,
  ArrowRight,
  Info,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  BarChart3,
} from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface EntityNode {
  id: string;
  name: string;
  type: string;
  properties: Record<string, any>;
  confidence: number;
}

interface Relationship {
  source_id: string;
  target_id: string;
  relationship_type: string;
  properties: Record<string, any>;
  confidence: number;
}

interface KnowledgeGraphResult {
  entities: EntityNode[];
  relationships: Relationship[];
  paths: EntityNode[][];
  query_entities: string[];
  confidence: number;
  processing_time_ms: number;
  metadata: Record<string, any>;
}

interface KnowledgeGraphPanelProps {
  query?: string;
  onEntityClick?: (entity: EntityNode) => void;
  onRelationshipClick?: (relationship: Relationship) => void;
  className?: string;
  maxEntities?: number;
  maxRelationships?: number;
}

export function KnowledgeGraphPanel({
  query,
  onEntityClick,
  onRelationshipClick,
  className = "",
  maxEntities = 10,
  maxRelationships = 15,
}: KnowledgeGraphPanelProps) {
  const { toast } = useToast();
  const [graphData, setGraphData] = useState<KnowledgeGraphResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState(query || "");
  const [selectedEntity, setSelectedEntity] = useState<EntityNode | null>(null);

  useEffect(() => {
    if (searchQuery && isExpanded) {
      loadKnowledgeGraphData();
    }
  }, [searchQuery, isExpanded]);

  const loadKnowledgeGraphData = async () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      // Query the knowledge graph
      const result = await api.queryKnowledgeGraph({
        query: searchQuery,
        query_type: "entity_relationship",
        max_entities: maxEntities,
        max_relationships: maxRelationships,
      });

      setGraphData(result);
    } catch (err: any) {
      setError(err.message || "Failed to load knowledge graph data");
      toast({
        title: "Error",
        description: "Failed to load knowledge graph data",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEntityClick = (entity: EntityNode) => {
    setSelectedEntity(entity);
    onEntityClick?.(entity);
  };

  const handleRelationshipClick = (relationship: Relationship) => {
    onRelationshipClick?.(relationship);
  };

  const getEntityTypeColor = (type: string) => {
    const typeColors: Record<string, string> = {
      technology: "bg-blue-100 text-blue-800",
      person: "bg-green-100 text-green-800",
      organization: "bg-purple-100 text-purple-800",
      concept: "bg-yellow-100 text-yellow-800",
      location: "bg-red-100 text-red-800",
      event: "bg-orange-100 text-orange-800",
    };
    return typeColors[type.toLowerCase()] || "bg-gray-100 text-gray-800";
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const formatProcessingTime = (time: number) => {
    if (time < 1000) return `${time.toFixed(0)}ms`;
    return `${(time / 1000).toFixed(1)}s`;
  };

  return (
    <Card className={`${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4 text-gray-600" />
            <CardTitle className="text-sm font-medium">
              Knowledge Graph
            </CardTitle>
            {graphData && (
              <Badge variant="secondary" className="text-xs">
                {graphData.entities.length} entities
              </Badge>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={loadKnowledgeGraphData}
              disabled={isLoading || !searchQuery.trim()}
            >
              <RefreshCw className={`h-3 w-3 ${isLoading ? "animate-spin" : ""}`} />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <ChevronUp className="h-3 w-3" />
              ) : (
                <ChevronDown className="h-3 w-3" />
              )}
            </Button>
          </div>
        </div>
        <CardDescription className="text-xs">
          Explore entity relationships and connections
        </CardDescription>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0">
          <div className="space-y-4">
            {/* Search Input */}
            <div className="flex space-x-2">
              <Input
                placeholder="Search entities or concepts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && loadKnowledgeGraphData()}
                className="flex-1"
              />
              <Button
                size="sm"
                onClick={loadKnowledgeGraphData}
                disabled={isLoading || !searchQuery.trim()}
              >
                <Search className="h-3 w-3" />
              </Button>
            </div>

            {/* Loading State */}
            {isLoading && (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="h-4 w-4 animate-spin text-gray-500" />
                <span className="ml-2 text-sm text-gray-500">
                  Loading knowledge graph...
                </span>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="text-sm text-red-600 py-2 bg-red-50 rounded p-2">
                {error}
              </div>
            )}

            {/* Graph Data */}
            {graphData && !isLoading && (
              <div className="space-y-4">
                {/* Summary */}
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>
                    Found {graphData.entities.length} entities and{" "}
                    {graphData.relationships.length} relationships
                  </span>
                  <span className={getConfidenceColor(graphData.confidence)}>
                    {Math.round(graphData.confidence * 100)}% confidence
                  </span>
                </div>

                {/* Entities */}
                {graphData.entities.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2 flex items-center">
                      <Network className="h-3 w-3 mr-1" />
                      Entities
                    </h4>
                    <ScrollArea className="h-32">
                      <div className="space-y-2">
                        {graphData.entities.map((entity) => (
                          <div
                            key={entity.id}
                            className={`p-2 border rounded cursor-pointer hover:bg-gray-50 transition-colors ${
                              selectedEntity?.id === entity.id
                                ? "bg-blue-50 border-blue-200"
                                : "border-gray-200"
                            }`}
                            onClick={() => handleEntityClick(entity)}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <Badge
                                  variant="secondary"
                                  className={`text-xs ${getEntityTypeColor(entity.type)}`}
                                >
                                  {entity.type}
                                </Badge>
                                <span className="text-sm font-medium">
                                  {entity.name}
                                </span>
                              </div>
                              <span
                                className={`text-xs ${getConfidenceColor(entity.confidence)}`}
                              >
                                {Math.round(entity.confidence * 100)}%
                              </span>
                            </div>
                            {entity.properties["description"] && (
                              <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                                {entity.properties["description"]}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </div>
                )}

                {/* Relationships */}
                {graphData.relationships.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2 flex items-center">
                      <ArrowRight className="h-3 w-3 mr-1" />
                      Relationships
                    </h4>
                    <ScrollArea className="h-32">
                      <div className="space-y-2">
                        {graphData.relationships.map((rel, index) => {
                          const sourceEntity = graphData.entities.find(
                            (e) => e.id === rel.source_id
                          );
                          const targetEntity = graphData.entities.find(
                            (e) => e.id === rel.target_id
                          );

                          return (
                            <div
                              key={index}
                              className="p-2 border border-gray-200 rounded hover:bg-gray-50 transition-colors cursor-pointer"
                              onClick={() => handleRelationshipClick(rel)}
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-2 text-sm">
                                  <span className="font-medium">
                                    {sourceEntity?.name || rel.source_id}
                                  </span>
                                  <ArrowRight className="h-3 w-3 text-gray-400" />
                                  <span className="text-blue-600 font-medium">
                                    {rel.relationship_type}
                                  </span>
                                  <ArrowRight className="h-3 w-3 text-gray-400" />
                                  <span className="font-medium">
                                    {targetEntity?.name || rel.target_id}
                                  </span>
                                </div>
                                <span
                                  className={`text-xs ${getConfidenceColor(rel.confidence)}`}
                                >
                                  {Math.round(rel.confidence * 100)}%
                                </span>
                              </div>
                              {rel.properties["description"] && (
                                <p className="text-xs text-gray-600 mt-1 line-clamp-1">
                                  {rel.properties["description"]}
                                </p>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </ScrollArea>
                  </div>
                )}

                {/* Processing Info */}
                <div className="text-xs text-gray-500 flex items-center justify-between">
                  <span>
                    Processing time: {formatProcessingTime(graphData.processing_time_ms)}
                  </span>
                  <span>
                    Query entities: {graphData.query_entities.join(", ")}
                  </span>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!graphData && !isLoading && !error && (
              <div className="text-center py-8 text-gray-500">
                <BarChart3 className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                <p className="text-sm">Enter a query to explore the knowledge graph</p>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
} 