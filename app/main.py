from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
from fastapi.openapi.docs import get_swagger_ui_html
from app.api.auth import router as auth_router
from app.api.applications import router as applications_router
from app.api.admin import router as admin_router
from app.api.cycles import router as cycles_router
from app.api.manager import router as manager_router
from app.api.profile import router as profile_router
from app.api.reviews import router as reviews_router
from app.core.error_handlers import register_exception_handlers

import os

app = FastAPI(
    title="AppPlatform API",
    description="Application Platform API",
    version="1.0.0",
)

# Register exception handlers
register_exception_handlers(app)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static for resume files
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Define HTTP Bearer security
security = HTTPBearer()


# Customize Swagger UI to use Bearer token
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )


# Include routers
app.include_router(auth_router)
app.include_router(applications_router)
app.include_router(admin_router)
app.include_router(cycles_router)
app.include_router(manager_router)
app.include_router(profile_router)
app.include_router(reviews_router)
