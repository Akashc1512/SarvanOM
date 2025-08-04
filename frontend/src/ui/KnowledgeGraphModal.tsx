"use client";

import { useState, useEffect, useRef } from "react";
import { Network } from "vis-network/standalone";
import { DataSet } from "vis-data/standalone";
import { Button } from "@/ui/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/ui/ui/dialog";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { Loader2, Network as NetworkIcon, ZoomIn, ZoomOut, RotateCcw } from "lucide-react";
import { useToast } from "@/hooks/useToast";

interface GraphNode {
  id: string;
  label: string;
  title?: string;
  group?: string;
  size?: number;
  color?: string;
}

interface GraphEdge {
  from: string;
  to: string;
  label?: string;
  arrows?: string;
  color?: string;
  width?: number;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface KnowledgeGraphModalProps {
  topic?: string;
  depth?: number;
  queryId?: string;
  isOpen: boolean;
  onClose: () => void;
}

export function KnowledgeGraphModal({
  topic = "",
  depth = 2,
  queryId,
  isOpen,
  onClose,
}: KnowledgeGraphModalProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const networkRef = useRef<HTMLDivElement>(null);
  const networkInstanceRef = useRef<Network | null>(null);

  const fetchGraphData = async () => {
    if (!topic && !queryId) {
      setError("No topic or query ID provided");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (topic) params.append("topic", topic);
      if (depth) params.append("depth", depth.toString());
      if (queryId) params.append("user_id", queryId);

      const response = await fetch(`/graph/context?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch graph data: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Transform the API response to vis-network format
      const transformedData = transformApiDataToGraphData(data);
      setGraphData(transformedData);
    } catch (error) {
      console.error("Error fetching graph data:", error);
      setError(error instanceof Error ? error.message : "Failed to fetch graph data");
      toast({
        title: "Graph Loading Failed",
        description: "Failed to load knowledge graph data",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const transformApiDataToGraphData = (apiData: any): GraphData => {
    // If the API returns a proper graph structure, use it
    if (apiData.nodes && apiData.edges) {
      return {
        nodes: apiData.nodes.map((node: any) => ({
          id: node.id || node.name,
          label: node.label || node.name,
          title: node.description || node.name,
          group: node.type || "default",
          size: node.weight ? node.weight * 20 + 10 : 20,
          color: getNodeColor(node.type),
        })),
        edges: apiData.edges.map((edge: any) => ({
          from: edge.from || edge.source,
          to: edge.to || edge.target,
          label: edge.label || edge.relationship,
          arrows: "to",
          color: getEdgeColor(edge.type),
          width: edge.weight ? edge.weight * 2 + 1 : 1,
        })),
      };
    }

    // Fallback: create a sample graph structure
    const nodes: GraphNode[] = [
      {
        id: "main",
        label: topic || "Query Topic",
        title: "Main topic of the query",
        group: "main",
        size: 30,
        color: "#3b82f6",
      },
      {
        id: "related1",
        label: "Related Concept 1",
        title: "First related concept",
        group: "related",
        size: 20,
        color: "#10b981",
      },
      {
        id: "related2",
        label: "Related Concept 2",
        title: "Second related concept",
        group: "related",
        size: 20,
        color: "#10b981",
      },
      {
        id: "sub1",
        label: "Sub-concept 1",
        title: "Sub-concept of related concept 1",
        group: "sub",
        size: 15,
        color: "#f59e0b",
      },
      {
        id: "sub2",
        label: "Sub-concept 2",
        title: "Sub-concept of related concept 2",
        group: "sub",
        size: 15,
        color: "#f59e0b",
      },
    ];

    const edges: GraphEdge[] = [
      {
        from: "main",
        to: "related1",
        label: "relates to",
        arrows: "to",
        color: "#6b7280",
        width: 2,
      },
      {
        from: "main",
        to: "related2",
        label: "relates to",
        arrows: "to",
        color: "#6b7280",
        width: 2,
      },
      {
        from: "related1",
        to: "sub1",
        label: "contains",
        arrows: "to",
        color: "#9ca3af",
        width: 1,
      },
      {
        from: "related2",
        to: "sub2",
        label: "contains",
        arrows: "to",
        color: "#9ca3af",
        width: 1,
      },
    ];

    return { nodes, edges };
  };

  const getNodeColor = (type?: string): string => {
    switch (type) {
      case "main":
        return "#3b82f6";
      case "related":
        return "#10b981";
      case "sub":
        return "#f59e0b";
      default:
        return "#6b7280";
    }
  };

  const getEdgeColor = (type?: string): string => {
    switch (type) {
      case "strong":
        return "#3b82f6";
      case "medium":
        return "#10b981";
      case "weak":
        return "#f59e0b";
      default:
        return "#6b7280";
    }
  };

  const initializeNetwork = () => {
    if (!networkRef.current || !graphData) return;

    const nodes = new DataSet(graphData.nodes);
    const edges = new DataSet(graphData.edges);

    const options = {
      nodes: {
        shape: "dot",
        font: {
          size: 14,
          face: "Arial",
        },
        borderWidth: 2,
        shadow: true,
      },
      edges: {
        width: 2,
        shadow: true,
        font: {
          size: 10,
          align: "middle",
        },
        color: { inherit: "both" },
        smooth: {
          type: "continuous",
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
      layout: {
        hierarchical: {
          enabled: false,
          levelSeparation: 150,
          nodeSpacing: 100,
          treeSpacing: 200,
          blockShifting: true,
          edgeMinimization: true,
          parentCentralization: true,
          direction: "UD",
          sortMethod: "hubsize",
        },
      },
    };

    const network = new Network(networkRef.current, { nodes, edges }, options);
    networkInstanceRef.current = network;

    // Add event listeners
    network.on("click", function (params) {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const node = nodes.get(nodeId);
        console.log("Clicked node:", node);
      }
    });

    network.on("doubleClick", function (params) {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const node = nodes.get(nodeId);
        console.log("Double-clicked node:", node);
      }
    });
  };

  const handleZoomIn = () => {
    if (networkInstanceRef.current) {
      networkInstanceRef.current.moveTo({ scale: 1.2 });
    }
  };

  const handleZoomOut = () => {
    if (networkInstanceRef.current) {
      networkInstanceRef.current.moveTo({ scale: 0.8 });
    }
  };

  const handleReset = () => {
    if (networkInstanceRef.current) {
      networkInstanceRef.current.fit();
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchGraphData();
    }
  }, [isOpen, topic, depth, queryId]);

  useEffect(() => {
    if (graphData && networkRef.current) {
      initializeNetwork();
    }
  }, [graphData]);

  useEffect(() => {
    return () => {
      if (networkInstanceRef.current) {
        networkInstanceRef.current.destroy();
      }
    };
  }, []);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <NetworkIcon className="h-5 w-5" />
            Knowledge Graph Visualization
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Graph Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="outline">
                {topic || "Query Topic"}
              </Badge>
              <Badge variant="outline">
                Depth: {depth}
              </Badge>
              {graphData && (
                <Badge variant="outline">
                  {graphData.nodes.length} nodes, {graphData.edges.length} edges
                </Badge>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleZoomIn}
                disabled={!graphData}
              >
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleZoomOut}
                disabled={!graphData}
              >
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                disabled={!graphData}
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Graph Container */}
          <div className="relative border rounded-lg bg-gray-50">
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-6 w-6 animate-spin" />
                  <span>Loading knowledge graph...</span>
                </div>
              </div>
            )}

            {error && (
              <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
                <div className="text-center">
                  <p className="text-red-600 font-medium">Error loading graph</p>
                  <p className="text-sm text-gray-600">{error}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={fetchGraphData}
                    className="mt-2"
                  >
                    Retry
                  </Button>
                </div>
              </div>
            )}

            <div
              ref={networkRef}
              className="w-full h-[600px]"
              style={{ minHeight: "600px" }}
            />
          </div>

          {/* Graph Legend */}
          {graphData && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Graph Legend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <span>Main Topic</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span>Related Concepts</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span>Sub-concepts</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
} 