# Demonstration 01: Microsoft Purview + OneLake Catalog

## Demonstration introduction

In this **instructor-led demonstration**, you observe how **Microsoft Purview** governs Azure data services (SQL, Cosmos DB) and how **OneLake Catalog** (built into Fabric) provides lineage and discovery for Fabric-native assets.

There are no per-attendee steps — follow along on the instructor's screen.

## Estimated timing: 20 minutes

## Demonstration scenario

By the end of Labs 01–03, you have created:

- A Fabric Lakehouse `lh_pepsi_pradipta` with `bronze_*`, `silver_*`, and `gold_sales` tables.
- A semantic model `sm_pepsi_sales` and a Power BI report `rpt_pepsi_sales_overview`.
- An Eventhouse `eh_pepsi_rti` with a streaming `bikes_new` table.
- Azure SQL `vectordb` with `dbo.product_docs` (vector embeddings from Lab 03).

This demo shows how a central governance team sees all of these assets — Purview for Azure services, OneLake Catalog for Fabric.

## What the instructor will show

- Section 1: Purview — Azure SQL scanned, assets discovered.
- Section 2: Purview — Browse `dbo.product_docs`, column-level metadata & classifications.
- Section 3: OneLake Catalog — Fabric assets, lineage, endorsement.
- Section 4: Governance story — how Purview + OneLake Catalog complement each other.

---

## Section 1: Purview Data Map — Azure SQL

1. Open the **Microsoft Purview governance portal** — `https://web.purview.azure.com`.

2. Navigate to the Purview account **pv-pepsiws-embmtykicepum**.

3. In the left pane, select **Data map → Sources**. Show the registered sources:

    | Source | Type | Status |
    |---|---|---|
    | `sql-pepsiws-vectordb` | Azure SQL Database | Scanned ✓ |
    | `cosmos-workshop2026` | Azure Cosmos DB | Registered |

4. Click on **sql-pepsiws-vectordb** and show:
    - The scan `scan-vectordb` ran successfully.
    - Assets discovered: `vectordb` database, `dbo.product_docs` table, columns.

5. **Talking point**: "One API call registers a source, one API call triggers a scan. The MSI handles auth — no passwords stored."

---

## Section 2: Purview — Browse `dbo.product_docs`

1. In the **Data catalog**, search for `product_docs`.

2. Open the asset and point out:
    - **Schema tab**: columns `doc_id`, `product_id`, `title`, `content`, `embedding` (VECTOR type), `created_at`.
    - **Classification**: Purview auto-classified `content` as potential free-text (if detected).
    - **Lineage tab**: shows the SQL Database as the source.

3. **Talking points**:
    - "Purview discovers the VECTOR column — this is new. Your governance team sees that embeddings are stored here."
    - "Column-level visibility is critical for RAG architectures — you need to know WHERE embeddings live and WHAT data they encode."
    - "This is the same `product_docs` table your Lab 03 Python script queries. Governance covers the retrieval layer."

---

## Section 3: OneLake Catalog — Fabric Assets

1. Switch to the **Fabric portal** — `https://app.fabric.microsoft.com`.

2. In the left navigation, click **OneLake catalog** (or **OneLake data hub** depending on version).

3. Search for `lh_pepsi_pradipta`. Show:
    - The Lakehouse appears with all its tables (bronze_*, silver_*, gold_sales).
    - Click on `gold_sales` — see schema, preview data.
    - Show the **Lineage view**: Files/raw → bronze → silver → gold → semantic model → report.

4. Search for `sm_pepsi_sales`. Show:
    - The semantic model is linked to the Lakehouse (upstream) and the report (downstream).
    - Endorsement status (if any).

5. Search for `eh_pepsi_rti`. Show:
    - The Eventhouse with `bikes_new` table from the Eventstream.

6. **Talking points**:
    - "OneLake Catalog is built INTO Fabric — zero setup, automatic discovery."
    - "It shows lineage that Purview cannot see: notebook transformations, Eventstream flows."
    - "For Fabric-native assets, this is your first stop. For cross-platform (SQL, Cosmos, Blob), use Purview."

---

## Section 4: The Governance Story

1. Show this side-by-side mental model:

    | Capability | Microsoft Purview | OneLake Catalog |
    |---|---|---|
    | **Scope** | Azure-wide (SQL, Cosmos, Blob, Fabric*) | Fabric-only |
    | **Lineage** | Cross-system (SQL → Fabric → Power BI) | In-Fabric (notebook → table → model) |
    | **Classification** | Auto + custom (PII, financial, etc.) | Basic metadata |
    | **Sensitivity labels** | Yes — propagates across assets | Inherits from Purview |
    | **DLP policies** | Yes — blocks sensitive data in exports/agents | No |
    | **Setup** | Register + scan | Zero (automatic) |

    *\*Purview scanning Fabric requires Fabric Admin tenant settings enabled.*

2. **Talking points**:
    - "You need BOTH. Purview is the enterprise map. OneLake Catalog is the Fabric speedometer."
    - "Sensitivity labels travel with the data — into Power BI exports AND into your agents."
    - "For agentic workloads (Day 2): labels + DLP enforce what the agent can surface. Same policy, new surface."
    - "Lineage is the governance feature you under-invest in. Start with one cross-system flow and grow."

---

## Credentials for this demo

| Resource | URL |
|---|---|
| Purview portal | `https://web.purview.azure.com` → account `pv-pepsiws-embmtykicepum` |
| Fabric portal | `https://app.fabric.microsoft.com` → workspace `ws-pepsi-pradipta-dash` |
| Azure SQL | `sql-pepsiws-embmtykicepum.database.windows.net` → database `vectordb` |

---

## Review

In 20 minutes you have seen how Purview catalogs Azure data services with automatic scanning and classification, and how OneLake Catalog provides zero-setup discovery and lineage for Fabric-native assets. Together they give a CPG data platform complete governance coverage from raw storage through to the AI agent layer.

## Further reading

- [Microsoft Purview overview](https://learn.microsoft.com/purview/purview)
- [Purview lineage for Microsoft Fabric](https://learn.microsoft.com/purview/how-to-lineage-fabric)
- [OneLake Catalog](https://learn.microsoft.com/fabric/governance/onelake-catalog)
- [Sensitivity labels in Fabric](https://learn.microsoft.com/fabric/governance/information-protection)
- [Copilot in Microsoft Fabric](https://learn.microsoft.com/fabric/get-started/copilot-fabric-overview)
