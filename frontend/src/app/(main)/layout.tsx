import { CosmicAppShell } from "@/components/layout/CosmicAppShell";
import { SecurityFooter } from "@/components/security/SecurityFooter";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <CosmicAppShell>
      {children}
      <SecurityFooter variant="default" />
    </CosmicAppShell>
  );
}
