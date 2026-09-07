import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output standalone build for lightweight production Docker deployment
  output: "standalone",

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

  // Proxy API requests to FastAPI backend
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
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
