"""
Glossary Extraction & Validation API
Main FastAPI application entry point
"""
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.backend.database import get_db, initialize_database, check_database_connection
from src.backend.config import config
from src.backend.routers import glossary, documents, admin, graph, search, relationships
from src.backend.services.neo4j_service import get_neo4j_service

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events

    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown")
    """
    # Startup: Initialize database and Neo4j
    logger.info("Starting Glossary Extraction API...")
    initialize_database()
    logger.info("Database initialized successfully")

    # Initialize Neo4j connection
    neo4j_service = get_neo4j_service()
    if neo4j_service.is_connected():
        neo4j_service.init_schema()
        logger.info("Neo4j initialized successfully")
    else:
        logger.warning("Neo4j not available - graph features disabled")

    yield  # Application runs here

    # Shutdown: Cleanup resources
    logger.info("Shutting down Glossary Extraction API...")
    if neo4j_service.is_connected():
        await neo4j_service.close()
        logger.info("Neo4j connection closed")
    logger.info("Shutdown complete")


app = FastAPI(
    title="Glossary Extraction & Validation API",
    version="2.0.0",
    description="API for extracting terminology from PDFs and validating against IATE",
    lifespan=lifespan  # Use modern lifespan handler
)

# Include routers (order matters for route resolution)
logger.info(f"Loading glossary router: {glossary.router}")
app.include_router(glossary.router)
logger.info(f"Loading documents router: {documents.router}")
app.include_router(documents.router)
logger.info(f"Loading admin router: {admin.router}")
app.include_router(admin.router)  # Admin operations
logger.info(f"Loading graph router: {graph.router}")
app.include_router(graph.router)  # Neo4j knowledge graph
logger.info(f"Loading search router: {search.router}")
app.include_router(search.router)  # FTS5 full-text search
logger.info(f"Loading relationships router: {relationships.router}")
app.include_router(relationships.router)  # Term relationships & NLP extraction
logger.info(f"All routers loaded. Total routes: {len(app.routes)}")

# CORS middleware configuration
# Allow both default port 3000 and alternate port 3001 for development
allowed_origins = [
    config.FRONTEND_URL,  # http://localhost:3000
    "http://localhost:3001",  # Alternate port when 3000 is in use
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded documents (PDF viewing)
# This allows the frontend to access PDFs via HTTP
data_dir = Path(__file__).parent.parent.parent / "data"
if not data_dir.exists():
    data_dir.mkdir(parents=True, exist_ok=True)
app.mount("/data", StaticFiles(directory=str(data_dir)), name="data")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Glossary Extraction & Validation API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    Returns status of database connections and system health
    """
    # Check SQLite connection
    db_status = "connected" if check_database_connection() else "disconnected"

    # Check Neo4j status
    neo4j_service = get_neo4j_service()
    neo4j_connected = neo4j_service.is_connected()
    neo4j_stats = neo4j_service.get_term_statistics() if neo4j_connected else None

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": {
            "type": "SQLite",
            "status": db_status,
            "url": config.DATABASE_URL
        },
        "neo4j": {
            "status": "connected" if neo4j_connected else "not_connected",
            "message": "Knowledge graph active" if neo4j_connected else "Optional - start Neo4j container to enable",
            "statistics": neo4j_stats
        },
        "api_version": "2.0.0",
        "environment": "development" if config.DEBUG else "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG
    )
