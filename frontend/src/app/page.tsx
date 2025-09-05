'use client';

import { useState } from 'react';
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
    <div className="space-y-8">
      <header className="text-center">
        <h1 className="text-4xl font-bold cosmic-text-primary mb-4">Welcome to SarvanOM</h1>
        <p className="text-lg cosmic-text-secondary max-w-2xl mx-auto">
          Your universal knowledge platform powered by advanced AI. Search, discover, and explore the cosmos of information.
        </p>
      </header>

      <div className="max-w-4xl mx-auto">
        <StreamingSearch
          onComplete={handleSearchComplete}
          onError={handleSearchError}
          className="w-full"
        />
      </div>

      {searchComplete && (
        <section className="text-center">
          <div className="cosmic-card p-6 max-w-md mx-auto">
            <div className="text-cosmic-success mb-2">
              <svg className="w-8 h-8 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="cosmic-text-primary font-medium">Search completed successfully!</p>
            <p className="cosmic-text-tertiary text-sm mt-1">Your results are ready for exploration.</p>
          </div>
        </section>
      )}
    </div>
  );
}

