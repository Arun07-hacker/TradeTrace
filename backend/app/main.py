from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router


from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print(f"[{settings.APP_NAME}] Starting up in {settings.ENVIRONMENT} mode (Demo: {settings.DEMO_MODE})")
    try:
        await init_db()
        print(f"[{settings.APP_NAME}] Database initialized successfully")
    except Exception as e:
        print(f"[{settings.APP_NAME}] Database init warning (operating in fallback demo mode): {e}")
    yield
    # Shutdown logic
    print(f"[{settings.APP_NAME}] Shutting down cleanly")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "TradeTrace — AI Trading Research, Risk & Learning Assistant.\n\n"
        "Tagline: Research -> Challenge -> Decide -> Monitor -> Trace -> Learn\n\n"
        "DISCLAIMER: TradeTrace is an analytical research, paper trading, and learning assistant. "
        "It does NOT predict stock prices and does NOT provide guaranteed financial advice. "
        "Real-money trading execution is disabled."
    ),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include v1 API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    """Root entry point providing service metadata."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "tagline": settings.TAGLINE,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "demo_mode": settings.DEMO_MODE,
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
