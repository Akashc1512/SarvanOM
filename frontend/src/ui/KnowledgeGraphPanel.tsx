"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Network, 
  Settings, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw,
  Maximize2,
  Minimize2,
  Info,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface KnowledgeGraphNode {
  id: string;
  label: string;
  type: 'person' | 'organization' | 'concept' | 'location' | 'event';
  size: number;
  color: string;
}

interface KnowledgeGraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  weight: number;
}

interface KnowledgeGraphPanelProps {
  nodes?: KnowledgeGraphNode[];
  edges?: KnowledgeGraphEdge[];
  className?: string;
  isExpanded?: boolean;
  onToggle?: () => void;
  onNodeClick?: (node: KnowledgeGraphNode) => void;
  onEdgeClick?: (edge: KnowledgeGraphEdge) => void;
}

export default function KnowledgeGraphPanel({
  nodes = [],
  edges = [],
  className,
  isExpanded = true,
  onToggle,
  onNodeClick,
  onEdgeClick
}: KnowledgeGraphPanelProps) {
  const [selectedNode, setSelectedNode] = useState<KnowledgeGraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<KnowledgeGraphEdge | null>(null);
  const [zoom, setZoom] = useState(1);
  const [showControls, setShowControls] = useState(true);

  const handleNodeClick = (node: KnowledgeGraphNode) => {
    setSelectedNode(node);
    setSelectedEdge(null);
    onNodeClick?.(node);
  };

  const handleEdgeClick = (edge: KnowledgeGraphEdge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
    onEdgeClick?.(edge);
  };

  const getNodeTypeColor = (type: string) => {
    switch (type) {
      case 'person':
        return 'bg-cosmic-success';
      case 'organization':
        return 'bg-cosmic-primary-500';
      case 'concept':
        return 'bg-cosmic-secondary-500';
      case 'location':
        return 'bg-cosmic-warning';
      case 'event':
        return 'bg-cosmic-error';
      default:
        return 'bg-cosmic-border-primary';
    }
  };

  const getNodeTypeIcon = (type: string) => {
    switch (type) {
      case 'person':
        return '👤';
      case 'organization':
        return '🏢';
      case 'concept':
        return '💡';
      case 'location':
        return '📍';
      case 'event':
        return '📅';
      default:
        return '🔗';
    }
  };

  const displayNodes = nodes;
  const displayEdges = edges;

  return (
    <Card className={cn("cosmic-card", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="cosmic-text-primary flex items-center gap-2">
            <Network className="h-5 w-5 text-cosmic-primary-500" />
              Knowledge Graph
            </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowControls(!showControls)}
              className="cosmic-btn-secondary"
            >
              <Settings className="h-4 w-4" />
            </Button>
            {onToggle && (
            <Button
              variant="ghost"
              size="sm"
                onClick={onToggle}
                className="cosmic-btn-secondary"
              >
                {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <AnimatePresence>
      {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            <CardContent>
              {/* Graph Visualization Placeholder */}
              <div className="relative h-64 cosmic-bg-secondary rounded-lg border border-cosmic-border-primary mb-4 overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <Network className="h-12 w-12 text-cosmic-text-tertiary mx-auto mb-2" />
                    <p className="text-sm cosmic-text-tertiary">Interactive Graph Visualization</p>
                    <p className="text-xs cosmic-text-tertiary mt-1">
                      {displayNodes.length} nodes, {displayEdges.length} relationships
                    </p>
                  </div>
            </div>

                {/* Mock graph nodes */}
                <div className="absolute inset-0 p-4">
                  {displayNodes.slice(0, 5).map((node, index) => (
                    <motion.div
                      key={node.id}
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1 }}
                      className={cn(
                        "absolute rounded-full flex items-center justify-center text-white text-xs font-medium cursor-pointer hover:scale-110 transition-transform",
                        getNodeTypeColor(node.type),
                        `w-${Math.max(8, Math.min(16, node.size))} h-${Math.max(8, Math.min(16, node.size))}`
                      )}
                      style={{
                        left: `${20 + (index * 15)}%`,
                        top: `${30 + (index % 2) * 30}%`,
                      }}
                      onClick={() => handleNodeClick(node)}
                    >
                      {getNodeTypeIcon(node.type)}
                    </motion.div>
                  ))}
              </div>
              </div>

              {/* Controls */}
              {showControls && (
              <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm cosmic-text-secondary">Zoom</span>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
                        className="cosmic-btn-secondary"
                      >
                        <ZoomOut className="h-4 w-4" />
                      </Button>
                      <span className="text-sm cosmic-text-primary w-12 text-center">
                        {Math.round(zoom * 100)}%
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setZoom(Math.min(2, zoom + 0.1))}
                        className="cosmic-btn-secondary"
                      >
                        <ZoomIn className="h-4 w-4" />
                      </Button>
                  </div>
                </div>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="cosmic-btn-secondary"
                    >
                      <RotateCcw className="h-4 w-4 mr-1" />
                      Reset View
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="cosmic-btn-secondary"
                    >
                      <Maximize2 className="h-4 w-4 mr-1" />
                      Fullscreen
                    </Button>
                </div>
              </div>
            )}

              {/* Node Types Legend */}
              <div className="mt-4 pt-4 border-t border-cosmic-border-primary">
                <h4 className="text-sm font-medium cosmic-text-primary mb-3 flex items-center gap-2">
                  <Info className="h-4 w-4" />
                  Node Types
                </h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {['person', 'organization', 'concept', 'location', 'event'].map((type) => (
                    <div key={type} className="flex items-center gap-2">
                      <div className={cn("w-3 h-3 rounded-full", getNodeTypeColor(type))}></div>
                      <span className="cosmic-text-secondary capitalize">{type}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Selected Node/Edge Info */}
              {(selectedNode || selectedEdge) && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-3 cosmic-bg-secondary rounded-lg border border-cosmic-border-primary"
                >
                  {selectedNode && (
                    <div>
                      <h5 className="font-medium cosmic-text-primary mb-1">
                        {getNodeTypeIcon(selectedNode.type)} {selectedNode.label}
                      </h5>
                      <p className="text-xs cosmic-text-secondary">
                        Type: {selectedNode.type} • Size: {selectedNode.size}
                      </p>
              </div>
            )}
                  {selectedEdge && (
                    <div>
                      <h5 className="font-medium cosmic-text-primary mb-1">
                        Relationship
                      </h5>
                      <p className="text-xs cosmic-text-secondary">
                        {selectedEdge.label} • Weight: {selectedEdge.weight}
                      </p>
          </div>
                  )}
                </motion.div>
              )}
        </CardContent>
          </motion.div>
      )}
      </AnimatePresence>
    </Card>
  );
} 