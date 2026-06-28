"""Prompt-injection classifier — Grok LLM judge (preferred), HF DistilBERT, sklearn fallback."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass

from app.config import settings
from app.services.grok_classifier import classify_prompt, is_grok_configured

logger = logging.getLogger(__name__)

ML_RULE_ID = "ml:injection"
_UNSAFE_LABELS = frozenset(
    {
        "INJECTION",
        "INJECT",
        "UNSAFE",
        "MALICIOUS",
        "LABEL_1",
        "1",
    }
)

_pipeline = None
_sklearn_model = None
_grok_ready = False
_load_attempted = False
_lock = threading.Lock()


@dataclass(frozen=True)
class MLPrediction:
    enabled: bool
    loaded: bool
    backend: str
    model_name: str
    injection_score: float
    label: str
    error: str | None = None


def _is_injection_label(label: str) -> bool:
    normalized = label.strip().upper().replace(" ", "_")
    if normalized in _UNSAFE_LABELS:
        return True
    return normalized.endswith("_1") or normalized == "1"


def _score_from_hf_result(item: dict) -> tuple[float, str]:
    label = str(item.get("label", ""))
    score = float(item.get("score", 0.0))
    if _is_injection_label(label):
        return score, "injection"
    return 1.0 - score, "benign"


def _load_hf_pipeline():
    from transformers import pipeline

    return pipeline(
        "text-classification",
        model=settings.ML_GUARD_MODEL,
        truncation=True,
        max_length=settings.ML_GUARD_MAX_LENGTH,
        device=-1,
    )


def _load_sklearn():
    import joblib

    path = settings.ML_GUARD_SKLEARN_PATH
    if not path.exists():
        return None
    return joblib.load(path)


def _ensure_loaded() -> tuple[str, object | None]:
    global _pipeline, _sklearn_model, _grok_ready, _load_attempted

    with _lock:
        if _load_attempted:
            if _grok_ready:
                return "grok", "api"
            if _pipeline is not None:
                return "hf", _pipeline
            if _sklearn_model is not None:
                return "sklearn", _sklearn_model
            return "none", None

        _load_attempted = True
        backend = settings.ML_GUARD_BACKEND.lower()

        if backend in {"grok", "auto"} and is_grok_configured():
            _grok_ready = True
            logger.info("ML guard using Grok classifier: %s", settings.ML_GUARD_GROK_MODEL)
            return "grok", "api"

        if backend in {"hf", "auto", "transformers"}:
            try:
                _pipeline = _load_hf_pipeline()
                logger.info("ML guard loaded HF model: %s", settings.ML_GUARD_MODEL)
                return "hf", _pipeline
            except Exception:
                logger.exception("Failed to load HF model %s", settings.ML_GUARD_MODEL)

        if backend in {"sklearn", "auto"}:
            try:
                _sklearn_model = _load_sklearn()
                if _sklearn_model is not None:
                    logger.info(
                        "ML guard loaded sklearn model from %s",
                        settings.ML_GUARD_SKLEARN_PATH,
                    )
                    return "sklearn", _sklearn_model
            except Exception:
                logger.exception("Failed to load sklearn fallback model")

        return "none", None


def reload_model() -> bool:
    global _pipeline, _sklearn_model, _grok_ready, _load_attempted
    with _lock:
        _pipeline = None
        _sklearn_model = None
        _grok_ready = False
        _load_attempted = False
    backend, model = _ensure_loaded()
    return model is not None


def predict_injection(text: str) -> MLPrediction:
    if not settings.ML_GUARD_ENABLED:
        return MLPrediction(
            enabled=False,
            loaded=False,
            backend="off",
            model_name="",
            injection_score=0.0,
            label="benign",
        )

    normalized = text.strip()
    if not normalized:
        return MLPrediction(
            enabled=True,
            loaded=False,
            backend=settings.ML_GUARD_BACKEND,
            model_name=settings.ML_GUARD_MODEL,
            injection_score=0.0,
            label="benign",
        )

    backend, model = _ensure_loaded()
    if model is None:
        return MLPrediction(
            enabled=True,
            loaded=False,
            backend=backend,
            model_name=settings.ML_GUARD_MODEL,
            injection_score=0.0,
            label="benign",
            error="Model not loaded",
        )

    try:
        if backend == "grok":
            injection_score, label, error = classify_prompt(normalized)
            return MLPrediction(
                enabled=True,
                loaded=error is None,
                backend="grok",
                model_name=settings.ML_GUARD_GROK_MODEL,
                injection_score=injection_score,
                label=label,
                error=error,
            )

        if backend == "hf":
            raw = model(normalized)[0]
            injection_score, label = _score_from_hf_result(raw)
            return MLPrediction(
                enabled=True,
                loaded=True,
                backend="hf",
                model_name=settings.ML_GUARD_MODEL,
                injection_score=injection_score,
                label=label,
            )

        proba = model.predict_proba([normalized])[0]
        classes = list(model.classes_)
        unsafe_idx = classes.index(1) if 1 in classes else 0
        injection_score = float(proba[unsafe_idx])
        block_at, _ = _thresholds_for_backend("sklearn")
        label = "injection" if injection_score >= block_at else "benign"
        return MLPrediction(
            enabled=True,
            loaded=True,
            backend="sklearn",
            model_name=str(settings.ML_GUARD_SKLEARN_PATH.name),
            injection_score=injection_score,
            label=label,
        )
    except Exception as exc:
        logger.exception("ML prediction failed")
        return MLPrediction(
            enabled=True,
            loaded=True,
            backend=backend,
            model_name=settings.ML_GUARD_MODEL,
            injection_score=0.0,
            label="benign",
            error=str(exc),
        )


def _thresholds_for_backend(backend: str) -> tuple[float, float]:
    if backend == "grok":
        return (
            settings.ML_GUARD_GROK_BLOCK_THRESHOLD,
            settings.ML_GUARD_GROK_WARN_THRESHOLD,
        )
    if backend == "sklearn":
        return (
            settings.ML_GUARD_SKLEARN_BLOCK_THRESHOLD,
            settings.ML_GUARD_WARN_THRESHOLD,
        )
    return settings.ML_GUARD_BLOCK_THRESHOLD, settings.ML_GUARD_WARN_THRESHOLD


def ml_decision(injection_score: float, backend: str = "hf") -> str | None:
    block_at, warn_at = _thresholds_for_backend(backend)
    if injection_score >= block_at:
        return "block"
    if injection_score >= warn_at:
        return "warn"
    return None


def classifier_status() -> dict:
    backend, model = _ensure_loaded() if settings.ML_GUARD_ENABLED else ("off", None)
    model_name = settings.ML_GUARD_MODEL
    block_threshold = settings.ML_GUARD_BLOCK_THRESHOLD
    warn_threshold = settings.ML_GUARD_WARN_THRESHOLD

    if backend == "grok":
        model_name = settings.ML_GUARD_GROK_MODEL
        block_threshold = settings.ML_GUARD_GROK_BLOCK_THRESHOLD
        warn_threshold = settings.ML_GUARD_GROK_WARN_THRESHOLD

    return {
        "enabled": settings.ML_GUARD_ENABLED,
        "loaded": model is not None,
        "backend": backend if settings.ML_GUARD_ENABLED else "off",
        "model": model_name,
        "grok_configured": is_grok_configured(),
        "sklearn_path": str(settings.ML_GUARD_SKLEARN_PATH),
        "sklearn_exists": settings.ML_GUARD_SKLEARN_PATH.exists(),
        "block_threshold": block_threshold,
        "warn_threshold": warn_threshold,
        "rule_id": ML_RULE_ID,
    }