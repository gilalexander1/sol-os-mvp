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

# Import the FastAPI app
try:
    from main import app
except ImportError as e:
    # Create a minimal FastAPI app if main import fails
    from fastapi import FastAPI
    app = FastAPI(title="Sol OS MVP API", description="ADHD AI Companion API")
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "Sol OS MVP API"}

# Export the app for Vercel
handler = app