"""Scoring script invoked by Azure ML's managed online endpoint."""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import joblib
import numpy as np

_model = None

FEATURE_ORDER = [
    "alcohol", "malic_acid", "ash", "alcalinity_of_ash", "magnesium",
    "total_phenols", "flavanoids", "nonflavanoid_phenols", "proanthocyanins",
    "color_intensity", "hue", "od280/od315_of_diluted_wines", "proline",
]


def init() -> None:
    global _model
    path = os.path.join(os.getenv("AZUREML_MODEL_DIR", "."), "model.joblib")
    _model = joblib.load(path)
    logging.info("model loaded from %s", path)


def run(raw_data: str | bytes) -> dict[str, Any]:
    """raw_data is a JSON payload like {"data": [{"alcohol": ..., ...}, ...]}"""
    payload = json.loads(raw_data) if isinstance(raw_data, (str, bytes)) else raw_data
    rows = payload.get("data") or payload.get("inputs") or []
    if not rows:
        return {"error": "no rows in 'data'"}

    X = np.array([[r[f] for f in FEATURE_ORDER] for r in rows], dtype=float)
    preds = _model.predict(X).tolist()

    if hasattr(_model, "predict_proba"):
        probas = _model.predict_proba(X)
        confidence = probas.max(axis=1).tolist()
    else:
        confidence = [None] * len(preds)

    return {"predictions": preds, "confidence": confidence}
