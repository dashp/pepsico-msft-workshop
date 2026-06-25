# Lab 03: Vector Search on Azure SQL

## Lab introduction

In this lab you learn to build a **retrieval tool over Azure SQL Database** using the new native **`VECTOR`** data type. You will create a vector table, embed a small corpus of product descriptions with **Azure OpenAI**, load the embeddings, run a **cosine similarity** search, and wrap the retrieval as a reusable Python function that Day 2 will expose through an MCP server.

You will also briefly review the same pattern on **Azure Cosmos DB for NoSQL** and **Azure Database for PostgreSQL (pgvector)**. Those alternatives are read-along only — no provisioning in this lab.

This lab requires an Azure subscription. The steps are written using **Sweden Central**.

## Prerequisites — verify before you start

- [ ] You can sign in to `https://portal.azure.com` with your workshop account.
- [ ] **Python 3.10+** is installed on your workstation (`python --version`).
- [ ] **Microsoft ODBC Driver 18 for SQL Server** is installed. Download from: https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server — choose the installer for your OS/architecture.
- [ ] You can reach `sql-pepsiws-embmtykicepum.database.windows.net` from your network (port 1433 outbound).

## Estimated timing: 50 minutes

## Lab scenario

Your downstream agents need to ground their answers on product narratives and policy documents stored in Azure SQL. You will build the retrieval primitive end-to-end: data, embeddings, index, query, function. Day 2 wraps the function as an **MCP server** so any agent can call `retrieve_documents(query, k)` over a standard protocol.

## Architecture diagram


## Job skills

- Task 1: Confirm the Bicep deployment provisioned Azure SQL with `VECTOR` support.
- Task 2: Create a vector table and a covering schema.
- Task 3: Embed a small corpus with Azure OpenAI and load it.
- Task 4: Run a cosine similarity query.
- Task 5: Wrap retrieval as a reusable Python function.
- Task 6 (read-along): The same pattern on Cosmos DB and PostgreSQL.

---

## Task 1: Confirm Azure SQL is ready

In this task, you will verify the SQL server and database that the workshop's Bicep template provisioned for you.

1. Sign in to the Azure portal — `https://portal.azure.com`.

2. Navigate to your resource group `pep-azr-aisp-msft-training-lab-sbx-eus-01-rg`, open the SQL server `sql-pepsiws-embmtykicepum`, then the database `vectordb`.

3. Confirm:
    - **Pricing tier**: General Purpose serverless (or workshop default).
    - **Microsoft Entra admin**: set to your workshop login (or the team lead).
    - **Networking → Public access**: **Selected networks**, with your client IP allowed.


4. In the database's **Query editor (preview)**, sign in with **Microsoft Entra Single sign-on**, then run:

    ```sql
    SELECT @@VERSION AS sql_version;
    ```

    > **Note**: If you see a "VECTOR type not supported" error in a later step, your database is on a region/SKU where `VECTOR` is not yet rolled out. Ask the trainer for a workaround.

---

## Task 2: Create the vector table

1. Still in the **Query editor**, run:

    ```sql
    IF OBJECT_ID('dbo.product_docs', 'U') IS NOT NULL DROP TABLE dbo.product_docs;

    CREATE TABLE dbo.product_docs (
        doc_id      INT IDENTITY PRIMARY KEY,
        product_id  NVARCHAR(50)     NOT NULL,
        title       NVARCHAR(200)    NOT NULL,
        content     NVARCHAR(MAX)    NOT NULL,
        embedding   VECTOR(1536)     NOT NULL,
        created_at  DATETIME2        DEFAULT SYSUTCDATETIME()
    );
    ```

2. Confirm the table was created:

    ```sql
    SELECT name FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.product_docs');
    ```


---

## Task 3: Embed the corpus and load it

In this task, you will run a Python script that reads `product_descriptions.json`, calls **Azure OpenAI** to embed each document, and inserts rows into `dbo.product_docs`.

1. On your workstation, open a terminal in the cloned workshop repo and create a virtual env:

    **Windows (PowerShell):**
    ```powershell
    cd workshop\Allfiles\lab03
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install --only-binary :all: -r requirements.txt
    ```

    **macOS / Linux (Bash):**
    ```bash
    cd workshop/Allfiles/lab03
    python -m venv .venv
    source .venv/bin/activate
    pip install --only-binary :all: -r requirements.txt
    ```

    > **Tip**: The `--only-binary :all:` flag avoids compiling native extensions from source. If you see a build error about `link.exe` or `cryptography`, you are missing this flag.

2. Set the workshop environment variables. Authentication uses your interactive Microsoft Entra session via `DefaultAzureCredential` — no passwords are stored.

    **PowerShell (Windows):**
    ```powershell
    $env:AOAI_ENDPOINT="https://aif-workshop2026.cognitiveservices.azure.com"
    $env:AOAI_EMBED_DEPLOYMENT="text-embedding-3-small"
    $env:SQL_SERVER="sql-pepsiws-embmtykicepum.database.windows.net"
    $env:SQL_DATABASE="vectordb"
    ```

    **Bash (macOS / Linux):**
    ```bash
    export AOAI_ENDPOINT="https://aif-workshop2026.cognitiveservices.azure.com"
    export AOAI_EMBED_DEPLOYMENT="text-embedding-3-small"
    export SQL_SERVER="sql-pepsiws-embmtykicepum.database.windows.net"
    export SQL_DATABASE="vectordb"
    ```

