"""
VintedScanner Web - FastAPI Application Entry Point

This is the main application file that starts the web server.
It sets up:
- The FastAPI web framework
- CORS (Cross-Origin Resource Sharing) so the frontend can talk to the backend
- Database connections
- API routes (endpoints like /api/alerts, /api/brands, etc.)
- Health check endpoint for monitoring
- Static file serving for the React frontend (in self-hosted mode)

When you run this with 'uvicorn backend.main:app', this file starts the entire backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.database import engine, Base
from backend.config import settings
from backend.services.scheduler_service import start_scheduler, stop_scheduler

# Create FastAPI app
app = FastAPI(
    title="VintedScanner Web API",
    description="REST API for Vinted marketplace alerts",
    version="1.0.0"
)

# Startup event - start alert scheduler
@app.on_event("startup")
async def startup_event():
    """Start background scheduler when application starts."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")

    # Start alert scanner
    start_scheduler()
    logger.info("Alert scheduler started")

# Shutdown event - stop scheduler gracefully
@app.on_event("shutdown")
async def shutdown_event():
    """Stop background scheduler when application shuts down."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Shutting down application...")

    # Stop scheduler
    stop_scheduler()
    logger.info("Alert scheduler stopped")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Import API routers
from backend.api.routes import (
    auth_router,
    alerts_router,
    brands_router,
    categories_router,
    history_router
)

# Register API routers
app.include_router(auth_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(brands_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(history_router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "VintedScanner Web API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Serve frontend static files in self-hosted mode
if settings.DEPLOYMENT_MODE == "self-hosted":
    frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    if os.path.exists(frontend_dist):
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
