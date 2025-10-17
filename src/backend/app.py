"""
Glossary Extraction & Validation API
Main FastAPI application entry point
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from src.backend.database import get_db, initialize_database, check_database_connection
from src.backend.config import config
from src.backend.routers import glossary, documents, admin

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Glossary Extraction & Validation API",
    version="2.0.0",
    description="API for extracting terminology from PDFs and validating against IATE"
)

# Include routers (order matters for route resolution)
print(f"Loading glossary router: {glossary.router}")
app.include_router(glossary.router)
print(f"Loading documents router: {documents.router}")
app.include_router(documents.router)
print(f"Loading admin router: {admin.router}")
app.include_router(admin.router)  # Admin operations
print(f"All routers loaded. Total routes: {len(app.routes)}")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Starting Glossary Extraction API...")
    initialize_database()
    print("Database initialized successfully")

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

    # Neo4j status (will be implemented in Phase 2)
    neo4j_status = "not_configured"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": {
            "type": "SQLite",
            "status": db_status,
            "url": config.DATABASE_URL
        },
        "neo4j": {
            "status": neo4j_status,
            "message": "Optional - Phase 2 feature"
        },
        "api_version": "1.0.0",
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
