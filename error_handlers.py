"""
Error handling middleware and exception handlers for Turkish Legal AI API
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("turkish_legal_api.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class MCPToolError(APIError):
    """MCP tool specific error"""
    def __init__(self, tool_name: str, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=f"MCP tool '{tool_name}' error: {message}",
            status_code=500,
            details={"tool_name": tool_name, **(details or {})}
        )

class GovernmentServerError(APIError):
    """Government server connectivity error"""
    def __init__(self, server_name: str, message: str):
        super().__init__(
            message=f"Government server '{server_name}' error: {message}",
            status_code=503,
            details={"server_name": server_name, "retry_suggested": True}
        )

class ValidationError(APIError):
    """Request validation error"""
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error for field '{field}': {message}",
            status_code=422,
            details={"field": field}
        )

def create_error_response(
    status_code: int,
    message: str,
    error_type: str = "APIError",
    details: Dict[str, Any] = None,
    request_id: str = None
) -> JSONResponse:
    """Create standardized error response"""
    
    error_response = {
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
        }
    }
    
    if details:
        error_response["error"]["details"] = details
    
    if request_id:
        error_response["error"]["request_id"] = request_id
    
    # Add helpful information based on error type
    if status_code == 503:
        error_response["error"]["suggestions"] = [
            "Try again in a few moments",
            "Check government server status at /api/yargi/health",
            "Verify your internet connection"
        ]
    elif status_code == 422:
        error_response["error"]["suggestions"] = [
            "Check the API documentation at /docs",
            "Verify all required parameters are provided",
            "Ensure parameter types match the specification"
        ]
    elif status_code == 404:
        error_response["error"]["suggestions"] = [
            "Check the endpoint URL for typos",
            "Verify the resource ID exists",
            "Consult the API documentation at /docs"
        ]
    elif status_code == 500:
        error_response["error"]["suggestions"] = [
            "Try again in a few moments",
            "Contact support if the problem persists",
            "Check the API status at /health"
        ]
    
    return JSONResponse(
        status_code=status_code,
        content=error_response,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom API errors"""
    logger.error(f"APIError: {exc.message} | Details: {exc.details}")
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_type=exc.__class__.__name__,
        details=exc.details,
        request_id=getattr(request.state, 'request_id', None)
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP Exception: {exc.status_code} | {exc.detail}")
    
    # Map common HTTP errors to user-friendly messages
    error_messages = {
        404: "The requested resource was not found",
        405: "Method not allowed for this endpoint", 
        429: "Rate limit exceeded. Please try again later",
        503: "Service temporarily unavailable"
    }
    
    message = error_messages.get(exc.status_code, str(exc.detail))
    
    return create_error_response(
        status_code=exc.status_code,
        message=message,
        error_type="HTTPError",
        request_id=getattr(request.state, 'request_id', None)
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    logger.warning(f"Validation Error: {exc.errors()}")
    
    # Extract validation error details
    error_details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "Validation error")
        error_details.append({
            "field": field,
            "message": message,
            "type": error.get("type", "validation_error")
        })
    
    return create_error_response(
        status_code=422,
        message="Request validation failed",
        error_type="ValidationError",
        details={"validation_errors": error_details},
        request_id=getattr(request.state, 'request_id', None)
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return create_error_response(
        status_code=500,
        message="An unexpected error occurred. Please try again or contact support.",
        error_type="InternalServerError",
        details={"error_class": exc.__class__.__name__} if logger.level <= logging.DEBUG else None,
        request_id=getattr(request.state, 'request_id', None)
    )

# Middleware for request ID tracking and logging
class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Generate request ID
        import uuid
        request_id = str(uuid.uuid4())[:8]
        
        # Add to scope for access in handlers
        scope["state"] = {"request_id": request_id}
        
        # Log request
        method = scope.get("method", "")
        path = scope.get("path", "")
        logger.info(f"[{request_id}] {method} {path}")
        
        await self.app(scope, receive, send)

def setup_error_handlers(app):
    """Setup all error handlers for the FastAPI app"""
    
    # Add custom exception handlers
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Error handlers and middleware configured")