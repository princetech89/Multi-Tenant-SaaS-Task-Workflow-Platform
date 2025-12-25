"""
Security Headers System
Implements comprehensive security headers for API responses
"""

from typing import Dict, Optional
from enum import Enum

# ============================================================================
# Security Header Configuration
# ============================================================================

class SecurityHeadersConfig:
    """Configuration for security headers"""
    
    # CORS Configuration
    CORS_ALLOW_ORIGINS = ["https://app.example.com", "https://www.example.com"]
    CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = ["Authorization", "Content-Type", "X-Request-ID", "X-Organization-ID"]
    CORS_EXPOSE_HEADERS = ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
    CORS_MAX_AGE = 86400  # 24 hours
    CORS_ALLOW_CREDENTIALS = True
    
    # Content Security Policy
    CSP_DIRECTIVES = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'", "https://cdn.example.com"],
        "style-src": ["'self'", "'unsafe-inline'", "https://cdn.example.com"],
        "img-src": ["'self'", "https:", "data:"],
        "font-src": ["'self'", "https://cdn.example.com"],
        "connect-src": ["'self'", "https://api.example.com"],
        "frame-ancestors": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"]
    }
    
    # Permissions Policy (formerly Feature Policy)
    PERMISSIONS_POLICY = {
        "geolocation": [],  # Disabled
        "camera": [],  # Disabled
        "microphone": [],  # Disabled
        "payment": ["self"],
        "usb": [],  # Disabled
        "accelerometer": [],  # Disabled
        "gyroscope": []  # Disabled
    }
    
    # HSTS Configuration
    HSTS_MAX_AGE = 31536000  # 1 year
    HSTS_INCLUDE_SUBDOMAINS = True
    HSTS_PRELOAD = True
    
    # Referrer Policy
    REFERRER_POLICY = "strict-origin-when-cross-origin"

# ============================================================================
# Security Headers Middleware
# ============================================================================

