import logging
import time
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and outgoing responses
    with timing, headers, and error information
    """
    
    def __init__(self, app, log_body: bool = False):
        """
        Args:
            app: FastAPI application
            log_body: Whether to log request/response bodies (be careful with sensitive data)
        """
        super().__init__(app)
        self.log_body = log_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request and log details
        """
        # Start timer
        start_time = time.time()
        
        # Generate request ID for tracking
        request_id = self._generate_request_id(request)
        
        # Log incoming request
        await self._log_request(request, request_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"
            
            # Log response
            self._log_response(request, response, process_time, request_id)
            
            return response
            
        except Exception as e:
            # Calculate processing time even for errors
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                f"[{request_id}] ERROR | "
                f"{request.method} {request.url.path} | "
                f"Time: {process_time:.4f}s | "
                f"Error: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            
            # Re-raise to be handled by exception handlers
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details"""
        # Get client info
        client_host = request.client.host if request.client else "unknown"
        
        # Build log message
        log_msg = (
            f"[{request_id}] REQUEST | "
            f"{request.method} {request.url.path} | "
            f"Client: {client_host}"
        )
        
        # Add query parameters if present
        if request.url.query:
            log_msg += f" | Query: {request.url.query}"
        
        # Add user agent if present
        user_agent = request.headers.get("user-agent", "unknown")
        log_msg += f" | User-Agent: {user_agent[:50]}"
        
        # Log request body for debugging (be careful with sensitive data)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Limit body size in logs
                    body_str = body.decode()[:500]
                    log_msg += f" | Body: {body_str}"
            except:
                pass
        
        logger.info(log_msg)
    
    def _log_response(self, request: Request, response: Response, process_time: float, request_id: str):
        """Log outgoing response details"""
        # Determine log level based on status code
        status_code = response.status_code
        
        if status_code < 400:
            log_level = logging.INFO
            status_emoji = "✅"
        elif status_code < 500:
            log_level = logging.WARNING
            status_emoji = "⚠️"
        else:
            log_level = logging.ERROR
            status_emoji = "❌"
        
        # Build log message
        log_msg = (
            f"[{request_id}] RESPONSE {status_emoji} | "
            f"{request.method} {request.url.path} | "
            f"Status: {status_code} | "
            f"Time: {process_time:.4f}s"
        )
        
        # Add response size if available
        content_length = response.headers.get("content-length")
        if content_length:
            log_msg += f" | Size: {content_length} bytes"
        
        logger.log(log_level, log_msg)
    
    def _generate_request_id(self, request: Request) -> str:
        """
        Generate a unique request ID for tracking
        Uses existing X-Request-ID header if present
        """
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            # Generate simple ID based on timestamp
            import uuid
            request_id = str(uuid.uuid4())[:8]
        return request_id


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware that only adds timing information
    Use this if you want minimal logging overhead
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        
        return response


class HealthCheckFilter(logging.Filter):
    """
    Filter to exclude health check endpoints from logs
    Reduces log noise from monitoring tools
    """
    
    def __init__(self, paths_to_exclude: list = None):
        super().__init__()
        self.paths_to_exclude = paths_to_exclude or ["/health", "/ready", "/metrics"]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Return False to exclude the log record"""
        message = record.getMessage()
        
        # Check if any excluded path is in the log message
        for path in self.paths_to_exclude:
            if path in message:
                return False
        
        return True