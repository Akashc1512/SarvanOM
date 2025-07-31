"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "@/lib/utils";

interface BreadcrumbItem {
  label: string;
  href: string;
  current?: boolean;
}

export function Breadcrumbs() {
  const pathname = usePathname();

  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const segments = pathname.split("/").filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [{ label: "Home", href: "/" }];

    let currentPath = "";
    segments.forEach((segment, index) => {
      currentPath += `/${segment}`;

      // Map segment to readable label
      const label = segment
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");

      breadcrumbs.push({
        label,
        href: currentPath,
        current: index === segments.length - 1,
      });
    });

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  // Don't show breadcrumbs on home page
  if (breadcrumbs.length <= 1) {
    return null;
  }

  return (
    <nav
      className="flex items-center space-x-1 text-sm text-gray-500 mb-4"
      aria-label="Breadcrumb"
    >
      {breadcrumbs.map((item, index) => (
        <React.Fragment key={item.href}>
          {index > 0 && (
            <ChevronRight
              className="h-4 w-4 text-gray-400"
              aria-hidden="true"
            />
          )}

          {item.current ? (
            <span
              className={cn("font-medium text-gray-900", "cursor-default")}
              aria-current="page"
            >
              {index === 0 ? <Home className="h-4 w-4 inline" /> : item.label}
            </span>
          ) : (
            <Link
              href={item.href}
              className={cn(
                "hover:text-gray-700 transition-colors",
                index === 0 && "flex items-center",
              )}
            >
              {index === 0 ? (
                <>
                  <Home className="h-4 w-4 mr-1" />
                  {item.label}
                </>
              ) : (
                item.label
              )}
            </Link>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
}
