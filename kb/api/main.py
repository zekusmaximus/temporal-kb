# kb/api/main.py

import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..core.config import get_config
from ..core.database import get_db
from .routes import entries, export, links, projects, search, stats, tags, temporal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize config and database
config = get_config()
get_db()

# Create FastAPI app
app = FastAPI(
    title="Temporal Knowledge Base API",
    description="Personal knowledge management with temporal intelligence",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check
@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }

# Root endpoint
@app.get("/", tags=["system"])
async def root():
    """API root with basic information"""
    return {
        "name": "Temporal Knowledge Base API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

# Include routers
app.include_router(entries.router, prefix="/api/v1/entries", tags=["entries"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(links.router, prefix="/api/v1/links", tags=["links"])
app.include_router(temporal.router, prefix="/api/v1/temporal", tags=["temporal"])
app.include_router(tags.router, prefix="/api/v1/tags", tags=["tags"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["statistics"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Temporal Knowledge Base API")
    logger.info(f"Data directory: {config.data_dir}")
    logger.info(f"Database: {config.db_path}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Temporal Knowledge Base API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "kb.api.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True
    )
