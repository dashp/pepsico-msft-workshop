# Lab 01 — Trainer Handbook

> Companion to [`LAB_01-Fabric_Lakehouse_Data_Agent.md`](./LAB_01-Fabric_Lakehouse_Data_Agent.md). The lab doc is for attendees; this doc is for **you** — what to say, why each step matters, where attendees will get stuck, and AWS-equivalent mappings for a data engineer audience.

---

## Lab in one sentence

> *We are going to turn a folder of raw CSVs into a governed, query-able, AI-assistant-callable data product — using only Microsoft Fabric, in 60 minutes.*

## Why this lab opens Day 2

Day 1 closed with a **Foundry agent** that needed grounded data. Lab 01 builds the **source-of-truth dataset and the natural-language interface** that the Day 2 Foundry agent will call. If Lab 01 fails, the entire afternoon falls over.

## Target outcomes (what the attendee should be able to say at the end)

1. *"I can ingest data into Fabric, refine it into a medallion architecture, and expose it to Power BI without copying data."*
2. *"I understand what Direct Lake mode is and why it's different from Import mode."*
3. *"I can build a Fabric Data Agent that answers business questions in natural language."*
4. *"I know the three gotchas that will trip me up the first time I try this on my own data."*

## Audience assumption check (calibrate in the first 5 min)

Ask the room:
- *"Who has used Spark/Databricks?"* → if many hands, skim the notebook code.
- *"Who has used DAX before?"* → if few, slow down Task 3 dramatically.
- *"Who has used a Lakehouse or any medallion architecture?"* → drives how much you explain bronze/silver/gold.

## Pacing guide (60 min total)

| Task | Plan | If slipping |
|---|---|---|
| 1. Workspace + Lakehouse | 5 min | — |
| 2. Notebook + Bronze/Silver/Gold | 15 min | Skip the silver dedup explanation |
| 3. Semantic model + DAX | 15 min | Pre-create the model and just show measures |
| 4. Power BI report | 10 min | Build 1 visual not 3 |
| 5. Data Agent | 15 min | Pre-create instructions, just test prompts |

---

## Task 1: Workspace + Lakehouse

### What we're building
A **Fabric workspace** (a project container) with a **Lakehouse** inside it (a unified store backed by OneLake / Parquet).

### Why it matters for PepsiCo
PepsiCo's data lives in many systems. A Lakehouse becomes the single landing zone where analytics + AI workloads share the same physical data — no more "marketing has their copy, finance has theirs, AI team has a third."

### Microsoft concepts introduced
- **OneLake** — the tenant-wide logical data lake. *"It's like AWS S3, but it's automatically shared across every Fabric service in your tenant — there is only one OneLake per Microsoft 365 tenant."*
- **Workspace** — a project boundary with role-based access.
- **Lakehouse** — a Delta Parquet store + SQL endpoint + Spark engine, all in one item.
- **Schema-enabled Lakehouse** — newer feature; tables live under `dbo` (or custom schemas), like SQL Server namespacing.

### AWS equivalent (for Pradipta)
| Microsoft | AWS |
|---|---|
| OneLake | S3 (one per tenant vs one bucket per project) |
| Workspace | A folder in S3 + IAM policies + an AWS account boundary, roughly |
| Lakehouse | S3 + Glue catalog + Athena + Redshift Spectrum, **bundled into one item** |
| Fabric Capacity | Always-on Redshift cluster you pre-pay for |
| Direct Lake | Redshift Spectrum querying S3 Parquet directly (no copy) |

### Talking points
- *"This is the first time in Microsoft's history you can have lake-scale storage **and** SQL **and** BI **and** ML on the same physical files — no shuffling, no syncing."*
- *"Notice we haven't picked between Spark vs SQL vs BI. We're not committing to a compute engine. We commit to a storage format — Delta Parquet — and every engine sees the same thing."*

### Gotchas + WHY

