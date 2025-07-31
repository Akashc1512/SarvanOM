import { lazy, Suspense } from "react";
import { LoadingSpinner } from "@/components/atoms/loading-spinner";

// Lazy load the AnswerDisplay component
const AnswerDisplay = lazy(() =>
  import("@/components/AnswerDisplay").then((module) => ({
    default: module.AnswerDisplay,
  })),
);

interface LazyAnswerDisplayProps {
  query: any;
  onFeedback?: (_rating: number, _helpful: boolean, _feedback?: string) => void;
}

export function LazyAnswerDisplay({
  query,
  onFeedback,
}: LazyAnswerDisplayProps) {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center p-8">
          <LoadingSpinner size="lg" />
          <span className="ml-2 text-gray-600">Loading answer...</span>
        </div>
      }
    >
      {onFeedback ? (
        <AnswerDisplay query={query} onFeedback={onFeedback} />
      ) : (
        <AnswerDisplay query={query} />
      )}
    </Suspense>
  );
}
