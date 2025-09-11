"use client";

import { useState, Suspense } from "react";
import dynamic from "next/dynamic";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { Input } from "@/ui/ui/input";
import { Label } from "@/ui/ui/label";
import { Skeleton } from "@/ui/ui/skeleton";

// Lazy load the heavy graph visualization component
const KnowledgeGraphVisualization = dynamic(() => import("@/ui/KnowledgeGraphVisualization"), {
  loading: () => <Skeleton className="h-96 w-full" />,
  ssr: false // Disable SSR for this component as it's likely canvas-based
});
import { 
  Network, 
  Search, 
  Settings, 
  Info, 
  BookOpen,
  Users,
  MapPin,
  Lightbulb,
  Calendar,
  ArrowLeft
} from "lucide-react";
import Link from "next/link";

export default function GraphVisualizationPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [maxNodes, setMaxNodes] = useState(50);
  const [maxEdges, setMaxEdges] = useState(100);

  const exampleQueries = [
    {
      title: "AI and Machine Learning",
      description: "Explore relationships between AI concepts",
      query: "artificial intelligence machine learning neural networks",
      icon: Lightbulb
    },
    {
      title: "Technology Companies",
      description: "View tech company relationships",
      query: "Google Microsoft Apple Amazon technology companies",
      icon: Users
    },
    {
      title: "Geographic Locations",
      description: "Explore location-based relationships",
      query: "United States Europe Asia cities countries",
      icon: MapPin
    },
    {
      title: "Historical Events",
      description: "Connect historical events and figures",
      query: "World War II Cold War historical events",
      icon: Calendar
    }
  ];

  return (
    <div className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container cosmic-section space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Link href="/" className="cosmic-text-tertiary hover:cosmic-text-primary">
                <ArrowLeft className="h-4 w-4" />
              </Link>
              <h1 className="text-3xl font-bold cosmic-text-primary">Knowledge Graph Explorer</h1>
            </div>
            <p className="cosmic-text-secondary">
              Interactive visualization of knowledge graph relationships and entities
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="flex items-center gap-1 border-cosmic-border-primary text-cosmic-text-primary">
              <Info className="h-3 w-3" />
              Interactive
            </Badge>
          </div>
        </div>

        {/* Search and Controls */}
        <Card className="cosmic-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 cosmic-text-primary">
              <Search className="h-5 w-5 text-cosmic-primary-500" />
              Graph Search
            </CardTitle>
            <CardDescription className="cosmic-text-secondary">
              Search for entities, concepts, or relationships to visualize in the knowledge graph
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="search" className="cosmic-text-primary">Search Query</Label>
                <Input
                  id="search"
                  placeholder="Enter search terms..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="mt-1 cosmic-input"
                />
              </div>
              <div>
                <Label htmlFor="maxNodes" className="cosmic-text-primary">Max Nodes</Label>
                <Input
                  id="maxNodes"
                  type="number"
                  min="10"
                  max="200"
                  value={maxNodes}
                  onChange={(e) => setMaxNodes(parseInt(e.target.value) || 50)}
                  className="mt-1 cosmic-input"
                />
              </div>
              <div>
                <Label htmlFor="maxEdges" className="cosmic-text-primary">Max Edges</Label>
                <Input
                  id="maxEdges"
                  type="number"
                  min="20"
                  max="500"
                  value={maxEdges}
                  onChange={(e) => setMaxEdges(parseInt(e.target.value) || 100)}
                  className="mt-1 cosmic-input"
                />
              </div>
            </div>
          </CardContent>
      </Card>

        {/* Example Queries */}
        <Card className="cosmic-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 cosmic-text-primary">
              <BookOpen className="h-5 w-5 text-cosmic-primary-500" />
              Example Queries
            </CardTitle>
            <CardDescription className="cosmic-text-secondary">
              Try these example searches to explore different types of relationships
            </CardDescription>
          </CardHeader>
        <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {exampleQueries.map((example, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="h-auto p-4 flex flex-col items-start gap-2 cosmic-btn-secondary"
                  onClick={() => setSearchQuery(example.query)}
                >
                  <example.icon className="h-5 w-5 text-cosmic-primary-500" />
                  <div className="text-left">
                    <div className="font-medium text-sm cosmic-text-primary">{example.title}</div>
                    <div className="text-xs cosmic-text-tertiary mt-1">
                      {example.description}
                    </div>
                  </div>
                </Button>
              ))}
            </div>
        </CardContent>
      </Card>

      {/* Graph Visualization */}
      <KnowledgeGraphVisualization
        query={searchQuery}
        maxNodes={maxNodes}
        maxEdges={maxEdges}
        height="700px"
        showControls={true}
        onNodeClick={(node) => {
          console.log("Node clicked:", node);
        }}
        onEdgeClick={(edge) => {
          console.log("Edge clicked:", edge);
        }}
      />

        {/* Information Panel */}
        <Card className="cosmic-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 cosmic-text-primary">
              <Settings className="h-5 w-5 text-cosmic-primary-500" />
              Graph Controls
            </CardTitle>
            <CardDescription className="cosmic-text-secondary">
              How to interact with the knowledge graph visualization
            </CardDescription>
          </CardHeader>
                  <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3 cosmic-text-primary">Navigation</h4>
                <ul className="space-y-2 text-sm cosmic-text-secondary">
                  <li>• <strong>Drag</strong> to pan around the graph</li>
                  <li>• <strong>Scroll</strong> to zoom in/out</li>
                  <li>• <strong>Click nodes</strong> to see details</li>
                  <li>• <strong>Click edges</strong> to view relationships</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-3 cosmic-text-primary">Node Types</h4>
                <ul className="space-y-2 text-sm cosmic-text-secondary">
                  <li>• <span className="inline-block w-3 h-3 bg-cosmic-success rounded-full mr-2"></span> <strong>Green:</strong> People</li>
                  <li>• <span className="inline-block w-3 h-3 bg-cosmic-primary-500 rounded-full mr-2"></span> <strong>Blue:</strong> Organizations</li>
                  <li>• <span className="inline-block w-3 h-3 bg-cosmic-warning rounded-full mr-2"></span> <strong>Orange:</strong> Locations</li>
                  <li>• <span className="inline-block w-3 h-3 bg-cosmic-secondary-500 rounded-full mr-2"></span> <strong>Purple:</strong> Concepts</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 