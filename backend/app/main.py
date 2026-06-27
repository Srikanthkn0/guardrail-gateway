from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import gateway, health, logs, rules
from app.storage.log_store import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="LLM safety gateway for input/output guardrails and request logging.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(rules.router, tags=["rules"])
app.include_router(gateway.router)
app.include_router(logs.router)


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
        "docs": "/docs",
    }