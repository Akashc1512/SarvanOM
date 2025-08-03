"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";

export function Analytics() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Track page views
    const trackPageView = () => {
      // Example: Send to analytics service
      // analytics.track('page_view', {
      //   path: pathname,
      //   search: searchParams.toString(),
      //   title: document.title,
      //   timestamp: new Date().toISOString(),
      // });

      console.log("Page view:", {
        path: pathname,
        search: searchParams.toString(),
        title: document.title,
      });
    };

    trackPageView();
  }, [pathname, searchParams]);

  // Track user interactions
  useEffect(() => {
    const trackUserInteraction = (event: MouseEvent | KeyboardEvent) => {
      const target = event.target as HTMLElement;

      // Track button clicks
      if (target.tagName === "BUTTON" || target.closest("button")) {
        const button =
          target.tagName === "BUTTON" ? target : target.closest("button");
        const text = button?.textContent?.trim();
        const className = button?.className;

        console.log("Button click:", { text, className });
      }

      // Track form submissions
      if (target.tagName === "FORM" || target.closest("form")) {
        const form =
          target.tagName === "FORM" ? target : target.closest("form");
        const action = form?.getAttribute("action");
        const method = form?.getAttribute("method");

        console.log("Form interaction:", { action, method });
      }
    };

    document.addEventListener("click", trackUserInteraction);
    document.addEventListener("keydown", trackUserInteraction);

    return () => {
      document.removeEventListener("click", trackUserInteraction);
      document.removeEventListener("keydown", trackUserInteraction);
    };
  }, []);

  // Track performance metrics
  useEffect(() => {
    if (typeof window !== "undefined" && "performance" in window) {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === "navigation") {
            const navEntry = entry as PerformanceNavigationTiming;
            console.log("Performance metrics:", {
              loadTime: navEntry.loadEventEnd - navEntry.loadEventStart,
              domContentLoaded:
                navEntry.domContentLoadedEventEnd -
                navEntry.domContentLoadedEventStart,
              firstPaint: navEntry.responseStart - navEntry.requestStart,
            });
          }
        }
      });

      observer.observe({ entryTypes: ["navigation"] });

      return () => observer.disconnect();
    }
    
    // Return undefined when performance API is not available
    return undefined;
  }, []);

  return null;
}
