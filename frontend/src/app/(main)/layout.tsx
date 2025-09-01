import { CosmicNavigation } from "@/components/navigation/CosmicNavigation";
import { CosmicLayout } from "@/components/layout/CosmicLayout";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <CosmicLayout>
      <div>
        <CosmicNavigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </div>
    </CosmicLayout>
  );
}
