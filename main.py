from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
# The following imports are confirmed to exist based on directory scan
from config.settings import settings
from api import reviews
from extensions import limiter, audit_logger
import structlog
import logging
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

# Standard handler for rate limit exceeded

def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded. Please try again later."}
    )

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Plug-and-Play Product Reviews API",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Audit Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.FileHandler("audit.log"), logging.StreamHandler()]
)
structlog.configure(
    processors=[structlog.processors.JSONRenderer()],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
audit_logger = structlog.get_logger("audit")

# Include routers
app.include_router(reviews.router, prefix="/api/v1", tags=["reviews"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": f"{settings.app_name} API is running",
        "version": settings.version,
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "supabase": "connected",
            "shopify": "configured"
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 