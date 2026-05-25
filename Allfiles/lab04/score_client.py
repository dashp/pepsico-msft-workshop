"""Standalone client to score the managed online endpoint from a laptop."""
from __future__ import annotations

import json
import os
import sys
import urllib.request


def main() -> None:
    uri = os.environ.get("AML_ENDPOINT_URI")
    key = os.environ.get("AML_ENDPOINT_KEY")
    if not uri or not key:
        sys.exit("set AML_ENDPOINT_URI and AML_ENDPOINT_KEY environment variables")

    with open("sample_request.json", "rb") as f:
        body = f.read()

    req = urllib.request.Request(
        uri, data=body, method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(json.loads(resp.read()))


if __name__ == "__main__":
    main()
