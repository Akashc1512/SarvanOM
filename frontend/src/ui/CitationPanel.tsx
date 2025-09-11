"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  ExternalLink, 
  Copy, 
  Calendar, 
  User, 
  FileText, 
  ChevronDown, 
  ChevronUp,
  Star,
  Globe
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Citation {
  id: string;
  title: string;
  url?: string;
  author?: string;
  date?: string;
  type?: 'academic' | 'news' | 'report' | 'website';
  relevance?: number;
  summary?: string;
}

interface CitationPanelProps {
  citations?: Citation[];
  className?: string;
  isExpanded?: boolean;
  onToggle?: () => void;
}

export default function CitationPanel({
  citations = [],
  className,
  isExpanded = true,
  onToggle
}: CitationPanelProps) {
  const [expandedCitations, setExpandedCitations] = useState<Set<string>>(new Set());

  const toggleCitation = (citationId: string) => {
    const newExpanded = new Set(expandedCitations);
    if (newExpanded.has(citationId)) {
      newExpanded.delete(citationId);
    } else {
      newExpanded.add(citationId);
    }
    setExpandedCitations(newExpanded);
  };

  const getTypeIcon = (type?: string) => {
    switch (type) {
      case 'academic':
        return <FileText className="h-4 w-4" />;
      case 'news':
        return <Globe className="h-4 w-4" />;
      case 'report':
        return <FileText className="h-4 w-4" />;
      default:
        return <Globe className="h-4 w-4" />;
    }
  };

  const getTypeColor = (type?: string) => {
    switch (type) {
      case 'academic':
        return 'border-cosmic-primary-500 text-cosmic-primary-500';
      case 'news':
        return 'border-cosmic-secondary-500 text-cosmic-secondary-500';
      case 'report':
        return 'border-cosmic-warning text-cosmic-warning';
      default:
        return 'border-cosmic-border-primary text-cosmic-text-primary';
    }
  };

  if (citations.length === 0) {
    return (
      <Card className={cn("cosmic-card", className)}>
        <CardHeader>
          <CardTitle className="cosmic-text-primary">Sources</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="cosmic-text-secondary text-center py-4">
            No sources available yet.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("cosmic-card", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="cosmic-text-primary">Sources & Citations</CardTitle>
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
              <div className="space-y-3">
                {citations.map((citation, index) => (
                  <motion.div
                    key={citation.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-3 cosmic-bg-secondary rounded-lg border border-cosmic-border-primary"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-cosmic-primary-500">
                          [{index + 1}]
                        </span>
                        <Badge 
                          variant="outline" 
                          className={cn("text-xs", getTypeColor(citation.type))}
                        >
                          {getTypeIcon(citation.type)}
                          <span className="ml-1">{citation.type || 'source'}</span>
                        </Badge>
                        {citation.relevance && (
                          <Badge variant="outline" className="text-xs border-cosmic-border-primary text-cosmic-text-primary">
                            <Star className="h-3 w-3 mr-1" />
                            {citation.relevance}% relevant
                          </Badge>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleCitation(citation.id)}
                        className="h-6 w-6 p-0"
                      >
                        {expandedCitations.has(citation.id) ? 
                          <ChevronUp className="h-3 w-3" /> : 
                          <ChevronDown className="h-3 w-3" />
                        }
                      </Button>
                    </div>
                    
                    <h4 className="font-medium cosmic-text-primary mb-1 line-clamp-2">
                      {citation.title}
                    </h4>
                    
                    <div className="flex items-center gap-4 text-xs cosmic-text-tertiary mb-2">
                      {citation.author && (
                        <span className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          {citation.author}
                        </span>
                      )}
                      {citation.date && (
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {citation.date}
                        </span>
                      )}
                    </div>
                    
                    <AnimatePresence>
                      {expandedCitations.has(citation.id) && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                          className="border-t border-cosmic-border-primary pt-2 mt-2"
                        >
                          {citation.summary && (
                            <p className="text-sm cosmic-text-secondary mb-3">
                              {citation.summary}
                            </p>
                          )}
                          
                          <div className="flex items-center gap-2">
                            {citation.url && (
                              <Button
                                variant="outline"
                                size="sm"
                                asChild
                                className="cosmic-btn-secondary"
                              >
                                <a href={citation.url} target="_blank" rel="noopener noreferrer">
                                  <ExternalLink className="h-3 w-3 mr-1" />
                                  View Source
                                </a>
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                const citationText = `${citation.title}${citation.author ? ` by ${citation.author}` : ''}${citation.date ? ` (${citation.date})` : ''}`;
                                navigator.clipboard.writeText(citationText);
                              }}
                              className="cosmic-btn-secondary"
                            >
                              <Copy className="h-3 w-3 mr-1" />
                              Copy Citation
                            </Button>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}