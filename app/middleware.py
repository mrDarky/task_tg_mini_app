from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
from typing import Callable, Optional
from app.services.activity_service import ActivityService
import re


class ActivityLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests for activity monitoring
    - Logs IP addresses, endpoints, status codes
    - Detects suspicious activity (404s, 500s, invalid endpoints)
    - Blocks requests from blocked IP addresses
    """
    
    # Endpoints to exclude from activity logging (to reduce noise)
    EXCLUDED_ENDPOINTS = [
        r'^/static/.*',
        r'^/health$',
        r'^/docs.*',
        r'^/redoc.*',
        r'^/openapi\.json$'
    ]
    
    # Patterns that indicate suspicious activity
    SUSPICIOUS_PATTERNS = [
        r'\.\./',  # Path traversal
        r'\.php$',  # PHP file requests (this is a Python app)
        r'\.asp$',  # ASP file requests
        r'\.jsp$',  # JSP file requests
        r'/admin/config',  # Common attack patterns
        r'/wp-admin',  # WordPress admin
        r'/phpmyadmin',  # phpMyAdmin
        r'<script',  # XSS attempts
        r'SELECT.*FROM',  # SQL injection attempts (case insensitive)
        r'UNION.*SELECT',  # SQL injection
        r'/\.env',  # Attempts to access env files
        r'/\.git',  # Attempts to access git files
    ]
    
    # Known valid endpoints (regex patterns)
    VALID_ENDPOINTS = [
        r'^/$',
        r'^/admin.*',
        r'^/miniapp.*',
        r'^/api/.*',
        r'^/static/.*',
        r'^/health$',
        r'^/docs.*',
        r'^/redoc.*',
        r'^/openapi\.json$'
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract IP address
        ip_address = self._get_client_ip(request)
        
        # Check if IP is blocked
        if await ActivityService.is_ip_blocked(ip_address):
            return Response(
                content="Access forbidden: Your IP address has been blocked",
                status_code=403
            )
        
        # Process the request
        response = await call_next(request)
        
        # Check if we should log this request
        if not self._should_exclude(request.url.path):
            # Determine if this is suspicious activity
            is_suspicious = self._is_suspicious(request, response)
            
            # Extract user ID from request state if available
            user_id = getattr(request.state, 'user_id', None)
            
            # Get user agent
            user_agent = request.headers.get('user-agent', '')
            
            # Determine action type
            action_type = self._determine_action_type(request)
            
            # Log the activity
            await ActivityService.log_activity(
                ip_address=ip_address,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                user_id=user_id,
                user_agent=user_agent,
                action_type=action_type,
                details=f"{request.method} {request.url.path}",
                is_suspicious=is_suspicious
            )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check X-Forwarded-For header (for proxy/load balancer)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(',')[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        # Fall back to direct client
        if request.client:
            return request.client.host
        
        return 'unknown'
    
    def _should_exclude(self, path: str) -> bool:
        """Check if the endpoint should be excluded from logging"""
        for pattern in self.EXCLUDED_ENDPOINTS:
            if re.match(pattern, path):
                return True
        return False
    
    def _is_suspicious(self, request: Request, response: Response) -> bool:
        """Determine if the request is suspicious"""
        path = request.url.path
        
        # Check for error responses
        if response.status_code >= 400:
            # 404s are suspicious if they're not to valid-looking endpoints
            if response.status_code == 404:
                if not self._is_valid_endpoint(path):
                    return True
            # 500 errors might indicate attacks
            elif response.status_code >= 500:
                return True
        
        # Check for suspicious patterns in the path
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        
        # Check query string for suspicious patterns
        if request.url.query:
            for pattern in self.SUSPICIOUS_PATTERNS:
                if re.search(pattern, request.url.query, re.IGNORECASE):
                    return True
        
        return False
    
    def _is_valid_endpoint(self, path: str) -> bool:
        """Check if the endpoint matches known valid patterns"""
        for pattern in self.VALID_ENDPOINTS:
            if re.match(pattern, path):
                return True
        return False
    
    def _determine_action_type(self, request: Request) -> Optional[str]:
        """Determine the type of action based on the endpoint"""
        path = request.url.path
        method = request.method
        
        if path.startswith('/api/users'):
            if method == 'GET':
                return 'view_users'
            elif method == 'POST':
                return 'create_user'
            elif method in ['PUT', 'PATCH']:
                return 'update_user'
            elif method == 'DELETE':
                return 'delete_user'
        elif path.startswith('/api/tasks'):
            if method == 'GET':
                return 'view_tasks'
            elif method == 'POST':
                return 'create_task'
            elif method in ['PUT', 'PATCH']:
                return 'update_task'
            elif method == 'DELETE':
                return 'delete_task'
        elif path.startswith('/admin/login'):
            return 'admin_login'
        elif path.startswith('/admin/logout'):
            return 'admin_logout'
        elif path.startswith('/admin'):
            return 'admin_access'
        elif path.startswith('/miniapp'):
            return 'miniapp_access'
        elif path.startswith('/api/'):
            return 'api_request'
        
        return None
