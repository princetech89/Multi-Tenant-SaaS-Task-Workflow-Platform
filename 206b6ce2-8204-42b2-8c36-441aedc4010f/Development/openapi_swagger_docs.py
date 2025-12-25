"""
OpenAPI/Swagger Documentation Generation
Generates comprehensive API documentation with Swagger/OpenAPI 3.0 specification
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import json
from datetime import datetime

# ============================================================================
# OpenAPI Schema Builder
# ============================================================================

class OpenAPIGenerator:
    """Generate OpenAPI 3.0 specification for the API"""
    
    def __init__(self, title: str, version: str, description: str):
        self.spec = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "version": version,
                "description": description,
                "contact": {
                    "name": "API Support",
                    "email": "api-support@example.com"
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT"
                }
            },
            "servers": [
                {
                    "url": "https://api.example.com/v1",
                    "description": "Production server"
                },
                {
                    "url": "https://staging-api.example.com/v1",
                    "description": "Staging server"
                },
                {
                    "url": "http://localhost:8000/v1",
                    "description": "Development server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT access token for API authentication"
                    },
                    "apiKey": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                        "description": "API key for service-to-service authentication"
                    }
                },
                "responses": {},
                "parameters": {}
            },
            "security": [
                {"bearerAuth": []}
            ],
            "tags": [
                {"name": "Authentication", "description": "Authentication and authorization endpoints"},
                {"name": "Organizations", "description": "Organization management"},
                {"name": "Projects", "description": "Project management"},
                {"name": "Tasks", "description": "Task management"},
                {"name": "Members", "description": "Member management"},
                {"name": "Invitations", "description": "Organization invitations"}
            ]
        }
    
    def add_schema(self, name: str, schema: Dict) -> None:
        """Add a component schema"""
        self.spec["components"]["schemas"][name] = schema
    
    def add_path(self, path: str, method: str, operation: Dict) -> None:
        """Add an API path operation"""
        if path not in self.spec["paths"]:
            self.spec["paths"][path] = {}
        self.spec["paths"][path][method.lower()] = operation
    
    def get_spec(self) -> Dict:
        """Get the complete OpenAPI specification"""
        return self.spec
    
    def to_json(self, indent: int = 2) -> str:
        """Export as JSON"""
        return json.dumps(self.spec, indent=indent)

# ============================================================================
# Define Common Schemas
# ============================================================================

def define_common_schemas(api: OpenAPIGenerator):
    """Define reusable schemas"""
    
    # Error schema
    api.add_schema("Error", {
        "type": "object",
        "required": ["error", "message", "status_code"],
        "properties": {
            "error": {"type": "string", "example": "Forbidden"},
            "message": {"type": "string", "example": "You do not have permission to access this resource"},
            "status_code": {"type": "integer", "example": 403},
            "details": {"type": "object", "additionalProperties": True}
        }
    })
    
    # Success response
    api.add_schema("SuccessResponse", {
        "type": "object",
        "required": ["success", "message"],
        "properties": {
            "success": {"type": "boolean", "example": True},
            "message": {"type": "string", "example": "Operation completed successfully"}
        }
    })
    
    # Organization schema
    api.add_schema("Organization", {
        "type": "object",
        "required": ["organization_id", "name", "slug", "tier", "status"],
        "properties": {
            "organization_id": {"type": "string", "format": "uuid"},
            "name": {"type": "string", "minLength": 1, "maxLength": 255},
            "slug": {"type": "string", "pattern": "^[a-z0-9-]+$", "minLength": 3, "maxLength": 63},
            "tier": {"type": "string", "enum": ["free", "pro", "enterprise"]},
            "status": {"type": "string", "enum": ["active", "suspended", "deleted"]},
            "settings": {"type": "object", "additionalProperties": True},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    })
    
    # Organization member
    api.add_schema("OrganizationMember", {
        "type": "object",
        "required": ["member_id", "organization_id", "user_id", "email", "role"],
        "properties": {
            "member_id": {"type": "string", "format": "uuid"},
            "organization_id": {"type": "string", "format": "uuid"},
            "user_id": {"type": "string", "format": "uuid"},
            "email": {"type": "string", "format": "email"},
            "role": {"type": "string", "enum": ["owner", "admin", "manager", "member", "viewer"]},
            "added_by": {"type": "string", "format": "uuid"},
            "added_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    })
    
    # Project schema
    api.add_schema("Project", {
        "type": "object",
        "required": ["project_id", "organization_id", "name", "owner_id", "status"],
        "properties": {
            "project_id": {"type": "string", "format": "uuid"},
            "organization_id": {"type": "string", "format": "uuid"},
            "name": {"type": "string", "minLength": 1, "maxLength": 255},
            "description": {"type": "string", "maxLength": 5000},
            "owner_id": {"type": "string", "format": "uuid"},
            "status": {"type": "string", "enum": ["active", "archived", "deleted"]},
            "visibility": {"type": "string", "enum": ["private", "team", "organization"]},
            "metadata": {"type": "object", "additionalProperties": True},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    })
    
    # Task schema
    api.add_schema("Task", {
        "type": "object",
        "required": ["task_id", "project_id", "title", "status", "priority"],
        "properties": {
            "task_id": {"type": "string", "format": "uuid"},
            "project_id": {"type": "string", "format": "uuid"},
            "title": {"type": "string", "minLength": 1, "maxLength": 500},
            "description": {"type": "string", "maxLength": 10000},
            "status": {"type": "string", "enum": ["todo", "in_progress", "review", "done", "blocked"]},
            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
            "assignee_id": {"type": "string", "format": "uuid"},
            "created_by": {"type": "string", "format": "uuid"},
            "due_date": {"type": "string", "format": "date-time"},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"}
        }
    })
    
    # JWT tokens
    api.add_schema("TokenPair", {
        "type": "object",
        "required": ["access_token", "refresh_token", "token_type", "expires_in"],
        "properties": {
            "access_token": {"type": "string", "description": "JWT access token"},
            "refresh_token": {"type": "string", "description": "JWT refresh token"},
            "token_type": {"type": "string", "example": "Bearer"},
            "expires_in": {"type": "integer", "example": 900, "description": "Seconds until access token expires"}
        }
    })
    
    # Rate limit info
    api.add_schema("RateLimitInfo", {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "example": 100},
            "remaining": {"type": "integer", "example": 95},
            "reset": {"type": "integer", "example": 1640000000, "description": "Unix timestamp when limit resets"}
        }
    })

# ============================================================================
# Define API Endpoints
# ============================================================================

def define_organization_endpoints(api: OpenAPIGenerator):
    """Define organization management endpoints"""
    
    # POST /organizations - Create organization
    api.add_path("/organizations", "post", {
        "tags": ["Organizations"],
        "summary": "Create a new organization",
        "description": "Creates a new organization and adds the creator as owner",
        "operationId": "createOrganization",
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "required": ["name", "slug"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1, "maxLength": 255},
                            "slug": {"type": "string", "pattern": "^[a-z0-9-]+$", "minLength": 3, "maxLength": 63},
                            "tier": {"type": "string", "enum": ["free", "pro", "enterprise"], "default": "free"},
                            "settings": {"type": "object", "additionalProperties": True}
                        }
                    }
                }
            }
        },
        "responses": {
            "201": {
                "description": "Organization created successfully",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Organization"}
                    }
                }
            },
            "400": {"$ref": "#/components/responses/BadRequest"},
            "401": {"$ref": "#/components/responses/Unauthorized"},
            "429": {"$ref": "#/components/responses/TooManyRequests"}
        },
        "security": [{"bearerAuth": []}]
    })
    
    # GET /organizations - List organizations
    api.add_path("/organizations", "get", {
        "tags": ["Organizations"],
        "summary": "List all organizations",
        "description": "Returns a list of all organizations the user has access to",
        "operationId": "listOrganizations",
        "parameters": [
            {
                "name": "status",
                "in": "query",
                "schema": {"type": "string", "enum": ["active", "suspended", "deleted"]},
                "description": "Filter by status"
            },
            {
                "name": "tier",
                "in": "query",
                "schema": {"type": "string", "enum": ["free", "pro", "enterprise"]},
                "description": "Filter by tier"
            },
            {
                "name": "page",
                "in": "query",
                "schema": {"type": "integer", "minimum": 1, "default": 1},
                "description": "Page number"
            },
            {
                "name": "limit",
                "in": "query",
                "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                "description": "Items per page"
            }
        ],
        "responses": {
            "200": {
                "description": "List of organizations",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "data": {"type": "array", "items": {"$ref": "#/components/schemas/Organization"}},
                                "count": {"type": "integer"},
                                "page": {"type": "integer"},
                                "limit": {"type": "integer"}
                            }
                        }
                    }
                }
            },
            "401": {"$ref": "#/components/responses/Unauthorized"},
            "429": {"$ref": "#/components/responses/TooManyRequests"}
        },
        "security": [{"bearerAuth": []}]
    })
    
    # GET /organizations/{id} - Get organization
    api.add_path("/organizations/{id}", "get", {
        "tags": ["Organizations"],
        "summary": "Get organization by ID",
        "operationId": "getOrganization",
        "parameters": [
            {
                "name": "id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"}
            }
        ],
        "responses": {
            "200": {
                "description": "Organization details",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Organization"}
                    }
                }
            },
            "401": {"$ref": "#/components/responses/Unauthorized"},
            "403": {"$ref": "#/components/responses/Forbidden"},
            "404": {"$ref": "#/components/responses/NotFound"},
            "429": {"$ref": "#/components/responses/TooManyRequests"}
        },
        "security": [{"bearerAuth": []}]
    })
    
    # PUT /organizations/{id} - Update organization
    api.add_path("/organizations/{id}", "put", {
        "tags": ["Organizations"],
        "summary": "Update organization",
        "operationId": "updateOrganization",
        "parameters": [
            {
                "name": "id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"}
            }
        ],
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "minLength": 1, "maxLength": 255},
                            "slug": {"type": "string", "pattern": "^[a-z0-9-]+$"},
                            "tier": {"type": "string", "enum": ["free", "pro", "enterprise"]},
                            "settings": {"type": "object", "additionalProperties": True}
                        }
                    }
                }
            }
        },
        "responses": {
            "200": {
                "description": "Organization updated",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/Organization"}
                    }
                }
            },
            "400": {"$ref": "#/components/responses/BadRequest"},
            "401": {"$ref": "#/components/responses/Unauthorized"},
            "403": {"$ref": "#/components/responses/Forbidden"},
            "404": {"$ref": "#/components/responses/NotFound"},
            "429": {"$ref": "#/components/responses/TooManyRequests"}
        },
        "security": [{"bearerAuth": []}]
    })
    
    # DELETE /organizations/{id} - Delete organization
    api.add_path("/organizations/{id}", "delete", {
        "tags": ["Organizations"],
        "summary": "Delete organization",
        "description": "Soft deletes an organization (can be restored)",
        "operationId": "deleteOrganization",
        "parameters": [
            {
                "name": "id",
                "in": "path",
                "required": True,
                "schema": {"type": "string", "format": "uuid"}
            }
        ],
        "responses": {
            "200": {"$ref": "#/components/responses/Success"},
            "401": {"$ref": "#/components/responses/Unauthorized"},
            "403": {"$ref": "#/components/responses/Forbidden"},
            "404": {"$ref": "#/components/responses/NotFound"},
            "429": {"$ref": "#/components/responses/TooManyRequests"}
        },
        "security": [{"bearerAuth": []}]
    })

def define_common_responses(api: OpenAPIGenerator):
    """Define common response schemas"""
    
    api.spec["components"]["responses"] = {
        "Success": {
            "description": "Operation successful",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                }
            }
        },
        "BadRequest": {
            "description": "Invalid request parameters",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Error"}
                }
            }
        },
        "Unauthorized": {
            "description": "Missing or invalid authentication",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Error"}
                }
            }
        },
        "Forbidden": {
            "description": "Insufficient permissions",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Error"}
                }
            }
        },
        "NotFound": {
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Error"}
                }
            }
        },
        "TooManyRequests": {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "schema": {
                        "allOf": [
                            {"$ref": "#/components/schemas/Error"},
                            {
                                "type": "object",
                                "properties": {
                                    "rate_limit": {"$ref": "#/components/schemas/RateLimitInfo"}
                                }
                            }
                        ]
                    }
                }
            },
            "headers": {
                "X-RateLimit-Limit": {
                    "schema": {"type": "integer"},
                    "description": "Request limit per window"
                },
                "X-RateLimit-Remaining": {
                    "schema": {"type": "integer"},
                    "description": "Requests remaining in current window"
                },
                "X-RateLimit-Reset": {
                    "schema": {"type": "integer"},
                    "description": "Time when rate limit resets (Unix timestamp)"
                },
                "Retry-After": {
                    "schema": {"type": "integer"},
                    "description": "Seconds to wait before retrying"
                }
            }
        }
    }

# ============================================================================
# Generate Complete API Documentation
# ============================================================================

openapi_gen = OpenAPIGenerator(
    title="Multi-Tenant Project Management API",
    version="1.0.0",
    description="""
    # Multi-Tenant Project Management API
    
    A comprehensive REST API for managing organizations, projects, tasks, and team collaboration
    in a multi-tenant environment with role-based access control.
    
    ## Features
    
    - 🔐 JWT-based authentication with refresh tokens
    - 🏢 Multi-tenant organization management
    - 👥 Role-based access control (RBAC)
    - 📊 Project and task management
    - 🔒 Tenant isolation and data security
    - ⚡ Rate limiting and request throttling
    - 📝 Comprehensive input validation
    - 🛡️ Security headers and CORS support
    
    ## Authentication
    
    All API endpoints require authentication using JWT Bearer tokens:
    
    ```
    Authorization: Bearer <access_token>
    ```
    
    Access tokens expire after 15 minutes. Use refresh tokens to obtain new access tokens.
    
    ## Rate Limiting
    
    API requests are rate limited based on user tier:
    - Free tier: 100 requests per minute
    - Pro tier: 500 requests per minute
    - Enterprise tier: 2000 requests per minute
    
    Rate limit information is included in response headers:
    - `X-RateLimit-Limit`: Total requests allowed per window
    - `X-RateLimit-Remaining`: Requests remaining in current window
    - `X-RateLimit-Reset`: Time when rate limit resets
    
    ## Error Handling
    
    All errors follow a consistent format with appropriate HTTP status codes
    and detailed error messages.
    """
)

# Define schemas and endpoints
define_common_schemas(openapi_gen)
define_common_responses(openapi_gen)
define_organization_endpoints(openapi_gen)

# Export OpenAPI spec
openapi_spec = openapi_gen.get_spec()
openapi_json = openapi_gen.to_json(indent=2)

print("=" * 100)
print("OPENAPI/SWAGGER DOCUMENTATION GENERATED")
print("=" * 100)
print()
print(f"📘 API Title: {openapi_spec['info']['title']}")
print(f"📌 Version: {openapi_spec['info']['version']}")
print(f"🏷️  OpenAPI Version: {openapi_spec['openapi']}")
print()
print(f"🔧 Servers: {len(openapi_spec['servers'])}")
for server in openapi_spec['servers']:
    print(f"   • {server['description']}: {server['url']}")
print()
print(f"🏷️  Tags: {len(openapi_spec['tags'])}")
for tag in openapi_spec['tags']:
    print(f"   • {tag['name']}: {tag['description']}")
print()
print(f"📋 Schemas: {len(openapi_spec['components']['schemas'])}")
for schema_name in openapi_spec['components']['schemas'].keys():
    print(f"   • {schema_name}")
print()
print(f"🔐 Security Schemes: {len(openapi_spec['components']['securitySchemes'])}")
for scheme_name, scheme in openapi_spec['components']['securitySchemes'].items():
    print(f"   • {scheme_name}: {scheme['type']} ({scheme.get('scheme', 'N/A')})")
print()
print(f"🛣️  Endpoints: {sum(len(methods) for methods in openapi_spec['paths'].values())}")
for path, methods in openapi_spec['paths'].items():
    for method in methods.keys():
        print(f"   • {method.upper():6s} {path}")
print()
print("=" * 100)
print("✅ OpenAPI Documentation Complete")
print("=" * 100)
print()
print("INTEGRATION:")
print("• Import openapi_json into Swagger UI for interactive documentation")
print("• Use openapi_spec dictionary for programmatic access")
print("• Generate client SDKs using OpenAPI Generator")
print("• Validate API responses against schemas")
