"""TaxReport Pro — FastAPI приложение."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.api.v1.router import api_router


def create_application() -> FastAPI:
    application = FastAPI(
        title="TaxReport Pro API",
        version="1.0.0",
        docs_url="/api/docs" if settings.APP_DEBUG else None,
        redoc_url="/api/redoc" if settings.APP_DEBUG else None,
        openapi_url="/api/openapi.json" if settings.APP_DEBUG else None,
    )

    # ── Middleware ────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[settings.APP_DOMAIN, f"*.{settings.APP_DOMAIN}", "localhost"],
    )

    # ── Роутеры ───────────────────────────────────────────────
    application.include_router(api_router, prefix="/api/v1")

    # ── Health-check ──────────────────────────────────────────
    @application.get("/health", tags=["system"])
    async def health() -> dict:
        return {"status": "ok", "version": "1.0.0"}

    return application


app = create_application()
