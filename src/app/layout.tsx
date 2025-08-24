import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Sol OS MVP',
  description: 'ADHD AI Companion MVP - Simplified scope with security-first architecture',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}