| Gotcha | Why it happens | What to say to the room |
|---|---|---|
| `AppMetadataInaccessible` when opening workspace | User account has no Fabric / Power BI license | *"If you see this, you don't have a Fabric license assigned. Raise a hand — we'll fix it before Task 2."* |
| Capacity dropdown empty | User not a capacity admin or workspace not bound to a capacity | *"Always check the capacity badge next to the workspace name top-bar. No badge = no compute = nothing will work."* |
| `dbo` folder unexpectedly under Tables | New schema-enabled Lakehouse default | *"Don't worry about `dbo`. It's a namespace. Your Spark code will work exactly the same either way."* |

---

## Task 2: Bronze / Silver / Gold via notebook

### What we're building
The classic **medallion architecture** — raw CSV → typed/deduped → joined analytics-ready — all as Delta tables in the same Lakehouse.

### Why it matters for PepsiCo
- **Reproducibility**: every layer is recomputable from the layer below.
- **Cost optimization**: business users query Gold (small, joined); data scientists can drop to Silver/Bronze when they need to.
- **Governance**: PII can be masked in Silver while leaving Bronze under tight IAM.

### Microsoft concepts introduced
- **Default Lakehouse on a notebook** — the lakehouse that mounts at `/lakehouse/default/` and resolves bare table names. *Only one notebook ↔ default lakehouse mapping.*
- **`saveAsTable`** — auto-registers the Delta table in the Lakehouse's metastore (which is also the SQL endpoint).
- **Schema enforcement** — Delta will reject writes whose schemas don't match the existing table; this is the *feature* attendees most often hit as a bug.

### AWS equivalent
| Microsoft | AWS |
|---|---|
| Spark notebook in Fabric | Glue notebook / EMR notebook / Databricks notebook |
| Delta table via `saveAsTable` | Glue catalog table over S3 Parquet |
| `/lakehouse/default/Files/` | Mounted S3 prefix in EMR / Glue |
| Bronze→Silver→Gold | Identical pattern — Databricks medallion is the canonical reference |

### Talking points
- *"Bronze is 'land it as-is, no transformation.' Silver is 'now make it good.' Gold is 'now make it useful for a specific business question.'"*
- *"Notice we use `inferSchema=True` for Bronze and explicit casts for Silver. That's intentional — Bronze must always succeed, Silver may fail loudly if the data shape changes."*
- When the join in the Gold cell completes: *"This is exactly what Power BI is about to query — except it won't copy the result. It'll point at this same Parquet file."*

### Gotchas + WHY

| Gotcha | Why it happens | What to say |
|---|---|---|
| `Bad Request, 400, HEAD ... user/trusted-service-user/Files/...` | No default lakehouse set on the notebook → Spark uses session-local filesystem | *"This is the #1 error in this lab. Click the **radio button** next to the lakehouse name. If you only see a check mark, that's just 'attached' not 'default'. They are different."* |
| Tables don't appear after Spark cells succeed | Lakehouse explorer doesn't auto-refresh | *"Hit F5 or click the three-dot menu next to Tables. Fabric's UI doesn't watch the metastore in real-time."* |
| `gold_sales rows: 0` | `to_date()` mask didn't match CSV format | Confirm CSV samples in `dim_*` before changing the notebook |

---

## Task 3: Direct Lake semantic model + DAX measures

### What we're building
A **Power BI semantic model** in **Direct Lake** mode — meaning BI queries hit OneLake Parquet directly, with zero data copy and zero refresh schedules.

### Why it matters for PepsiCo
Traditional BI = copy data into the BI engine (cube refresh). At PepsiCo scale, that means hours of overnight pipelines and stale dashboards. Direct Lake = queries are sub-second on Parquet directly, dashboards are always current, no refresh job to babysit.

### Microsoft concepts introduced
- **Semantic model** — the metadata layer (measures, relationships, security) that sits between raw tables and end users.
- **Direct Lake vs Import vs DirectQuery** — three storage modes; this one is unique to Fabric.
- **DAX** — the formula language for Power BI. Different mental model from SQL: filter context, row context, measures vs columns.

