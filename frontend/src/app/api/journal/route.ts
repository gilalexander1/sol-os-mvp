import { NextRequest, NextResponse } from 'next/server';

// Mock journal entries storage (in production, use database)
let journalEntries: any[] = [
  {
    id: 1,
    title: 'Welcome to Sol OS',
    content: 'Your ADHD companion is ready to help you stay organized and focused.',
    mood: 'optimistic',
    timestamp: new Date().toISOString(),
    tags: ['welcome', 'setup']
  }
];

export async function GET() {
  return NextResponse.json({
    success: true,
    entries: journalEntries.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const newEntry = {
      id: journalEntries.length + 1,
      title: body.title || 'Untitled Entry',
      content: body.content || '',
      mood: body.mood || 'neutral',
      timestamp: new Date().toISOString(),
      tags: body.tags || []
    };
    
    journalEntries.push(newEntry);
    
    return NextResponse.json({
      success: true,
      message: 'Journal entry created',
      entry: newEntry
    });
    
  } catch (error) {
    return NextResponse.json({
      success: false,
      message: 'Failed to create journal entry'
    }, { status: 500 });
  }
}