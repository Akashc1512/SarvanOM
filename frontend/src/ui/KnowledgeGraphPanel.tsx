"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Input } from "@/ui/ui/input";
import { Badge } from "@/ui/ui/badge";
import { useToast } from "@/hooks/useToast";
import { LoadingSpinner } from "@/ui/atoms/loading-spinner";
import { 
  BarChart3, 
  RefreshCw, 
  ChevronUp, 
  ChevronDown,
  Search,
  AlertCircle,
  Sparkles,
  MessageSquare
} from "lucide-react";
import { api } from "@/services/api";
import { Network, DataSet } from "vis-network/standalone";
import type { Node, Edge } from "vis-network";

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
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState(query || "");
  const [currentQuery, setCurrentQuery] = useState<string>("");
  const [selectedEntity, setSelectedEntity] = useState<EntityNode | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);

  // Load graph data when query changes
  useEffect(() => {
    if (currentQuery) {
      async function loadGraph() {
        setIsLoading(true);
        setError(null);

        try {
          const res = await fetch(`${process.env["NEXT_PUBLIC_API_URL"] || "http://localhost:8000"}/knowledge-graph/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: currentQuery })
          });
          
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          
          const graphData = await res.json();
          setGraphData(graphData);
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
      }
      
      loadGraph();
    }
  }, [currentQuery, toast]);

  // Render graph with vis-network when graphData changes
  useEffect(() => {
    if (graphData && containerRef.current) {
      // Convert graph data to vis-network format
      const nodes = new DataSet<Node>();
      const edges = new DataSet<Edge>();

      // Add nodes
      graphData.entities.forEach((entity) => {
        const node: Node = {
          id: entity.id,
          label: entity.name,
          title: `${entity.name} (${entity.type}) - ${Math.round(entity.confidence * 100)}% confidence`,
          color: getEntityTypeColor(entity.type),
          size: Math.max(20, entity.confidence * 30),
          shape: "circle",
          font: {
            size: 12,
            color: "#333"
          }
        };
        nodes.add(node);
      });

      // Add edges
      graphData.relationships.forEach((rel) => {
        const edge: Edge = {
          from: rel.source_id,
          to: rel.target_id,
          label: rel.relationship_type,
          title: `${rel.relationship_type} - ${Math.round(rel.confidence * 100)}% confidence`,
          color: getRelationshipColor(rel.confidence),
          width: Math.max(1, rel.confidence * 3),
          arrows: "to"
        };
        edges.add(edge);
      });

      // Network options
      const options = {
        layout: { 
          improvedLayout: true,
          hierarchical: false
        },
        physics: {
          enabled: true,
          barnesHut: {
            gravitationalConstant: -2000,
            springConstant: 0.04,
            springLength: 200
          }
        },
        interaction: {
          hover: true,
          zoomView: true,
          dragView: true
        },
        nodes: {
          borderWidth: 2,
          shadow: true
        },
        edges: {
          smooth: {
            enabled: true,
            type: "continuous",
            roundness: 0.5
          },
          font: {
            size: 10,
            align: "middle"
          }
        }
      };

      // Create network
      const network = new Network(containerRef.current, { nodes, edges }, options);
      networkRef.current = network;

      // Add event listeners
      network.on("click", (params) => {
        if (params.nodes.length > 0) {
          const nodeId = params.nodes[0];
          const entity = graphData.entities.find(e => e.id === nodeId);
          if (entity) {
            handleEntityClick(entity);
          }
        }
        if (params.edges.length > 0) {
          const edgeId = params.edges[0];
          const edge = edges.get(edgeId);
          if (edge && 'from' in edge && 'to' in edge) {
            const relationship = graphData.relationships.find(r => 
              r.source_id === edge.from && r.target_id === edge.to
            );
            if (relationship) {
              handleRelationshipClick(relationship);
            }
          }
        }
      });

      return () => {
        if (networkRef.current) {
          networkRef.current.destroy();
          networkRef.current = null;
        }
      };
    }
    
    // Return cleanup function for when graphData is null or containerRef is null
    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [graphData]);

  const loadKnowledgeGraphData = useCallback(async () => {
    if (!searchQuery.trim()) return;
    setCurrentQuery(searchQuery);
  }, [searchQuery]);

  const handleEntityClick = (entity: EntityNode) => {
    setSelectedEntity(entity);
    onEntityClick?.(entity);
  };

  const handleRelationshipClick = (relationship: Relationship) => {
    onRelationshipClick?.(relationship);
  };

  const getEntityTypeColor = (type: string) => {
    const typeColors: Record<string, string> = {
      technology: "#3B82F6", // blue
      person: "#10B981", // green
      organization: "#8B5CF6", // purple
      concept: "#F59E0B", // yellow
      location: "#EF4444", // red
      event: "#F97316", // orange
    };
    return typeColors[type.toLowerCase()] || "#6B7280"; // gray
  };

  const getRelationshipColor = (confidence: number) => {
    if (confidence >= 0.8) return "#10B981"; // green
    if (confidence >= 0.6) return "#F59E0B"; // yellow
    return "#EF4444"; // red
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
                onKeyPress={(e) => e.key === 'Enter' && loadKnowledgeGraphData()}
                className="flex-1"
              />
              <Button
                onClick={loadKnowledgeGraphData}
                disabled={isLoading || !searchQuery.trim()}
                size="sm"
              >
                <Search className="h-4 w-4" />
              </Button>
            </div>

            {/* Error Display */}
            {error && (
              <div className="flex items-center space-x-2 text-sm text-red-600">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="flex items-center justify-center py-8">
                <LoadingSpinner size="lg" />
                <span className="ml-2 text-sm text-gray-600">Loading knowledge graph...</span>
              </div>
            )}

            {/* Graph Container */}
            {graphData && !isLoading && (
              <div className="space-y-4">
                {/* Graph Stats */}
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="text-center">
                    <div className="font-semibold text-blue-600">{graphData.entities.length}</div>
                    <div className="text-gray-500">Entities</div>
                  </div>
                  <div className="text-center">
                    <div className="font-semibold text-green-600">{graphData.relationships.length}</div>
                    <div className="text-gray-500">Relationships</div>
                  </div>
                  <div className="text-center">
                    <div className={`font-semibold ${getConfidenceColor(graphData.confidence)}`}>
                      {Math.round(graphData.confidence * 100)}%
                    </div>
                    <div className="text-gray-500">Confidence</div>
                  </div>
                </div>

                {/* Graph Visualization */}
                <div 
                  ref={containerRef} 
                  className="w-full h-96 border border-gray-200 rounded-lg"
                  style={{ minHeight: '400px' }}
                />

                {/* Processing Info */}
                <div className="text-xs text-gray-500 text-center">
                  Processed in {formatProcessingTime(graphData.processing_time_ms)}
                </div>
              </div>
            )}

            {/* Empty State */}
            {!graphData && !isLoading && !error && (
              <div className="text-center py-8 text-gray-500">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-sm">Enter a query to explore the knowledge graph</p>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
} 