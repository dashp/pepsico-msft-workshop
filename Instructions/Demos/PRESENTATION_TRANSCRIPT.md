# PepsiCo Workshop Day 3 — Presentation Transcript & Talking Points

> **Total deck: 53 slides | ~2.5 hours presentation + 4 labs**
> This is your detailed speaker guide. Each slide has: what it shows, what to say, and a **"Why this matters for PepsiCo"** callout where relevant.

---

## SLIDE 1 — Title Slide
**"PepsiCo Data & AI Workshop — Day 3"**

> "Good morning everyone! Welcome to Day 3. Quick recap — Day 1 we covered Azure fundamentals and cloud architecture. Day 2 was AI services and OpenAI. Today we're getting into the **data platform itself** — how you store, move, analyze, govern, and act on data at enterprise scale.
>
> We have four sessions with a hands-on lab after each. By end of day, you'll have built a lakehouse, streamed real-time data, run vector search for RAG, and trained a forecasting model with AutoML. Let's get started."

---

## SLIDE 2 — Session 1 Divider: Microsoft Fabric

> "Session 1 — Microsoft Fabric. Let me start with a question: how many different tools does your team use today for data integration, warehousing, data science, and reporting? I'm guessing it's 5-10 different products. Fabric's promise is: **one platform, one license, one security model** for all of it."

---

## SLIDE 3 — Unifying the Data Estate

> "The theme is unification. Here's the reality today at most enterprises — you have Azure Data Factory for pipelines, Synapse for Spark, a SQL data warehouse, maybe Databricks for ML, Power BI for reports, and Purview for governance. Each has its own security model, its own storage, its own billing. Your data engineers spend 40% of their time just **moving data between systems** and maintaining connections.
>
> Fabric eliminates that tax. Everything runs on one platform, one copy of data, one set of permissions."

---

## SLIDE 4 — The Data and AI Landscape

> "This slide makes the point visually. Every icon here is a real product in the data and AI space. There are literally hundreds. The burden is on YOUR team to figure out:
> - Which ones work together?
> - How are they licensed?
> - Who manages the infrastructure?
> - How do you secure data that flows between them?
>
> At PepsiCo scale — with data coming from manufacturing plants, supply chain systems, retail partners, IoT sensors — this complexity is exponential. Fabric's answer is: **stop integrating tools, start delivering value**."

**💡 PepsiCo context:** "Think about how many systems touch a single bottle of Pepsi — from raw material sourcing, through manufacturing quality sensors, distribution logistics, retail shelf data, and finally consumer purchase signals. Today that's 10+ disconnected systems. Fabric can unify that."

---

## SLIDE 5 — Microsoft Fabric Platform Overview

> "Let me walk through what's actually inside Fabric:
>
> **Data Factory** — This is your integration engine. 170+ connectors. If you've used Azure Data Factory, think of this as the SaaS version — no infrastructure to manage, but same power. You can build pipelines that pull from SAP, Salesforce, Oracle, flat files, APIs — anything.
>
> **Analytics (Spark + SQL)** — Two engines, same data. Data engineers use Spark notebooks (Python, Scala, SQL). Data analysts use T-SQL against the warehouse. Both read from the same lakehouse — no data copying.
>
> **Real-Time Intelligence** — This is for streaming data. IoT sensors, click streams, transaction events. Sub-second ingestion, real-time queries, automated alerts.
>
> **Databases** — Operational databases (SQL, PostgreSQL) built into the platform. For transactional workloads.
>
> **Power BI** — The reporting layer. 35 million+ users. Directly connected to lakehouse data via Direct Lake — no import needed.
>
> **Fabric IQ** — Brand new (GA June 2026). This is the semantic intelligence layer. I'll explain this in detail in Session 2.
>
> All of these sit on **OneLake** — one storage layer, open Delta Parquet format, governed by one catalog."

**💡 Key differentiator:** "Unlike competitors who acquired separate companies and bolted them together (looking at you, Snowflake + Streamlit, or Google's 5 different analytics products), Microsoft **built these from scratch** to share the same engine. That's why data doesn't need to move between workloads."

---

## SLIDE 6 — 35,000+ Fabric Customers

> "The adoption is staggering — 35,000+ customers, 90% of the Fortune 500. That includes companies in CPG, retail, manufacturing — your peers.
>
> Why does this matter? Because it means the platform is **production-proven** at enterprise scale. When you hit edge cases, there's a community and Microsoft support team that's seen it before."

---

## SLIDE 7 — Gartner Recognition

> "For those who trust analyst validation — Microsoft is the **only vendor** that leads in ALL FOUR Gartner Magic Quadrants covering the data space: Data Integration, Cloud Databases, AI, and Business Intelligence.
>
> No other vendor — not Snowflake, not Databricks, not Google — has leadership across all four. They each lead in one or two. Microsoft leads everywhere."

