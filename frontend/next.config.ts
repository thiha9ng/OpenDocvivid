import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  
  // Enable standalone output mode, optimize Docker deployment
  output: 'standalone',
  
  // Compression optimization
  compress: true,
  
  // Production environment optimization
  poweredByHeader: false,
};

export default nextConfig;
