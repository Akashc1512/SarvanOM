import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface UseUrlStateOptions {
  replace?: boolean;
  scroll?: boolean;
}

export function useUrlState<T extends Record<string, any>>(
  initialState: T,
  options: UseUrlStateOptions = {},
) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [state, setState] = useState<T>(() => {
    // Initialize state from URL params
    const urlState: Partial<T> = {};
    for (const [key, value] of searchParams.entries()) {
      if (key in initialState) {
        // Try to parse the value based on the initial state type
        const initialValue = initialState[key as keyof T];
        if (typeof initialValue === "number") {
          urlState[key as keyof T] = Number(value) as T[keyof T];
        } else if (typeof initialValue === "boolean") {
          urlState[key as keyof T] = (value === "true") as T[keyof T];
        } else {
          urlState[key as keyof T] = value as T[keyof T];
        }
      }
    }
    return { ...initialState, ...urlState };
  });

  const updateUrl = useCallback(
    (newState: Partial<T>) => {
      const params = new URLSearchParams(searchParams.toString());

      // Update URL params based on new state
      Object.entries(newState).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
          params.set(key, String(value));
        } else {
          params.delete(key);
        }
      });

      const newUrl = `${window.location.pathname}?${params.toString()}`;

      if (options.replace) {
        router.replace(newUrl, { scroll: options.scroll ?? false });
      } else {
        router.push(newUrl, { scroll: options.scroll ?? false });
      }
    },
    [router, searchParams, options.replace, options.scroll],
  );

  const setUrlState = useCallback(
    (newState: Partial<T> | ((prev: T) => Partial<T>)) => {
      const updatedState =
        typeof newState === "function" ? newState(state) : newState;
      setState((prev) => ({ ...prev, ...updatedState }));
      updateUrl(updatedState);
    },
    [state, updateUrl],
  );

  // Sync state with URL params when they change
  useEffect(() => {
    const urlState: Partial<T> = {};
    let hasChanges = false;

    for (const [key, value] of searchParams.entries()) {
      if (key in initialState) {
        const initialValue = initialState[key as keyof T];
        let parsedValue: any;

        if (typeof initialValue === "number") {
          parsedValue = Number(value);
        } else if (typeof initialValue === "boolean") {
          parsedValue = value === "true";
        } else {
          parsedValue = value;
        }

        if (state[key as keyof T] !== parsedValue) {
          urlState[key as keyof T] = parsedValue as T[keyof T];
          hasChanges = true;
        }
      }
    }

    if (hasChanges) {
      setState((prev) => ({ ...prev, ...urlState }));
    }
  }, [searchParams, initialState, state]);

  return [state, setUrlState] as const;
}
