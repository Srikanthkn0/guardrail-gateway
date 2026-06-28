"""Prompt-injection classifier — Grok LLM judge with sklearn/HF fallback cascade."""

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
_sklearn_load_attempted = False
_hf_load_attempted = False
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
    fallback_used: bool = False


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


def ensure_sklearn_loaded() -> bool:
    global _sklearn_model, _sklearn_load_attempted
    with _lock:
        if _sklearn_load_attempted:
            return _sklearn_model is not None
        _sklearn_load_attempted = True
        try:
            _sklearn_model = _load_sklearn()
            if _sklearn_model is not None:
                logger.info("Sklearn fallback model loaded from %s", settings.ML_GUARD_SKLEARN_PATH)
                return True
        except Exception:
            logger.exception("Failed to load sklearn fallback model")
        return False


def _ensure_hf_loaded() -> object | None:
    global _pipeline, _hf_load_attempted
    with _lock:
        if _hf_load_attempted:
            return _pipeline
        _hf_load_attempted = True
        backend = settings.ML_GUARD_BACKEND.lower()
        if backend not in {"hf", "auto", "transformers"}:
            return None
        try:
            _pipeline = _load_hf_pipeline()
            logger.info("HF fallback model loaded: %s", settings.ML_GUARD_MODEL)
            return _pipeline
        except Exception:
            logger.exception("Failed to load HF model %s", settings.ML_GUARD_MODEL)
            return None


def _predict_sklearn(text: str) -> MLPrediction | None:
    if not ensure_sklearn_loaded() or _sklearn_model is None:
        return None
    proba = _sklearn_model.predict_proba([text])[0]
    classes = list(_sklearn_model.classes_)
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


def _predict_hf(text: str) -> MLPrediction | None:
    model = _ensure_hf_loaded()
    if model is None:
        return None
    raw = model(text)[0]
    injection_score, label = _score_from_hf_result(raw)
    return MLPrediction(
        enabled=True,
        loaded=True,
        backend="hf",
        model_name=settings.ML_GUARD_MODEL,
        injection_score=injection_score,
        label=label,
    )


def reload_model() -> bool:
    global _pipeline, _sklearn_model, _sklearn_load_attempted, _hf_load_attempted
    with _lock:
        _pipeline = None
        _sklearn_model = None
        _sklearn_load_attempted = False
        _hf_load_attempted = False
    return ensure_sklearn_loaded() or _ensure_hf_loaded() is not None or is_grok_configured()


def _should_try_grok() -> bool:
    backend = settings.ML_GUARD_BACKEND.lower()
    return backend in {"grok", "auto"} and is_grok_configured()


def _run_cascade(text: str) -> MLPrediction:
    if _should_try_grok():
        try:
            injection_score, label, error = classify_prompt(text)
            if error is None:
                return MLPrediction(
                    enabled=True,
                    loaded=True,
                    backend="grok",
                    model_name=settings.ML_GUARD_GROK_MODEL,
                    injection_score=injection_score,
                    label=label,
                )
            logger.warning("Grok classifier failed, falling back: %s", error)
        except Exception as exc:
            logger.warning("Grok classifier exception, falling back: %s", exc)

    sklearn_pred = _predict_sklearn(text)
    if sklearn_pred is not None:
        return MLPrediction(
            enabled=sklearn_pred.enabled,
            loaded=sklearn_pred.loaded,
            backend=sklearn_pred.backend,
            model_name=sklearn_pred.model_name,
            injection_score=sklearn_pred.injection_score,
            label=sklearn_pred.label,
            fallback_used=_should_try_grok(),
        )

    hf_pred = _predict_hf(text)
    if hf_pred is not None:
        return MLPrediction(
            enabled=hf_pred.enabled,
            loaded=hf_pred.loaded,
            backend=hf_pred.backend,
            model_name=hf_pred.model_name,
            injection_score=hf_pred.injection_score,
            label=hf_pred.label,
            fallback_used=True,
        )

    return MLPrediction(
        enabled=True,
        loaded=False,
        backend="none",
        model_name="",
        injection_score=0.0,
        label="benign",
        error="No ML backend available",
    )


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

    try:
        return _run_cascade(normalized)
    except Exception as exc:
        logger.exception("ML prediction failed")
        return MLPrediction(
            enabled=True,
            loaded=False,
            backend="error",
            model_name="",
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
    sklearn_ready = ensure_sklearn_loaded()
    hf_ready = _ensure_hf_loaded() is not None
    grok_ready = is_grok_configured()

    if grok_ready:
        primary_backend = "grok"
        primary_model = settings.ML_GUARD_GROK_MODEL
        block_threshold = settings.ML_GUARD_GROK_BLOCK_THRESHOLD
        warn_threshold = settings.ML_GUARD_GROK_WARN_THRESHOLD
    elif hf_ready:
        primary_backend = "hf"
        primary_model = settings.ML_GUARD_MODEL
        block_threshold = settings.ML_GUARD_BLOCK_THRESHOLD
        warn_threshold = settings.ML_GUARD_WARN_THRESHOLD
    elif sklearn_ready:
        primary_backend = "sklearn"
        primary_model = str(settings.ML_GUARD_SKLEARN_PATH.name)
        block_threshold = settings.ML_GUARD_SKLEARN_BLOCK_THRESHOLD
        warn_threshold = settings.ML_GUARD_WARN_THRESHOLD
    else:
        primary_backend = "none"
        primary_model = ""
        block_threshold = settings.ML_GUARD_BLOCK_THRESHOLD
        warn_threshold = settings.ML_GUARD_WARN_THRESHOLD

    return {
        "enabled": settings.ML_GUARD_ENABLED,
        "loaded": grok_ready or sklearn_ready or hf_ready,
        "backend": primary_backend if settings.ML_GUARD_ENABLED else "off",
        "model": primary_model,
        "grok_configured": grok_ready,
        "sklearn_loaded": sklearn_ready,
        "hf_loaded": hf_ready,
        "sklearn_path": str(settings.ML_GUARD_SKLEARN_PATH),
        "sklearn_exists": settings.ML_GUARD_SKLEARN_PATH.exists(),
        "block_threshold": block_threshold,
        "warn_threshold": warn_threshold,
        "rule_id": ML_RULE_ID,
    }