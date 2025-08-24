import { NextRequest, NextResponse } from 'next/server';

// Mock tasks storage (in production, use database)
let tasks: any[] = [
  {
    id: 1,
    title: 'Set up your Sol OS profile',
    description: 'Complete your personalized ADHD companion setup',
    completed: false,
    priority: 'high',
    dueDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    createdAt: new Date().toISOString()
  },
  {
    id: 2,
    title: 'Try the focus timer',
    description: 'Use the Pomodoro technique to boost productivity',
    completed: false,
    priority: 'medium',
    dueDate: null,
    createdAt: new Date().toISOString()
  }
];

export async function GET() {
  return NextResponse.json({
    success: true,
    tasks: tasks.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const newTask = {
      id: tasks.length + 1,
      title: body.title || 'New Task',
      description: body.description || '',
      completed: false,
      priority: body.priority || 'medium',
      dueDate: body.dueDate || null,
      createdAt: new Date().toISOString()
    };
    
    tasks.push(newTask);
    
    return NextResponse.json({
      success: true,
      message: 'Task created',
      task: newTask
    });
    
  } catch (error) {
    return NextResponse.json({
      success: false,
      message: 'Failed to create task'
    }, { status: 500 });
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const { id, ...updates } = body;
    
    const taskIndex = tasks.findIndex(task => task.id === id);
    if (taskIndex === -1) {
      return NextResponse.json({
        success: false,
        message: 'Task not found'
      }, { status: 404 });
    }
    
    tasks[taskIndex] = { ...tasks[taskIndex], ...updates };
    
    return NextResponse.json({
      success: true,
      message: 'Task updated',
      task: tasks[taskIndex]
    });
    
  } catch (error) {
    return NextResponse.json({
      success: false,
      message: 'Failed to update task'
    }, { status: 500 });
  }
}