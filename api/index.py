"""
KeyAuth — Vercel Serverless Function Entry Point
Wraps the FastAPI app for Vercel's Python runtime
"""
import sys
import os

# Add backend directory to Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set Vercel-specific environment defaults
os.environ.setdefault('DATABASE_URL', 'sqlite:////tmp/keystroke_auth.db')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('CORS_ORIGINS', '*')

# Import the FastAPI app (this triggers init_db via startup event)
from app.main import app

# Ensure database tables exist (serverless may not fire startup events reliably)
from app.database import init_db
init_db()
