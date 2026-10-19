import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: [
    "100.100.30.50",
    "100.100.30.50:3004",
    "localhost:3004",
  ],
  experimental: {
    optimizePackageImports: ["lucide-react", "@tanstack/react-query"],
  },
  /* config options here */
  // cacheComponents: true,
  // partialPrefetching: true,
  // turbopack: {
  //   rules: {
  //     "*.css": {
  //       loaders: ["@tailwindcss/turbopack"],
  //       as: "*.css",
  //     },
  //   },
  // },
};

export default nextConfig;
