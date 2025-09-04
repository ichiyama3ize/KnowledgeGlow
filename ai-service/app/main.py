#!/usr/bin/env python3
"""
KnowledgeGlow AI Service
FastAPI-based AI processing service for knowledge management
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_database
from routes.processing import router as processing_router
from routes.knowledge import router as knowledge_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting KnowledgeGlow AI Service...")
    init_database()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("🛑 Shutting down KnowledgeGlow AI Service...")

# Create FastAPI app
app = FastAPI(
    title="KnowledgeGlow AI Service",
    description="AI-powered knowledge processing and management service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(processing_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "service": "KnowledgeGlow AI Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-service"
    }

if __name__ == "__main__":
    port = int(os.getenv("AI_SERVICE_PORT", 59147))
    print(f"🤖 Starting AI Service on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )