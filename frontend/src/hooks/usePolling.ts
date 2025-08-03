import { useEffect, useRef, useCallback } from "react";

interface UsePollingOptions {
  enabled: boolean;
  interval: number;
  onPoll: () => Promise<void>;
  onError?: (error: Error) => void;
  maxAttempts?: number;
}

export function usePolling({
  enabled,
  interval,
  onPoll,
  onError,
  maxAttempts = 10,
}: UsePollingOptions) {
  const intervalRef = useRef<NodeJS.Timeout>();
  const attemptsRef = useRef(0);
  const isPollingRef = useRef(false);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = undefined;
    }
    isPollingRef.current = false;
  }, []);

  const startPolling = useCallback(() => {
    if (!enabled || isPollingRef.current) return;

    isPollingRef.current = true;
    attemptsRef.current = 0;

    const poll = async () => {
      if (attemptsRef.current >= maxAttempts) {
        stopPolling();
        return;
      }

      try {
        await onPoll();
        attemptsRef.current++;
      } catch (error) {
        onError?.(error as Error);
        stopPolling();
      }
    };

    // Initial poll
    poll();

    // Set up interval
    intervalRef.current = setInterval(poll, interval);
  }, [enabled, interval, onPoll, onError, maxAttempts, stopPolling]);

  useEffect(() => {
    if (enabled) {
      startPolling();
    } else {
      stopPolling();
    }

    return stopPolling;
  }, [enabled, startPolling, stopPolling]);

  return { stopPolling };
}
