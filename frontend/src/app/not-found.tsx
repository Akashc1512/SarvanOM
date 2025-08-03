"use client";

import Link from "next/link";
import { Button } from "@/ui/ui/button";
import { Search, Home, ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            {/* 404 Icon */}
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <Search className="h-6 w-6 text-red-600" />
            </div>

            {/* Error Message */}
            <h1 className="text-4xl font-bold text-gray-900 mb-2">404</h1>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Page Not Found
            </h2>
            <p className="text-gray-600 mb-8">
              Sorry, we couldn&apos;t find the page you&apos;re looking for. It
              might have been moved, deleted, or you entered the wrong URL.
            </p>

            {/* Action Buttons */}
            <div className="space-y-4">
              <Button asChild className="w-full">
                <Link href="/">
                  <Home className="w-4 h-4 mr-2" />
                  Go to Homepage
                </Link>
              </Button>

              <Button variant="outline" asChild className="w-full">
                <Link href="/queries">
                  <Search className="w-4 h-4 mr-2" />
                  Browse Queries
                </Link>
              </Button>

              <Button
                variant="ghost"
                onClick={() => window.history.back()}
                className="w-full"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Go Back
              </Button>
            </div>

            {/* Helpful Links */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-900 mb-3">
                Popular Pages
              </h3>
              <div className="grid grid-cols-1 gap-2 text-sm">
                <Link
                  href="/"
                  className="text-blue-600 hover:text-blue-800 hover:underline"
                >
                  New Query
                </Link>
                <Link
                  href="/queries"
                  className="text-blue-600 hover:text-blue-800 hover:underline"
                >
                  Manage Queries
                </Link>
                <Link
                  href="/dashboard"
                  className="text-blue-600 hover:text-blue-800 hover:underline"
                >
                  System Dashboard
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
