'use client';

import { useState } from 'react';
import Link from 'next/link';
import { StreamingSearch } from '../components/search/StreamingSearch';

export default function SearchPage() {
  const [searchComplete, setSearchComplete] = useState(false);

  const handleSearchComplete = (data: any) => {
    console.log('Search completed:', data);
    setSearchComplete(true);
  };

  const handleSearchError = (error: string) => {
    console.error('Search error:', error);
    setSearchComplete(false);
  };

  return (
    <main className="cosmic min-h-screen">
      <div className="container-std section-std">
        <header className="flex items-center justify-between">
          <h1 className="text-title">SarvanOM</h1>
          <nav className="text-sm opacity-90 flex gap-4">
            <Link className="link-std" href="/landing">Landing</Link>
            <Link className="link-std" href="/analytics">Analytics</Link>
            <Link className="link-std" href="/blog">Blog</Link>
            <Link className="link-std" href="/showcase">Showcase</Link>
          </nav>
        </header>

        <div className="mt-4">
          <StreamingSearch
            onComplete={handleSearchComplete}
            onError={handleSearchError}
            className="w-full"
          />
        </div>

        {searchComplete && (
          <section className="mt-6">
            <div className="text-center text-gray-400">
              <p>Search completed successfully!</p>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

