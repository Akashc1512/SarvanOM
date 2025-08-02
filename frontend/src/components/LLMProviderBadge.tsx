"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Sparkles,
  MessageSquare,
  Brain,
  Zap,
  Clock,
  Cpu,
} from "lucide-react";

export type LLMProvider = 'ollama' | 'openai' | 'huggingface' | 'anthropic' | 'azure' | 'google' | 'unknown';

interface LLMProviderBadgeProps {
  provider: LLMProvider;
  model: string;
  responseTime?: number | undefined;
  confidence?: number | undefined;
  className?: string;
  showDetails?: boolean;
}

export function LLMProviderBadge({
  provider,
  model,
  responseTime,
  confidence,
  className = "",
  showDetails = true,
}: LLMProviderBadgeProps) {
  const getProviderInfo = (provider: LLMProvider) => {
    switch (provider) {
      case 'ollama':
        return {
          name: 'Ollama',
          icon: Sparkles,
          color: 'bg-blue-100 text-blue-800 border-blue-200',
          description: 'Local AI model running on your device',
        };
      case 'openai':
        return {
          name: 'OpenAI',
          icon: MessageSquare,
          color: 'bg-green-100 text-green-800 border-green-200',
          description: 'OpenAI GPT model',
        };
      case 'huggingface':
        return {
          name: 'HuggingFace',
          icon: Brain,
          color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          description: 'HuggingFace model',
        };
      case 'anthropic':
        return {
          name: 'Anthropic',
          icon: Cpu,
          color: 'bg-purple-100 text-purple-800 border-purple-200',
          description: 'Anthropic Claude model',
        };
      case 'azure':
        return {
          name: 'Azure',
          icon: Zap,
          color: 'bg-blue-100 text-blue-800 border-blue-200',
          description: 'Azure OpenAI model',
        };
      case 'google':
        return {
          name: 'Google',
          icon: Brain,
          color: 'bg-red-100 text-red-800 border-red-200',
          description: 'Google Gemini model',
        };
      default:
        return {
          name: 'Unknown',
          icon: MessageSquare,
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          description: 'Unknown AI provider',
        };
    }
  };

  const providerInfo = getProviderInfo(provider);
  const IconComponent = providerInfo.icon;

  const formatResponseTime = (time?: number) => {
    if (!time) return null;
    if (time < 1) return `${(time * 1000).toFixed(0)}ms`;
    return `${time.toFixed(1)}s`;
  };

  const getModelDisplayName = (model: string) => {
    // Extract readable model names
    const modelMap: Record<string, string> = {
      'gpt-4': 'GPT-4',
      'gpt-3.5-turbo': 'GPT-3.5 Turbo',
      'gpt-4-turbo': 'GPT-4 Turbo',
      'claude-3-5-sonnet': 'Claude 3.5 Sonnet',
      'claude-3-opus': 'Claude 3 Opus',
      'llama3.2:3b': 'Llama 3.2 3B',
      'llama3.2:8b': 'Llama 3.2 8B',
      'mistral:7b': 'Mistral 7B',
      'codellama:7b': 'Code Llama 7B',
      'gemini-pro': 'Gemini Pro',
    };

    return modelMap[model] || model;
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return '';
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const tooltipContent = (
    <div className="space-y-2">
      <div className="font-medium">{providerInfo.name}</div>
      <div className="text-sm text-gray-600">{providerInfo.description}</div>
      <div className="text-sm">
        <span className="font-medium">Model:</span> {getModelDisplayName(model)}
      </div>
      {responseTime && (
        <div className="text-sm">
          <span className="font-medium">Response Time:</span> {formatResponseTime(responseTime)}
        </div>
      )}
      {confidence && (
        <div className="text-sm">
          <span className="font-medium">Confidence:</span> {Math.round(confidence * 100)}%
        </div>
      )}
    </div>
  );

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className={`inline-flex items-center space-x-1 ${className}`}>
            <Badge
              variant="outline"
              className={`text-xs font-medium border ${providerInfo.color}`}
            >
              <IconComponent className="h-3 w-3 mr-1" />
              {showDetails ? (
                <span className="flex items-center space-x-1">
                  <span>{providerInfo.name}</span>
                  {responseTime && (
                    <>
                      <span>•</span>
                      <Clock className="h-3 w-3" />
                      <span>{formatResponseTime(responseTime)}</span>
                    </>
                  )}
                  {confidence && (
                    <>
                      <span>•</span>
                      <span className={getConfidenceColor(confidence)}>
                        {Math.round(confidence * 100)}%
                      </span>
                    </>
                  )}
                </span>
              ) : (
                <span>{providerInfo.name}</span>
              )}
            </Badge>
          </div>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs">
          {tooltipContent}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

// Compact version for use in tight spaces
export function CompactLLMProviderBadge({
  provider,
  model,
  responseTime,
  className = "",
}: LLMProviderBadgeProps) {
  return (
    <LLMProviderBadge
      provider={provider}
      model={model}
      responseTime={responseTime}
      className={className}
      showDetails={false}
    />
  );
}

// Detailed version with full information
export function DetailedLLMProviderBadge({
  provider,
  model,
  responseTime,
  confidence,
  className = "",
}: LLMProviderBadgeProps) {
  return (
    <LLMProviderBadge
      provider={provider}
      model={model}
      responseTime={responseTime}
      confidence={confidence}
      className={className}
      showDetails={true}
    />
  );
} 