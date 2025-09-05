import Link from 'next/link';
import dynamic from 'next/dynamic';

// Fallback component for when BlackspikeLanding is not available
const FallbackLanding = () => (
  <section className="cosmic-section">
    <h1 className="text-4xl font-bold cosmic-text-primary">SarvanOM</h1>
    <p className="text-lg cosmic-text-secondary">
      Universal AI meta-search with sources, streaming answers, and a cosmic UI.
    </p>
    <div className="mt-6">
      <Link href="/" className="cosmic-btn-primary">Go to Search</Link>
    </div>
  </section>
);

// Use dynamic import with proper error handling
const BlackspikeLanding = dynamic(
  () => import('@/components/landing/BlackspikeLanding').then(mod => ({ default: mod.BlackspikeLanding })),
  { 
    ssr: true,
    loading: () => <FallbackLanding />
  }
);

export const metadata = { title: 'SarvanOM — Landing' };

export default function LandingPage() {
  return (
    <main className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container">
        <BlackspikeLanding />
      </div>
    </main>
  );
}