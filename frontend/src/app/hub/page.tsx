import PersonalHub from '@/components/hub/PersonalHub';

// Metadata removed - this is a client component due to dynamic imports

export default function HubPage() {
  return (
    <main className="cosmic min-h-screen">
      <div className="container-std">
        <PersonalHub />
      </div>
    </main>
  );
}
