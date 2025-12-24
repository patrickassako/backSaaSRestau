from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.health import routes as health_routes
from app.modules.restaurants import routes as restaurant_routes

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
app.include_router(restaurant_routes.router)


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
