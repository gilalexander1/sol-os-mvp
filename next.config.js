/** @type {import('next').NextConfig} */
const nextConfig = {
  // Standard Next.js configuration for Vercel
  trailingSlash: false,
  
  // Vercel-specific optimizations
  images: {
    domains: [],
  },
}

module.exports = nextConfig