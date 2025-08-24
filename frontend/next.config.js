/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove Docker-specific rewrites for Vercel deployment
  // API routes will be handled by Vercel functions
  
  // Vercel-specific optimizations
  images: {
    domains: [],
  },
  
  // Ensure proper API routing for Vercel
  trailingSlash: false,
  
  // Use default output for Vercel
  // output: 'export' // Only if needed for static export
}

module.exports = nextConfig