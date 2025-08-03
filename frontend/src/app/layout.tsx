import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppProvider } from "@/providers/app-provider";
import { MainNav } from "@/ui/navigation/main-nav";
import { Breadcrumbs } from "@/ui/navigation/breadcrumbs";
import { RouteGuard } from "@/ui/auth/route-guard";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap", // Optimize font loading
});

export const metadata: Metadata = {
  title: {
    default: "Universal Knowledge Hub",
    template: "%s | UKH",
  },
  description:
    "The next-generation knowledge platform that combines AI-powered insights with collaborative document management for enterprise teams.",
  keywords: [
    "knowledge platform",
    "AI-powered",
    "collaboration",
    "document management",
    "enterprise",
    "search",
    "analytics",
  ],
  authors: [{ name: "Universal Knowledge Hub Team" }],
  creator: "Universal Knowledge Hub",
  publisher: "Universal Knowledge Hub",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(
    process.env["NEXT_PUBLIC_APP_URL"] || "http://localhost:3000",
  ),
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "/",
    title: "Universal Knowledge Hub",
    description:
      "The next-generation knowledge platform that combines AI-powered insights with collaborative document management for enterprise teams.",
    siteName: "Universal Knowledge Hub",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Universal Knowledge Hub",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Universal Knowledge Hub",
    description:
      "The next-generation knowledge platform that combines AI-powered insights with collaborative document management for enterprise teams.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: process.env["NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION"] ? {
    google: process.env["NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION"],
  } : {},
  // Performance optimizations
  other: {
    "X-DNS-Prefetch-Control": "on",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#000000" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="color-scheme" content="light dark" />

        {/* Preload critical resources */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />

        {/* DNS prefetch for external domains */}
        <link rel="dns-prefetch" href="//api.example.com" />
        <link rel="dns-prefetch" href="//cdn.example.com" />
      </head>
      <body className={`${inter.variable} antialiased`}>
        <AppProvider>
          <RouteGuard>
            <div className="min-h-screen bg-gray-50">
              <MainNav />
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <Breadcrumbs />
                {children}
              </main>
            </div>
          </RouteGuard>
        </AppProvider>
      </body>
    </html>
  );
}
