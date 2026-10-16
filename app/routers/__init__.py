from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.roles import router as roles_router
from app.routers.customers import router as customers_router
from app.routers.businesses import router as businesses_router
from app.routers.system import router as system_router

__all__ = [
    "auth_router",
    "users_router",
    "roles_router",
    "customers_router",
    "businesses_router",
    "system_router",
]
