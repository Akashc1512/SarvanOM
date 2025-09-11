import Link from 'next/link';
import BlackspikeLanding from '@/components/landing/BlackspikeLanding';

// Metadata removed - this is a client component due to dynamic imports

export default function LandingPage() {
  return (
    <main className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container">
        <BlackspikeLanding />
      </div>
    </main>
  );
}