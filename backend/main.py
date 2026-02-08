from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv
import os
from app.api.v1.router import api_router
from app.core.exception_handlers import (
    travel_planner_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.core.exceptions import TravelPlannerException
from app.core.middleware import LoggingMiddleware, SecurityHeadersMiddleware
from app.core.logging_config import setup_logging
from app.models.api_models import ErrorResponse

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))

# Create FastAPI app
app = FastAPI(
    title="AI Travel Planner API",
    description="Backend API for AI-powered travel planning application",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add middleware (order matters - first added is outermost)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom 404 handler for consistent error format
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Custom 404 handler to ensure consistent error response format.
    """
    error_response = ErrorResponse(
        message="The requested resource was not found",
        error_code="NOT_FOUND"
    )
    
    return JSONResponse(
        status_code=404,
        content=error_response.model_dump()
    )

# Add exception handlers
app.add_exception_handler(TravelPlannerException, travel_planner_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, custom_404_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API router
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "AI Travel Planner API is running",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)