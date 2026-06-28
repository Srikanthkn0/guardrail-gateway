#!/usr/bin/env python3
"""Train sklearn fallback classifier for environments without torch."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from app.services.ml_training_data import BENIGN, UNSAFE

OUT = BACKEND / "app" / "data" / "models" / "injection_classifier.joblib"


def main() -> int:
    texts = list(BENIGN) + list(UNSAFE)
    labels = [0] * len(BENIGN) + [1] * len(UNSAFE)
    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    model = Pipeline(
        [
            (
                "features",
                FeatureUnion(
                    [
                        (
                            "word",
                            TfidfVectorizer(
                                ngram_range=(1, 2),
                                max_features=8000,
                                sublinear_tf=True,
                            ),
                        ),
                        (
                            "char",
                            TfidfVectorizer(
                                analyzer="char_wb",
                                ngram_range=(3, 5),
                                max_features=8000,
                                sublinear_tf=True,
                            ),
                        ),
                    ]
                ),
            ),
            (
                "clf",
                LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
            ),
        ]
    )
    model.fit(x_train, y_train)
    accuracy = model.score(x_test, y_test)
    print(f"sklearn accuracy: {accuracy:.2%}")

    import joblib

    OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUT)
    print(f"saved {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())