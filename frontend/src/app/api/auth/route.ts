import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Simple mock authentication for MVP
    if (body.username && body.password) {
      // In production, validate against database
      return NextResponse.json({
        success: true,
        message: 'Authentication successful',
        token: 'mock-jwt-token-' + Date.now(),
        user: {
          id: 1,
          username: body.username,
          name: 'Sol User'
        }
      });
    }
    
    return NextResponse.json({
      success: false,
      message: 'Invalid credentials'
    }, { status: 401 });
    
  } catch (error) {
    return NextResponse.json({
      success: false,
      message: 'Authentication error'
    }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'Sol OS MVP Authentication API',
    endpoints: {
      login: 'POST /api/auth',
      health: 'GET /api/health'
    }
  });
}