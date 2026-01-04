"""
Main FastAPI Application Entry Point

Reorganized monolithic architecture with clean separation:
- API routes in /api/v1/
- Business logic in /services/
- Configuration in /core/
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Add parent directory to path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.api.v1.router import api_router

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_TITLE,
    description="Multi-Stage Plagiarism Detection API for Vietnamese",
    version="2.0.0",
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Health check
@app.get("/")
async def root():
    return {
        "message": "Plagiarism Checker API",
        "version": "2.0.0",
        "docs": "/docs"
    }

