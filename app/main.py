from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, roles, customers, businesses, system, catalogue, promotions, sales, redis
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "Authentication", "description": "Authentication and authorization endpoints"},
        {"name": "Users", "description": "User management endpoints"},
        {"name": "Roles", "description": "Role and permission management"},
        {"name": "Customers", "description": "Customer and address management"},
        {"name": "Businesses", "description": "Business management"},
        {"name": "Catalogue", "description": "Product catalogue management (categories, brands, products, variants, etc.)"},
        {"name": "Promotions", "description": "Promotion and coupon management"},
        {"name": "Sales", "description": "Sales management (stores, orders, payments, returns)"},
        {"name": "Redis", "description": "Redis cache management"},
        {"name": "System", "description": "System utilities (sessions, invitations, audit logs)"},
    ],
)

# Add JWT Bearer authentication to Swagger UI
app.openapi_components = {
    "securitySchemes": {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: Bearer <your-token>. Get your token by logging in via POST /auth/login"
        },
        "OAuth2Password": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {}
                }
            },
            "description": "Use your email and password to login. This will generate a JWT token that will be used for authentication."
        }
    }
}

app.openapi_security = [{"BearerAuth": []}, {"OAuth2Password": []}]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(customers.router)
app.include_router(businesses.router)
app.include_router(catalogue.router)
app.include_router(promotions.router)
app.include_router(sales.router)
app.include_router(redis.router)
app.include_router(system.router)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
