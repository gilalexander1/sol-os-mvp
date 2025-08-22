"""
Vercel serverless function adapter for Sol OS MVP backend
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Import the FastAPI app
from main import app

# Vercel expects a handler function
def handler(request, response):
    return app