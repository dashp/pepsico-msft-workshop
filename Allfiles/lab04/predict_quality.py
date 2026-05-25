"""predict_quality - the Day 2 agent-tool contract.

Day 2 imports this module unchanged and exposes `predict_quality` as an MCP
tool. Do not change the function signature without coordinating with the
Day 2 MAF lab owner.

Usage (CLI):
    python predict_quality.py --emit-schema > predict_quality.schema.json
    python predict_quality.py --demo
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

FEATURE_ORDER = [
    "alcohol", "malic_acid", "ash", "alcalinity_of_ash", "magnesium",
    "total_phenols", "flavanoids", "nonflavanoid_phenols", "proanthocyanins",
    "color_intensity", "hue", "od280/od315_of_diluted_wines", "proline",
]


def _env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"environment variable {name} is required")
    return v


def predict_quality(features: dict) -> dict:
    """Call the AML managed online endpoint and return a normalized dict.

    Args:
        features: dict containing the 13 wine features (see FEATURE_ORDER).

    Returns:
        {"prediction": int, "probability": float}
    """
    missing = [f for f in FEATURE_ORDER if f not in features]
    if missing:
        raise ValueError(f"missing features: {missing}")

    uri = _env("AML_ENDPOINT_URI")
    key = _env("AML_ENDPOINT_KEY")

    body = json.dumps({"data": [features]}).encode("utf-8")
    req = urllib.request.Request(
        uri,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())

    return {
        "prediction": int(result["predictions"][0]),
        "probability": float(result.get("confidence", [None])[0] or 0.0),
    }


SCHEMA = {
    "name": "predict_quality",
    "description": "Predicts product-quality class (0,1,2) from 13 numeric "
                   "process telemetry features. Returns a prediction and a "
                   "probability between 0 and 1.",
    "parameters": {
        "type": "object",
        "properties": {f: {"type": "number"} for f in FEATURE_ORDER},
        "required": FEATURE_ORDER,
        "additionalProperties": False,
    },
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-schema", action="store_true",
                    help="Print the OpenAI function-calling JSON schema and exit.")
    ap.add_argument("--demo", action="store_true",
                    help="Call the endpoint with a fixed payload.")
    args = ap.parse_args()

    if args.emit_schema:
        print(json.dumps(SCHEMA, indent=2))
        return

    if args.demo:
        demo = {
            "alcohol": 13.5, "malic_acid": 1.8, "ash": 2.4,
            "alcalinity_of_ash": 18.5, "magnesium": 100.0,
            "total_phenols": 2.7, "flavanoids": 2.8,
            "nonflavanoid_phenols": 0.3, "proanthocyanins": 1.7,
            "color_intensity": 5.0, "hue": 1.0,
            "od280/od315_of_diluted_wines": 3.0, "proline": 1000.0,
        }
        print(predict_quality(demo))
        return

    ap.print_help()


if __name__ == "__main__":
    main()
