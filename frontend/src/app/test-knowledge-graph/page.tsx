"use client";

import React, { useState } from "react";
import { KnowledgeGraphPanel } from "@/ui/KnowledgeGraphPanel";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Input } from "@/ui/ui/input";

export default function TestKnowledgeGraphPage() {
  const [testQuery, setTestQuery] = useState("artificial intelligence companies");
  const [selectedEntity, setSelectedEntity] = useState<any>(null);
  const [selectedRelationship, setSelectedRelationship] = useState<any>(null);

  const handleEntityClick = (entity: any) => {
    setSelectedEntity(entity);
    console.log("Entity clicked:", entity);
  };

  const handleRelationshipClick = (relationship: any) => {
    setSelectedRelationship(relationship);
    console.log("Relationship clicked:", relationship);
  };

  const testQueries = [
    "artificial intelligence companies",
    "machine learning researchers",
    "tech startups in silicon valley",
    "AI ethics and governance",
    "natural language processing",
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Knowledge Graph Test</h1>
        <p className="text-gray-600">
          Test the vis-network integration with knowledge graph visualization
        </p>
      </div>

      {/* Test Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Test Controls</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-2">
            <Input
              placeholder="Enter test query..."
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              className="flex-1"
            />
            <Button onClick={() => setTestQuery(testQuery)}>
              Test Query
            </Button>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {testQueries.map((query, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => setTestQuery(query)}
              >
                {query}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Knowledge Graph Panel */}
      <KnowledgeGraphPanel
        query={testQuery}
        onEntityClick={handleEntityClick}
        onRelationshipClick={handleRelationshipClick}
        maxEntities={15}
        maxRelationships={20}
      />

      {/* Selected Entity Info */}
      {selectedEntity && (
        <Card>
          <CardHeader>
            <CardTitle>Selected Entity</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
              {JSON.stringify(selectedEntity, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}

      {/* Selected Relationship Info */}
      {selectedRelationship && (
        <Card>
          <CardHeader>
            <CardTitle>Selected Relationship</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
              {JSON.stringify(selectedRelationship, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Test Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>1. Enter a query or click one of the test queries above</p>
          <p>2. The knowledge graph will load and display entities and relationships</p>
          <p>3. Click on nodes (entities) or edges (relationships) in the graph</p>
          <p>4. Use mouse wheel to zoom, drag to pan, and hover for tooltips</p>
          <p>5. Check the console for click event logs</p>
        </CardContent>
      </Card>
    </div>
  );
} 