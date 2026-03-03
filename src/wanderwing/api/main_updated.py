"""FastAPI application entry point with all routes."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wanderwing.api.routes import (
    connections,
    experiments_enhanced,
    feedback_enhanced,
    intent,
    matches_enhanced,
    profiles,
    recommendations_new,
    trips,
)
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
    description="""
    LLM-powered travel companion matching platform.

    ## Core Features

    * **Traveler Profiles** - Comprehensive profiles with preferences and safety settings
    * **Intent Parsing** - Convert natural language trip descriptions to structured data
    * **Smart Matching** - Hybrid LLM + rule-based compatibility scoring
    * **Activity Recommendations** - AI-generated shared activity suggestions
    * **Feedback System** - Rating, reporting, and continuous improvement
    * **A/B Experiments** - Built-in experimentation framework

    ## Authentication

    For MVP, use `X-User-Id` header for authentication.
    Production will implement JWT/OAuth.

    ## Rate Limiting

    - Intent parsing: 50 requests/hour
    - Matching: 10 requests/hour
    - Recommendations: 20 requests/hour
    """,
    version="0.1.0",
    contact={
        "name": "WanderWing Team",
        "email": "support@wanderwing.example.com",
    },
    license_info={
        "name": "MIT",
    },
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
app.include_router(profiles.router)
app.include_router(intent.router)
app.include_router(trips.router)
app.include_router(matches_enhanced.router)
app.include_router(recommendations_new.router)
app.include_router(connections.router)
app.include_router(feedback_enhanced.router)
app.include_router(experiments_enhanced.router)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on startup."""
    # Create tables
    Base.metadata.create_all(bind=engine)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "message": "WanderWing API - LLM-Powered Travel Companion Matching",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
    }


@app.get("/api-info", tags=["system"])
async def api_info() -> dict:
    """Get API metadata and endpoint summary."""
    return {
        "endpoints": {
            "profiles": {
                "POST /profiles": "Create traveler profile",
                "GET /profiles/{id}": "Get profile",
                "PATCH /profiles/{id}": "Update profile",
            },
            "intent_parsing": {
                "POST /parse-intent": "Parse natural language trip intent",
                "POST /parse-intent/refine": "Refine parsed intent",
            },
            "matching": {
                "POST /matches": "Find compatible travelers",
                "POST /matches/{id}/interest": "Express interest",
                "POST /matches/{id}/decline": "Decline match",
            },
            "recommendations": {
                "POST /recommendations": "Generate activity recommendations",
                "POST /recommendations/{id}/accept": "Accept recommendation",
            },
            "feedback": {
                "POST /feedback": "Submit feedback event",
                "POST /feedback/match-rating": "Rate a match",
                "POST /feedback/report-user": "Report user",
            },
            "experiments": {
                "GET /experiments/summary": "Get A/B test results",
                "GET /experiments/{name}": "Get experiment details",
            },
        },
        "authentication": "X-User-Id header (MVP) / JWT (production)",
        "rate_limits": {
            "intent_parsing": "50/hour",
            "matching": "10/hour",
            "recommendations": "20/hour",
        },
    }


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
