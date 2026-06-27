from fastapi import APIRouter, HTTPException, Query

from app.models import Decision, GatewayLogEntry, GatewayStatsResponse, LogsListResponse
from app.storage.log_store import get_log, get_stats, list_logs

router = APIRouter(tags=["logs"])


@router.get("/logs", response_model=LogsListResponse)
async def get_logs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    decision: Decision | None = None,
    provider: str | None = None,
):
    return list_logs(
        limit=limit,
        offset=offset,
        decision=decision,
        provider=provider.strip().lower() if provider else None,
    )


@router.get("/logs/{request_id}", response_model=GatewayLogEntry)
async def get_log_detail(request_id: str):
    entry = get_log(request_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Log '{request_id}' not found.")
    return entry


@router.get("/stats", response_model=GatewayStatsResponse)
async def stats():
    return get_stats()