class SecurityHeadersMiddleware:
    """Middleware to add security headers to all API responses"""
    
    def __init__(self, config: SecurityHeadersConfig = None):
        self.config = config or SecurityHeadersConfig()
    
    def get_security_headers(
        self,
        request_origin: Optional[str] = None,
        request_method: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate all security headers for a response
        
        Args:
            request_origin: Origin header from request (for CORS)
            request_method: Method from request (for CORS preflight)
        
        Returns:
            Dictionary of security headers
        """
        headers = {}
        
        # Add CORS headers
        headers.update(self._get_cors_headers(request_origin, request_method))
        
        # Add Content Security Policy
        headers["Content-Security-Policy"] = self._build_csp()
        
        # Add Strict Transport Security (HSTS)
        hsts_value = f"max-age={self.config.HSTS_MAX_AGE}"
        if self.config.HSTS_INCLUDE_SUBDOMAINS:
            hsts_value += "; includeSubDomains"
        if self.config.HSTS_PRELOAD:
            hsts_value += "; preload"
        headers["Strict-Transport-Security"] = hsts_value
        
        # X-Frame-Options: Prevents clickjacking
        headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options: Prevents MIME sniffing
        headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection: XSS filter
        headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy: Controls referrer information
        headers["Referrer-Policy"] = self.config.REFERRER_POLICY
        
        # Permissions-Policy: Controls browser features
        headers["Permissions-Policy"] = self._build_permissions_policy()
        
        # X-Permitted-Cross-Domain-Policies: Adobe products
        headers["X-Permitted-Cross-Domain-Policies"] = "none"
        
        # Cache-Control: Prevent sensitive data caching
        headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
        headers["Pragma"] = "no-cache"
        headers["Expires"] = "0"
        
        return headers
    
    def _get_cors_headers(
        self,
        request_origin: Optional[str],
        request_method: Optional[str]
    ) -> Dict[str, str]:
        """Generate CORS headers"""
        headers = {}
        
        # Check if origin is allowed
        if request_origin and self._is_origin_allowed(request_origin):
            headers["Access-Control-Allow-Origin"] = request_origin
        else:
            # Default to first allowed origin if no specific match
            if self.config.CORS_ALLOW_ORIGINS:
                headers["Access-Control-Allow-Origin"] = self.config.CORS_ALLOW_ORIGINS[0]
        
        # Allow credentials
        if self.config.CORS_ALLOW_CREDENTIALS:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        # For preflight requests
        if request_method == "OPTIONS":
            headers["Access-Control-Allow-Methods"] = ", ".join(self.config.CORS_ALLOW_METHODS)
            headers["Access-Control-Allow-Headers"] = ", ".join(self.config.CORS_ALLOW_HEADERS)
            headers["Access-Control-Max-Age"] = str(self.config.CORS_MAX_AGE)
        
        # Expose specific headers to browser
        if self.config.CORS_EXPOSE_HEADERS:
            headers["Access-Control-Expose-Headers"] = ", ".join(self.config.CORS_EXPOSE_HEADERS)
        
        # Vary header to prevent caching issues
        headers["Vary"] = "Origin"
        
        return headers
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if an origin is in the allowed list"""
        return origin in self.config.CORS_ALLOW_ORIGINS
    
    def _build_csp(self) -> str:
        """Build Content Security Policy header value"""
        directives = []
        for directive, sources in self.config.CSP_DIRECTIVES.items():
            if sources:
                sources_str = " ".join(sources)
                directives.append(f"{directive} {sources_str}")
            else:
                directives.append(f"{directive} 'none'")
        return "; ".join(directives)
    
    def _build_permissions_policy(self) -> str:
        """Build Permissions Policy header value"""
        policies = []
        for feature, origins in self.config.PERMISSIONS_POLICY.items():
            if origins:
                origins_str = " ".join(origins)
                policies.append(f"{feature}=({origins_str})")
            else:
                policies.append(f"{feature}=()")
        return ", ".join(policies)

# ============================================================================
# Error Handling with Security Headers
# ============================================================================

class SecureErrorResponse:
    """Generate secure error responses with appropriate headers"""
    
    def __init__(self, headers_middleware: SecurityHeadersMiddleware):
        self.headers_middleware = headers_middleware
    
    def create_error_response(
        self,
        status_code: int,
        error: str,
        message: str,
        details: Optional[Dict] = None,
        request_origin: Optional[str] = None
    ) -> Dict:
        """
        Create a secure error response with all security headers
        
        Returns:
            Dictionary with status_code, body, and headers
        """
        # Generate security headers
        headers = self.headers_middleware.get_security_headers(
            request_origin=request_origin
        )
        
        # Build error body
        body = {
            "error": error,
            "message": message,
            "status_code": status_code
        }
        
        if details:
            body["details"] = details
        
        # Don't expose internal error details in production
        if status_code >= 500:
            body["message"] = "An internal server error occurred"
            # Log actual error internally but don't expose to client
        
        return {
            "status_code": status_code,
            "headers": headers,
            "body": body
        }

# ============================================================================
# Testing and Demonstration
# ============================================================================

print("=" * 100)
print("SECURITY HEADERS SYSTEM")
print("=" * 100)
print()

# Initialize middleware
security_middleware = SecurityHeadersMiddleware()
error_handler = SecureErrorResponse(security_middleware)

print("🔒 SECURITY HEADERS CONFIGURATION")
print("-" * 100)
print()

print("CORS Configuration:")
print(f"  • Allowed Origins: {', '.join(SecurityHeadersConfig.CORS_ALLOW_ORIGINS)}")
print(f"  • Allowed Methods: {', '.join(SecurityHeadersConfig.CORS_ALLOW_METHODS)}")
print(f"  • Allow Credentials: {SecurityHeadersConfig.CORS_ALLOW_CREDENTIALS}")
print(f"  • Max Age: {SecurityHeadersConfig.CORS_MAX_AGE}s")
print()

print("HSTS Configuration:")
print(f"  • Max Age: {SecurityHeadersConfig.HSTS_MAX_AGE}s (1 year)")
print(f"  • Include Subdomains: {SecurityHeadersConfig.HSTS_INCLUDE_SUBDOMAINS}")
print(f"  • Preload: {SecurityHeadersConfig.HSTS_PRELOAD}")
print()

print("Content Security Policy:")
for directive, sources in SecurityHeadersConfig.CSP_DIRECTIVES.items():
    sources_str = ", ".join(sources) if sources else "none"
    print(f"  • {directive}: {sources_str}")
print()

print()
print("📋 GENERATED SECURITY HEADERS")
print("-" * 100)

# Generate headers for a normal request
headers = security_middleware.get_security_headers(
    request_origin="https://app.example.com",
    request_method="GET"
)

print()
print("For standard API request (GET):")
for header, value in sorted(headers.items()):
    # Truncate long values for display
    display_value = value if len(value) <= 80 else value[:77] + "..."
    print(f"  {header}: {display_value}")

print()
print()
print("📋 PREFLIGHT REQUEST HEADERS (OPTIONS)")
print("-" * 100)

# Generate headers for preflight request
preflight_headers = security_middleware.get_security_headers(
    request_origin="https://app.example.com",
    request_method="OPTIONS"
)

print()
for header, value in sorted(preflight_headers.items()):
    if "Access-Control" in header:  # Only show CORS headers for preflight
        display_value = value if len(value) <= 80 else value[:77] + "..."
        print(f"  {header}: {display_value}")

print()
print()
print("🚨 SECURE ERROR RESPONSES")
print("-" * 100)

# Test error responses
error_scenarios = [
    (400, "Bad Request", "Invalid input parameters", {"field": "email", "issue": "invalid format"}),
    (401, "Unauthorized", "Missing or invalid authentication token", None),
    (403, "Forbidden", "Insufficient permissions to access this resource", None),
    (404, "Not Found", "The requested resource was not found", None),
    (429, "Too Many Requests", "Rate limit exceeded", {"retry_after": 60}),
    (500, "Internal Server Error", "Database connection failed", None)
]

for status_code, error, message, details in error_scenarios:
    response = error_handler.create_error_response(
        status_code=status_code,
        error=error,
        message=message,
        details=details,
        request_origin="https://app.example.com"
    )
    
    print()
    print(f"{status_code} {error}")
    print(f"  Message: {response['body']['message']}")
    if details and status_code < 500:  # Don't show details for 5xx errors
        print(f"  Details: {response['body'].get('details', 'N/A')}")
    print(f"  Security Headers: {len(response['headers'])} headers applied")

print()
print()
print("=" * 100)
print("✅ Security Headers System Implemented Successfully")
print("=" * 100)
print()
print("SECURITY FEATURES:")
print("• CORS with origin validation and credentials support")
print("• Content Security Policy (CSP) to prevent XSS")
print("• HTTP Strict Transport Security (HSTS)")
print("• X-Frame-Options to prevent clickjacking")
print("• X-Content-Type-Options to prevent MIME sniffing")
print("• X-XSS-Protection for additional XSS protection")
print("• Referrer-Policy for privacy")
print("• Permissions-Policy to control browser features")
print("• Cache-Control headers for sensitive data")
print("• Secure error responses that don't leak internal details")
print()
print("INTEGRATION:")
print("• Apply SecurityHeadersMiddleware to all API responses")
print("• Use SecureErrorResponse for all error handling")
print("• Configure CORS_ALLOW_ORIGINS for your domains")
print("• Adjust CSP directives based on your frontend needs")
print("• Enable HSTS only after testing (irreversible for duration)")
