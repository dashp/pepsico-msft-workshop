"""Query the Azure SQL vector table with cosine similarity.

This module exposes a single function `retrieve_documents(query, k)` that
Day 2 will wrap as an MCP tool. The CLI is just for smoke testing.

Usage:
    python retrieve_documents.py "best electrolyte drink for hot days" --k 3
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from typing import Any

import pyodbc
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

SQL_COPT_SS_ACCESS_TOKEN = 1256


def env(name: str, default: str | None = None) -> str:
    val = os.environ.get(name, default)
    if not val:
        sys.exit(f"environment variable {name} is required")
    return val


def _sql() -> pyodbc.Connection:
    cred = DefaultAzureCredential()
    token = cred.get_token("https://database.windows.net/.default").token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token)}s", len(token), token)
    return pyodbc.connect(
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{env('SQL_SERVER')},1433;"
        f"Database={env('SQL_DATABASE', 'db_pepsi_rag')};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;",
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct},
    )


def _embed(text: str) -> list[float]:
    cred = DefaultAzureCredential()
    client = AzureOpenAI(
        azure_endpoint=env("AOAI_ENDPOINT"),
        api_version="2024-06-01",
        azure_ad_token_provider=lambda: cred.get_token(
            "https://cognitiveservices.azure.com/.default"
        ).token,
    )
    deployment = env("AOAI_EMBED_DEPLOYMENT", "text-embedding-3-small")
    return client.embeddings.create(model=deployment, input=text).data[0].embedding


def retrieve_documents(query: str, k: int = 5) -> list[dict[str, Any]]:
    """Return the top-k documents nearest to `query` by cosine distance.

    This is the Day 2 tool contract. Do not change the signature without
    coordinating with the Day 2 MCP server lab.
    """
    if not query.strip():
        return []
    q_vec = _embed(query)

    with _sql() as conn, conn.cursor() as cur:
        cur.execute(
            """
            DECLARE @q VECTOR(1536) = CAST(CAST(? AS NVARCHAR(MAX)) AS VECTOR(1536));

            SELECT TOP (?)
                product_id,
                title,
                content,
                VECTOR_DISTANCE('cosine', embedding, @q) AS distance
            FROM dbo.product_docs
            ORDER BY distance ASC;
            """,
            json.dumps(q_vec),
            int(k),
        )
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--print-embedding", action="store_true",
                    help="Print the JSON embedding for the query and exit.")
    args = ap.parse_args()

    if args.print_embedding:
        print(json.dumps(_embed(args.query)))
        return

    results = retrieve_documents(args.query, k=args.k)
    for r in results:
        print(f"[{r['distance']:.4f}]  {r['product_id']:8s}  {r['title']}")


if __name__ == "__main__":
    main()
