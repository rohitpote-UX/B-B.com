import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "B&B Intelligence — BrandBattle",
  description: "Internal intelligence platform for BrandBattle. Discover the signal. Verify the evidence. Make the move.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="theme-color" content="#030305" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
