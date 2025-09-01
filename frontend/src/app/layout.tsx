import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppProvider } from "@/providers/app-provider";
import { CosmicNavigation } from "@/components/navigation/CosmicNavigation";
import { CosmicLayout } from "@/components/layout/CosmicLayout";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap", // Optimize font loading
});

export const metadata: Metadata = {
  title: {
    default: "SarvanOM - Universal Knowledge Platform",
    template: "%s | SarvanOM",
  },
  description:
    "The next-generation universal knowledge platform powered by advanced AI and cosmic intelligence.",
  keywords: [
    "knowledge platform",
    "AI-powered",
    "cosmic intelligence",
    "universal knowledge",
    "search",
    "analytics",
    "collaboration",
  ],
  authors: [{ name: "SarvanOM Team" }],
  creator: "SarvanOM",
  publisher: "SarvanOM",
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
    title: "SarvanOM - Universal Knowledge Platform",
    description:
      "The next-generation universal knowledge platform powered by advanced AI and cosmic intelligence.",
    siteName: "SarvanOM",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "SarvanOM",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "SarvanOM - Universal Knowledge Platform",
    description:
      "The next-generation universal knowledge platform powered by advanced AI and cosmic intelligence.",
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
        <link rel="icon" href="/favicon-new.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#0b1020" />
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
          {children}
        </AppProvider>
      </body>
    </html>
  );
}