### AWS equivalent
| Microsoft | AWS |
|---|---|
| Semantic model | QuickSight Dataset + calculated fields |
| Direct Lake | QuickSight querying Athena directly (no SPICE) |
| Import mode | QuickSight loading data into SPICE (in-memory copy) |
| DAX | A blend of QuickSight calculated fields + SQL window functions |

### Talking points
- *"DAX takes a week to learn. Today we'll write 4 measures so you can recognize the pattern, not become an expert."*
- On `Avg Selling Price = DIVIDE([Total Revenue], [Total Units])`: *"Notice this references **other measures**, not columns. That's the DAX power move — composition. You build small measures and combine them."*
- On `Revenue MoM %`: *"This is where DAX shines — time intelligence in 3 lines. In SQL this would be a CTE with LAG."*

### Gotchas + WHY

| Gotcha | Why it happens | What to say |
|---|---|---|
| `The syntax for 'Units' is incorrect` when pasting `Total Units = SUM(...)` | The web modeller separates Name field from Formula field — pasting the full assignment puts the `=` inside the formula | *"Don't paste the `Name = `. Put the name in the Properties pane on the right, only the right-hand-side in the formula bar."* |
| **Circular dependency error** on `Total Revenue` | IntelliSense autocompletes `[Total Revenue]` while editing the measure named `Total Revenue` | *"This will happen to half of you. When typing `S` for SUM, IntelliSense suggests `[Total Revenue]`. Press Esc, then type your formula."* |
| Measure named `Measure` or `Measure 2` | User typed the formula but never set the Name | *"After typing the formula, glance at the right-side panel. If it still says `Measure`, rename it."* |

---

## Task 4: Power BI report

### What we're building
A 3-visual report on top of the semantic model — Card, Stacked bar, Line chart.

### Why it matters for PepsiCo
Visual validation before exposing to a Data Agent. **Trust the numbers visually first**; the agent will quote those same numbers tomorrow.

### Microsoft concepts introduced
- **Report vs Dashboard** — a report has interactive pages bound to a semantic model; a dashboard is a stitched view of report tiles.
- **Field wells** — drag fields into the right pane.
- **Drill / drill-up** — the date hierarchy lets you go day → month → quarter → year in one click.

### AWS equivalent
QuickSight Analyses (the report) vs Dashboards (the published artifact).

### Talking points
- *"Notice the line chart goes to daily by default. That's hard to read in a demo. One click to switch to Month — and notice the bar chart's region order matches the line chart's daily peaks."*
- *"What you see here is what the Data Agent in the next task will see. If a number is wrong here, the agent will quote it wrong."*

### Gotchas + WHY

| Gotcha | Why it happens | What to say |
|---|---|---|
| Bar chart not sorted | Power BI sorts alphabetically by default | *"Click the visual's three-dot menu → Sort by → pick the measure, descending."* |
| Card shows `(Blank)` | A column dragged instead of a measure, or a filter wiped the data | Re-drag the measure (🧮 icon) |
| Line chart shows one dot | X-axis is set as a single date value, not the hierarchy | Switch X-axis from Date hierarchy to Month |

---

## Task 5: Fabric Data Agent

### What we're building
A natural-language interface over the Gold layer — attendees can ask "Top 5 stores by revenue?" and get a grounded answer.

### Why it matters for PepsiCo
This is what makes the workshop matter. Everything else (Lakehouse, Semantic model, Power BI) is foundational. The Data Agent is the **product** business stakeholders will actually demo. It's also what Sandeep's Foundry agent calls in Day 2.

### Microsoft concepts introduced
- **Data Agent** — Fabric's NL2SQL agent grounded on Lakehouse tables.
- **Instructions / system prompt** — the trainer's lever to control behavior.
- **Save vs Publish** — Save persists; Publish makes effective. *Critical distinction.*
- **Capacity requirement** — Data Agent needs F64+ or Trial capacity.

### AWS equivalent
- Amazon Q in QuickSight (NL → analytics)
- Bedrock Knowledge Bases with structured data (similar pattern with retrieval)
- Athena + LLM-on-top patterns (DIY)

