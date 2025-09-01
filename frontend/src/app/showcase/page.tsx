import dynamic from 'next/dynamic';

// Fallback component for when PortfolioShowcase is not available
const FallbackShowcase = () => (
  <section className="section-std">
    <h1 className="text-title">Showcase</h1>
    <p className="text-body opacity-90">Component demos and portfolio will appear here.</p>
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
    <main className="cosmic min-h-screen">
      <div className="container-std">
        <PortfolioShowcase />
      </div>
    </main>
  );
}