---

## SLIDE 8 — OneLake: The OneDrive for Data

> "OneLake is the foundation that makes everything else possible. Think of it like OneDrive — but for organizational data instead of files.
>
> **What it actually does:**
> - Stores ALL data in **open Delta Parquet format** — meaning any engine can read it (Spark, SQL, Python, even non-Microsoft tools)
> - **Automatically indexed** — you don't organize data manually, it's discoverable via catalog
> - **One security model** — permissions set once, enforced everywhere (notebooks, SQL, Power BI, APIs)
> - **No storage accounts to manage** — Fabric handles all the infrastructure
>
> The practical impact: your data engineer writes data from a Spark notebook, and 30 seconds later a Power BI report sees it — no pipeline, no refresh, no ETL. That's Direct Lake."

**💡 PepsiCo example:** "Imagine your supply chain team writes sales forecast data to a lakehouse. Immediately, the finance team's Power BI dashboard updates. The planning team's Spark model reads the same data. The executive Data Agent answers questions about it. All from ONE copy of data, ONE set of permissions."

---

## SLIDE 9 — OneLake Unifies the World's Data

> "But what about data that's NOT in Fabric? That's where this gets powerful.
>
> OneLake doesn't require you to migrate everything. It connects to data **wherever it lives**:
> - **Shortcuts** — virtual pointers to data in AWS S3, Azure Blob, GCP, or other lakehouses. Zero data movement. Zero storage cost. The data appears as if it's local.
> - **Mirroring** — near-real-time replicas of operational databases (Azure SQL, Cosmos DB, Snowflake, Databricks Unity Catalog) into OneLake. Change data capture keeps it in sync.
>
> So your data stays where it is. OneLake provides ONE catalog, ONE security layer, ONE query surface over ALL of it."

**💡 Real scenario:** "If PepsiCo has sales data in Snowflake, IoT data in AWS S3, and CRM data in Cosmos DB — OneLake shortcuts + mirroring brings all three together without a single ETL pipeline. Your analyst queries across all three with one SQL statement."

---

## SLIDE 10 — Data Factory

> "Let's go deeper on Data Factory. This is for when you DO need to move and transform data.
>
> **What makes it different from standalone ADF:**
> - **Fully SaaS** — no integration runtimes to manage, no VNet configurations for basic scenarios
> - **Dataflows Gen2** — Power Query (the same UI your Excel users know) but running at cloud scale. Drag-and-drop transformations.
> - **170+ connectors** — SAP, Oracle, Salesforce, REST APIs, SFTP, databases, you name it
> - **Copilot-powered** — describe what you want in English, it generates the pipeline
>
> You'll build a pipeline in Lab 01 when you run the notebook that transforms Bronze → Silver → Gold."

---

## SLIDE 11 — Data Engineering (Spark)

> "For data engineers who prefer code over drag-and-drop:
>
> **Spark in Fabric** gives you:
> - **Notebooks** — Python, PySpark, Scala, R, SQL. Same notebook experience as Databricks.
> - **Native execution engine** — Fabric's Spark runs 3-4x faster than open-source Spark because of vectorized processing (written in C++ under the hood)
> - **Autoscale** — clusters spin up in seconds, scale out automatically, pause when idle. You never manage cluster infra.
> - **Materialized views** — cache expensive query results for re-use
>
> In Lab 01, you'll run a Spark notebook that reads raw CSV data (Bronze), cleans and validates it (Silver), and aggregates it into business-ready tables (Gold). This is the classic **medallion architecture**."

**💡 Why it matters:** "Your data engineers don't choose between 'do I use Spark or SQL?' — they use BOTH on the same data. The Spark notebook writes to the lakehouse, and a SQL analyst immediately queries it with T-SQL. No data movement."

---

## SLIDE 12 — Data Warehouse

> "For SQL professionals, Fabric Data Warehouse is a **lake-centric relational warehouse**.
>
> What does that mean practically?
> - You write T-SQL (your existing skills work)
> - Data is stored in OneLake in open Delta format (not proprietary)
> - **No compute to configure** — no knobs, no tuning, no cluster sizing
> - **Cross-database queries** — query across multiple lakehouses and warehouses in one statement
> - **Full ACID transactions** — same guarantees as SQL Server
>
> The 'lake-centric' part is key: because data is in open format, Power BI can do **Direct Lake** reads (microsecond query performance without importing data) and Spark notebooks can access the same tables."

---

## SLIDE 13 — Data Science

