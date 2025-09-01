"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to home page
    router.push("/");
  }, [router]);

  return (
    <div className="min-h-screen bg-cosmos-bg flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cosmos-accent mx-auto mb-4"></div>
        <p className="text-cosmos-fg">Loading...</p>
      </div>
    </div>
  );
}
