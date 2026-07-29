import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/context/ThemeProvider";

export const metadata: Metadata = {
  title: {
    default: "Brand Battle — Find The Best Product. Win Every Purchase.",
    template: "%s — Brand Battle",
  },
  description:
    "AI-powered product comparison and deal discovery. Compare products, find the best deals, track prices, and make confident purchase decisions across Amazon, Flipkart, and more.",
  keywords: [
    "product comparison",
    "deal finder",
    "price tracker",
    "best deals",
    "brand battle",
    "AI shopping advisor",
  ],
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
  openGraph: {
    type: "website",
    locale: "en_IN",
    siteName: "Brand Battle",
    title: "Brand Battle — Find The Best Product. Win Every Purchase.",
    description:
      "AI-powered product comparison and deal discovery platform.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Brand Battle",
    description:
      "AI-powered product comparison and deal discovery platform.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <meta name="theme-color" content="#0a0a0f" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
      </head>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
