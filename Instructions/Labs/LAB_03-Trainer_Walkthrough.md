# Lab 03: Vector Search on Azure SQL — Trainer Walkthrough

> **Duration:** ~50 minutes
> **Goal:** Participants build a semantic search system using Azure SQL's native VECTOR type + Azure OpenAI embeddings. This becomes the retrieval layer for RAG.

---

## Pre-Lab Setup (Trainer — before session)

Verify these are working:

```
SQL Server:  sql-pepsiws-embmtykicepum.database.windows.net
Database:    vectordb
AOAI:        https://aif-workshop2026.cognitiveservices.azure.com
Embedding:   text-embedding-3-small
```

Firewall must be open for participant IPs (or use "Allow Azure services" + "0.0.0.0-255.255.255.255" for workshop day).

---

## Context-Setting (2 min — before lab starts)

> "Alright, in the previous session we talked about vector search and RAG at a conceptual level. Now you're going to BUILD it.
>
> Here's the scenario: PepsiCo has product descriptions — Gatorade, Lay's, Doritos, Quaker — and we want an AI agent to be able to search them by MEANING, not keywords.
>
> If a salesperson asks 'what's good for a hot summer workout?' — we want the system to find Gatorade products even though the word 'Gatorade' wasn't in the query.
>
> By end of this lab, you'll have that working. And tomorrow, this exact function becomes a tool that an AI agent can call."

---

## Task 1: Confirm Azure SQL is Ready (5 min)

### What it is
Participants verify the SQL server exists and they can connect via the Azure Portal query editor.

### What to say

> "First, let's confirm everyone can reach the database. Go to portal.azure.com, find resource group `pep-azr-aisp-msft-training-lab-sbx-eus-01-rg`, open the SQL server `sql-pepsiws-embmtykicepum`, then click into the database `vectordb`.
>
> Now click **Query editor (preview)** in the left nav. Sign in using **Microsoft Entra authentication** — that's your workshop login. No passwords needed."

### What to do

1. Navigate: Azure Portal → Resource Group → SQL server → `vectordb` database
2. Click **Query editor (preview)**
3. Sign in with **Microsoft Entra Single sign-on**
4. Run:

```sql
SELECT @@VERSION AS sql_version;
```

### Expected output
```
Microsoft SQL Azure (RTM) - 12.0.2000.8 ...
```

### What to explain

> "This is Azure SQL Database — the same SQL Server engine you know, running as a fully managed SaaS. What's new is it now has a native **VECTOR** data type. Not an extension, not a hack — a first-class column type. This was added in 2024 and is now GA."

### Troubleshooting
| Issue | Fix |
|-------|-----|
| "Client IP not allowed" | Add their IP in SQL server → Networking → Firewall |
| "Login failed" | Ensure Microsoft Entra admin is set on the SQL server |
| Query editor won't load | Try InPrivate browser, or use Azure Data Studio |

---

## Task 2: Create the Vector Table (5 min)

### What it is
Create a table with a `VECTOR(1536)` column alongside normal relational columns.

### What to say

> "Now let's create our table. Notice what's special here — the `embedding` column has type `VECTOR(1536)`. That 1536 is the dimensionality of OpenAI's text-embedding-3-small model. Every piece of text gets converted to a list of 1536 floating-point numbers.
>
> The beauty is: this lives right next to your normal columns — product_id, title, content. It's not a separate vector database — it's your existing SQL database with superpowers."

### What to do

Run in Query editor:

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

Then verify:

```sql
SELECT name, TYPE_NAME(system_type_id) as type 
FROM sys.columns
WHERE object_id = OBJECT_ID('dbo.product_docs');
```

### Expected output
```
doc_id      | int
product_id  | nvarchar
title       | nvarchar
content     | nvarchar
embedding   | vector
created_at  | datetime2
```

### What to explain

