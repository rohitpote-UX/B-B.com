import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output standalone build for Docker deployments (omit on Vercel for native serverless/edge optimization)
  ...(process.env.VERCEL ? {} : { output: "standalone" as const }),

  // Permanent redirects for consolidated/removed routes
  async redirects() {
    return [
      {
        source: "/how-it-works",
        destination: "/about",
        permanent: true,
      },
    ];
  },

  // Proxy /api/* requests to the FastAPI backend (used by SSR and server components)
  // Controlled by NEXT_PUBLIC_API_BASE_URL — same var as the Axios client in src/lib/api.ts
  async rewrites() {
    const rawApiUrl = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000')
      .replace(/\/+$/, '')
      .replace(/\/api$/, '')
    return [
      {
        source: '/api/:path*',
        destination: `${rawApiUrl}/api/:path*`,
      },
    ]
  },

  // Allow external product images from e-commerce CDNs
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "rukminim2.flixcart.com" },
      { protocol: "https", hostname: "rukminim1.flixcart.com" },
      { protocol: "https", hostname: "m.media-amazon.com" },
      { protocol: "https", hostname: "images-na.ssl-images-amazon.com" },
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "assets.myntassets.com" },
      { protocol: "https", hostname: "media.croma.com" },
      { protocol: "https", hostname: "www.transparenttextures.com" },
      { protocol: "https", hostname: "dummyjson.com" },
      { protocol: "https", hostname: "upload.wikimedia.org" },
    ],
    // Disable default image optimization for external images to avoid 429s
    unoptimized: true,
  },

  // Enable React strict mode
  reactStrictMode: true,

  // Compress responses with Gzip/Brotli
  compress: true,
};

export default nextConfig;
