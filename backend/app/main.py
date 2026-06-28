import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.middleware.auth import ApiKeyMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.routes import gateway, health, logs, rules
from app.services.ml_classifier import ensure_sklearn_loaded
from app.storage.log_store import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    ensure_sklearn_loaded()
    logger.info(
        "Gateway ready env=%s provider_auto=%s ml=%s api_key=%s",
        settings.APP_ENV,
        settings.DEFAULT_PROVIDER,
        settings.ML_GUARD_BACKEND,
        "required" if settings.require_api_key else "off",
    )
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="LLM safety gateway for input/output guardrails and request logging.",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_origin_regex=r"https://guardrail-gateway(?:-[a-z0-9]+)?\.vercel\.app",
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "X-Request-ID"],
)
app.add_middleware(ApiKeyMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app.include_router(health.router, tags=["health"])
app.include_router(rules.router, tags=["rules"])
app.include_router(gateway.router)
app.include_router(logs.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", _request.url.path)
    detail = (
        "Internal server error."
        if settings.is_production
        else f"Internal server error: {exc}"
    )
    return JSONResponse(status_code=500, content={"detail": detail})


@app.get("/")
async def root():
    return {
        "message": settings.APP_NAME,
        "health": "/health",
        "rules": "/rules",
        "rules_test": "/rules/test",
        "gateway_chat": "/gateway/chat",
        "logs": "/logs",
        "stats": "/stats",
    }