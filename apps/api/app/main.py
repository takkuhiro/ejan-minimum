"""
FastAPI application entry point.
Sets up the application with CORS, error handling, and routing.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import logging
from typing import Any, Dict, AsyncGenerator

from app.core.config import settings
from app.api.routes import styles, tutorials

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Always use INFO level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Suppress DEBUG logs from external libraries
logging.getLogger("google.auth").setLevel(logging.WARNING)
logging.getLogger("google.auth._default").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"CORS origins: {settings.cors_origins}")

    # Verify required settings
    if not settings.google_api_key:
        logger.warning("GOOGLE_API_KEY not configured")
    if not settings.project_id:
        logger.warning("PROJECT_ID not configured")
    if not settings.storage_bucket:
        logger.warning("STORAGE_BUCKET not configured")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title="Ejan API",
    description="Backend API for Ejan - AI-powered makeup style recommendation and tutorial generation",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions with consistent format."""
    # Keep detail as-is if it's a dict, otherwise convert to string
    detail = exc.detail if isinstance(exc.detail, (dict, list)) else str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": detail,
            "status_code": exc.status_code,
            "type": "http_error",
        },
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "status_code": 422,
            "type": "validation_error",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)

    # Don't expose internal errors in production
    if settings.is_production:
        message = "An internal error occurred"
    else:
        message = str(exc)

    return JSONResponse(
        status_code=500,
        content={"detail": message, "status_code": 500, "type": "internal_error"},
    )


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify the service is running.

    Returns:
        JSON response with service status.
    """
    return {"status": "healthy", "service": "ejan-api", "version": "1.0.0"}


# Include API routes
app.include_router(styles.router)
app.include_router(tutorials.router)
