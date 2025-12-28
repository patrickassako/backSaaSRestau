from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.health import routes as health_routes
from app.modules.restaurants import routes as restaurant_routes
from app.modules.onboarding import routes as onboarding_routes
from app.modules.profiles import routes as profile_routes
from app.modules.uploads import routes as upload_routes
from app.modules.public import routes as public_routes
from app.modules.menu_categories import routes as menu_category_routes
from app.modules.menu_items import routes as menu_item_routes
from app.modules.menu_sides import routes as menu_side_routes
from app.modules.sides import routes as sides_routes

app = FastAPI(
    title="Restaurant SaaS Backend",
    description="Backend API for Multi-tenant Restaurant SaaS",
    version="0.1.0"
)

# CORS Configuration
# Allowing all origins for initial development as requested
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_routes.router, tags=["Health"])
app.include_router(public_routes.router)
app.include_router(profile_routes.router)
app.include_router(upload_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(onboarding_routes.router)
app.include_router(menu_category_routes.router)
app.include_router(menu_item_routes.router)
app.include_router(menu_side_routes.router)
app.include_router(sides_routes.router)


@app.get("/")
async def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "message": "Welcome to the Restaurant SaaS Backend",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