> "Data science in Fabric means you don't need a separate ML platform.
>
> **The workflow:**
> 1. Access data directly from your lakehouse (no export/copy)
> 2. Explore in notebooks with pandas, scikit-learn, or Spark ML
> 3. Track experiments with MLflow (built in)
> 4. Register models to a model registry
> 5. Deploy as serving endpoints (REST APIs)
> 6. Power BI consumes predictions directly
>
> In Lab 04 today, you'll see this in action with Databricks AutoML — it automatically trains multiple forecasting models (Prophet, ARIMA) and picks the best one. Then you'll deploy it as a real-time serving endpoint and build an AI agent that calls it."

**💡 PepsiCo relevance:** "Think demand forecasting for SKUs, quality prediction on manufacturing lines, or price optimization. The model trains on your lakehouse data and deploys as an API that any app can call."

---

## SLIDE 14 — Real-Time Intelligence Overview

> "Now here's where it gets exciting for operations teams.
>
> **RTI handles data that's moving** — not data at rest. Think:
> - IoT sensors on a bottling line reporting temperature every second
> - Point-of-sale transactions streaming from 100,000 retail locations
> - Supply chain events (shipment departed, delivery confirmed)
> - Social media mentions of your brand
>
> Traditional analytics sees this data hours or days later in a data warehouse. RTI processes it **as it arrives** — sub-second latency. And it doesn't just store it — it can **trigger actions automatically**.
>
> Example: if a sensor on a bottling line shows temperature exceeding threshold → RTI detects the anomaly → triggers an alert → calls a maintenance workflow. All in under 10 seconds. No human in the loop."

**💡 PepsiCo operations:** "Imagine 50,000 vending machines reporting inventory levels every hour. RTI can detect which machines will run out of specific products tomorrow and automatically generate restock orders — before a single customer sees an 'out of stock.'"

---

## SLIDE 15 — Semantic Model Superpowers

> "Now let me explain something that's deceptively powerful: **semantic models**.
>
> The problem: your company has 500 reports. In 200 of them, 'revenue' is calculated differently. Some include returns, some don't. Some are gross, some are net. When the CFO asks 'what's our revenue?' — they get 5 different numbers.
>
> **A semantic model solves this permanently.** It's a curated layer that defines:
> - What 'Revenue' means (the exact DAX formula)
> - How 'Customer' relates to 'Order' relates to 'Product'
> - Which fields are measures vs. dimensions
> - Business-friendly names (not `tbl_fact_sales.amt_net_rev`)
>
> Once defined, **every report, every dashboard, every AI agent** uses the same definitions. 22 million semantic models already exist in Fabric. 35 million+ users consume them.
>
> And here's the AI angle: when you point a Data Agent at a semantic model, it doesn't just query tables — it **understands the business**. It knows that 'revenue' has a specific formula and applies it correctly every time."

---

## SLIDE 16 — Power BI

> "Power BI is the consumption layer — how business users actually SEE the data.
>
> But in Fabric, Power BI is fundamentally upgraded:
> - **Direct Lake mode** — reports read directly from lakehouse files. No import, no scheduled refresh. Data is always current.
> - **Copilot** — users type questions in natural language: 'Show me top 10 SKUs by revenue decline this quarter' → instant visualization
> - **Embedded everywhere** — Teams, Excel, PowerPoint, SharePoint, mobile
>
> The shift: reports are no longer static snapshots built weekly by an analyst. They're **live windows into your data estate** that any employee can interact with conversationally."

---

## SLIDE 17 — Semantic Models: Grounding BI and AI

> "This slide reinforces why semantic models are the **most important invisible thing** in your data stack.
>
> They sit between raw data and consumers (both human and AI):
> - Lakehouses, warehouses, eventhouses → feed INTO semantic models
> - Power BI reports, Copilot, Data Agents, external apps → consume FROM semantic models
>
> Without them, every consumer must understand raw table structures. With them, consumers work with business concepts. That's the difference between 'SELECT SUM(amt_net_rev) FROM tbl_fact_sales WHERE dt_fiscal_period = ...' and 'What was Q4 revenue?'"

---

## SLIDE 18 — AI Agents in Fabric

> "Fabric now has AI agents built directly into the platform. Two types:
>
> **Data Agents** — your virtual data analysts. They can:
> - Answer natural language questions about your data
> - Write and execute SQL/DAX queries
> - Create visualizations on the fly
> - Reason over relationships (e.g., 'which customers overlap between these two product lines?')
>
> **Operations Agents** — your virtual operations team. They can:
> - Monitor real-time data streams continuously
> - Detect anomalies and patterns
> - Take automated actions (send alerts, trigger workflows, call APIs)
> - Learn from feedback and improve over time
>
> Both types are **grounded in your semantic model** — so they understand YOUR business, not just generic data."

**💡 Practical example:** "A PepsiCo Data Agent grounded in your supply chain semantic model could answer: 'Which distribution centers are at risk of stockout for Lay's Classic in the next 7 days?' — and it would know exactly what 'stockout' means, what 'at risk' threshold is, and where to find the data."

