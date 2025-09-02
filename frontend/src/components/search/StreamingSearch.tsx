import React, { useState, useCallback, useEffect } from 'react';
import { useSSEStream } from '../../hooks/useSSEStream';

interface StreamingSearchProps {
  onComplete?: (data: any) => void;
  onError?: (error: string) => void;
  className?: string;
}

interface SearchResult {
  answer: string;
  sources: Array<{
    title: string;
    url: string;
    snippet: string;
    domain: string;
    provider: string;
    relevance_score: number;
  }>;
  citations?: Array<{
    marker: string;
    source: {
      title: string;
      url: string;
      snippet: string;
      source_type: string;
      relevance_score: number;
      credibility_score: number;
      domain: string;
      provider: string;
    };
    confidence: number;
    sentence_start: number;
    sentence_end: number;
    claim_type: string;
  }>;
  bibliography?: string[];
  uncertainty_flags?: string[];
  overall_confidence?: number;
}

export function StreamingSearch({ onComplete, onError, className = '' }: StreamingSearchProps) {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<SearchResult['sources']>([]);
  const [citations, setCitations] = useState<SearchResult['citations']>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'reconnecting'>('disconnected');
  const [heartbeatData, setHeartbeatData] = useState<any>(null);
  const [traceId, setTraceId] = useState<string>('');

  const handleContent = useCallback((content: string) => {
    setAnswer(prev => prev + content);
  }, []);

  const handleComplete = useCallback((data: any) => {
    console.log('Stream completed:', data);
    
    if (data.sources) {
      setSources(data.sources);
    }
    
    if (data.citations) {
      setCitations(data.citations);
    }

    setIsLoading(false);
    setConnectionStatus('disconnected');
    
    onComplete?.(data);
  }, [onComplete]);

  const handleError = useCallback((error: string) => {
    console.error('Stream error:', error);
    setIsLoading(false);
    setConnectionStatus('disconnected');
    onError?.(error);
  }, [onError]);

  const handleHeartbeat = useCallback((data: any) => {
    setHeartbeatData(data);
    console.log('Heartbeat received:', data);
  }, []);

  const { start, stop, isConnected, isReconnecting, reconnectAttempts, traceId: streamTraceId, error } = useSSEStream({
    query,
    maxTokens: 1000,
    temperature: 0.2,
    onContent: handleContent,
    onComplete: handleComplete,
    onError: handleError,
    onHeartbeat: handleHeartbeat,
    silenceThreshold: 15, // 15 seconds of silence triggers reconnect
    maxReconnectAttempts: 3,
    reconnectDelay: 2000
  });

  // Update connection status based on stream state
  useEffect(() => {
    if (isConnected) {
      setConnectionStatus('connected');
    } else if (isReconnecting) {
      setConnectionStatus('reconnecting');
    } else if (isLoading && !isConnected) {
      setConnectionStatus('connecting');
    } else {
      setConnectionStatus('disconnected');
    }
  }, [isConnected, isReconnecting, isLoading]);

  // Update trace ID
  useEffect(() => {
    if (streamTraceId) {
      setTraceId(streamTraceId);
    }
  }, [streamTraceId]);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim() || isLoading) return;

    // Reset state
    setAnswer('');
    setSources([]);
    setCitations([]);
    setHeartbeatData(null);
    setIsLoading(true);
    setConnectionStatus('connecting');

    // Start streaming
    start();
  }, [query, isLoading, start]);

  const handleStop = useCallback(() => {
    stop();
    setIsLoading(false);
    setConnectionStatus('disconnected');
  }, [stop]);

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-500';
      case 'connecting': return 'text-yellow-500';
      case 'reconnecting': return 'text-orange-500';
      case 'disconnected': return 'text-gray-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'reconnecting': return `Reconnecting... (${reconnectAttempts}/3)`;
      case 'disconnected': return 'Disconnected';
      default: return 'Unknown';
    }
  };

  return (
    <div className={`streaming-search ${className}`}>
      {/* Search Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything..."
            className="flex-1 rounded-md bg-white/10 px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="rounded-md bg-blue-500 px-6 py-3 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
          {isLoading && (
            <button
              type="button"
              onClick={handleStop}
              className="rounded-md bg-red-500 px-4 py-3 text-white font-medium"
            >
              Stop
            </button>
          )}
        </div>
      </form>

      {/* Connection Status */}
      <div className="mb-4 flex items-center gap-4 text-sm">
        <div className={`flex items-center gap-2 ${getStatusColor()}`}>
          <div className={`w-2 h-2 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500' :
            connectionStatus === 'connecting' ? 'bg-yellow-500' :
            connectionStatus === 'reconnecting' ? 'bg-orange-500' :
            'bg-gray-500'
          }`} />
          <span>{getStatusText()}</span>
        </div>
        
        {traceId && (
          <div className="text-gray-400">
            Trace ID: {traceId}
          </div>
        )}
        
        {heartbeatData && (
          <div className="text-gray-400">
            Uptime: {Math.round(heartbeatData.uptime_seconds || 0)}s
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 rounded-md bg-red-500/20 border border-red-500/30 px-4 py-3 text-red-200">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Answer Display */}
      {answer && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-white">Answer</h3>
          <div className="prose prose-invert max-w-none">
            <div className="whitespace-pre-wrap text-gray-200 leading-relaxed">
              {answer}
              {isLoading && <span className="animate-pulse">|</span>}
            </div>
          </div>
        </div>
      )}

      {/* Sources Display */}
      {sources.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-white">Sources</h3>
          <div className="space-y-3">
            {sources.map((source, index) => (
              <div key={index} className="bg-white/5 rounded-lg p-4 border border-white/10">
                <h4 className="font-medium text-white mb-2">
                  <a 
                    href={source.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="hover:text-blue-400 transition-colors"
                  >
                    {source.title}
                  </a>
                </h4>
                <p className="text-gray-300 text-sm mb-2">{source.snippet}</p>
                <div className="flex items-center gap-4 text-xs text-gray-400">
                  <span>{source.domain}</span>
                  <span>Provider: {source.provider}</span>
                  <span>Score: {(source.relevance_score * 100).toFixed(1)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Citations Display */}
      {citations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-white">Citations</h3>
          <div className="space-y-2">
            {citations.map((citation, index) => (
              <div key={index} className="bg-white/5 rounded-lg p-3 border border-white/10">
                <div className="flex items-start gap-3">
                  <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded">
                    {citation.marker}
                  </span>
                  <div className="flex-1">
                    <p className="text-gray-200 text-sm mb-1">
                      {citation.source.title}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>Confidence: {(citation.confidence * 100).toFixed(1)}%</span>
                      <span>Type: {citation.claim_type}</span>
                      <a 
                        href={citation.source.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300"
                      >
                        View Source
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Debug Info (only in development) */}
      {process.env.NODE_ENV === 'development' && heartbeatData && (
        <div className="mt-6 p-4 bg-gray-800 rounded-lg">
          <h4 className="text-sm font-medium text-gray-300 mb-2">Debug Info</h4>
          <pre className="text-xs text-gray-400 overflow-auto">
            {JSON.stringify(heartbeatData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
