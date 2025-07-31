import { useEffect, useCallback, useRef } from "react";

interface UseKeyboardNavigationOptions {
  onEnter?: () => void;
  onEscape?: () => void;
  onTab?: (direction: "forward" | "backward") => void;
  enabled?: boolean;
}

export function useKeyboardNavigation({
  onEnter,
  onEscape,
  onTab,
  enabled = true,
}: UseKeyboardNavigationOptions = {}) {
  const elementRef = useRef<HTMLElement>(null);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      switch (event.key) {
        case "Enter":
          if (onEnter) {
            event.preventDefault();
            onEnter();
          }
          break;
        case "Escape":
          if (onEscape) {
            event.preventDefault();
            onEscape();
          }
          break;
        case "Tab":
          if (onTab) {
            const direction = event.shiftKey ? "backward" : "forward";
            onTab(direction);
          }
          break;
      }
    },
    [enabled, onEnter, onEscape, onTab],
  );

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    element.addEventListener("keydown", handleKeyDown);
    return () => element.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  return elementRef;
}
