"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sparkles } from "lucide-react";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the new search interface
    router.replace("/search");
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-purple-900 flex items-center justify-center">
      <div className="text-center">
        <div className="relative mb-4">
          <Sparkles className="h-16 w-16 text-purple-600 dark:text-purple-400 mx-auto animate-pulse" />
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-purple-400 rounded-full animate-pulse" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Welcome to SarvanOM
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Redirecting to search interface...
        </p>
      </div>
    </div>
  );
}