---

## SLIDE 19 — Data Agents (GA)

> "Data Agents went GA recently. New capabilities:
>
> - **Graph model support** — agents can reason about relationships (not just tables). 'Which suppliers also supply our competitors?'
> - **Purview integration** — every agent interaction is audited. You can see who asked what, what data was accessed, and whether sensitive columns were exposed.
> - **Outbound access protection** — agents can't exfiltrate data to unauthorized destinations. Security is built in, not bolted on.
>
> You'll create a Data Agent in Lab 01 Task 5 (optional) — point it at your semantic model and ask it questions about your gold-layer sales data."

---

## SLIDE 20 — Lab 01 Slide

> "Time for hands-on! **Lab 01: Fabric Lakehouse + Data Agent**
>
> What you'll build:
> 1. **Create a Lakehouse** — your personal data lake in 2 clicks
> 2. **Run a Spark notebook** — Bronze (raw CSV) → Silver (cleaned) → Gold (aggregated) — classic medallion architecture
> 3. **Build a Direct Lake semantic model** — define measures and relationships
> 4. **Create a Power BI report** — visualize your gold data with no import
> 5. **(Optional) Create a Data Agent** — ask natural language questions about your data
>
> You have ~45 minutes. Open the lab guide and start. Raise your hand if you need help — especially on Task 3 where you create the semantic model."

⚠️ **Trainer note:** If participants hit "Free User cannot apply model changes" error on Task 3, it means their workspace isn't on Fabric capacity. Run the capacity assignment script.

🕐 **[LAB TIME — ~45 min]**

---

## SLIDE 21 — Session 2 Divider: Fabric IQ + Real-Time Intelligence

> "Welcome back! How did the lab go? Anyone get the Data Agent working? Cool.
>
> Now let's talk about two capabilities that take Fabric from a 'data platform' to an 'intelligence platform': **Fabric IQ** and **Real-Time Intelligence**."

---

## SLIDE 22 — Fabric IQ

> "Fabric IQ is Microsoft's newest and most ambitious addition to Fabric. Let me explain what problem it solves with a concrete example..."

---

## SLIDE 23 — Without Shared Context

> "Consider this: an airline has the concept of an 'active plane.'
> - **Maintenance** defines it as: 'not in the hangar' (could be flying OR parked at gate)
> - **Operations** defines it as: 'assigned to a flight today'
> - **Finance** defines it as: 'generating revenue this period'
>
> Leadership asks: 'How many active planes do we have?' — and gets THREE different numbers.
>
> Sound familiar? At PepsiCo, think about 'active SKU', 'fill rate', 'on-time delivery', or 'market share.' Does every team calculate these the same way? Probably not.
>
> This is what Fabric IQ solves. It creates ONE definition that everyone — humans AND AI agents — uses."

---

## SLIDE 24 — Massive Data, Fragmented Meaning

> "The data explosion makes this worse, not better. More data doesn't help if nobody agrees on what it means.
>
> Three symptoms:
> 1. **People rely on disparate systems** — each team has their own Excel, their own dashboard, their own 'source of truth'
> 2. **Every question requires an expert** — 'Can you pull that number for me?' becomes a 2-week project
> 3. **Decision-making is slow and subjective** — by the time 3 teams align on the definition, the window to act has passed
>
> Fabric IQ's solution: create an **ontology** — a formal model of your business concepts, relationships, and rules — and make it the single source of truth for all analytics and AI."

---

## SLIDE 25 — Fabric IQ: From Data to Decisions

> "So what IS an ontology in practical terms?
>
> Think of it as a **business glossary on steroids**:
> - **Entities**: Customer, Product, Store, Shipment, Manufacturing Line
> - **Relationships**: Customer BUYS Product, Store STOCKS Product, Line PRODUCES Product
> - **Rules**: 'Revenue' = SUM(net_amount) WHERE return_flag = 0
> - **Actions**: IF fill_rate < 85% THEN trigger restock workflow
>
> Once this exists, any AI agent in your organization can reason about your business without being re-taught from scratch every time. It knows what a 'customer' is, how they relate to 'orders', and what 'at risk' means."

**💡 The big picture:** "Fabric IQ is the **shared brain** of your organization — it ensures every person, every report, and every AI agent understands your business the same way. Without it, every AI deployment requires bespoke prompt engineering to explain your business. With it, agents just 'know.'"

---

## SLIDE 26 — Unify Business Semantics (No-Code)