The Microsoft pitch: it's **built in**, grounded automatically on your Lakehouse, and Fabric handles RBAC + observability. No glue code.

### Talking points
- *"Watch what just happened: I asked a question in English. It generated SQL. It ran the SQL against our Gold table. It formatted the answer. That whole pipeline used to be a multi-week project."*
- After the Texas → TX failure: *"This is the most important lesson of this lab. **NL2SQL is literal**, not semantic. The agent will not magically know that Texas means TX. You have to teach it — explicitly, in the instructions."*
- *"In a production deployment, you'd add a data dictionary like this for every encoded dimension — gender codes, status codes, product categories — anything where the user might phrase it differently from the storage form."*

### Gotchas + WHY

| Gotcha | Why it happens | What to say |
|---|---|---|
| `+ New item` doesn't show "Data agent" | F2-F32 capacity doesn't support it | *"This requires F64+. The trainer has scaled the capacity for you. If you don't see it, refresh the browser tab."* |
| Instructions changes ignored | User clicked Save but not Publish | *"Always Publish after Save. Save is your edit; Publish is what the agent actually uses."* |
| "Texas" returns 0 products | LLM did `WHERE state = 'Texas'` against TX-coded data | The whole CRITICAL DATA RULES section in instructions exists to fix this. **Demo it as a feature**: *"Let me show you what happens without the data dictionary..."* |
| First prompt takes 30 sec | Cold start | *"First query warms the Spark session. Subsequent queries are 5-15 seconds."* |
| Inconsistent answers (works once, fails next) | LLM non-determinism | *"This is the LLM's stochastic nature. In production you'd add deterministic post-processing or evaluations. For demo, just re-ask."* |

### The "wow" moment of the lab

Run this sequence live:
1. Ask `Show me top 5 stores by revenue this quarter.` → table appears.
2. Ask `Now break that down by product category.` → it carries context forward.
3. Ask `Which of those products had a sales spike in March?` → grounds again.

That conversational flow on top of governed data is the demo people remember.

---

## Lab close

### What attendees walk away with
- A working Lakehouse with medallion architecture in their own workspace.
- A Direct Lake semantic model + DAX measures they can extend.
- A live Power BI report they can show their boss.
- A **Data Agent** that answers business questions in plain English — this is the Day 2 dependency.

### Hand-off line to Day 2
> *"Tomorrow afternoon, a Foundry agent is going to call YOUR Data Agent. The questions you asked it just now? The Foundry agent will ask the same kinds of questions on behalf of an end-user chat experience. You just built the data half of an enterprise AI application."*

### Trainer post-flight checklist

- [ ] All attendees have `gold_sales` populated (~30k rows)
- [ ] All attendees have at least 1 Data Agent prompt working
- [ ] You captured names of any attendee whose Data Agent failed — they need a fix before Day 2's lab depends on it
- [ ] Capacity scaled back to F2 if cost-conscious (≈ $8/hr saved)

---

## Cheat sheet — copy/paste ready answers for FAQ

> **Q: Why Sweden Central and not East US 2?**
> A: That's where the workshop subscription has Fabric capacity quota. The labs work identically in any region; only the region string changes.

> **Q: Can I use Trial capacity instead of F64?**
> A: Yes — Trial capacity has F64 features for 60 days. Many of you are on Trial automatically.

> **Q: Why is my semantic model in Import mode?**
> A: You created it from the wrong entry point. Always: Lakehouse → New semantic model. Any other path defaults to Import.

> **Q: Will Direct Lake work with petabyte data?**
> A: Yes — but with caveats around column cardinality and join keys. For today's 30k-row demo this is overkill; for real workloads the engineering review matters.

> **Q: Does the Data Agent see my Power BI measures?**
> A: Currently no — the Data Agent grounds on Lakehouse tables, not on semantic-model measures. So if your business logic lives in DAX, the agent will reimplement it in SQL. Plan accordingly.

> **Q: Can I deploy this Data Agent to a Teams chat?**
> A: Yes — via the Microsoft 365 Agent Store toggle in the Publish dialog. We skipped it today to keep the agent workshop-only.
