import React, { useState, useCallback, useEffect } from 'react';
import { useSSEStream } from '../../hooks/useSSEStream';
import { LaneChips, LaneProgress, PartialAnswerBanner, TTFTIndicator, type LaneStatus } from '../streaming/LaneChips';
import { TraceIdDisplay, StreamingStatus } from '../streaming/TraceIdDisplay';
import { FallbackBadge } from '../ui/FallbackBadge';

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
  const [lanes, setLanes] = useState<LaneStatus[]>([
    { id: 'web', name: 'Web', status: 'pending', timeout: 3000 },
    { id: 'vector', name: 'Vector', status: 'pending', timeout: 3000 },
    { id: 'kg', name: 'KG', status: 'pending', timeout: 3000 },
    { id: 'llm', name: 'LLM', status: 'pending', timeout: 3000 },
    { id: 'youtube', name: 'YouTube', status: 'pending', timeout: 3000 }
  ]);
  const [ttft, setTtft] = useState<number | undefined>();
  const [showPartialBanner, setShowPartialBanner] = useState(false);

  const handleContent = useCallback((content: string) => {
    setAnswer(prev => prev + content);
    
    // Update lanes when content starts flowing
    setLanes(prev => prev.map(lane => {
      if (lane.status === 'pending') {
        return { ...lane, status: 'running', startTime: lane.startTime || Date.now() };
      }
      return lane;
    }));
    
    // Show partial banner if not all lanes are complete
    const completedLanes = lanes.filter(lane => lane.status === 'completed').length;
    if (completedLanes < lanes.length && !showPartialBanner) {
      setShowPartialBanner(true);
    }
  }, [lanes, showPartialBanner]);

  const handleComplete = useCallback((data: any) => {
    console.log('Stream completed:', data);
    
    if (data.sources) {
      setSources(data.sources);
    }
    
    if (data.citations) {
      setCitations(data.citations);
    }

    // Mark all lanes as completed
    setLanes(prev => prev.map(lane => ({
      ...lane,
      status: 'completed' as const,
      endTime: Date.now()
    })));
    
    setIsLoading(false);
    setConnectionStatus('disconnected');
    setShowPartialBanner(false);
    
    onComplete?.(data);
  }, [onComplete]);

  const handleError = useCallback((error: string) => {
    console.error('Stream error:', error);
    
    // Mark all lanes as error
    setLanes(prev => prev.map(lane => ({
      ...lane,
      status: 'error' as const,
      endTime: Date.now(),
      error
    })));
    
    setIsLoading(false);
    setConnectionStatus('disconnected');
    setShowPartialBanner(false);
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
    setTtft(undefined);
    setShowPartialBanner(false);
    
    // Initialize lanes
    setLanes([
      { id: 'web', name: 'Web', status: 'pending', timeout: 3000 },
      { id: 'vector', name: 'Vector', status: 'pending', timeout: 3000 },
      { id: 'kg', name: 'KG', status: 'pending', timeout: 3000 },
      { id: 'llm', name: 'LLM', status: 'pending', timeout: 3000 },
      { id: 'youtube', name: 'YouTube', status: 'pending', timeout: 3000 }
    ]);

    const startTime = Date.now();

    // Start streaming
    start();
    
    // Set TTFT when first content arrives
    setTimeout(() => {
      const ttftTime = Date.now() - startTime;
      setTtft(ttftTime);
    }, 100);
  }, [query, isLoading, start]);

  const handleStop = useCallback(() => {
    stop();
    setIsLoading(false);
    setConnectionStatus('disconnected');
  }, [stop]);

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-cosmic-success';
      case 'connecting': return 'text-cosmic-warning';
      case 'reconnecting': return 'text-cosmic-error';
      case 'disconnected': return 'cosmic-text-tertiary';
      default: return 'cosmic-text-tertiary';
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
            className="cosmic-input flex-1"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="cosmic-btn-primary px-6 py-3 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
          {isLoading && (
            <button
              type="button"
              onClick={handleStop}
              className="cosmic-btn-secondary bg-cosmic-error hover:bg-cosmic-error/80 text-white px-4 py-3 font-medium"
            >
              Stop
            </button>
          )}
        </div>
      </form>

      {/* Streaming Status */}
      <div className="mb-4 space-y-3">
        <div className="flex items-center justify-between">
          <StreamingStatus
            isStreaming={isLoading}
            connectionStatus={connectionStatus}
            lastHeartbeat={heartbeatData?.timestamp}
          />
          {traceId && <TraceIdDisplay traceId={traceId} size="sm" />}
        </div>
        
        {/* Lane Progress */}
        {isLoading && <LaneProgress lanes={lanes} />}
        
        {/* Lane Chips */}
        {isLoading && <LaneChips lanes={lanes} />}
        
        {/* TTFT Indicator */}
        {ttft && <TTFTIndicator ttft={ttft} />}
      </div>

      {/* Error Display */}
      {error && (
        <div className="cosmic-card border-cosmic-error bg-cosmic-error/5 p-4 mb-4">
          <strong className="text-cosmic-error">Error:</strong> <span className="text-cosmic-error/80">{error}</span>
        </div>
      )}

      {/* Partial Answer Banner */}
      <PartialAnswerBanner
        isVisible={showPartialBanner}
        completedLanes={lanes.filter(lane => lane.status === 'completed').length}
        totalLanes={lanes.length}
        onDismiss={() => setShowPartialBanner(false)}
      />

      {/* Answer Display */}
      {answer && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 cosmic-text-primary">Answer</h3>
          <div className="cosmic-card p-4">
            <div className="whitespace-pre-wrap cosmic-text-primary leading-relaxed">
              {answer}
              {isLoading && <span className="animate-pulse">|</span>}
            </div>
          </div>
        </div>
      )}

      {/* Sources Display */}
      {sources.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 cosmic-text-primary">Sources</h3>
          <div className="space-y-3">
            {sources.map((source, index) => (
              <div key={index} className="cosmic-card p-4">
                <h4 className="font-medium cosmic-text-primary mb-2">
                  <a 
                    href={source.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-cosmic-primary-500 hover:text-cosmic-primary-400 transition-colors"
                  >
                    {source.title}
                  </a>
                </h4>
                <p className="cosmic-text-secondary text-sm mb-2">{source.snippet}</p>
                <div className="flex items-center gap-4 text-xs cosmic-text-tertiary">
                  <span>{source.domain}</span>
                  <span>Provider: {source.provider}</span>
                  <span>Score: {(source.relevance_score * 100).toFixed(1)}%</span>
                  {/* Fallback Badge - show if provider is keyless */}
                  <FallbackBadge
                    fallbackUsed={source.provider?.includes('keyless') || source.provider?.includes('fallback')}
                    source={source.provider?.includes('keyless') ? 'keyless' : 'keyed'}
                    provider={source.provider}
                    lane="web_search"
                    traceId={traceId}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Citations Display */}
      {citations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 cosmic-text-primary">Citations</h3>
          <div className="space-y-2">
            {citations.map((citation, index) => (
              <div key={index} className="cosmic-card p-3">
                <div className="flex items-start gap-3">
                  <span className="bg-cosmic-primary-500 text-white text-xs px-2 py-1 rounded">
                    {citation.marker}
                  </span>
                  <div className="flex-1">
                    <p className="cosmic-text-primary text-sm mb-1">
                      {citation.source.title}
                    </p>
                    <div className="flex items-center gap-4 text-xs cosmic-text-tertiary">
                      <span>Confidence: {(citation.confidence * 100).toFixed(1)}%</span>
                      <span>Type: {citation.claim_type}</span>
                      <a 
                        href={citation.source.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-cosmic-primary-500 hover:text-cosmic-primary-400"
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
        <div className="mt-6 cosmic-card p-4">
          <h4 className="text-sm font-medium cosmic-text-primary mb-2">Debug Info</h4>
          <pre className="text-xs cosmic-text-tertiary overflow-auto">
            {JSON.stringify(heartbeatData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
