"use client";

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2, 
  Minimize2,
  Settings,
  Network,
  Info,
  MousePointer,
  Move,
  Search
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface GraphNode {
  id: string;
  label: string;
  type: 'person' | 'organization' | 'concept' | 'location' | 'event';
  size: number;
  x?: number;
  y?: number;
  color: string;
  description?: string;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  weight: number;
  type?: 'related' | 'part_of' | 'causes' | 'influences';
}

interface KnowledgeGraphVisualizationProps {
  query?: string;
  maxNodes?: number;
  maxEdges?: number;
  height?: string;
  showControls?: boolean;
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  className?: string;
}

export default function KnowledgeGraphVisualization({
  query = "",
  maxNodes = 50,
  maxEdges = 100,
  height = "500px",
  showControls = true,
  onNodeClick,
  onEdgeClick,
  className
}: KnowledgeGraphVisualizationProps) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const svgRef = useRef<SVGSVGElement>(null);


  const getNodeColor = (type: GraphNode['type']): string => {
    switch (type) {
      case 'person':
        return '#10b981'; // cosmic-success
      case 'organization':
        return '#3b82f6'; // cosmic-primary-500
      case 'concept':
        return '#8b5cf6'; // cosmic-secondary-500
      case 'location':
        return '#f59e0b'; // cosmic-warning
      case 'event':
        return '#ef4444'; // cosmic-error
      default:
        return '#6b7280'; // cosmic-border-primary
    }
  };

  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.5));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target === svgRef.current) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
    setSelectedEdge(null);
    onNodeClick?.(node);
  };

  const handleEdgeClick = (edge: GraphEdge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
    onEdgeClick?.(edge);
  };

    return (
    <div className={cn("space-y-4", className)}>
      {/* Controls */}
      {showControls && (
        <Card className="cosmic-card">
          <CardHeader>
            <CardTitle className="cosmic-text-primary flex items-center gap-2">
              <Settings className="h-5 w-5 text-cosmic-primary-500" />
              Graph Controls
            </CardTitle>
          </CardHeader>
          <CardContent>
          <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleZoomOut}
                  className="cosmic-btn-secondary"
                >
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <span className="text-sm cosmic-text-primary w-16 text-center">
                  {Math.round(zoom * 100)}%
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleZoomIn}
                  className="cosmic-btn-secondary"
                >
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleReset}
                  className="cosmic-btn-secondary"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary">
                  <Network className="h-3 w-3 mr-1" />
                  {nodes.length} nodes
                </Badge>
                <Badge variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary">
                  {edges.length} edges
                </Badge>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsFullscreen(!isFullscreen)}
                  className="cosmic-btn-secondary"
                >
                  {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Graph Visualization */}
      <Card className="cosmic-card">
        <CardHeader>
          <CardTitle className="cosmic-text-primary flex items-center gap-2">
            <Network className="h-5 w-5 text-cosmic-primary-500" />
            Knowledge Graph
            {query && (
              <Badge variant="outline" className="border-cosmic-primary-500 text-cosmic-primary-500">
                "{query}"
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div 
            className="relative overflow-hidden rounded-lg border border-cosmic-border-primary"
            style={{ height }}
          >
            {nodes.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <Network className="h-12 w-12 text-cosmic-text-tertiary mx-auto mb-2" />
                  <p className="cosmic-text-secondary">Enter a query to visualize the knowledge graph</p>
                </div>
              </div>
            ) : (
              <svg
                ref={svgRef}
                className="w-full h-full cursor-grab active:cursor-grabbing"
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                style={{ 
                  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                  transformOrigin: 'center'
                }}
              >
                {/* Edges */}
                {edges.map((edge) => {
                  const sourceNode = nodes.find(n => n.id === edge.source);
                  const targetNode = nodes.find(n => n.id === edge.target);
                  
                  if (!sourceNode || !targetNode || sourceNode.x === undefined || sourceNode.y === undefined || targetNode.x === undefined || targetNode.y === undefined) return null;
                  
                  return (
                    <line
                      key={edge.id}
                      x1={sourceNode.x}
                      y1={sourceNode.y}
                      x2={targetNode.x}
                      y2={targetNode.y}
                      stroke="#6b7280"
                      strokeWidth={edge.weight * 2}
                      opacity={0.6}
                      className="cursor-pointer hover:stroke-cosmic-primary-500"
                      onClick={() => handleEdgeClick(edge)}
                    />
                  );
                })}
                
                {/* Nodes */}
                {nodes.map((node) => (
                  <g key={node.id}>
                    <circle
                      cx={node.x || 0}
                      cy={node.y || 0}
                      r={node.size}
                      fill={node.color}
                      className="cursor-pointer hover:opacity-80 transition-opacity"
                      onClick={() => handleNodeClick(node)}
                    />
                    <text
                      x={node.x || 0}
                      y={(node.y || 0) + 4}
                      textAnchor="middle"
                      className="text-xs fill-white font-medium pointer-events-none"
                    >
                      {node.label.length > 8 ? node.label.substring(0, 8) + '...' : node.label}
                    </text>
                  </g>
                ))}
              </svg>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Node/Edge Information */}
      {(selectedNode || selectedEdge) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
            {selectedNode && (
            <Card className="cosmic-card">
              <CardHeader>
                <CardTitle className="cosmic-text-primary flex items-center gap-2">
                  <div 
                    className="w-4 h-4 rounded-full" 
                    style={{ backgroundColor: selectedNode.color }}
                  />
                  {selectedNode.label}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary">
                      {selectedNode.type}
                    </Badge>
                    <Badge variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary">
                      Size: {Math.round(selectedNode.size)}
                    </Badge>
                </div>
                  {selectedNode.description && (
                    <p className="text-sm cosmic-text-secondary">{selectedNode.description}</p>
                  )}
                  </div>
              </CardContent>
            </Card>
          )}

          {selectedEdge && (
            <Card className="cosmic-card">
              <CardHeader>
                <CardTitle className="cosmic-text-primary">Relationship</CardTitle>
              </CardHeader>
              <CardContent>
                    <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary">
                      {selectedEdge.type || 'related'}
                    </Badge>
                    <Badge variant="outline" className="border-cosmic-border-primary text-cosmic-text-primary">
                      Weight: {selectedEdge.weight.toFixed(2)}
                    </Badge>
                        </div>
                  {selectedEdge.label && (
                    <p className="text-sm cosmic-text-secondary">{selectedEdge.label}</p>
                )}
              </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}

      {/* Instructions */}
      <Card className="cosmic-card">
        <CardHeader>
          <CardTitle className="cosmic-text-primary flex items-center gap-2">
            <Info className="h-5 w-5 text-cosmic-primary-500" />
            How to Use
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm cosmic-text-secondary">
                <div>
              <h4 className="font-medium cosmic-text-primary mb-2 flex items-center gap-2">
                <MousePointer className="h-4 w-4" />
                Navigation
              </h4>
              <ul className="space-y-1">
                <li>• Click and drag to pan around the graph</li>
                <li>• Use zoom controls to zoom in/out</li>
                <li>• Click nodes to see details</li>
                <li>• Click edges to view relationships</li>
              </ul>
                </div>
                <div>
              <h4 className="font-medium cosmic-text-primary mb-2 flex items-center gap-2">
                <Search className="h-4 w-4" />
                Node Types
              </h4>
              <ul className="space-y-1">
                <li>• <span className="inline-block w-3 h-3 bg-cosmic-success rounded-full mr-2"></span> People</li>
                <li>• <span className="inline-block w-3 h-3 bg-cosmic-primary-500 rounded-full mr-2"></span> Organizations</li>
                <li>• <span className="inline-block w-3 h-3 bg-cosmic-secondary-500 rounded-full mr-2"></span> Concepts</li>
                <li>• <span className="inline-block w-3 h-3 bg-cosmic-warning rounded-full mr-2"></span> Locations</li>
                <li>• <span className="inline-block w-3 h-3 bg-cosmic-error rounded-full mr-2"></span> Events</li>
              </ul>
                    </div>
                  </div>
        </CardContent>
      </Card>
    </div>
  );
} 