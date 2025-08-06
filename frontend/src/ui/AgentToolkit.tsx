"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { 
  Brain, 
  Search, 
  FileText, 
  Code, 
  Database, 
  Network, 
  Globe, 
  Loader2, 
  CheckCircle, 
  XCircle,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { api } from "@/services/api";

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
    id: 'search',
    name: 'Search Agent',
    description: 'Search across knowledge base and web',
    icon: Search,
    category: 'search',
    status: 'available',
    endpoint: '/api/search'
  },
  {
    id: 'pdf',
    name: 'PDF Processor',
    description: 'Extract and analyze PDF documents',
    icon: FileText,
    category: 'document',
    status: 'available',
    endpoint: '/api/pdf'
  },
  {
    id: 'code',
    name: 'Code Analyzer',
    description: 'Analyze and execute code snippets',
    icon: Code,
    category: 'code',
    status: 'available',
    endpoint: '/api/code'
  },
  {
    id: 'knowledge-graph',
    name: 'Knowledge Graph',
    description: 'Query knowledge graph relationships',
    icon: Network,
    category: 'knowledge',
    status: 'available',
    endpoint: '/api/knowledge-graph'
  },
  {
    id: 'database',
    name: 'Database Query',
    description: 'Execute database queries',
    icon: Database,
    category: 'analysis',
    status: 'available',
    endpoint: '/api/database'
  },
  {
    id: 'web-crawler',
    name: 'Web Crawler',
    description: 'Crawl and extract web content',
    icon: Globe,
    category: 'search',
    status: 'available',
    endpoint: '/api/crawler'
  }
];

export default function AgentToolkit({ 
  availableAgents = defaultAgents, 
  onToolSelected,
  className = ''
}: AgentToolkitProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [results, setResults] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isClient, setIsClient] = useState(false);

  // Ensure we're on the client side
  useState(() => {
    setIsClient(true);
  });

  const handleToolInvoke = async (agent: Agent) => {
    setLoading(prev => ({ ...prev, [agent.id]: true }));
    setErrors(prev => ({ ...prev, [agent.id]: '' }));

    try {
      let result: any = null;

      switch (agent.id) {
        case 'search':
          const query = prompt('Enter search query:');
          if (query) {
            result = await api.makeRequest('post', agent.endpoint, { query });
          }
          break;
          
        case 'pdf':
          // Create a file input for PDF upload
          if (isClient && typeof document !== "undefined") {
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
          }
          break;
          
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
          <CardDescription>
            {isExpanded ? 'Available AI agents' : 'Click to expand'}
          </CardDescription>
        </CardHeader>
        
        {isExpanded && (
          <CardContent className="space-y-3">
            {availableAgents.map((agent) => (
              <div key={agent.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  {getStatusIcon(agent)}
                  <div>
                    <h4 className="font-medium text-sm">{agent.name}</h4>
                    <p className="text-xs text-gray-600">{agent.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={`text-xs ${getStatusColor(agent)}`}>
                    {agent.status}
                  </Badge>
                  <Button
                    size="sm"
                    onClick={() => handleToolInvoke(agent)}
                    disabled={loading[agent.id]}
                    className="h-8 px-3"
                  >
                    {loading[agent.id] ? 'Running...' : 'Run'}
                  </Button>
                </div>
              </div>
            ))}
            
            {Object.keys(errors).length > 0 && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="font-medium text-red-800 mb-2">Errors:</h4>
                {Object.entries(errors).map(([agentId, error]) => (
                  <div key={agentId} className="text-sm text-red-600">
                    <strong>{agentId}:</strong> {error}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        )}
        
        <div className="p-3 border-t">
          <Button
            variant="ghost"
            onClick={() => setIsExpanded(!isExpanded)}
            className="w-full"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="h-4 w-4 mr-2" />
                Collapse
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4 mr-2" />
                Expand
              </>
            )}
          </Button>
        </div>
      </Card>
    </div>
  );
} 