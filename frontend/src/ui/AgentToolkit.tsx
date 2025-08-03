'use client';

import React, { useState } from 'react';
import { Button } from '@/ui/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/ui/card';
import { Badge } from '@/ui/ui/badge';
import { 
  Search, 
  FileText, 
  Code, 
  Brain, 
  Database, 
  Globe,
  Upload,
  Play,
  Loader2,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { api } from '@/services/api';

export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<any>;
  category: 'search' | 'document' | 'code' | 'analysis' | 'knowledge';
  status: 'available' | 'busy' | 'error';
  endpoint: string;
}

export interface AgentToolkitProps {
  availableAgents: Agent[];
  onToolSelected?: (agentId: string, result?: any) => void;
  className?: string;
}

const defaultAgents: Agent[] = [
  {
    id: 'browser',
    name: 'Web Search',
    description: 'Search the web for real-time information',
    icon: Search,
    category: 'search',
    status: 'available',
    endpoint: '/api/agents/browser'
  },
  {
    id: 'pdf',
    name: 'PDF Processor',
    description: 'Upload and analyze PDF documents',
    icon: FileText,
    category: 'document',
    status: 'available',
    endpoint: '/api/agents/pdf'
  },
  {
    id: 'code',
    name: 'Code Executor',
    description: 'Run and execute code snippets',
    icon: Code,
    category: 'code',
    status: 'available',
    endpoint: '/api/agents/code-executor'
  },
  {
    id: 'knowledge-graph',
    name: 'Knowledge Graph',
    description: 'Query the knowledge graph database',
    icon: Brain,
    category: 'knowledge',
    status: 'available',
    endpoint: '/api/agents/knowledge-graph'
  },
  {
    id: 'database',
    name: 'Database Query',
    description: 'Query structured databases',
    icon: Database,
    category: 'analysis',
    status: 'available',
    endpoint: '/api/agents/database'
  },
  {
    id: 'web-crawler',
    name: 'Web Crawler',
    description: 'Crawl and index web pages',
    icon: Globe,
    category: 'search',
    status: 'available',
    endpoint: '/api/agents/web-crawler'
  }
];

export default function AgentToolkit({ 
  availableAgents = defaultAgents, 
  onToolSelected,
  className = ''
}: AgentToolkitProps) {
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleToolInvoke = async (agent: Agent) => {
    if (loading[agent.id]) return;

    setActiveAgent(agent.id);
    setLoading(prev => ({ ...prev, [agent.id]: true }));
    setErrors(prev => ({ ...prev, [agent.id]: '' }));

    try {
      let result: any;
      
      switch (agent.id) {
        case 'browser':
          const query = prompt('Enter search term:');
          if (query) {
            result = await api.makeRequest('post', agent.endpoint, { query });
          }
          break;
          
        case 'pdf':
          // Create a file input for PDF upload
          const input = document.createElement('input');
          input.type = 'file';
          input.accept = '.pdf';
          input.onchange = async (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (file) {
              const formData = new FormData();
              formData.append('file', file);
              result = await api.makeRequest('post', agent.endpoint, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
              });
              setResults(prev => ({ ...prev, [agent.id]: result.data }));
              onToolSelected?.(agent.id, result.data);
            }
          };
          input.click();
          setLoading(prev => ({ ...prev, [agent.id]: false }));
          return;
          
        case 'code':
          const code = prompt('Enter code to run:');
          if (code) {
            result = await api.makeRequest('post', agent.endpoint, { code });
          }
          break;
          
        case 'knowledge-graph':
          const kgQuery = prompt('Enter knowledge graph query:');
          if (kgQuery) {
            result = await api.makeRequest('post', agent.endpoint, { query: kgQuery });
          }
          break;
          
        case 'database':
          const dbQuery = prompt('Enter database query:');
          if (dbQuery) {
            result = await api.makeRequest('post', agent.endpoint, { query: dbQuery });
          }
          break;
          
        case 'web-crawler':
          const url = prompt('Enter URL to crawl:');
          if (url) {
            result = await api.makeRequest('post', agent.endpoint, { url });
          }
          break;
          
        default:
          throw new Error(`Unknown agent: ${agent.id}`);
      }

      if (result) {
        setResults(prev => ({ ...prev, [agent.id]: result.data }));
        onToolSelected?.(agent.id, result.data);
      }
    } catch (error: any) {
      const errorMessage = error.message || 'An error occurred';
      setErrors(prev => ({ ...prev, [agent.id]: errorMessage }));
      console.error(`Error invoking ${agent.name}:`, error);
    } finally {
      setLoading(prev => ({ ...prev, [agent.id]: false }));
    }
  };

  const getStatusIcon = (agent: Agent) => {
    if (loading[agent.id]) {
      return <Loader2 className="h-4 w-4 animate-spin" />;
    }
    
    if (errors[agent.id]) {
      return <XCircle className="h-4 w-4 text-red-500" />;
    }
    
    if (results[agent.id]) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
    
    return <agent.icon className="h-4 w-4" />;
  };

  const getStatusColor = (agent: Agent) => {
    if (loading[agent.id]) return 'bg-blue-100 text-blue-800';
    if (errors[agent.id]) return 'bg-red-100 text-red-800';
    if (results[agent.id]) return 'bg-green-100 text-green-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div className={`fixed bottom-4 right-4 z-50 ${className}`}>
      <Card className="w-80 shadow-lg">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Agent Toolkit
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {availableAgents.map(agent => (
            <div key={agent.id} className="space-y-2">
              <Button
                variant="outline"
                className={`w-full justify-between ${getStatusColor(agent)}`}
                onClick={() => handleToolInvoke(agent)}
                disabled={loading[agent.id]}
              >
                <div className="flex items-center gap-2">
                  {getStatusIcon(agent)}
                  <div className="text-left">
                    <div className="font-medium">{agent.name}</div>
                    <div className="text-xs opacity-75">{agent.description}</div>
                  </div>
                </div>
                <Badge variant="secondary" className="text-xs">
                  {agent.category}
                </Badge>
              </Button>
              
              {errors[agent.id] && (
                <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                  {errors[agent.id]}
                </div>
              )}
              
              {results[agent.id] && (
                <div className="text-xs bg-green-50 p-2 rounded">
                  <div className="font-medium text-green-800">Result:</div>
                  <div className="text-green-700 mt-1">
                    {typeof results[agent.id] === 'string' 
                      ? results[agent.id] 
                      : JSON.stringify(results[agent.id], null, 2)
                    }
                  </div>
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
} 