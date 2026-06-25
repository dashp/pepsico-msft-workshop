"""
=============================================================================
Embed product descriptions with Azure OpenAI and load into Azure SQL Database
=============================================================================

This script performs 3 key steps:
  1. Reads a JSON file of product descriptions (product_id, title, content)
  2. Sends each product's "content" to Azure OpenAI's embedding model,
     which returns a 1536-dimensional vector representing the MEANING of the text
  3. Inserts the original text + embedding vector into Azure SQL's native VECTOR column

Usage:
    python embed_and_load.py product_descriptions.json

Environment variables:
    AOAI_ENDPOINT          - Azure OpenAI endpoint URL
    AOAI_EMBED_DEPLOYMENT  - Deployment name (e.g. "text-embedding-3-small")
    SQL_SERVER             - Azure SQL server FQDN
    SQL_DATABASE           - Database name (default: "vectordb")

Authentication:
    Uses DefaultAzureCredential — no passwords or API keys needed.
    Just run `az login` first and the script picks up your session.
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

# This is a pyodbc constant for passing an Azure AD access token
# to SQL Server during connection — it replaces username/password auth
SQL_COPT_SS_ACCESS_TOKEN = 1256


# =============================================================================
# Helper Functions
# =============================================================================

def env(name: str, default: str | None = None) -> str:
    """Read an environment variable or exit with a clear error message."""
    val = os.environ.get(name, default)
    if not val:
        sys.exit(f"environment variable {name} is required")
    return val


def get_sql_connection() -> pyodbc.Connection:
    """
    Connect to Azure SQL Database using Entra ID (Azure AD) token auth.

    How it works:
    1. DefaultAzureCredential gets an access token for the SQL resource
    2. The token is encoded as UTF-16-LE bytes (required by ODBC driver)
    3. Packed into a struct with its length prefix (ODBC protocol requirement)
    4. Passed to pyodbc as a pre-connection attribute

    This means: NO passwords, NO connection strings with secrets.
    Your `az login` identity must be set as the SQL Server's Entra admin.
    """
    server = env("SQL_SERVER")
    database = env("SQL_DATABASE", "vectordb")

    # Get an access token for Azure SQL
    cred = DefaultAzureCredential()
    token = cred.get_token("https://database.windows.net/.default").token.encode("utf-16-le")

    # ODBC expects the token as: [4-byte length][token bytes]
    token_struct = struct.pack(f"<I{len(token)}s", len(token), token)

    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{server},1433;"
        f"Database={database};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})


def get_aoai_client() -> AzureOpenAI:
    """
    Create an Azure OpenAI client using Entra ID token auth.

    Instead of passing an API key, we provide a token_provider function
    that fetches a fresh token on each request. This is more secure
    because tokens expire and rotate automatically.
    """
    endpoint = env("AOAI_ENDPOINT")
    cred = DefaultAzureCredential()

    # This function is called by the SDK before each API request
    def token_provider() -> str:
        return cred.get_token("https://cognitiveservices.azure.com/.default").token

    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_version="2024-06-01",
        azure_ad_token_provider=token_provider,
    )


@retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=1, max=30))
def embed_batch(client: AzureOpenAI, deployment: str, texts: list[str]) -> list[list[float]]:
    """
    Send a batch of texts to the embedding model and get back vectors.

    Each text is converted to a 1536-dimensional vector (list of floats).
    The @retry decorator automatically retries on rate-limit (429) errors
    with exponential backoff — handles AOAI throttling gracefully.

    Example:
        texts = ["Gatorade is a sports drink", "Lay's are potato chips"]
        vectors = embed_batch(client, "text-embedding-3-small", texts)
        # vectors[0] = [0.023, -0.041, 0.089, ...] (1536 floats)
        # vectors[1] = [-0.012, 0.067, 0.003, ...] (1536 floats)
    """
    resp = client.embeddings.create(model=deployment, input=texts)
    return [item.embedding for item in resp.data]


def chunks(seq: list, n: int) -> Iterable[list]:
    """Split a list into batches of size n (last batch may be smaller)."""
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


# =============================================================================
# Main Script
# =============================================================================

def main() -> None:
    ap = argparse.ArgumentParser(description="Embed product docs and load into Azure SQL")
    ap.add_argument("source", type=Path, help="path to product_descriptions.json")
    ap.add_argument("--batch", type=int, default=16, help="docs per AOAI API call (default: 16)")
    args = ap.parse_args()

    # --- Step 1: Load product descriptions from JSON ---
    deployment = env("AOAI_EMBED_DEPLOYMENT", "text-embedding-3-small")
    docs = json.loads(args.source.read_text(encoding="utf-8"))
    if not docs:
        sys.exit("no docs in source file")
    print(f"loaded {len(docs)} docs from {args.source}")

    # --- Step 2: Initialize clients ---
    aoai = get_aoai_client()   # Azure OpenAI for embeddings
    conn = get_sql_connection() # Azure SQL for storage
    cur = conn.cursor()

    # Clear existing data — makes the script idempotent (safe to re-run)
    cur.execute("DELETE FROM dbo.product_docs")

    # --- Step 3: Embed and insert each batch ---
    # The INSERT uses a double CAST:
    #   CAST(? AS NVARCHAR(MAX))  — treat the JSON string as text
    #   CAST(... AS VECTOR(1536)) — parse the JSON array into native vector type
    # This is how you load vectors from application code into Azure SQL.
    insert_sql = (
        "INSERT INTO dbo.product_docs (product_id, title, content, embedding) "
        "VALUES (?, ?, ?, CAST(CAST(? AS NVARCHAR(MAX)) AS VECTOR(1536)))"
    )

    inserted = 0
    for batch in chunks(docs, args.batch):
        # Extract the text content from each document
        texts = [d["content"] for d in batch]

        # Call Azure OpenAI — converts text → vectors
        # "Gatorade Frost is a thirst quencher..." → [0.023, -0.041, ...] (1536 numbers)
        vectors = embed_batch(aoai, deployment, texts)

        # Prepare rows for SQL insertion
        rows = []
        for doc, vec in zip(batch, vectors):
            pid = doc.get("product_id") or doc.get("policy_id") or "UNKNOWN"
            rows.append((
                pid,
                doc["title"],
                doc["content"],
                json.dumps(vec),  # Convert Python list → JSON string for SQL CAST
            ))

        # Bulk insert this batch and commit
        cur.executemany(insert_sql, rows)
        conn.commit()
        inserted += len(rows)
        print(f"  inserted {inserted}/{len(docs)}")

    # --- Step 4: Verify final row count ---
    cur.execute("SELECT COUNT(*) FROM dbo.product_docs")
    total, = cur.fetchone()
    print(f"done. dbo.product_docs row count: {total}")


if __name__ == "__main__":
    main()
