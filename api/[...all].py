"""
Vercel serverless function adapter for Sol OS MVP backend
Handles all API routes through FastAPI
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Set environment variables for production
os.environ.setdefault('ENVIRONMENT', 'production')

# Import the FastAPI app
try:
    from main import app
    
    # Configure for serverless deployment
    @app.get("/api/health")
    async def health_check():
        return {"status": "healthy", "service": "Sol OS MVP API", "environment": "production"}
    
except ImportError as e:
    # Create a minimal FastAPI app if main import fails
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(title="Sol OS MVP API", description="ADHD AI Companion API")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/api/health")
    async def health_check():
        return {"status": "healthy", "service": "Sol OS MVP API (minimal)", "error": str(e)}
    
    @app.get("/api")
    async def root():
        return {"message": "Sol OS MVP API - ADHD AI Companion"}

# Export the app for Vercel
handler = app