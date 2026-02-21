"""
KeyAuth - FastAPI Application Entry Point
Cross-Platform Keystroke Dynamics Passwordless Authentication System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes import registration, authentication, user

# ── Create App ──────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "🔐 Keystroke Dynamics Based Cross-Platform Passwordless Authentication System. "
        "Authenticate users by analyzing their unique typing patterns — no passwords needed."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ─────────────────────────────────────────────

app.include_router(registration.router)
app.include_router(authentication.router)
app.include_router(user.router)

# ── Startup Event ───────────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    """Initialize database tables on application startup."""
    init_db()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started!")
    print(f"📊 Enrollment requires {settings.ENROLLMENT_SAMPLES_REQUIRED} samples")
    print(f"🎯 Auth confidence threshold: {settings.AUTH_CONFIDENCE_THRESHOLD}")

# ── Root Endpoint ───────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Health check and API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Keystroke Dynamics Passwordless Authentication API",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "register": "POST /api/register",
            "enroll": "POST /api/enroll",
            "enrollment_status": "GET /api/enrollment-status/{username}",
            "authenticate": "POST /api/authenticate",
            "profile": "GET /api/user/profile",
            "auth_history": "GET /api/user/auth-history",
        },
    }