> "See that `vector` type in the output? That's the native type. Under the hood, it stores a fixed-length array of float32 values — very compact, very fast.
>
> Why 1536? Because that's what OpenAI's `text-embedding-3-small` outputs. If you used a different model (like Cohere with 1024 dimensions, or OpenAI's larger model with 3072), you'd change this number.
>
> The table otherwise looks completely normal. You can JOIN it, filter it, index it — all standard T-SQL."

---

## Task 3: Embed the Corpus and Load It (15 min)

### What it is
Run a Python script that:
1. Reads `product_descriptions.json` (17 PepsiCo products)
2. Calls Azure OpenAI to convert each product description → 1536-dimensional vector
3. Inserts into the SQL table

### What to say

> "Now we need to fill that table. We have 17 PepsiCo product descriptions — Gatorade varieties, Mountain Dew, Lay's, Doritos, Quaker Oats, Aquafina, etc. Each is a short paragraph describing the product.
>
> The Python script will:
> 1. Read each product description
> 2. Send it to Azure OpenAI's embedding model (text-embedding-3-small)
> 3. Get back 1536 numbers that represent the MEANING of that text
> 4. Insert those numbers as a VECTOR into our SQL table
>
> Let's set it up."

### What to do

**Step 1: Open terminal, navigate to lab03 folder**

```powershell
cd workshop\Allfiles\lab03
```

**Step 2: Create virtual environment and install dependencies**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --only-binary :all: -r requirements.txt
```

> "We're installing pyodbc for SQL connectivity, openai for the embedding API, and azure-identity for passwordless auth. The `--only-binary` flag avoids compilation issues on Windows."

**Step 3: Set environment variables**

```powershell
$env:AOAI_ENDPOINT="https://aif-workshop2026.cognitiveservices.azure.com"
$env:AOAI_EMBED_DEPLOYMENT="text-embedding-3-small"
$env:SQL_SERVER="sql-pepsiws-embmtykicepum.database.windows.net"
$env:SQL_DATABASE="vectordb"
```

> "No API keys anywhere! We're using `DefaultAzureCredential` — it automatically picks up your `az login` session. Passwordless, secure, no secrets in code."

**Step 4: Run the loader**

```bash
python embed_and_load.py product_descriptions.json
```

### Expected output
```
loaded 17 docs from product_descriptions.json
  inserted 16/17
  inserted 17/17
done. dbo.product_docs row count: 17
```

**Step 5: Verify in Query editor**

```sql
SELECT COUNT(*) AS row_count FROM dbo.product_docs;
SELECT TOP 5 doc_id, product_id, title FROM dbo.product_docs;
```

### What to explain (while it runs)

> "Let's look at what's happening under the hood. Open `product_descriptions.json` — each entry has a product_id, title, and content. The content is a short paragraph, maybe 2-3 sentences.
>
> The embedding model reads that text and outputs 1536 floating-point numbers. These numbers capture the MEANING — products about 'hydration' and 'sports' will have similar numbers. Products about 'snacks' and 'lunch' will cluster together differently.
>
> The INSERT statement uses a CAST: `CAST(CAST(? AS NVARCHAR(MAX)) AS VECTOR(1536))`. We're sending the embedding as a JSON array string, and SQL Server casts it to the native vector type."

### Show the actual data

> "Let's peek at what an embedding looks like:"

```sql
SELECT TOP 1 product_id, title, 
       LEFT(CAST(embedding AS NVARCHAR(MAX)), 100) AS embedding_preview
FROM dbo.product_docs;
```

> "See those numbers? That's the 'meaning' of 'Gatorade Frost' encoded as math. Humans can't read it, but math can compare it."

### Troubleshooting
| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: pyodbc` | Didn't activate venv. Run `.venv\Scripts\Activate.ps1` |
| ODBC Driver error | Install "Microsoft ODBC Driver 18 for SQL Server" from Microsoft |
| Throttling / 429 from AOAI | Wait 30s and retry. Script has built-in retry logic |
| `az login` expired | Run `az login` again in the terminal |
| Wrong database | Check `$env:SQL_DATABASE` is "vectordb" not "db_pepsi_rag" |

---

## Task 4: Run a Cosine Similarity Query (10 min)

### What it is
The "magic moment" — run a semantic search directly in T-SQL using `VECTOR_DISTANCE()`.

### What to say

> "THIS is the payoff. We now have product descriptions with their meaning encoded as vectors. Let's search by meaning.
>
> I'm going to find products similar to our first product (Gatorade Frost) without using any keywords. Pure math — cosine distance between vectors."

### What to do

**Demo 1: Find products similar to Gatorade Frost**

```sql
DECLARE @q VECTOR(1536) = (SELECT TOP 1 embedding FROM dbo.product_docs WHERE product_id = 'P001');

SELECT TOP 5
    product_id, title,
    VECTOR_DISTANCE('cosine', embedding, @q) AS distance
FROM dbo.product_docs
ORDER BY distance ASC;
```

### Expected output
```
P001  Gatorade Frost 28oz          0.0000  (identical - distance to itself)
P002  Gatorade Cool Blue 28oz      0.08xx  (very similar - same category)
P003  Gatorade Glacier Freeze      0.09xx  (very similar)
P004  Gatorade Zero Lemon-Lime     0.12xx  (similar - same brand, different variant)
P011  Aquafina 20oz                0.25xx  (somewhat similar - hydration category)
```

### What to explain

> "Look at the results!
>
> - Distance 0 = identical vector (Gatorade Frost compared to itself)
> - Distance ~0.08 = very similar (other Gatorade sports drinks)
> - Distance ~0.25 = somewhat related (Aquafina — hydration, but not sports)
> - Distance ~0.6+ = unrelated (snacks, oats)
>
> We didn't use any keywords, categories, or tags. The MATH figured out that Gatorade Frost, Cool Blue, and Glacier Freeze are semantically similar because their descriptions talk about similar concepts — electrolytes, athletes, hydration, sports.
>
> This is the power of vector search: **meaning-based retrieval**."

**Demo 2: Explain the distance function**

> "`VECTOR_DISTANCE` supports three metrics:
> - `'cosine'` — measures angle between vectors. Best for text embeddings (what we use)
> - `'euclidean'` — straight-line distance. Better for spatial data
> - `'dot'` — dot product. Used when vectors aren't normalized
>
> For OpenAI embeddings, always use cosine."

**Demo 3 (if time): Cross-category search in Query editor**

> "Now watch this — what if we compare a Gatorade with ALL products?"

```sql
DECLARE @q VECTOR(1536) = (SELECT TOP 1 embedding FROM dbo.product_docs WHERE product_id = 'P015');

SELECT TOP 5
    product_id, title,
    VECTOR_DISTANCE('cosine', embedding, @q) AS distance
FROM dbo.product_docs
ORDER BY distance ASC;
```

> "I searched from Lay's Classic. The nearest neighbors are Doritos and SunChips — the system knows they're all salty snacks even though the descriptions don't share many words!"

---

## Task 5: Wrap Retrieval as a Reusable Function (10 min)

### What it is
Run `retrieve_documents.py` — a Python function that takes a natural language query, embeds it, and searches. This is the exact function that becomes an MCP tool on Day 2.

### What to say

> "In Tasks 1-4 we manually embedded one document and compared it. In the real world, a USER types a question in English. We need to:
> 1. Take their question
> 2. Embed it (convert to vector)
> 3. Search the database for nearest documents
> 4. Return results
>
> That's what `retrieve_documents.py` does. And this exact function signature becomes the MCP tool contract for Day 2 — meaning an AI agent will be able to call `retrieve_documents('best summer drink', k=3)` over a standard protocol."

### What to do

**Run queries:**

```bash
python retrieve_documents.py "best electrolyte drink for hot days" --k 3
```

### Expected output
```
[0.5077]  P003      Gatorade Glacier Freeze 28oz
[0.5097]  P001      Gatorade Frost 28oz
[0.5404]  P002      Gatorade Cool Blue 28oz
```

**Try more queries:**

```bash
python retrieve_documents.py "low-sugar option" --k 3
```

```
[0.5125]  P004      Gatorade Zero Lemon-Lime
[0.6664]  P005      Mountain Dew Kickstart
[0.6738]  P024      Quaker Oats Old Fashioned
```

```bash
python retrieve_documents.py "snack for kids lunch box" --k 3
```

```
[0.5460]  P022      Quaker Chewy Granola Bar
[0.5759]  P019      SunChips Harvest Cheddar
[0.6151]  P015      Lay's Classic 2.625oz
```

### What to explain

> "Look at these results! 
>
> - 'best electrolyte drink for hot days' → found Gatorade products. None of the product descriptions contain the word 'hot days' — but the MEANING matches.
> - 'low-sugar option' → found Gatorade Zero (sugar-free) as #1. Perfect!
> - 'snack for kids lunch box' → found Quaker Chewy Granola Bar and SunChips. The system knows these are kid-friendly snacks.
>
> THIS is what makes RAG work. Your AI agent asks this function for context, gets back relevant product info, and uses it to generate a grounded answer.
>
> The function signature is simple:"

```python
def retrieve_documents(query: str, k: int = 5) -> list[dict]:
```

> "Takes a query string and a number k. Returns a list of dictionaries with product_id, title, content, and distance. That's the tool contract. Day 2's MCP server wraps this exact function."

### Key code walkthrough (show on screen)

> "Let me show you what's inside `retrieve_documents.py`:
>
> 1. **Lines 33-42**: `_sql()` — connects to Azure SQL using Entra token auth. No passwords.
> 2. **Lines 45-55**: `_embed()` — calls Azure OpenAI to convert text → vector
> 3. **Lines 58-85**: `retrieve_documents()` — the main function:
>    - Embeds the query
>    - Runs `VECTOR_DISTANCE` SQL query
>    - Returns top-k results as dictionaries
>
> That's 50 lines of code for a production-ready semantic search system. No Pinecone, no Weaviate, no vector database to manage. Just your existing SQL server."

---

## Task 6: Read-Along — Cosmos DB & PostgreSQL (3 min)

### What to say

> "Quick comparison. The same pattern works on two other Azure databases:
>
> **Cosmos DB** — use this when your data is already JSON documents, you need global distribution, or you want the vector co-located with the operational data. Query syntax: `VectorDistance(c.embedding, @q, false, { distanceFunction: 'cosine' })`
>
> **PostgreSQL with pgvector** — use this when your team already runs Postgres, or you want open-source. Query syntax: `embedding <=> $1::vector` (the `<=>` operator is cosine distance)
>
> All three give you the same result — semantic search. The choice depends on what database you already use and your scale/distribution requirements."

### Quick comparison table (say or show)

| | Azure SQL | Cosmos DB | PostgreSQL |
|--|-----------|-----------|------------|
| **Type** | `VECTOR(1536)` | JSON property | `vector(1536)` |
| **Query** | `VECTOR_DISTANCE()` | `VectorDistance()` | `<=>` operator |
| **Index** | Auto-optimized | DiskANN | IVFFlat/HNSW |
| **Best for** | Enterprise SQL shops | Global JSON apps | OSS/Postgres teams |

---

## Lab Wrap-Up (2 min)

### What to say

> "Let's recap what you just built:
>
> 1. ✅ A SQL table with a native `VECTOR(1536)` column
> 2. ✅ Embedded 17 PepsiCo product descriptions using Azure OpenAI
> 3. ✅ Ran semantic search — found relevant products by MEANING, not keywords
> 4. ✅ Built a reusable Python function with a clean API contract
>
> This is the **retrieval primitive** that every RAG system needs. In Day 2, we wrap this as an MCP tool, connect it to an AI agent, and the agent can answer questions like 'what drink should I stock for a summer outdoor event?' by calling YOUR function, getting YOUR product data, and generating a grounded answer.
>
> No hallucination. No guessing. Grounded in real data from your database.
>
> Questions before we move on?"

---

## Demo Script (if doing live demo instead of lab)

If participants don't have ODBC driver / Python setup, do this as a live walkthrough:

### Step 1: Show the data (Query editor)
```sql
SELECT product_id, title, content FROM dbo.product_docs ORDER BY product_id;
```
"17 PepsiCo products with descriptions."

### Step 2: Show an embedding
```sql
SELECT TOP 1 product_id, title, 
       LEFT(CAST(embedding AS NVARCHAR(MAX)), 200) AS vector_preview,
       LEN(CAST(embedding AS NVARCHAR(MAX))) AS vector_string_length
FROM dbo.product_docs;
```
"Each embedding is ~12,000 characters of numbers. That's 1536 floats."

### Step 3: Semantic search from Query editor
```sql
DECLARE @q VECTOR(1536) = (SELECT TOP 1 embedding FROM dbo.product_docs WHERE product_id = 'P001');

SELECT TOP 5
    product_id, title,
    VECTOR_DISTANCE('cosine', embedding, @q) AS distance
FROM dbo.product_docs
ORDER BY distance ASC;
```
"Gatorade Frost's nearest neighbors are other Gatorade products. The system KNOWS they're similar without us telling it."

### Step 4: Python demo (your machine)
```bash
python retrieve_documents.py "healthy breakfast option" --k 3
python retrieve_documents.py "party snack for teenagers" --k 3
python retrieve_documents.py "caffeine boost for morning shift" --k 3
```

"Each query takes <2 seconds: embed + search + return. Fast enough for real-time AI agent use."

---

## Common Questions & Answers

**Q: How fast is VECTOR_DISTANCE on large datasets?**
> "Azure SQL automatically creates internal indexes. For 100K-1M rows, queries return in <100ms. For 10M+, consider partitioning or Azure AI Search."

**Q: Why not just use Azure AI Search?**
> "AI Search is better when you need HYBRID search (keywords + vectors together), faceted filtering, or document-level ranking. Use SQL when vectors are part of a broader relational model and you need JOINs, transactions, and standard SQL tooling."

**Q: What does 1536 dimensions MEAN?**
> "Think of it as 1536 different aspects of meaning. Some dimensions might capture 'is this about food?', others 'is this about sports?', others more subtle concepts. The model learned these dimensions during training. We don't control them — we just use the output."

**Q: Can I update embeddings when product descriptions change?**
> "Yes — just re-embed the changed text and UPDATE the row. The vector column is mutable like any other column."

**Q: What about chunking long documents?**
> "For short text (product descriptions, paragraphs) — embed as-is. For long documents (policies, manuals) — chunk into 500-1000 token segments, one row per chunk. The retrieve function returns chunks, and the LLM assembles them."
