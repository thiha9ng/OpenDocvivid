"""
FastAPI application module for AI DocVivid Service
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from src.models.base import engine
from src.utils.logger import get_logger
from src.utils.middleware import JWTAuthMiddleware
from src.routes.system import router as system_router
from src.routes.video import router as video_router
from src.routes.auth import router as auth_router
from src.routes.credit import router as credit_router
from src.routes.webhook import router as webhook_router
from src.models.base import Base, engine
import traceback

# Get logger for this module
logger = get_logger(__name__)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    logger.info("Starting application...")
    await create_tables()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await engine.dispose()
    logger.info("Application shutdown completed")

def create_app() -> FastAPI:
    """Create FastAPI application instance"""
    logger.info("Creating FastAPI application instance...")
    
    app = FastAPI(
        title="ai-docvivid-service",
        description="ai-docvivid-service API",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins, recommend specifying specific domains in production
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )
    logger.info("CORS middleware configured")
    
    # Configure JWT Authentication Middleware
    app.add_middleware(JWTAuthMiddleware)
    logger.info("JWT authentication middleware configured")
    
    # Register global exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(
            f"HTTP exception occurred: {exc.status_code} - {exc.detail}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail,
                "error_code": exc.status_code
            }
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle all uncaught exceptions"""
        # Log detailed error information
        error_traceback = traceback.format_exc()
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "traceback": error_traceback
            },
            exc_info=True
        )
        
        # Return unified error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error occurred",
                "error_code": 500,
                "detail": str(exc) if logger.level <= 10 else None  # Return detailed error only in DEBUG mode
            }
        )
    
    logger.info("Global exception handlers registered")
    
    # Register routes
    app.include_router(system_router, tags=["system"])
    app.include_router(video_router, prefix="/api/v1/video", tags=["video"])
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(credit_router, prefix="/api/v1/credit", tags=["credit"])
    app.include_router(webhook_router, prefix="/api/v1/webhook", tags=["webhook"])
    logger.info("Routes registered successfully")
    
    return app

# Create application instance
app = create_app()
logger.info("Application instance created successfully") 