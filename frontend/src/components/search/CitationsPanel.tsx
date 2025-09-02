"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  DocumentTextIcon, 
  LinkIcon, 
  ChevronDownIcon,
  ChevronUpIcon,
  ExternalLinkIcon,
  CalendarIcon,
  UserIcon,
  StarIcon
} from "@heroicons/react/24/outline";
import { cn } from "@/lib/utils";
import { CitationNumber } from "./CitationTooltip";
import type { Citation } from "@/lib/api";

interface CitationsPanelProps {
  citations?: Citation[];
  className?: string;
  isExpanded?: boolean;
  onToggle?: () => void;
}

export function CitationsPanel({ 
  citations = [], 
  className,
  isExpanded = true,
  onToggle 
}: CitationsPanelProps) {
  const [expandedCitations, setExpandedCitations] = useState<Set<string>>(new Set());

  const toggleCitation = (id: string) => {
    const newExpanded = new Set(expandedCitations);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedCitations(newExpanded);
  };

  const getTypeIcon = (type: Citation["type"]) => {
    switch (type) {
      case "article":
        return "📄";
      case "paper":
        return "📊";
      case "book":
        return "📚";
      case "website":
        return "🌐";
      case "document":
        return "📋";
      default:
        return "📄";
    }
  };

  const getTypeColor = (type: Citation["type"]) => {
    switch (type) {
      case "article":
        return "text-blue-400";
      case "paper":
        return "text-green-400";
      case "book":
        return "text-purple-400";
      case "website":
        return "text-orange-400";
      case "document":
        return "text-gray-400";
      default:
        return "text-cosmos-accent";
    }
  };

  if (!citations.length) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className={cn("w-full", className)}
      >
        <div className="bg-cosmos-card/30 backdrop-blur-sm border border-cosmos-accent/20 rounded-2xl p-6">
          <div className="text-center">
            <DocumentTextIcon className="w-12 h-12 text-cosmos-accent/50 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-cosmos-fg mb-2">No Citations Yet</h3>
            <p className="text-cosmos-fg/60 text-sm">
              Sources and references will appear here when you search
            </p>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn("w-full", className)}
    >
      <div className="bg-cosmos-card/50 backdrop-blur-sm border border-cosmos-accent/20 rounded-2xl overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-cosmos-accent/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-cosmos-accent/20 rounded-lg flex items-center justify-center">
                <DocumentTextIcon className="w-5 h-5 text-cosmos-accent" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-cosmos-fg">Sources & Citations</h3>
                <p className="text-sm text-cosmos-fg/60">{citations.length} references found</p>
              </div>
            </div>
            
            {onToggle && (
              <button
                onClick={onToggle}
                className="p-2 rounded-lg hover:bg-cosmos-accent/10 transition-colors"
              >
                {isExpanded ? (
                  <ChevronUpIcon className="w-5 h-5 text-cosmos-fg/60" />
                ) : (
                  <ChevronDownIcon className="w-5 h-5 text-cosmos-fg/60" />
                )}
              </button>
            )}
          </div>
        </div>

        {/* Citations List */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="max-h-96 overflow-y-auto"
            >
              <div className="p-4 space-y-3">
                {citations.map((citation, index) => (
                  <motion.div
                    key={citation.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-cosmos-bg/20 border border-cosmos-accent/10 rounded-xl p-4 hover:bg-cosmos-bg/30 transition-all"
                  >
                    {/* Citation Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3 flex-1">
                        <div className="flex items-center gap-2">
                          <CitationNumber
                            citation={citation}
                            number={index + 1}
                            className="flex-shrink-0"
                          />
                          <span className="text-2xl">{getTypeIcon(citation.type)}</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-cosmos-fg truncate">
                            {citation.title}
                          </h4>
                          <p className="text-sm text-cosmos-fg/60 truncate">
                            {citation.source}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1 text-xs text-cosmos-fg/60">
                          <StarIcon className="w-3 h-3" />
                          <span>{Math.round(citation.relevance * 100)}%</span>
                        </div>
                        <button
                          onClick={() => toggleCitation(citation.id)}
                          className="p-1 rounded hover:bg-cosmos-accent/10 transition-colors"
                        >
                          {expandedCitations.has(citation.id) ? (
                            <ChevronUpIcon className="w-4 h-4 text-cosmos-fg/60" />
                          ) : (
                            <ChevronDownIcon className="w-4 h-4 text-cosmos-fg/60" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Citation Metadata */}
                    <div className="flex items-center gap-4 text-xs text-cosmos-fg/60 mb-3">
                      {citation.author && (
                        <div className="flex items-center gap-1">
                          <UserIcon className="w-3 h-3" />
                          <span>{citation.author}</span>
                        </div>
                      )}
                      {citation.date && (
                        <div className="flex items-center gap-1">
                          <CalendarIcon className="w-3 h-3" />
                          <span>{citation.date}</span>
                        </div>
                      )}
                      <span className={cn("px-2 py-1 rounded-full text-xs font-medium", getTypeColor(citation.type))}>
                        {citation.type}
                      </span>
                    </div>

                    {/* Expanded Content */}
                    <AnimatePresence>
                      {expandedCitations.has(citation.id) && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="border-t border-cosmos-accent/10 pt-3"
                        >
                          {citation.excerpt && (
                            <p className="text-sm text-cosmos-fg/80 mb-3 leading-relaxed">
                              {citation.excerpt}
                            </p>
                          )}
                          
                          <div className="flex items-center gap-2">
                            {citation.url && (
                              <a
                                href={citation.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 px-3 py-2 bg-cosmos-accent/10 hover:bg-cosmos-accent/20 text-cosmos-accent rounded-lg transition-all text-sm"
                              >
                                <ExternalLinkIcon className="w-4 h-4" />
                                <span>View Source</span>
                              </a>
                            )}
                            <button className="flex items-center gap-2 px-3 py-2 bg-cosmos-card/50 hover:bg-cosmos-card/70 text-cosmos-fg/80 rounded-lg transition-all text-sm">
                              <LinkIcon className="w-4 h-4" />
                              <span>Copy Link</span>
                            </button>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
