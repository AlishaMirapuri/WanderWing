"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wanderwing.api.routes import connections, feedback, matches, trips
from wanderwing.db import Base, engine
from wanderwing.utils.config import get_settings
from wanderwing.utils.logging import setup_logging

# Initialize logging
setup_logging()

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="WanderWing API",
    description="LLM-powered travel companion matching platform",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trips.router)
app.include_router(matches.router)
app.include_router(connections.router)
app.include_router(feedback.router)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on startup."""
    # Create tables
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "WanderWing API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


def run() -> None:
    """Run the API server (for CLI entry point)."""
    import uvicorn

    uvicorn.run(
        "wanderwing.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )


if __name__ == "__main__":
    run()