3. Run the loader:

    ```bash
    python embed_and_load.py product_descriptions.json
    ```

4. Confirm rows were inserted:

    ```sql
    SELECT COUNT(*) AS row_count FROM dbo.product_docs;
    SELECT TOP 3 doc_id, product_id, title FROM dbo.product_docs;
    ```


---

## Task 4: Run a cosine similarity query

1. In the **Query editor**, run a similarity search that compares the first document's embedding against all others. This verifies `VECTOR_DISTANCE` works on your database.

    ```sql
    DECLARE @q VECTOR(1536) = (SELECT TOP 1 embedding FROM dbo.product_docs WHERE product_id = 'P001');

    SELECT TOP 5
        product_id, title,
        VECTOR_DISTANCE('cosine', embedding, @q) AS distance
    FROM dbo.product_docs
    ORDER BY distance ASC;
    ```

    You should see `P001` at distance 0 (identical vector) and similar products nearby.

2. The function `VECTOR_DISTANCE` also supports `'euclidean'` and `'dot'`. For embeddings produced by Azure OpenAI, `'cosine'` is correct.

3. In **Task 5** you will use the Python script `retrieve_documents.py` which embeds a free-text query and runs the same pattern end-to-end.

---

## Task 5: Wrap retrieval as a reusable function

In this task, you will use the helper script `retrieve_documents.py`. Day 2 wraps this exact function as an MCP tool — the function signature is the contract.

1. From `workshop/Allfiles/lab03`, run:

    ```bash
    python retrieve_documents.py "best electrolyte drink for hot days" --k 3
    ```

2. The script prints the top-k matches with `product_id`, `title`, and `distance`. Confirm the results look sensible.


3. Try two more queries:

    ```bash
    python retrieve_documents.py "low-sugar option" --k 3
    python retrieve_documents.py "what is our return policy" --k 3
    ```

4. Open `retrieve_documents.py` and locate the function signature:

    ```python
    def retrieve_documents(query: str, k: int = 5) -> list[dict]:
        ...
    ```

    This is the **tool contract** for Day 2. Day 2 imports this function unchanged and exposes it as an MCP tool named `retrieve_documents`.

---

## Task 6 (read-along): The same pattern on Cosmos DB and PostgreSQL

The Azure SQL pattern you just built has direct equivalents on two other Microsoft data services. You will **not** provision either in this lab — review the snippets so you know when to pick each.

### Azure Cosmos DB for NoSQL (vector index)

- Vector index is configured on a container at creation.
- Items are JSON; the embedding lives on a property like `/embedding`.
- Query uses `VectorDistance(c.embedding, @q, false, { distanceFunction: 'cosine' })` in SQL API.

```sql
SELECT TOP 5
    c.id, c.title, VectorDistance(c.embedding, @q, false,
        { distanceFunction: 'cosine' }) AS distance
FROM c
ORDER BY VectorDistance(c.embedding, @q, false,
        { distanceFunction: 'cosine' })
```

**Pick Cosmos when:** the data is already JSON, you need global distribution, or you co-locate vectors with the operational document (one item = one chunk + metadata).

### Azure Database for PostgreSQL — pgvector

- Enable the `vector` extension once: `CREATE EXTENSION vector;`
- Column type: `embedding vector(1536)`.
- Index: `CREATE INDEX ON product_docs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);`
- Query:

```sql
SELECT product_id, title, embedding <=> $1::vector AS distance
FROM product_docs
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

**Pick PostgreSQL when:** the team already runs Postgres, you need rich SQL joins between vectors and relational data, or you prefer open-source tooling.

---

## Review

In this lab you built the retrieval primitive your Day 2 agents will depend on: a `VECTOR` column in Azure SQL, an embedded corpus loaded with Azure OpenAI, a cosine search, and a clean Python contract. You also know when to switch to Cosmos DB or pgvector without re-learning the pattern.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Invalid object name 'dbo.product_docs'` | Wrong database selected in Query editor | Switch the database dropdown to `vectordb` |
| `Login failed for user '<token>'` | Entra admin not set | Azure SQL server → **Microsoft Entra ID** → set admin |
| `VECTOR_DISTANCE` unknown function | Region/SKU on older SQL build | Ask the trainer for the shared fallback DB |
| `embed_and_load.py` throttles | AOAI rate limit | Retry with `--rate 5`; the script auto-batches |
| `pyodbc` driver missing | ODBC Driver 18 not installed | Install **Microsoft ODBC Driver 18 for SQL Server** for your OS |

## Further reading

- [Azure SQL Database — Vector data type](https://learn.microsoft.com/sql/relational-databases/vectors/vectors-sql-server)
- [Azure Cosmos DB — Vector search](https://learn.microsoft.com/azure/cosmos-db/nosql/vector-search)
- [Azure Database for PostgreSQL — pgvector](https://learn.microsoft.com/azure/postgresql/flexible-server/how-to-use-pgvector)
- [Azure OpenAI embeddings — `text-embedding-3-*`](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#embeddings-models)
