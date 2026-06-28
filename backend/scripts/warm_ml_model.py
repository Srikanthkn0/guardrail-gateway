#!/usr/bin/env python3
"""Pre-download HF classifier during deploy build."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.services.ml_classifier import reload_model


def main() -> int:
    if not settings.ML_GUARD_ENABLED:
        print("ML_GUARD_ENABLED=false — skip warm")
        return 0
    if settings.ML_GUARD_BACKEND.lower() == "sklearn":
        print("ML_GUARD_BACKEND=sklearn — skip HF warm")
        return 0

    ok = reload_model()
    if not ok:
        print("HF model warm failed — sklearn fallback may apply at runtime", file=sys.stderr)
        return 0
    print(f"HF model ready: {settings.ML_GUARD_MODEL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())