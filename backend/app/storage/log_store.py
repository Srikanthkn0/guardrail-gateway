import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.config import DATA_DIR
from app.models import (
    ChatResponse,
    GatewayLogEntry,
    GatewayStatsResponse,
    LogsListResponse,
    ProviderStat,
)

DB_PATH = DATA_DIR / "gateway.db"
PROMPT_PREVIEW_LEN = 120


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS gateway_logs (
                request_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                prompt TEXT NOT NULL,
                provider TEXT,
                model TEXT,
                input_decision TEXT NOT NULL,
                output_decision TEXT,
                final_decision TEXT NOT NULL,
                forwarded INTEGER NOT NULL,
                latency_ms REAL,
                response_redacted INTEGER NOT NULL DEFAULT 0,
                response_text TEXT,
                input_hits_json TEXT NOT NULL,
                output_hits_json TEXT,
                reasons_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_gateway_logs_created_at
            ON gateway_logs (created_at DESC)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_gateway_logs_final_decision
            ON gateway_logs (final_decision)
            """
        )


def _prompt_preview(prompt: str) -> str:
    text = prompt.strip().replace("\n", " ")
    if len(text) <= PROMPT_PREVIEW_LEN:
        return text
    return f"{text[:PROMPT_PREVIEW_LEN]}..."


def _row_to_entry(row: sqlite3.Row) -> GatewayLogEntry:
    input_hits = json.loads(row["input_hits_json"])
    output_hits = json.loads(row["output_hits_json"] or "[]")
    return GatewayLogEntry(
        request_id=row["request_id"],
        created_at=row["created_at"],
        prompt_preview=_prompt_preview(row["prompt"]),
        provider=row["provider"],
        model=row["model"],
        input_decision=row["input_decision"],
        output_decision=row["output_decision"],
        final_decision=row["final_decision"],
        forwarded=bool(row["forwarded"]),
        latency_ms=row["latency_ms"],
        response_redacted=bool(row["response_redacted"]),
        input_hit_count=len(input_hits),
        output_hit_count=len(output_hits),
        reasons=json.loads(row["reasons_json"]),
        input_hits=input_hits,
        output_hits=output_hits,
        response_text=row["response_text"],
    )


def record_gateway_request(prompt: str, response: ChatResponse) -> None:
    created_at = datetime.now(UTC).isoformat()
    input_hits = [hit.model_dump() for hit in response.input_scan.hits]
    output_hits = (
        [hit.model_dump() for hit in response.output_scan.hits]
        if response.output_scan
        else []
    )
    output_decision = response.output_scan.decision if response.output_scan else None
    response_redacted = int(
        response.forwarded and response.output_scan is not None and not response.response_text
    )

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO gateway_logs (
                request_id,
                created_at,
                prompt,
                provider,
                model,
                input_decision,
                output_decision,
                final_decision,
                forwarded,
                latency_ms,
                response_redacted,
                response_text,
                input_hits_json,
                output_hits_json,
                reasons_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                response.request_id,
                created_at,
                prompt,
                response.provider,
                response.model,
                response.input_scan.decision,
                output_decision,
                response.final_decision,
                int(response.forwarded),
                response.latency_ms,
                response_redacted,
                response.response_text,
                json.dumps(input_hits),
                json.dumps(output_hits),
                json.dumps(response.reasons),
            ),
        )


def list_logs(
    *,
    limit: int = 50,
    offset: int = 0,
    decision: str | None = None,
    provider: str | None = None,
) -> LogsListResponse:
    clauses: list[str] = []
    params: list[Any] = []

    if decision:
        clauses.append("final_decision = ?")
        params.append(decision)
    if provider:
        clauses.append("provider = ?")
        params.append(provider)

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    with _connect() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) AS count FROM gateway_logs {where_sql}",
            params,
        ).fetchone()["count"]
        rows = conn.execute(
            f"""
            SELECT * FROM gateway_logs
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            [*params, limit, offset],
        ).fetchall()

    return LogsListResponse(
        count=total,
        limit=limit,
        offset=offset,
        logs=[_row_to_entry(row) for row in rows],
    )


def get_log(request_id: str) -> GatewayLogEntry | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM gateway_logs WHERE request_id = ?",
            (request_id,),
        ).fetchone()
    if row is None:
        return None
    return _row_to_entry(row)


def get_stats() -> GatewayStatsResponse:
    with _connect() as conn:
        summary = conn.execute(
            """
            SELECT
                COUNT(*) AS total_requests,
                SUM(CASE WHEN final_decision = 'allow' THEN 1 ELSE 0 END) AS allow_count,
                SUM(CASE WHEN final_decision = 'warn' THEN 1 ELSE 0 END) AS warn_count,
                SUM(CASE WHEN final_decision = 'block' THEN 1 ELSE 0 END) AS block_count,
                SUM(CASE WHEN forwarded = 1 THEN 1 ELSE 0 END) AS forwarded_count,
                AVG(latency_ms) AS avg_latency_ms
            FROM gateway_logs
            """
        ).fetchone()

        provider_rows = conn.execute(
            """
            SELECT
                COALESCE(provider, 'none') AS provider,
                COUNT(*) AS count,
                AVG(latency_ms) AS avg_latency_ms
            FROM gateway_logs
            GROUP BY COALESCE(provider, 'none')
            ORDER BY count DESC
            """
        ).fetchall()

    total = summary["total_requests"] or 0
    block_count = summary["block_count"] or 0
    warn_count = summary["warn_count"] or 0

    return GatewayStatsResponse(
        total_requests=total,
        allow_count=summary["allow_count"] or 0,
        warn_count=warn_count,
        block_count=block_count,
        forwarded_count=summary["forwarded_count"] or 0,
        block_rate=round(block_count / total, 4) if total else 0.0,
        warn_rate=round(warn_count / total, 4) if total else 0.0,
        avg_latency_ms=round(summary["avg_latency_ms"], 2)
        if summary["avg_latency_ms"] is not None
        else None,
        by_provider=[
            ProviderStat(
                provider=row["provider"],
                count=row["count"],
                avg_latency_ms=round(row["avg_latency_ms"], 2)
                if row["avg_latency_ms"] is not None
                else None,
            )
            for row in provider_rows
        ],
    )