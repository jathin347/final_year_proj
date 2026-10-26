from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, logger
from backend.app.core.security import SecurityException
from backend.app.services.article_extractor import ArticleExtractionException
from backend.app.models.database import init_db

# Import routers
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.providers import router as providers_router
from backend.app.api.routes.claims import router as claims_router
from backend.app.api.routes.history import router as history_router
from backend.app.api.routes.analyze import router as analyze_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    logger.info("Database schemas initialized.")
    yield
    # Shutdown actions
    logger.info(f"Shutting down {settings.APP_NAME}")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Real-Time Fake News Detector with Source Credibility Scoring and Multimodal Verification.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Security Exception Handler
@app.exception_handler(SecurityException)
async def security_exception_handler(request: Request, exc: SecurityException):
    logger.warning(f"Security policy violation: {str(exc)} on path {request.url.path}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": "SecurityPolicyViolation"}
    )

# Article Extraction Exception Handler
@app.exception_handler(ArticleExtractionException)
async def article_extraction_exception_handler(request: Request, exc: ArticleExtractionException):
    logger.warning(f"Article extraction failed: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "error_type": "ArticleExtractionFailed"}
    )

# Catch-all Exception Handler to prevent stack traces leaking to frontend
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred during analysis.", "error_type": "InternalServerError"}
    )

# Include API Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(providers_router, prefix="/api")
app.include_router(claims_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "documentation": "/docs",
        "health": "/api/health"
    }