> "Three things make Fabric IQ practical (not just theoretical):
>
> 1. **You don't start from scratch** — Fabric IQ builds on your existing Power BI semantic models. If you already have a well-curated semantic model with measures and relationships, IQ can promote that into a formal ontology. PepsiCo likely has hundreds of existing models.
>
> 2. **It breaks down silos** — the ontology is shared across the ENTIRE organization. Sales, Finance, Supply Chain, and Manufacturing all use the same entity definitions.
>
> 3. **No-code modeling** — your business analysts and domain experts (not just engineers) can define entities and rules through a visual interface. The people who KNOW the business can formalize it directly."

---

## SLIDE 27 — RTI Divider: From Data Streams to Instant Action

> "Now let's shift gears to Real-Time Intelligence. If Fabric IQ is the brain, RTI is the **nervous system** — it processes signals as they happen and triggers responses instantly."

---

## SLIDE 28 — Microsoft Fabric Platform (Unified)

> "Important point: RTI isn't a separate product you buy and integrate. It's **inside Fabric**. Same OneLake, same governance, same billing. Your real-time data lands in the same data estate as your batch data. No integration tax."

---

## SLIDE 29 — Real-Time Intelligence

> "What RTI gives you in concrete terms:
>
> - **Eventhouse** — a high-performance columnar database optimized for time-series and event data. Think of it as the real-time equivalent of a lakehouse. Can ingest millions of events per second.
> - **Eventstream** — no-code/low-code pipeline for routing streaming data. Connect to Kafka, Event Hubs, IoT Hub, custom sources, or Fabric's built-in sample sources.
> - **KQL (Kusto Query Language)** — purpose-built for time-series analytics. 10x more natural than SQL for questions like 'show me the 5-minute moving average of temperature for the last hour'
> - **Real-Time Dashboards** — live visualizations that auto-refresh (not scheduled — truly live)
> - **Activator** — rules engine that triggers actions when conditions are met (email, Teams, Power Automate, custom webhook)
>
> You'll build ALL of this in Lab 02."

---

## SLIDE 30-31 — The Opportunity with Streaming Data

> "Forbes research: there's a rapidly growing set of use cases that need decisions **20 times faster than a blink of an eye** — that's sub-50ms.
>
> Every company has hundreds of streaming data sources. The question isn't whether you HAVE real-time data — you absolutely do. The question is whether you're USING it in real-time or letting it age into a data warehouse before anyone sees it.
>
> Most companies today: event happens → lands in data lake → ETL runs overnight → shows up in dashboard next morning → someone notices 3 days later.
>
> With RTI: event happens → processed in under 1 second → rule triggers → action taken. The entire loop is automated."

**💡 PepsiCo scenarios:**
- Manufacturing: quality sensor detects anomaly → line stops automatically → maintenance notified
- Supply chain: truck GPS shows unexpected route deviation → alert to logistics team
- Retail: real-time POS data shows sudden spike in demand → auto-adjust next shipment
- Vending: machine reports 'almost empty' → restock order generated before stockout

---

## SLIDE 32 — From Fragmented to Unified

> "Let me make this tangible with a before/after:
>
> | FROM (Today) | TO (With RTI) |
> |---|---|
> | 5 different streaming tools (Kafka, Spark Streaming, custom processors) | One Eventstream, visual builder |
> | Need a senior data engineer to build any real-time pipeline | Business analyst can build with no-code |
> | Batch processing: data arrives in warehouse 6-24 hours late | Sub-second ingestion, instant query |
> | Data silos: streaming data disconnected from historical data | Same OneLake — real-time and batch together |
> | Anomalies discovered after the fact | AI-powered detection + automatic action |
>
> The bottom line: real-time capabilities are no longer reserved for companies with Google-level engineering teams. Fabric RTI democratizes it."

---

## SLIDE 33 — Industry Opportunities

