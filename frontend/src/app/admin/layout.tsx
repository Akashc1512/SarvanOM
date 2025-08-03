import { RouteGuard } from "@/ui/auth/route-guard";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Development mode - bypass authentication for testing
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  if (isDevelopment) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </div>
    );
  }

  // Production mode - require admin authentication
  return (
    <RouteGuard requiredRole="admin">
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </div>
    </RouteGuard>
  );
} 