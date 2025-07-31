import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { StatusBadge, type StatusType } from "@/components/atoms/status-badge";
import { LoadingSpinner } from "@/components/atoms/loading-spinner";
import { Clock, CheckCircle, AlertCircle, Loader2, AlertTriangle, Info } from "lucide-react";
import { type QueryResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

interface QueryStatusCardProps {
  query: QueryResponse;
  className?: string;
}

const getStatusConfig = (status: string) => {
  switch (status) {
    case "pending":
      return {
        type: "pending" as StatusType,
        icon: Clock,
        text: "Queued for processing",
        color: "text-yellow-600",
      };
    case "processing":
      return {
        type: "processing" as StatusType,
        icon: Loader2,
        text: "Analyzing and synthesizing...",
        color: "text-blue-600",
      };
    case "completed":
      return {
        type: "completed" as StatusType,
        icon: CheckCircle,
        text: "Research complete",
        color: "text-green-600",
      };
    case "failed":
      return {
        type: "failed" as StatusType,
        icon: AlertCircle,
        text: "Processing failed",
        color: "text-red-600",
      };
    default:
      return {
        type: "info" as StatusType,
        icon: Clock,
        text: "Unknown status",
        color: "text-gray-600",
      };
  }
};

export const QueryStatusCard = React.memo<QueryStatusCardProps>(
  ({ query, className }) => {
    const statusConfig = getStatusConfig(query.status);
    const IconComponent = statusConfig.icon;

    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    return (
      <Card className={cn("transition-all duration-200", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {query.status === "processing" ? (
              <LoadingSpinner size="sm" color="primary" />
            ) : (
              <IconComponent className={cn("h-5 w-5", statusConfig.color)} />
            )}
            Query Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-gray-700">Query:</p>
              <p className="text-gray-900 font-mono text-sm break-all">
                {query.query_id}
              </p>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-700">Status:</p>
              <div className="flex items-center gap-2 mt-1">
                <StatusBadge status={statusConfig.type} showIcon size="sm" />
                <span className="text-sm text-gray-600">
                  {statusConfig.text}
                </span>
              </div>
            </div>

            {query.confidence && (
              <div>
                <p className="text-sm font-medium text-gray-700">Confidence:</p>
                <div className="flex items-center gap-2">
                  <p className={cn(
                    "text-gray-900",
                    query.confidence < 0.7 && "text-yellow-600 font-medium"
                  )}>
                    {(query.confidence * 100).toFixed(1)}%
                  </p>
                  {query.confidence < 0.7 && (
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  )}
                </div>
              </div>
            )}

            {/* LLM Provider Information */}
            {query.llm_provider && (
              <div>
                <p className="text-sm font-medium text-gray-700">AI Provider:</p>
                <div className="flex items-center gap-2">
                  <p className={cn(
                    "text-gray-900",
                    query.llm_provider === "fallback" && "text-yellow-600 font-medium"
                  )}>
                    {query.llm_provider === "fallback" ? "Fallback Mode" : query.llm_provider}
                  </p>
                  {query.llm_provider === "fallback" && (
                    <Info className="h-4 w-4 text-blue-500" />
                  )}
                </div>
              </div>
            )}

            {/* LLM Model Information */}
            {query.llm_model && (
              <div>
                <p className="text-sm font-medium text-gray-700">AI Model:</p>
                <p className={cn(
                  "text-gray-900",
                  query.llm_model === "mock" && "text-yellow-600 font-medium"
                )}>
                  {query.llm_model === "mock" ? "Mock Response" : query.llm_model}
                </p>
              </div>
            )}

            {/* Answer Display */}
            {query.answer && (
              <div>
                <p className="text-sm font-medium text-gray-700">Answer:</p>
                <div className={cn(
                  "mt-2 p-3 rounded-lg border",
                  query.llm_provider === "fallback" 
                    ? "bg-yellow-50 border-yellow-200" 
                    : "bg-gray-50 border-gray-200"
                )}>
                  <p className="text-gray-900 text-sm leading-relaxed">
                    {query.answer}
                  </p>
                  {query.llm_provider === "fallback" && (
                    <div className="mt-2 flex items-center gap-2 text-xs text-yellow-700">
                      <AlertTriangle className="h-3 w-3" />
                      <span>This is a fallback response. For full AI capabilities, please configure your LLM provider.</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            <div>
              <p className="text-sm font-medium text-gray-700">Created:</p>
              <p className="text-gray-900 text-sm">
                {formatDate(query.created_at)}
              </p>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-700">Updated:</p>
              <p className="text-gray-900 text-sm">
                {formatDate(query.updated_at)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  },
);

QueryStatusCard.displayName = "QueryStatusCard";
