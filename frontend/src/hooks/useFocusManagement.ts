import { useCallback, useRef, useEffect } from "react";

interface UseFocusManagementOptions {
  trapFocus?: boolean;
  restoreFocus?: boolean;
  initialFocus?: string;
}

export function useFocusManagement({
  trapFocus = false,
  restoreFocus = true,
  initialFocus,
}: UseFocusManagementOptions = {}) {
  const containerRef = useRef<HTMLElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // Save the currently focused element
  const saveFocus = useCallback(() => {
    previousFocusRef.current = document.activeElement as HTMLElement;
  }, []);

  // Restore focus to the previously focused element
  const restorePreviousFocus = useCallback(() => {
    if (restoreFocus && previousFocusRef.current) {
      previousFocusRef.current.focus();
    }
  }, [restoreFocus]);

  // Focus the first focusable element in the container
  const focusFirstElement = useCallback(() => {
    if (!containerRef.current) return;

    const focusableElements = containerRef.current.querySelectorAll(
      "button, [href], input, select, textarea, [tabindex]:not([tabindex=\"-1\"])",
    );

    if (focusableElements.length > 0) {
      const firstElement = focusableElements[0] as HTMLElement;
      firstElement.focus();
    }
  }, []);

  // Focus a specific element by selector
  const focusElement = useCallback((selector: string) => {
    if (!containerRef.current) return;

    const element = containerRef.current.querySelector(selector) as HTMLElement;
    if (element) {
      element.focus();
    }
  }, []);

  // Trap focus within the container
  const trapFocusInContainer = useCallback(
    (event: KeyboardEvent) => {
      if (!containerRef.current || !trapFocus) return;

      const focusableElements = Array.from(
        containerRef.current.querySelectorAll(
          "button, [href], input, select, textarea, [tabindex]:not([tabindex=\"-1\"])",
        ),
      ) as HTMLElement[];

      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (event.key === "Tab") {
        if (event.shiftKey) {
          // Shift + Tab: move to previous element
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement?.focus();
          }
        } else {
          // Tab: move to next element
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement?.focus();
          }
        }
      }
    },
    [trapFocus],
  );

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Save current focus when component mounts
    saveFocus();

    // Focus initial element if specified
    if (initialFocus) {
      focusElement(initialFocus);
    } else {
      focusFirstElement();
    }

    // Add focus trap event listener
    if (trapFocus) {
      container.addEventListener("keydown", trapFocusInContainer);
    }

    return () => {
      if (trapFocus) {
        container.removeEventListener("keydown", trapFocusInContainer);
      }
      restorePreviousFocus();
    };
  }, [
    saveFocus,
    focusFirstElement,
    focusElement,
    initialFocus,
    trapFocus,
    trapFocusInContainer,
    restorePreviousFocus,
  ]);

  return {
    containerRef,
    focusFirstElement,
    focusElement,
    restorePreviousFocus,
  };
}
