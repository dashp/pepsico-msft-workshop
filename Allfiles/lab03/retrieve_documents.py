"""
=============================================================================
Retrieve documents from Azure SQL using vector similarity search
=============================================================================

This is the RETRIEVAL function for RAG (Retrieval-Augmented Generation).

How it works:
  1. User asks a natural language question (e.g., "best drink for hot workout")
  2. The question gets embedded into a 1536-dimensional vector using Azure OpenAI
  3. We search Azure SQL for the documents with the CLOSEST vectors (cosine distance)
  4. Return the top-k most semantically similar documents

The function signature `retrieve_documents(query, k)` is the "tool contract" —
Day 2 wraps this exact function as an MCP tool so any AI agent can call it.

Usage (CLI for testing):
    python retrieve_documents.py "best electrolyte drink for hot days" --k 3
    python retrieve_documents.py "low-sugar option" --k 3
    python retrieve_documents.py "snack for kids lunch box" --k 3

Environment variables:
    AOAI_ENDPOINT          - Azure OpenAI endpoint URL
    AOAI_EMBED_DEPLOYMENT  - Deployment name (default: "text-embedding-3-small")
    SQL_SERVER             - Azure SQL server FQDN
    SQL_DATABASE           - Database name (default: "vectordb")
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

# pyodbc constant for Azure AD token-based authentication
SQL_COPT_SS_ACCESS_TOKEN = 1256


# =============================================================================
# Helper Functions
# =============================================================================

def env(name: str, default: str | None = None) -> str:
    """Read an environment variable or exit with a clear error."""
    val = os.environ.get(name, default)
    if not val:
        sys.exit(f"environment variable {name} is required")
    return val


def _sql() -> pyodbc.Connection:
    """
    Connect to Azure SQL using Entra ID (passwordless auth).
    Same pattern as embed_and_load.py — token-based, no secrets.
    """
    cred = DefaultAzureCredential()
    token = cred.get_token("https://database.windows.net/.default").token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token)}s", len(token), token)
    return pyodbc.connect(
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{env('SQL_SERVER')},1433;"
        f"Database={env('SQL_DATABASE', 'vectordb')};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;",
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct},
    )


def _embed(text: str) -> list[float]:
    """
    Convert a text string into a 1536-dimensional embedding vector.

    This is the same embedding model used in embed_and_load.py.
    Because we use the SAME model for loading AND querying,
    similar texts produce similar vectors — which is what makes
    cosine distance meaningful.

    Example:
        _embed("sports drink for athletes")
        # → [0.023, -0.041, 0.089, ...] (1536 floats)
    """
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


# =============================================================================
# Main Retrieval Function — THIS IS THE MCP TOOL CONTRACT
# =============================================================================

def retrieve_documents(query: str, k: int = 5) -> list[dict[str, Any]]:
    """
    Return the top-k documents nearest to `query` by cosine distance.

    This is the function that Day 2's MCP server exposes as a tool.
    An AI agent calls: retrieve_documents("best summer drink", k=3)
    and gets back the most relevant product documents.

    The flow:
      1. Embed the user's query → 1536-dim vector
      2. Use VECTOR_DISTANCE('cosine', ...) in SQL to compare against all docs
      3. ORDER BY distance ASC (smallest distance = most similar)
      4. Return top-k results as a list of dictionaries

    Args:
        query: Natural language question (e.g., "best drink for hot workout")
        k: Number of results to return (default 5)

    Returns:
        List of dicts, each with: product_id, title, content, distance
        Sorted by distance ascending (most relevant first)
    """
    if not query.strip():
        return []

    # Step 1: Convert the user's query into a vector
    # "best drink for hot workout" → [0.023, -0.041, ...] (1536 numbers)
    q_vec = _embed(query)

    # Step 2: Search Azure SQL using cosine distance
    with _sql() as conn, conn.cursor() as cur:
        cur.execute(
            """
            -- Declare the query vector (cast JSON array string → native VECTOR type)
            DECLARE @q VECTOR(1536) = CAST(CAST(? AS NVARCHAR(MAX)) AS VECTOR(1536));

            -- Find the top-k documents with smallest cosine distance to the query
            -- Cosine distance: 0 = identical, 1 = orthogonal, 2 = opposite
            -- Typical "good" matches are 0.3-0.6 for text embeddings
            SELECT TOP (?)
                product_id,
                title,
                content,
                VECTOR_DISTANCE('cosine', embedding, @q) AS distance
            FROM dbo.product_docs
            ORDER BY distance ASC;
            """,
            json.dumps(q_vec),  # Pass the embedding as a JSON array string
            int(k),
        )

        # Step 3: Convert SQL rows into Python dictionaries
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


# =============================================================================
# CLI Entry Point (for testing — not used by MCP server)
# =============================================================================

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Semantic search over PepsiCo product documents"
    )
    ap.add_argument("query", help="Natural language search query")
    ap.add_argument("--k", type=int, default=5, help="Number of results (default: 5)")
    ap.add_argument("--print-embedding", action="store_true",
                    help="Print the raw embedding vector and exit (for debugging)")
    args = ap.parse_args()

    # Debug mode: just print the embedding vector
    if args.print_embedding:
        print(json.dumps(_embed(args.query)))
        return

    # Run the search and display results
    results = retrieve_documents(args.query, k=args.k)
    if not results:
        print("No results found.")
        return

    print(f"\nQuery: \"{args.query}\" (top {args.k} results)")
    print("-" * 60)
    for r in results:
        # Lower distance = more similar (0 = perfect match)
        print(f"[{r['distance']:.4f}]  {r['product_id']:8s}  {r['title']}")


if __name__ == "__main__":
    main()
