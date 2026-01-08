from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

# Custom Exception Classes
class CustomAPIException(Exception):
    """Base exception for custom API errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ModelNotLoadedException(CustomAPIException):
    """Raised when ML model fails to load"""
    def __init__(self, message: str = "ML model not loaded"):
        super().__init__(message, status_code=503)


class PredictionException(CustomAPIException):
    """Raised when prediction fails"""
    def __init__(self, message: str = "Prediction failed"):
        super().__init__(message, status_code=500)

class DatabaseException(CustomAPIException):
    """Raised when database operation fails"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)

def register_exception_handler(app: FastAPI):
    """
    Register global exception handlers for the FastAPI application
    """
    
    @app.exception_handler(CustomAPIException)
    async def custom_api_exception_handler(request: Request, exc: CustomAPIException):
        """Handle custom API exceptions"""
        logger.error(f"Custom API Error: {exc.message} - Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle FastAPI HTTP exceptions"""
        logger.warning(f"HTTP {exc.status_code}: {exc.detail} - Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors (Pydantic)"""
        errors = []
        for error in exc.errors():
            errors.append({
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(f"Validation Error - Path: {request.url.path} - Errors: {errors}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation failed",
                "details": errors
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle database errors"""
        logger.error(f"Database Error: {str(exc)} - Path: {request.url.path}")
        
        # Don't expose internal database errors in production
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database operation failed",
                "message": "An error occurred while processing your request"
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors"""
        logger.warning(f"ValueError: {str(exc)} - Path: {request.url.path}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid value",
                "message": str(exc)
            }
        )
    
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions"""
        logger.error(f"Unhandled Exception: {type(exc).__name__}: {str(exc)} - Path: {request.url.path}", exc_info=True)
        
        # Don't expose internal errors in production
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
                "type": type(exc).__name__
            }
        )