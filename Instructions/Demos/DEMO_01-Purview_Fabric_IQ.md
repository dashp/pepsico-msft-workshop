# Demonstration 01: Microsoft Purview + Microsoft Fabric IQ

## Demonstration introduction

In this **instructor-led demonstration**, you observe how **Microsoft Purview** governs data assets that the labs have just produced, and how **Microsoft Fabric IQ** complements that picture with platform-native data-quality, Copilot, and lineage signals.

There are no per-attendee steps — follow along in the instructor's screen.

## Estimated timing: 25 minutes

## Demonstration scenario

By the end of Labs 01–03, you have created:

- A Fabric Lakehouse `lh_pepsi_ws_team01` with `bronze_*`, `silver_*`, and `gold_sales` tables.
- A semantic model `sm_pepsi_sales` and a Power BI report.
- An Azure SQL database `db_pepsi_rag` with a vector table.
- A Fabric Data Agent `agent-pepsi-sales-team01`.

This demo shows how a central governance team sees all of those assets in **one** place — and where Fabric IQ adds value the central catalog cannot.

## Architecture diagram

![Diagram of the Purview + Fabric IQ flow.](../media/demo01-architecture.png)

## What the instructor will show

- Section 1: Purview Data Map of the workshop tenant.
- Section 2: Lineage from Azure SQL → Fabric Lakehouse → Power BI.
- Section 3: Sensitivity labels and DLP signals.
- Section 4: Fabric IQ — data-quality scores, Copilot in Fabric, recommended actions.

---

## Section 1: Purview Data Map of the workshop tenant

1. Open the **Microsoft Purview governance portal** — `https://purview.microsoft.com`.

2. In the left pane, select **Data map → Domains**, then open the `PepsiCo Workshop` domain.

3. Show the registered sources:

    | Source | Role |
    |---|---|
    | Microsoft Fabric tenant | Lakehouses, semantic models, Power BI reports |
    | Azure SQL Database | `db_pepsi_rag` with the vector table |
    | Azure Data Lake Storage | Bronze raw landing for the labs |

    ![Screenshot of the Purview Data Map sources view.](../media/demo01-section1-sources.png)

4. Open the **Catalog** and search for `gold_sales`. Point out:
    - The asset appears under both the Fabric Lakehouse and the underlying OneLake storage account — Purview reconciles them.
    - The semantic model `sm_pepsi_sales` is listed as a **downstream** asset.

---

## Section 2: Lineage Azure SQL → Fabric → Power BI

1. Still in the **Catalog**, open the `gold_sales` table and switch to the **Lineage** tab.

2. Trace the path:

    `Files/raw/sales.csv` → `bronze_sales` → `silver_sales` → `gold_sales` → `sm_pepsi_sales` → `rpt_pepsi_sales_overview`.

3. Pivot to the Azure SQL side: open `dbo.product_docs` and show its lineage from the embedding loader script and Azure OpenAI.

    ![Screenshot of the cross-system lineage graph.](../media/demo01-section2-lineage.png)

4. **Talking points**:
    - Purview is a *catalog of catalogs*, not a runtime. Lineage is harvested.
    - Custom lineage (for the embedding loader) is pushed via the Purview REST API by a small post-job hook.
    - Lineage is the single most under-used governance feature — start with one cross-system flow and grow.

---

## Section 3: Sensitivity labels and DLP

1. In Purview's **Information Protection**, show the workshop label taxonomy:

    | Label | Used for |
    |---|---|
    | `General` | Marketing collateral, public docs |
    | `Internal` | POS rollups, weather data |
    | `Confidential / PII` | Customer-identifying tables |
    | `Confidential / Highly restricted` | Forecast inputs, executive views |

2. Open `gold_sales` and apply the `Internal` label. Show that the label is **inherited** by the semantic model and by Power BI exports.

3. Open the **DLP** policy `PII never in chat` and show its match conditions:
    - Any AAD-authenticated copilot session.
    - Detected PII entity types.
    - Action: block + audit.

    ![Screenshot of a DLP policy summary.](../media/demo01-section3-dlp.png)

4. **Talking point**: For agentic workloads, labels and DLP are how you keep the *agent* from leaking what the user could have leaked anyway. The risk surface is the same, the controls move closer to the LLM.

---

## Section 4: Fabric IQ

Fabric IQ surfaces platform-native signals that Purview cannot see because they are inside Fabric.

1. In the Fabric portal, open the **Admin → Fabric IQ** view (admin role required). Show:
    - Capacity utilization heat map for the workshop capacity.
    - Top 5 most-queried semantic models and Lakehouses.
    - Suggested workspaces to migrate to a smaller capacity.

    ![Screenshot of Fabric IQ capacity insights.](../media/demo01-section4-iq.png)

2. Open `gold_sales` in the Lakehouse and click **Data quality**. Show:
    - Auto-detected nulls, duplicates, outliers.
    - A one-click rule to alert when the share of nulls in `revenue` exceeds 1%.

3. Open the Lakehouse SQL endpoint and invoke **Copilot in Fabric**:
    - Prompt: *"Show me the top 5 stores in Texas by revenue last quarter."*
    - Copilot returns a SQL query grounded on the schema.

4. Switch to the Data Agent created in Lab 01 and ask the same question. Point out that the **Data Agent** is conversational, the **Copilot** is SQL-generation. They complement each other.

---

## Review

In 25 minutes you have seen how Purview brings every asset under one catalog with lineage and labels, and how Fabric IQ adds capacity, quality, and Copilot signals from inside the Fabric tenant. For a CPG data platform, you need both — Purview is the *map*, Fabric IQ is the *speedometer*.

## Talking points to leave on screen

- "Lineage is the governance feature you under-invest in. Start with one cross-system flow."
- "Sensitivity labels travel with the data — including into Power BI exports and into your agents."
- "Fabric IQ is not a Purview replacement. It is the in-platform telemetry that no external catalog can collect."
- "DLP for agents is the same DLP, just enforced earlier — at the model boundary."

## Further reading

- [Microsoft Purview overview](https://learn.microsoft.com/purview/purview)
- [Purview lineage for Microsoft Fabric](https://learn.microsoft.com/purview/how-to-lineage-fabric)
- [Sensitivity labels for files and emails](https://learn.microsoft.com/purview/information-protection)
- [Fabric capacity metrics app](https://learn.microsoft.com/fabric/enterprise/metrics-app)
- [Copilot in Microsoft Fabric](https://learn.microsoft.com/fabric/get-started/copilot-fabric-overview)
