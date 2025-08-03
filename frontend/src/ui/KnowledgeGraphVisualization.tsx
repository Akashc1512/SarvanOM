"use client";

import { useEffect, useRef, useState } from "react";
import { Network } from "vis-network/standalone";
import { DataSet } from "vis-data/standalone";
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
import { Input } from "@/ui/ui/input";
import { Label } from "@/ui/ui/label";
import {
  Network as NetworkIcon,
  Search,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Settings,
  Info,
  Loader2,
  Eye,
  ExternalLink,
} from "lucide-react";
import { useToast } from "@/hooks/useToast";

interface GraphNode {
  id: string;
  label: string;
  title?: string;
  group?: string;
  size?: number;
  color?: string;
  shape?: string;
  properties?: Record<string, any>;
}

interface GraphEdge {
  id: string;
  from: string;
  to: string;
  label?: string;
  title?: string;
  color?: string;
  width?: number;
  arrows?: string;
  properties?: Record<string, any>;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: {
    total_nodes: number;
    total_edges: number;
    query_time: number;
    depth: number;
  };
}

interface KnowledgeGraphVisualizationProps {
  query?: string;
  maxNodes?: number;
  maxEdges?: number;
  height?: string;
  showControls?: boolean;
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
}

export function KnowledgeGraphVisualization({
  query = "",
  maxNodes = 50,
  maxEdges = 100,
  height = "600px",
  showControls = true,
  onNodeClick,
  onEdgeClick,
}: KnowledgeGraphVisualizationProps) {
  const { toast } = useToast();
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [zoomLevel, setZoomLevel] = useState(1);

  // Fetch graph data
  const fetchGraphData = async (searchQuery?: string) => {
    if (!searchQuery?.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/knowledge-graph/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: searchQuery.trim(),
          max_entities: maxNodes,
          max_relationships: maxEdges,
          query_type: "context",
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch graph data: ${response.statusText}`);
      }

      const data: GraphData = await response.json();
      setGraphData(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to load graph data";
      setError(errorMessage);
      toast({
        title: "Graph Loading Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Initialize network
  useEffect(() => {
    if (!containerRef.current || !graphData) return;

    const nodes = new DataSet(graphData.nodes);
    const edges = new DataSet(graphData.edges);

    const options = {
      nodes: {
        shape: "dot",
        size: 16,
        font: {
          size: 12,
          face: "Arial",
        },
        borderWidth: 2,
        shadow: true,
      },
      edges: {
        width: 2,
        shadow: true,
        smooth: {
          enabled: true,
          type: "continuous",
          roundness: 0.5,
        },
        font: {
          size: 10,
          align: "middle",
        },
        color: {
          color: "#848484",
          highlight: "#848484",
          hover: "#848484",
        },
      },
      physics: {
        stabilization: false,
        barnesHut: {
          gravitationalConstant: -80000,
          springConstant: 0.001,
          springLength: 200,
        },
      },
      interaction: {
        navigationButtons: true,
        keyboard: true,
        hover: true,
        tooltipDelay: 200,
      },
    };

    const network = new Network(containerRef.current, { nodes, edges }, options);

    // Event handlers
    network.on("click", (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const node = nodes.get(nodeId);
        if (node) {
          setSelectedNode(node as unknown as GraphNode);
          setSelectedEdge(null);
          onNodeClick?.(node as unknown as GraphNode);
        }
      } else if (params.edges.length > 0) {
        const edgeId = params.edges[0];
        const edge = edges.get(edgeId);
        if (edge) {
          setSelectedEdge(edge as unknown as GraphEdge);
          setSelectedNode(null);
          onEdgeClick?.(edge as unknown as GraphEdge);
        }
      }
    });

    network.on("stabilizationProgress", (params) => {
      // Optional: Show stabilization progress
    });

    network.on("stabilizationIterationsDone", () => {
      // Optional: Handle stabilization complete
    });

    networkRef.current = network;

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [graphData, onNodeClick, onEdgeClick]);

  // Handle search
  const handleSearch = () => {
    const queryToSearch = searchTerm.trim() || query;
    if (queryToSearch) {
      fetchGraphData(queryToSearch);
    }
  };

  // Handle zoom controls
  const handleZoomIn = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale * 1.2 });
      setZoomLevel(scale * 1.2);
    }
  };

  const handleZoomOut = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale * 0.8 });
      setZoomLevel(scale * 0.8);
    }
  };

  const handleFit = () => {
    if (networkRef.current) {
      networkRef.current.fit();
      setZoomLevel(1);
    }
  };

  // Auto-fetch when query prop changes
  useEffect(() => {
    if (query) {
      setSearchTerm(query);
      fetchGraphData(query);
    }
  }, [query]);

  const getNodeColor = (group?: string) => {
    switch (group) {
      case "person":
        return "#4CAF50";
      case "organization":
        return "#2196F3";
      case "location":
        return "#FF9800";
      case "concept":
        return "#9C27B0";
      case "event":
        return "#F44336";
      default:
        return "#607D8B";
    }
  };

  const getGroupLabel = (group?: string) => {
    switch (group) {
      case "person":
        return "Person";
      case "organization":
        return "Organization";
      case "location":
        return "Location";
      case "concept":
        return "Concept";
      case "event":
        return "Event";
      default:
        return "Entity";
    }
  };

  return (
    <div className="space-y-4">
      {/* Controls */}
      {showControls && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <NetworkIcon className="h-5 w-5" />
              Knowledge Graph Explorer
            </CardTitle>
            <CardDescription>
              Visualize relationships and entities in the knowledge graph
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Label htmlFor="search" className="sr-only">
                  Search Graph
                </Label>
                <Input
                  id="search"
                  placeholder="Search for entities or concepts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                />
              </div>
              <Button onClick={handleSearch} disabled={isLoading}>
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
                Search
              </Button>
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center gap-2 mt-4">
              <Button variant="outline" size="sm" onClick={handleZoomIn}>
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleZoomOut}>
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleFit}>
                <RotateCcw className="h-4 w-4" />
              </Button>
              <span className="text-sm text-gray-500 ml-2">
                Zoom: {(zoomLevel * 100).toFixed(0)}%
              </span>
            </div>

            {/* Graph Stats */}
            {graphData?.metadata && (
              <div className="flex items-center gap-4 mt-4 text-sm text-gray-600">
                <span>Nodes: {graphData.metadata.total_nodes}</span>
                <span>Edges: {graphData.metadata.total_edges}</span>
                <span>Depth: {graphData.metadata.depth}</span>
                <span>Query Time: {graphData.metadata.query_time}ms</span>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Graph Container */}
      <Card>
        <CardContent className="p-0">
          <div
            ref={containerRef}
            style={{ height, width: "100%" }}
            className="relative"
          >
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-6 w-6 animate-spin" />
                  <span>Loading graph...</span>
                </div>
              </div>
            )}

            {error && (
              <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
                <div className="text-center">
                  <div className="text-red-500 mb-2">
                    <Info className="h-8 w-8 mx-auto" />
                  </div>
                  <p className="text-red-600 font-medium">Failed to load graph</p>
                  <p className="text-sm text-gray-600 mt-1">{error}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => fetchGraphData(query)}
                    className="mt-2"
                  >
                    Retry
                  </Button>
                </div>
              </div>
            )}

            {!graphData && !isLoading && !error && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <NetworkIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Enter a search term to visualize the knowledge graph</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-2xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Info className="h-5 w-5" />
              Graph Element Details
            </DialogTitle>
          </DialogHeader>

          {(selectedNode || selectedEdge) && (
            <ScrollArea className="max-h-[60vh]">
              <div className="space-y-4">
                {selectedNode && (
                  <>
                    <div>
                      <h3 className="font-semibold text-lg mb-2">{selectedNode.label}</h3>
                      <div className="flex items-center gap-2 mb-3">
                        <Badge variant="outline">
                          {getGroupLabel(selectedNode.group)}
                        </Badge>
                        {selectedNode.size && (
                          <Badge variant="outline">
                            Size: {selectedNode.size}
                          </Badge>
                        )}
                      </div>
                    </div>

                    {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                      <>
                        <Separator />
                        <div>
                          <h4 className="font-medium mb-2">Properties</h4>
                          <div className="space-y-2">
                            {Object.entries(selectedNode.properties).map(([key, value]) => (
                              <div key={key} className="flex justify-between text-sm">
                                <span className="font-medium text-gray-600">{key}:</span>
                                <span className="text-gray-900">{String(value)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </>
                    )}
                  </>
                )}

                {selectedEdge && (
                  <>
                    <div>
                      <h3 className="font-semibold text-lg mb-2">
                        {selectedEdge.label || "Relationship"}
                      </h3>
                      <div className="flex items-center gap-2 mb-3">
                        <Badge variant="outline">
                          Edge ID: {selectedEdge.id}
                        </Badge>
                        {selectedEdge.width && (
                          <Badge variant="outline">
                            Width: {selectedEdge.width}
                          </Badge>
                        )}
                      </div>
                    </div>

                    {selectedEdge.properties && Object.keys(selectedEdge.properties).length > 0 && (
                      <>
                        <Separator />
                        <div>
                          <h4 className="font-medium mb-2">Properties</h4>
                          <div className="space-y-2">
                            {Object.entries(selectedEdge.properties).map(([key, value]) => (
                              <div key={key} className="flex justify-between text-sm">
                                <span className="font-medium text-gray-600">{key}:</span>
                                <span className="text-gray-900">{String(value)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </>
                    )}
                  </>
                )}

                <Separator />

                <div className="text-xs text-gray-500">
                  Click on nodes or edges in the graph to see their details
                </div>
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
} 