import dynamic from 'next/dynamic';

// Fallback component for when PortfolioShowcase is not available
const FallbackShowcase = () => (
  <section className="cosmic-section">
    <h1 className="text-4xl font-bold cosmic-text-primary">Showcase</h1>
    <p className="text-lg cosmic-text-secondary">Component demos and portfolio will appear here.</p>
  </section>
);

const PortfolioShowcase = dynamic(
  () => import('@/components/portfolio/PortfolioShowcase').then(mod => ({ default: mod.PortfolioShowcase })),
  { 
    ssr: true,
    loading: () => <FallbackShowcase />
  }
);

export const metadata = { title: 'SarvanOM — Showcase' };

export default function ShowcasePage() {
  return (
    <main className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container">
        <PortfolioShowcase />
      </div>
    </main>
  );
}