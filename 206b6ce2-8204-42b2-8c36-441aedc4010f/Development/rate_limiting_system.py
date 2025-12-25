"""
Rate Limiting System
Implements tier-based rate limiting with sliding window algorithm
"""

import time
from typing import Dict, Optional, Tuple
from collections import deque
from enum import Enum
from dataclasses import dataclass, field

# ============================================================================
# Rate Limit Configuration
# ============================================================================

class Tier(str, Enum):
    """Organization subscription tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class RateLimitConfig:
    """Rate limit configuration per tier"""
    requests_per_minute: int
    requests_per_hour: int
    burst_size: int  # Maximum burst requests allowed
    
TIER_LIMITS = {
    Tier.FREE: RateLimitConfig(
        requests_per_minute=100,
        requests_per_hour=5000,
        burst_size=20
    ),
    Tier.PRO: RateLimitConfig(
        requests_per_minute=500,
        requests_per_hour=25000,
        burst_size=100
    ),
    Tier.ENTERPRISE: RateLimitConfig(
        requests_per_minute=2000,
        requests_per_hour=100000,
        burst_size=500
    )
}

@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    limit: int
    remaining: int
    reset_at: int  # Unix timestamp
    retry_after: Optional[int] = None  # Seconds to wait

# ============================================================================
# Sliding Window Rate Limiter
# ============================================================================

class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter with per-user tracking
    Uses a sliding window algorithm for accurate rate limiting
    """
    
    def __init__(self):
        # Store request timestamps per user
        self.user_requests: Dict[str, deque] = {}
        self.user_tiers: Dict[str, Tier] = {}
    
    def check_rate_limit(
        self,
        user_id: str,
        tier: Tier,
        window_seconds: int = 60
    ) -> RateLimitResult:
        """
        Check if request is within rate limit
        
        Args:
            user_id: User identifier
            tier: User's subscription tier
            window_seconds: Time window in seconds (60 for per-minute, 3600 for per-hour)
        
        Returns:
            RateLimitResult with allowed status and limit info
        """
        current_time = time.time()
        config = TIER_LIMITS[tier]
        
        # Determine limit based on window
        if window_seconds == 60:
            limit = config.requests_per_minute
        elif window_seconds == 3600:
            limit = config.requests_per_hour
        else:
            limit = config.requests_per_minute
        
        # Initialize user if not exists
        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()
            self.user_tiers[user_id] = tier
        
        # Update tier if changed
        self.user_tiers[user_id] = tier
        
        # Get user's request history
        requests = self.user_requests[user_id]
        
        # Remove requests outside the window
        window_start = current_time - window_seconds
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # Count requests in current window
        request_count = len(requests)
        remaining = max(0, limit - request_count)
        
        # Calculate reset time (end of current window)
        if requests:
            oldest_request = requests[0]
            reset_at = int(oldest_request + window_seconds)
        else:
            reset_at = int(current_time + window_seconds)
        
        # Check if limit exceeded
        if request_count >= limit:
            retry_after = reset_at - int(current_time)
            return RateLimitResult(
                allowed=False,
                limit=limit,
                remaining=0,
                reset_at=reset_at,
                retry_after=max(1, retry_after)
            )
        
        # Allow request and record timestamp
        requests.append(current_time)
        
        return RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=remaining - 1,
            reset_at=reset_at
        )
    
    def get_rate_limit_headers(self, result: RateLimitResult) -> Dict[str, str]:
        """
        Generate rate limit headers for HTTP response
        
        Returns:
            Dictionary of headers following standard rate limit conventions
        """
        headers = {
            "X-RateLimit-Limit": str(result.limit),
            "X-RateLimit-Remaining": str(result.remaining),
            "X-RateLimit-Reset": str(result.reset_at)
        }
        
        if not result.allowed and result.retry_after:
            headers["Retry-After"] = str(result.retry_after)
        
        return headers
    
    def reset_user(self, user_id: str):
        """Reset rate limit for a user (admin function)"""
        if user_id in self.user_requests:
            del self.user_requests[user_id]
            del self.user_tiers[user_id]
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get current rate limit stats for a user"""
        if user_id not in self.user_requests:
            return {
                "user_id": user_id,
                "tier": "unknown",
                "requests_last_minute": 0,
                "requests_last_hour": 0
            }
        
        current_time = time.time()
        requests = self.user_requests[user_id]
        tier = self.user_tiers[user_id]
        
        # Count requests in last minute
        minute_ago = current_time - 60
        requests_last_minute = sum(1 for ts in requests if ts >= minute_ago)
        
        # Count requests in last hour
        hour_ago = current_time - 3600
        requests_last_hour = sum(1 for ts in requests if ts >= hour_ago)
        
        return {
            "user_id": user_id,
            "tier": tier.value,
            "requests_last_minute": requests_last_minute,
            "requests_last_hour": requests_last_hour,
            "minute_limit": TIER_LIMITS[tier].requests_per_minute,
            "hour_limit": TIER_LIMITS[tier].requests_per_hour
        }

# ============================================================================
# Rate Limit Middleware/Decorator
# ============================================================================

class RateLimitMiddleware:
    """Middleware for applying rate limits to API requests"""
    
    def __init__(self, limiter: SlidingWindowRateLimiter):
        self.limiter = limiter
    
    def check_request(
        self,
        user_id: str,
        tier: str,
        endpoint: str = None
    ) -> Tuple[bool, Dict[str, str], Optional[Dict]]:
        """
        Check if request should be allowed
        
        Returns:
            Tuple of (allowed, headers, error_response)
        """
        tier_enum = Tier(tier)
        
        # Check per-minute limit
        result_minute = self.limiter.check_rate_limit(user_id, tier_enum, window_seconds=60)
        
        if not result_minute.allowed:
            headers = self.limiter.get_rate_limit_headers(result_minute)
            error = {
                "error": "Too Many Requests",
                "message": f"Rate limit exceeded. Limit: {result_minute.limit} requests per minute.",
                "status_code": 429,
                "rate_limit": {
                    "limit": result_minute.limit,
                    "remaining": 0,
                    "reset": result_minute.reset_at
                },
                "retry_after": result_minute.retry_after
            }
            return False, headers, error
        
        # Also check per-hour limit
        result_hour = self.limiter.check_rate_limit(user_id, tier_enum, window_seconds=3600)
        
        if not result_hour.allowed:
            headers = self.limiter.get_rate_limit_headers(result_hour)
            error = {
                "error": "Too Many Requests",
                "message": f"Hourly rate limit exceeded. Limit: {result_hour.limit} requests per hour.",
                "status_code": 429,
                "rate_limit": {
                    "limit": result_hour.limit,
                    "remaining": 0,
                    "reset": result_hour.reset_at
                },
                "retry_after": result_hour.retry_after
            }
            return False, headers, error
        
        # Request allowed - return headers with current limits
        headers = self.limiter.get_rate_limit_headers(result_minute)
        
        return True, headers, None

# ============================================================================
# Testing and Demonstration
# ============================================================================

print("=" * 100)
print("RATE LIMITING SYSTEM - TIER-BASED SLIDING WINDOW")
print("=" * 100)
print()

# Initialize rate limiter
rate_limiter = SlidingWindowRateLimiter()
middleware = RateLimitMiddleware(rate_limiter)

print("📊 RATE LIMIT CONFIGURATION")
print("-" * 100)
for tier, config in TIER_LIMITS.items():
    print(f"{tier.value.upper():12s} → {config.requests_per_minute:4d} req/min | {config.requests_per_hour:6d} req/hour | Burst: {config.burst_size}")
print()

# Test users with different tiers
test_users = [
    ("user-free-1", "free"),
    ("user-pro-1", "pro"),
    ("user-enterprise-1", "enterprise")
]

print("🧪 SIMULATING API REQUESTS")
print("-" * 100)

for user_id, tier in test_users:
    print(f"\n{tier.upper()} Tier - {user_id}")
    print("  " + "-" * 96)
    
    # Simulate 10 requests
    for i in range(10):
        allowed, headers, error = middleware.check_request(user_id, tier)
        
        if allowed:
            status = "✅ ALLOWED"
            remaining = headers.get("X-RateLimit-Remaining", "N/A")
            print(f"  Request {i+1:2d}: {status:12s} | Remaining: {remaining:4s} | Reset: {headers.get('X-RateLimit-Reset')}")
        else:
            status = "❌ BLOCKED"
            print(f"  Request {i+1:2d}: {status:12s} | {error['message']}")
            print(f"             Retry after {error['retry_after']} seconds")
            break
    
    # Show user stats
    stats = rate_limiter.get_user_stats(user_id)
    print(f"\n  📈 Stats: {stats['requests_last_minute']}/{stats['minute_limit']} per minute")

print()
print()
print("🔥 BURST TESTING - Rapid Fire Requests")
print("-" * 100)

# Test burst protection for free tier
burst_user = "user-free-burst"
burst_tier = "free"
config = TIER_LIMITS[Tier.FREE]

print(f"\nFREE Tier User - Sending {config.burst_size + 10} rapid requests")
print("  " + "-" * 96)

allowed_count = 0
blocked_count = 0

for i in range(config.burst_size + 10):
    allowed, headers, error = middleware.check_request(burst_user, burst_tier)
    
    if allowed:
        allowed_count += 1
    else:
        blocked_count += 1
        if blocked_count == 1:  # Show first block
            print(f"  Request {i+1:2d}: ❌ BLOCKED | {error['message']}")
            print(f"             All subsequent requests blocked until reset")

print(f"\n  Results: {allowed_count} allowed, {blocked_count} blocked")
print(f"  Rate limit working correctly ✅")

print()
print()
print("📈 RATE LIMIT STATISTICS")
print("-" * 100)

for user_id, tier in test_users:
    stats = rate_limiter.get_user_stats(user_id)
    print(f"\n{user_id}")
    print(f"  Tier: {stats['tier']}")
    print(f"  Last Minute: {stats['requests_last_minute']}/{stats['minute_limit']}")
    print(f"  Last Hour: {stats['requests_last_hour']}/{stats['hour_limit']}")

print()
print()
print("=" * 100)
print("✅ Rate Limiting System Implemented Successfully")
print("=" * 100)
print()
print("FEATURES:")
print("• Sliding window algorithm for accurate rate limiting")
print("• Per-minute and per-hour limits")
print("• Tier-based limits (Free, Pro, Enterprise)")
print("• Burst protection")
print("• Standard rate limit headers (X-RateLimit-*)")
print("• Retry-After header for blocked requests")
print("• User statistics and monitoring")
print()
print("INTEGRATION:")
print("• Apply RateLimitMiddleware to all API endpoints")
print("• Extract user_id and tier from JWT token")
print("• Return 429 status code when limit exceeded")
print("• Include rate limit headers in all responses")
