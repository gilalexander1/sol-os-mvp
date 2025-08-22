/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.BACKEND_URL ? `${process.env.BACKEND_URL}/api/:path*` : 'http://localhost:8004/api/:path*',
      },
    ]
  },
  // Remove standalone output for Vercel deployment
  // output: 'standalone',
  
  // Update experimental config for Vercel compatibility
  experimental: {
    // Remove turbo config for Vercel deployment
  },
  
  // Vercel-specific optimizations
  images: {
    domains: [],
  },
  
  // Ensure proper API routing for Vercel
  trailingSlash: false,
}

module.exports = nextConfig