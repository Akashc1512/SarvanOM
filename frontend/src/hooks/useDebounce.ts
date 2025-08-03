import { useCallback, useRef } from "react";

export function useDebounce<T extends (..._args: any[]) => any>(
  callback: T,
  delay: number,
): T {
  const timeoutRef = useRef<NodeJS.Timeout>();

  const debouncedFunction = (...args: Parameters<T>) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => callback(...args), delay);
  };

  return debouncedFunction as T;
}
