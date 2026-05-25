"""Embed product_descriptions.json with Azure OpenAI and load into Azure SQL.

Usage:
    python embed_and_load.py product_descriptions.json

Environment variables (read from process env or .env in the same folder):
    AOAI_ENDPOINT             https://aoai-pepsi-shared.openai.azure.com
    AOAI_EMBED_DEPLOYMENT     text-embedding-3-small
    SQL_SERVER                sql-pepsi-ws-team01.database.windows.net
    SQL_DATABASE              db_pepsi_rag

Authentication uses DefaultAzureCredential (your interactive `az login`).
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from pathlib import Path
from typing import Iterable

import pyodbc
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

SQL_COPT_SS_ACCESS_TOKEN = 1256  # pyodbc magic number for AAD token


# ---------- helpers ----------------------------------------------------------

def env(name: str, default: str | None = None) -> str:
    val = os.environ.get(name, default)
    if not val:
        sys.exit(f"environment variable {name} is required")
    return val


def get_sql_connection() -> pyodbc.Connection:
    server = env("SQL_SERVER")
    database = env("SQL_DATABASE", "db_pepsi_rag")
    cred = DefaultAzureCredential()
    token = cred.get_token("https://database.windows.net/.default").token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token)}s", len(token), token)

    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{server},1433;"
        f"Database={database};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})


def get_aoai_client() -> AzureOpenAI:
    endpoint = env("AOAI_ENDPOINT")
    cred = DefaultAzureCredential()

    def token_provider() -> str:
        return cred.get_token("https://cognitiveservices.azure.com/.default").token

    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_version="2024-06-01",
        azure_ad_token_provider=token_provider,
    )


@retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=1, max=30))
def embed_batch(client: AzureOpenAI, deployment: str, texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=deployment, input=texts)
    return [item.embedding for item in resp.data]


def chunks(seq: list, n: int) -> Iterable[list]:
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


# ---------- main -------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path, help="path to product_descriptions.json")
    ap.add_argument("--batch", type=int, default=16, help="docs per AOAI call")
    args = ap.parse_args()

    deployment = env("AOAI_EMBED_DEPLOYMENT", "text-embedding-3-small")
    docs = json.loads(args.source.read_text(encoding="utf-8"))
    if not docs:
        sys.exit("no docs in source file")

    print(f"loaded {len(docs)} docs from {args.source}")

    aoai = get_aoai_client()
    conn = get_sql_connection()
    cur = conn.cursor()

    # Reset table contents to keep loads idempotent for the workshop.
    cur.execute("DELETE FROM dbo.product_docs")

    insert_sql = (
        "INSERT INTO dbo.product_docs (product_id, title, content, embedding) "
        "VALUES (?, ?, ?, CAST(? AS VECTOR(1536)))"
    )

    inserted = 0
    for batch in chunks(docs, args.batch):
        texts = [d["content"] for d in batch]
        vectors = embed_batch(aoai, deployment, texts)
        rows = []
        for doc, vec in zip(batch, vectors):
            pid = doc.get("product_id") or doc.get("policy_id") or "UNKNOWN"
            rows.append((
                pid,
                doc["title"],
                doc["content"],
                json.dumps(vec),  # SQL CASTs the JSON array to VECTOR
            ))
        cur.executemany(insert_sql, rows)
        conn.commit()
        inserted += len(rows)
        print(f"  inserted {inserted}/{len(docs)}")

    cur.execute("SELECT COUNT(*) FROM dbo.product_docs")
    total, = cur.fetchone()
    print(f"done. dbo.product_docs row count: {total}")


if __name__ == "__main__":
    main()