> "Every industry has high-value real-time use cases:
>
> For **CPG and Retail** (PepsiCo's world):
> - **Predictive inventory** — know what's going to sell out before it does
> - **Demand sensing** — detect demand spikes from weather, events, social media
> - **Supply chain visibility** — track every shipment in real-time
> - **Promotion effectiveness** — see if a promotion is working within hours, not weeks
> - **Quality monitoring** — catch manufacturing defects before they ship
>
> For other industries represented here:
> - Finance: fraud detection in <100ms
> - Manufacturing: predictive maintenance
> - Healthcare: patient vitals monitoring
> - Energy: grid optimization"

---

## SLIDE 34-35 — RTI in Fabric (Section Header)

> "Let me show you how the pieces fit together architecturally..."

---

## SLIDE 36 — Complete SaaS Solution

> "The RTI workflow in four steps:
>
> **1. Ingest & Process** — Eventstreams connect to your streaming sources. No infrastructure to manage. Just point at a Kafka topic, Event Hub, or IoT Hub and data flows in. You can also use no-code transforms right in the stream (filter, aggregate, route).
>
> **2. Analyze** — Once data lands in an Eventhouse, you query it with KQL. KQL is designed for time-series: 'StockEvents | where timestamp > ago(1h) | summarize avg(price) by bin(timestamp, 5m), symbol'. Try doing THAT elegantly in SQL.
>
> **3. Act** — Activator monitors your data continuously and fires rules. 'IF average temperature over 5 minutes > 95°F THEN send Teams message to plant manager AND create maintenance ticket.' No polling, no cron jobs — continuous evaluation.
>
> **4. AI Agents** — Operations Agents go beyond rules. They learn patterns, detect anomalies you didn't anticipate, and recommend actions. They get smarter over time."

---

## SLIDE 37 — RTI Architecture Diagram

> "Here's the full picture. Data flows left to right:
> - **Connectors** → raw events
> - **Eventstream** → routing and processing
> - **Eventhouse** → storage and indexing
> - **KQL Queryset** → ad-hoc and scheduled analysis
> - **Real-Time Dashboard** → live visualization
> - **Activator + Operations Agent** → automated response
>
> Everything in this diagram is fully managed. You never provision a VM, manage a Kafka cluster, or scale infrastructure manually."

---

## SLIDE 38 — Lab 02 Slide

> "Lab 02: **Real-Time Intelligence**. This is the most visual and fun lab.
>
> What you'll build:
> 1. **Eventhouse + KQL Database** — your real-time data store
> 2. **Eventstream** — connect a sample data source (simulated IoT)
> 3. **KQL queries** — explore event data with time-series queries
> 4. **Real-Time Dashboard** — live auto-refreshing charts
> 5. **Activator alert** — rule that fires when a threshold is crossed
>
> ~45 minutes. When you finish and see your dashboard updating live — that's the 'aha' moment. Enjoy!"

🕐 **[LAB TIME — ~45 min]**

---

## SLIDE 39 — Session 3 Divider: Data Services + AI Integration

> "Alright — Session 3. We're shifting from the data platform to the **AI integration layer**. Specifically: how do you make AI work with YOUR data, not just generic internet knowledge?
>
> The answer is **RAG — Retrieval-Augmented Generation**. And the foundation of RAG is **vector search**."

---

## SLIDE 40 — Why Vector Search?

> "Let me explain vector search with a simple example.
>
> **Traditional search** (keyword matching):
> - You search for 'beverage supply shortage' in your documents
> - It ONLY finds documents containing those exact words
> - It MISSES documents about 'drink inventory depletion' or 'low stock on soft drinks' — same meaning, different words
>
> **Vector search** (semantic matching):
> - Text gets converted to a **1536-dimensional vector** (a list of 1536 numbers) using an embedding model like OpenAI's text-embedding-ada-002
> - Similar MEANINGS produce similar vectors, regardless of exact words used
> - You compare vectors using **cosine distance** — closer vectors = more similar meaning
> - 'Beverage supply shortage' and 'drink inventory depletion' have nearly identical vectors
>
> This is the foundation for RAG: you store your company's documents as vectors, then find the MOST RELEVANT ones to include as context when the LLM answers a question."

**💡 Why this matters:** "Without vector search, your AI chatbot can only answer questions from its training data (generic internet knowledge). WITH vector search, it can answer questions about PepsiCo's internal policies, product specs, incident reports — anything you've embedded."

---

## SLIDE 41 — Azure Data Services for AI

> "Where do you STORE these vectors? You have options:
>
> - **Azure SQL** — native VECTOR type (new!). T-SQL, enterprise-grade, familiar to your DBAs. Use `VECTOR(1536)` column type and `VECTOR_DISTANCE()` function. This is what we'll use in Lab 03.
>
> - **Azure Cosmos DB** — multi-model, globally distributed. DiskANN index for billion-scale vector search in <10ms. Great for applications needing global reach.
>
> - **Azure Database for PostgreSQL** — pgvector extension. Open-source, familiar to developers. Good for teams already on PostgreSQL.
>
> - **Azure AI Search** — hybrid search (keyword + vector + semantic ranking). Best for document-heavy scenarios where you want the best of both approaches.
>
> Today we're using **Azure SQL** because it's the most familiar to enterprise teams — same T-SQL you already know, just with a new data type."

---

## SLIDE 42 — RAG Architecture Pattern

> "Here's the RAG pattern — this is how ChatGPT + Enterprise Data actually works:
>
> **Step 1:** User asks: 'What's our return policy for damaged goods in APAC?'
>
> **Step 2:** That question gets converted to a vector (1536 numbers)
>
> **Step 3:** Vector search finds the top 5 most relevant document chunks from your policy database — regardless of exact wording
>
> **Step 4:** Those 5 chunks get stuffed into the LLM's prompt as context: 'Based on the following documents, answer the user's question...'
>
> **Step 5:** The LLM generates a precise answer WITH citations: 'According to Policy Doc APAC-2024-RET section 3.2, damaged goods can be returned within 30 days with inspection report...'
>
> **Why this is better than fine-tuning:**
> - No retraining when documents change — just update the vector store
> - Always uses the LATEST data
> - You can see exactly WHICH documents informed the answer (auditability)
> - Works with any LLM — swap models without rebuilding"

**💡 PepsiCo applications:** Product knowledge bases, HR policy Q&A, supplier contract analysis, quality incident search, formula/recipe retrieval.

---

## SLIDE 43 — Lab 03 Slide

> "Lab 03: **Vector Search on Azure SQL**. This is the most technically satisfying lab.
>
> What you'll do:
> 1. **Explore the database** — see a table with a VECTOR(1536) column alongside normal text columns
> 2. **Generate embeddings** — call Azure OpenAI's embedding endpoint to convert text → vectors
> 3. **Load vectors** — insert them into the SQL table
> 4. **Semantic search with T-SQL** — use `VECTOR_DISTANCE()` to find similar documents. You'll see how 'soda shortage' finds results about 'beverage inventory depletion'
> 5. **Python retrieval script** — build a mini RAG pipeline: query → embed → search → return results
>
> ~45 minutes. This lab shows you the BUILDING BLOCKS of every enterprise AI chatbot."

🕐 **[LAB TIME — ~45 min]**

---

## SLIDE 44 — Session 4 Divider: Data Governance & Security

> "Final session — **Data Governance**. I know governance isn't the sexiest topic, but here's why it matters MORE now than ever: you're about to give AI agents access to your data. If you can't control who sees what, track what data was accessed, and enforce compliance policies — you have a security nightmare.
>
> Governance isn't the thing that slows you down. It's the thing that lets you go FAST with confidence."

---

## SLIDE 45 — Unified Data Governance

> "The governance stack in Fabric:
> - **Microsoft Purview** — data cataloging, classification, lineage, compliance
> - **OneLake Catalog** — discovery UI within Fabric, search for any data asset
> - **Sensitivity labels** — from Microsoft 365, applied to data (not just documents)
> - **Capacity admin** — resource governance, usage monitoring, cost control
>
> All integrated. Not 4 separate products — one unified experience."

---

## SLIDE 46 — OneLake Catalog

> "The OneLake Catalog is your **data Google** — a single place to find any data in the organization.
>
> Three audiences:
> 1. **Developers and data engineers** — find tables, understand schemas, check quality metrics
> 2. **Data stewards** — manage policies, monitor compliance, track lineage
> 3. **Business users** — discover datasets in Teams/Excel, understand what data is available
>
> The key insight: if people can't FIND data, they create their own copies. Data proliferation → inconsistency → governance breakdown. The catalog solves discovery, which prevents proliferation."

---

## SLIDE 47 — Fabric Platform + Governance

> "Every single workload in Fabric — Databases, Data Factory, Analytics, RTI, Power BI, Fabric IQ — inherits the SAME governance model. Set a sensitivity label on a lakehouse table → that label follows the data into Power BI reports, notebook outputs, and API responses. No gaps."

---

## SLIDE 48 — The Challenge: Culture vs. Control

> "The classic tension: IT wants control (lock everything down). Business wants freedom (give me access now).
>
> Fabric's approach: **govern by default, empower by policy**. Everything has a baseline of security, but you can create policies that grant access automatically based on role, purpose, and classification level. So data teams aren't filing tickets and waiting 2 weeks — they get access instantly if they meet the criteria."

---

## SLIDE 49 — OneLake Catalog Security

> "Three security layers:
>
> 1. **Network security** — private endpoints, managed VNets. Sensitive data never touches the public internet. Always-on, not opt-in.
>
> 2. **Access control** — granular at every level:
>    - Item level: who can see this lakehouse?
>    - Folder level: who can access this folder in OneLake?
>    - Row level: sales reps only see their region's data
>    - Column level: SSNs visible only to HR, masked for everyone else
>
> 3. **Governance policies** — automated enforcement. 'All tables with PII must have sensitivity labels.' 'No data can leave this geography.' Fabric monitors and alerts on violations."

---

## SLIDE 50 — Fabric Platform (Governance Focus)

> "Notice the Admin & Governance layer at the bottom of the Fabric architecture. This isn't an afterthought — it's the FOUNDATION. Security and governance are built into the platform, not products you buy separately and try to integrate."

---

## SLIDE 51 — OneLake Unifies (Governance Context)

> "From a governance perspective, the unification story is even more powerful. Whether your data is:
> - In a Fabric lakehouse
> - Mirrored from Snowflake
> - Shortcutted from AWS S3
> - In a Databricks Unity Catalog
>
> OneLake provides **ONE catalog** to discover it, **ONE lineage graph** to trace it, and **ONE policy engine** to govern it. Your compliance team doesn't need to learn 5 different tools."

---

## SLIDE 52 — Shortcuts and Mirroring (Deep Dive)

> "Let me go deeper on these two technologies because they're game-changers for governance:
>
> **Shortcuts:**
> - Symbolic links (like symlinks in Linux)
> - Zero data movement, zero storage cost
> - But governance still applies! Even though data stays in S3, your Fabric permissions and sensitivity labels govern access
> - Supports: ADLS Gen2, AWS S3, GCP Cloud Storage, cross-tenant OneLake, Dataverse
>
> **Mirroring:**
> - Near-real-time replicas of operational databases into OneLake
> - Uses CDC (Change Data Capture) — only moves deltas, not full copies
> - Currently supports: Azure SQL, Azure SQL MI, Cosmos DB, Snowflake, Databricks, PostgreSQL
> - Coming soon: SQL Server 2025, Oracle, Dataverse
> - **Free included storage** up to a limit — you don't pay extra for mirrored data
>
> Key benefit: your operational databases stay operational (no query load from analytics), but analytics gets fresh data in near-real-time. Best of both worlds."

---

## SLIDE 53 — Live Demo: Purview + OneLake Catalog

> "Let me show you this in action. I'll demonstrate three things:
>
> 1. **Purview Data Map** — how it auto-discovers and classifies data across your entire estate. I'll show how it finds PII columns (email, phone, SSN) and applies sensitivity labels automatically.
>
> 2. **OneLake Catalog** — I'll search for a dataset, show you the schema, quality metrics, who owns it, and what reports consume it.
>
> 3. **Data Lineage** — I'll trace a single metric from the Power BI report all the way back through the semantic model, through the transformation pipeline, to the raw source. End-to-end visibility.
>
> This is how you answer: 'Where did this number come from?' in 30 seconds instead of 3 days."

🎬 **[LIVE DEMO — ~15 min]**

---

## Timing Guide

| Time | Section | Duration |
|------|---------|----------|
| 9:00 AM | Session 1: Fabric (Slides 1-19) | 35 min |
| 9:35 AM | Lab 01: Lakehouse + Data Agent | 45 min |
| 10:20 AM | Break | 10 min |
| 10:30 AM | Session 2: Fabric IQ + RTI (Slides 21-37) | 35 min |
| 11:05 AM | Lab 02: Real-Time Intelligence | 45 min |
| 11:50 AM | Lunch | 45 min |
| 12:35 PM | Session 3: Data Services + AI (Slides 39-42) | 20 min |
| 12:55 PM | Lab 03: Vector Search | 45 min |
| 1:40 PM | Break | 10 min |
| 1:50 PM | Session 4: Governance (Slides 44-52) | 25 min |
| 2:15 PM | Demo: Purview + Catalog (Slide 53) | 15 min |
| 2:30 PM | Lab 04: Databricks AutoML + MCP Agent | 45 min |
| 3:15 PM | Wrap-up & Q&A | 15 min |

---

## Delivery Tips

**Energy management:**
- Highest energy: Slides 5, 14, 23, 40, 42 (the "aha" slides)
- Conversational tone: Slides 8, 15, 25 (concept explanations)
- Let the audience absorb: after Slides 23, 40 — pause 5 seconds before continuing

**Audience engagement:**
- After Slide 4: "Show of hands — how many tools does YOUR team stitch together today?"
- After Slide 23: "Has anyone here experienced conflicting metric definitions across teams?"
- After Slide 40: "Who's tried to build a search feature and found keyword matching falls short?"

**PepsiCo contextualization:**
- Whenever you say "your business" → make it concrete: "your bottling lines", "your distribution network", "your SKU portfolio"
- Reference real pain points: demand forecasting, supply chain visibility, quality monitoring
- Don't talk about Fabric in abstract — talk about what it DOES for CPG operations

**Lab transitions:**
- Don't just say "start the lab" — walk them through the FIRST step
- Stay standing and walk the room during labs
- Give 5-minute warnings before time runs out
- Have the next slide ready to go when they come back

**If you get tough questions:**
- "How is this different from Databricks?" → "Fabric is SaaS with built-in governance and Power BI. Databricks is infrastructure you manage. Different philosophy — we'll actually use Databricks in Lab 04 alongside Fabric."
- "We already have Snowflake" → "Great — Fabric mirrors Snowflake data in near-real-time via OneLake. You don't have to migrate. You ADD Fabric capabilities on top."
- "What about cost?" → "One capacity, predictable pricing. No per-query surprises. Auto-pause when idle. Your labs today run on a shared F64 capacity."
