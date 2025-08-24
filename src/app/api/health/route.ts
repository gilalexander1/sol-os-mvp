import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  return NextResponse.json({
    status: 'healthy',
    service: 'Sol OS MVP API',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString()
  });
}