"""
Middleware for rate limiting and request handling
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
import asyncio

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.call_times = defaultdict(list)
        self.cleanup_interval = 60  # Clean up old entries every minute
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address)
        client_ip = request.client.host
        
        # Clean up old entries periodically
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = current_time
        
        # Check rate limit
        if not self._is_allowed(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.calls_per_minute} requests per minute allowed"
                }
            )
        
        # Record the call
        self.call_times[client_ip].append(current_time)
        
        # Process the request
        response = await call_next(request)
        return response
    
    def _is_allowed(self, client_ip: str) -> bool:
        """Check if the client is within rate limits"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Filter calls within the last minute
        recent_calls = [
            call_time for call_time in self.call_times[client_ip]
            if call_time > minute_ago
        ]
        
        # Update the list
        self.call_times[client_ip] = recent_calls
        
        return len(recent_calls) < self.calls_per_minute
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory buildup"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean up each client's call times
        for client_ip in list(self.call_times.keys()):
            self.call_times[client_ip] = [
                call_time for call_time in self.call_times[client_ip]
                if call_time > minute_ago
            ]
            
            # Remove client if no recent calls
            if not self.call_times[client_ip]:
                del self.call_times[client_ip]