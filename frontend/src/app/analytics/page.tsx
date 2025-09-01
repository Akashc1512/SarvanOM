import dynamic from 'next/dynamic';

// Fallback component for when DataNovaDashboard is not available
const FallbackAnalytics = () => (
  <section className="section-std">
    <h1 className="text-title">Analytics</h1>
    <p className="text-body opacity-90">Real-time metrics will appear here.</p>
  </section>
);

const MaybeDashboard = dynamic(
  () => import('@/components/analytics/DataNovaDashboard'),
  { 
    ssr: true,
    loading: () => <FallbackAnalytics />
  }
);

export const metadata = { title: 'SarvanOM — Analytics' };

export default function AnalyticsPage() {
  return (
    <main className="cosmic min-h-screen">
      <div className="container-std">
        <MaybeDashboard />
      </div>
    </main>
  );
}