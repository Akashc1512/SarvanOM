import dynamic from 'next/dynamic';

// Fallback component for when PersonalHub is not available
const FallbackHub = () => (
  <section className="section-std">
    <h1 className="text-title">Personal Hub</h1>
    <p className="text-body opacity-90">Your shortcuts and tools will appear here.</p>
  </section>
);

const PersonalHub = dynamic(
  () => import('@/components/hub/PersonalHub').then(mod => ({ default: mod.PersonalHub })),
  { 
    ssr: true,
    loading: () => <FallbackHub />
  }
);

export const metadata = { title: 'SarvanOM — Hub' };

export default function HubPage() {
  return (
    <main className="cosmic min-h-screen">
      <div className="container-std">
        <PersonalHub />
      </div>
    </main>
  );
}
