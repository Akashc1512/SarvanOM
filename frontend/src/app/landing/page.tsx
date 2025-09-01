import Link from 'next/link';
import dynamic from 'next/dynamic';

// Fallback component for when BlackspikeLanding is not available
const FallbackLanding = () => (
  <section className="section-std">
    <h1 className="text-title">SarvanOM</h1>
    <p className="text-body opacity-90">
      Universal AI meta-search with sources, streaming answers, and a cosmic UI.
    </p>
    <div className="mt-6">
      <Link href="/" className="link-std">Go to Search</Link>
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
    <main className="cosmic min-h-screen">
      <div className="container-std">
        <BlackspikeLanding />
      </div>
    </main>
  );
}