/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://backend:8004/api/:path*',
      },
    ]
  },
  // Standalone output for Docker deployment
  output: 'standalone',
  
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