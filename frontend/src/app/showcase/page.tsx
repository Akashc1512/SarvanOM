import PortfolioShowcase from '@/components/portfolio/PortfolioShowcase';

// Metadata removed - this is a client component due to dynamic imports

export default function ShowcasePage() {
  return (
    <main className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container">
        <PortfolioShowcase />
      </div>
    </main>
  );
}