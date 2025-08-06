"use client";

import { useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
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
  AlertCircle,
} from "lucide-react";
import { useToast } from "@/hooks/useToast";

// Dynamically import vis-network components with SSR disabled
const Network = dynamic(() => import("vis-network/standalone").then(mod => ({ default: mod.Network })), {
  ssr: false,
  loading: () => <div className="h-full flex items-center justify-center">Loading network visualization...</div>
});

const DataSet = dynamic(() => import("vis-data/standalone").then(mod => ({ default: mod.DataSet })), {
  ssr: false,
});

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
  const networkRef = useRef<any>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [zoomLevel, setZoomLevel] = useState(1);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Fetch graph data
  const fetchGraphData = async (searchQuery?: string) => {
    if (!isClient) return;
    
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/knowledge-graph", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: searchQuery || query,
          max_nodes: maxNodes,
          max_edges: maxEdges,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch graph data: ${response.statusText}`);
      }

      const data = await response.json();
      setGraphData(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
      setError(error instanceof Error ? error.message : "Failed to fetch graph data");
      toast({
        title: "Graph Loading Failed",
        description: "Failed to load knowledge graph data. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Initialize network visualization
  useEffect(() => {
    if (!isClient || !graphData || !containerRef.current) return;

    const initializeNetwork = async () => {
      try {
        const { Network: VisNetwork, DataSet: VisDataSet } = await import("vis-network/standalone");
        const { DataSet: VisDataDataSet } = await import("vis-data/standalone");

        // Create nodes dataset
        const nodes = new VisDataDataSet(
          graphData.nodes.map((node) => ({
            id: node.id,
            label: node.label,
            title: node.title || node.label,
            group: node.group || "default",
            size: node.size || 20,
            color: node.color || getNodeColor(node.group),
            shape: node.shape || "circle",
            properties: node.properties || {},
          }))
        );

        // Create edges dataset
        const edges = new VisDataDataSet(
          graphData.edges.map((edge) => ({
            id: edge.id,
            from: edge.from,
            to: edge.to,
            label: edge.label || "",
            title: edge.title || edge.label || "",
            color: edge.color || "#666",
            width: edge.width || 1,
            arrows: edge.arrows || "to",
            properties: edge.properties || {},
          }))
        );

        // Network options
        const options = {
          nodes: {
            font: {
              size: 12,
              face: "Arial",
            },
            borderWidth: 2,
            shadow: true,
          },
          edges: {
            width: 1,
            shadow: true,
            smooth: {
              type: "continuous",
            },
          },
          physics: {
            enabled: true,
            barnesHut: {
              gravitationalConstant: -2000,
              springConstant: 0.04,
              springLength: 200,
            },
          },
          interaction: {
            hover: true,
            tooltipDelay: 200,
          },
        };

        // Create network
        const network = new VisNetwork(containerRef.current, { nodes, edges }, options);

        // Event handlers
        network.on("click", (params: any) => {
          if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = graphData.nodes.find((n) => n.id === nodeId);
            if (node) {
              setSelectedNode(node);
              setShowDetails(true);
              onNodeClick?.(node);
            }
          } else if (params.edges.length > 0) {
            const edgeId = params.edges[0];
            const edge = graphData.edges.find((e) => e.id === edgeId);
            if (edge) {
              setSelectedEdge(edge);
              setShowDetails(true);
              onEdgeClick?.(edge);
            }
          }
        });

        network.on("stabilizationProgress", (params: any) => {
          // Optional: Show stabilization progress
        });

        network.on("stabilizationIterationsDone", () => {
          // Network is ready
        });

        networkRef.current = network;
      } catch (error) {
        console.error("Error initializing network:", error);
        setError("Failed to initialize network visualization");
      }
    };

    initializeNetwork();

    // Cleanup
    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [graphData, isClient, onNodeClick, onEdgeClick]);

  // Load initial data
  useEffect(() => {
    if (isClient && query) {
      fetchGraphData();
    }
  }, [query, maxNodes, maxEdges, isClient]);

  const handleSearch = () => {
    if (searchTerm.trim()) {
      fetchGraphData(searchTerm);
    }
  };

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

  const getNodeColor = (group?: string) => {
    const colors: Record<string, string> = {
      person: "#4285f4",
      organization: "#34a853",
      location: "#fbbc05",
      concept: "#ea4335",
      event: "#9c27b0",
      default: "#666666",
    };
    return colors[group || "default"] || colors.default;
  };

  const getGroupLabel = (group?: string) => {
    const labels: Record<string, string> = {
      person: "Person",
      organization: "Organization",
      location: "Location",
      concept: "Concept",
      event: "Event",
      default: "Other",
    };
    return labels[group || "default"] || labels.default;
  };

  if (!isClient) {
    return (
      <div className="bg-white rounded-lg border p-6">
        <div className="h-96 bg-gray-100 animate-pulse rounded-lg flex items-center justify-center">
          <div className="text-gray-500">Loading visualization...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search Controls */}
      {showControls && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Graph Search
            </CardTitle>
            <CardDescription>
              Search for entities, concepts, or relationships to visualize
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                placeholder="Enter search terms..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                className="flex-1"
              />
              <Button onClick={handleSearch} disabled={isLoading}>
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Graph Visualization */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <NetworkIcon className="h-5 w-5" />
                Knowledge Graph
              </CardTitle>
              <CardDescription>
                Interactive visualization of knowledge relationships
              </CardDescription>
            </div>
            {showControls && (
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleZoomIn}
                  title="Zoom In"
                >
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleZoomOut}
                  title="Zoom Out"
                >
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleFit}
                  title="Fit to View"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="relative">
            {error ? (
              <div className="h-96 flex items-center justify-center text-red-500">
                <div className="text-center">
                  <AlertCircle className="h-12 w-12 mx-auto mb-2" />
                  <p>{error}</p>
                </div>
              </div>
            ) : isLoading ? (
              <div className="h-96 flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin" />
              </div>
            ) : (
              <div
                ref={containerRef}
                style={{ height }}
                className="border rounded-lg"
              />
            )}
          </div>
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {selectedNode ? "Node Details" : "Edge Details"}
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="max-h-96">
            {selectedNode && (
              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-medium">Label</Label>
                  <p className="text-lg font-semibold">{selectedNode.label}</p>
                </div>
                {selectedNode.group && (
                  <div>
                    <Label className="text-sm font-medium">Type</Label>
                    <Badge variant="outline">{getGroupLabel(selectedNode.group)}</Badge>
                  </div>
                )}
                {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                  <div>
                    <Label className="text-sm font-medium">Properties</Label>
                    <div className="space-y-2">
                      {Object.entries(selectedNode.properties).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-sm text-gray-600">{key}:</span>
                          <span className="text-sm">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            {selectedEdge && (
              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-medium">Relationship</Label>
                  <p className="text-lg font-semibold">{selectedEdge.label || "Unknown"}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">From</Label>
                  <p className="text-sm">{selectedEdge.from}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">To</Label>
                  <p className="text-sm">{selectedEdge.to}</p>
                </div>
                {selectedEdge.properties && Object.keys(selectedEdge.properties).length > 0 && (
                  <div>
                    <Label className="text-sm font-medium">Properties</Label>
                    <div className="space-y-2">
                      {Object.entries(selectedEdge.properties).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-sm text-gray-600">{key}:</span>
                          <span className="text-sm">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
} 