import dynamic from 'next/dynamic';

// Fallback component for when DataNovaDashboard is not available
const FallbackAnalytics = () => (
  <section className="cosmic-section">
    <h1 className="text-4xl font-bold cosmic-text-primary">Analytics</h1>
    <p className="text-lg cosmic-text-secondary">Real-time metrics will appear here.</p>
  </section>
);

const DataNovaDashboard = dynamic(
  () => import('@/components/analytics/DataNovaDashboard').then(mod => ({ default: mod.DataNovaDashboard })),
  { 
    ssr: true,
    loading: () => <FallbackAnalytics />
  }
);

export const metadata = { title: 'SarvanOM — Analytics' };

export default function AnalyticsPage() {
  return (
    <main className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container cosmic-section">
        <DataNovaDashboard />
      </div>
    </main>
  );
}