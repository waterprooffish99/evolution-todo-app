"""
FastAPI main application with CORS, authentication, and task endpoints.

This module initializes the FastAPI application, configures CORS middleware
for the Next.js frontend, includes the task API router, and sets up startup
events for database initialization.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import os
from app.database import create_db_and_tables
from app.api.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler.

    This function runs startup and shutdown events for the application.
    Currently only handles startup (database initialization).
    """
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: Add cleanup code here if needed


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Evolution Todo API",
    description="REST API for the Evolution Todo application with JWT authentication and multi-tenant isolation",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS middleware for Next.js frontend
# Get allowed origins from environment variable (comma-separated list)
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers (including Authorization)
    # Expose the authorization header to frontend
    expose_headers=["Access-Control-Allow-Origin"]
)


# Include task API router
app.include_router(tasks_router)


@app.get("/")
def root():
    """
    Root endpoint for health check and basic information.

    Returns:
        Dictionary with status and timestamp
    """
    return {
        "status": "ok",
        "message": "Evolution Todo API is running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Dictionary with health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "evolution-todo-api"
    }


# Additional routes can be added here as needed