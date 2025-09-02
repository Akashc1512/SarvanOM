import { CosmicNavigation } from "@/components/navigation/CosmicNavigation";
import { CosmicLayout } from "@/components/layout/CosmicLayout";
import { SecurityFooter } from "@/components/security/SecurityFooter";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <CosmicLayout>
      <div className="min-h-screen flex flex-col">
        <CosmicNavigation />
        <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <SecurityFooter variant="default" />
      </div>
    </CosmicLayout>
  );
}
