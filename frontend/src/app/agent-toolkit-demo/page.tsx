'use client';

import React, { useState } from 'react';
import AgentToolkit from '@/ui/AgentToolkit';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/ui/card';
import { Button } from '@/ui/ui/button';
import { Badge } from '@/ui/ui/badge';
import { Brain, Code, FileText, Search, Database, Globe } from 'lucide-react';

export default function AgentToolkitDemo() {
  const [results, setResults] = useState<Record<string, any>>({});
  const [showToolkit, setShowToolkit] = useState(true);

  const handleToolSelected = (agentId: string, result?: any) => {
    console.log(`Agent ${agentId} selected with result:`, result);
    if (result) {
      setResults(prev => ({ ...prev, [agentId]: result }));
    }
  };

  const customAgents = [
    {
      id: 'browser',
      name: 'Web Search',
      description: 'Search the web for real-time information',
      icon: Search as React.ComponentType<any>,
      category: 'search' as const,
      status: 'available' as const,
      endpoint: '/api/agents/browser'
    },
    {
      id: 'pdf',
      name: 'PDF Processor',
      description: 'Upload and analyze PDF documents',
      icon: FileText as React.ComponentType<any>,
      category: 'document' as const,
      status: 'available' as const,
      endpoint: '/api/agents/pdf'
    },
    {
      id: 'code',
      name: 'Code Executor',
      description: 'Run and execute code snippets',
      icon: Code as React.ComponentType<any>,
      category: 'code' as const,
      status: 'available' as const,
      endpoint: '/api/agents/code-executor'
    },
    {
      id: 'knowledge-graph',
      name: 'Knowledge Graph',
      description: 'Query the knowledge graph database',
      icon: Brain as React.ComponentType<any>,
      category: 'knowledge' as const,
      status: 'available' as const,
      endpoint: '/api/agents/knowledge-graph'
    },
    {
      id: 'database',
      name: 'Database Query',
      description: 'Query structured databases',
      icon: Database as React.ComponentType<any>,
      category: 'analysis' as const,
      status: 'available' as const,
      endpoint: '/api/agents/database'
    },
    {
      id: 'web-crawler',
      name: 'Web Crawler',
      description: 'Crawl and index web pages',
      icon: Globe as React.ComponentType<any>,
      category: 'search' as const,
      status: 'available' as const,
      endpoint: '/api/agents/web-crawler'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Agent Toolkit Demo
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Explore the dynamic agent toolkit that provides access to various AI agents for different tasks.
            Each agent specializes in specific capabilities like web search, document processing, code execution, and more.
          </p>
        </div>

        {/* Controls */}
        <div className="flex justify-center mb-8">
          <Button
            onClick={() => setShowToolkit(!showToolkit)}
            variant="outline"
            className="flex items-center gap-2"
          >
            <Brain className="h-4 w-4" />
            {showToolkit ? 'Hide' : 'Show'} Agent Toolkit
          </Button>
        </div>

        {/* Agent Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {customAgents.map(agent => (
            <Card key={agent.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <agent.icon className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{agent.name}</CardTitle>
                    <Badge variant="secondary" className="text-xs">
                      {agent.category}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-3">
                  {agent.description}
                </p>
                <div className="text-xs text-gray-500">
                  Endpoint: {agent.endpoint}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Results Display */}
        {Object.keys(results).length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Agent Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(results).map(([agentId, result]) => (
                  <div key={agentId} className="border rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline">{agentId}</Badge>
                      <span className="text-sm text-gray-500">
                        {new Date().toLocaleTimeString()}
                      </span>
                    </div>
                    <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto max-h-40">
                      {JSON.stringify(result, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Usage Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>How to Use</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">1. Agent Toolkit Panel</h3>
              <p className="text-sm text-gray-600">
                The Agent Toolkit appears as a floating panel in the bottom-right corner. 
                Click on any agent to invoke its functionality.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2">2. Available Agents</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li><strong>Web Search:</strong> Search the web for real-time information</li>
                <li><strong>PDF Processor:</strong> Upload and analyze PDF documents</li>
                <li><strong>Code Executor:</strong> Run code snippets in a safe environment</li>
                <li><strong>Knowledge Graph:</strong> Query the knowledge graph database</li>
                <li><strong>Database Query:</strong> Execute database queries</li>
                <li><strong>Web Crawler:</strong> Crawl and index web pages</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2">3. Integration</h3>
              <p className="text-sm text-gray-600">
                The AgentToolkit component can be easily integrated into any page by importing 
                and using it with custom agent configurations.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Toolkit */}
      {showToolkit && (
        <AgentToolkit
          availableAgents={customAgents}
          onToolSelected={handleToolSelected}
        />
      )}
    </div>
  );
} 