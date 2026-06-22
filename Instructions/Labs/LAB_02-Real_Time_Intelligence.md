# Lab 02: Real-Time Intelligence in Microsoft Fabric

## Lab introduction

In this lab you learn to build a **Real-Time Intelligence (RTI)** solution in Microsoft Fabric. You will create an **Eventhouse**, ingest a sample streaming source through an **Eventstream**, query the data using **KQL**, and build a **Real-Time Dashboard** with a **data activator alert**.

This lab requires a Microsoft Fabric capacity. You may change the region, but the steps are written using **Sweden Central**.

## Prerequisites — verify before you start

- [ ] You completed **Lab 01** (you have a workspace `ws-pepsi-<yourName>` bound to a Fabric capacity).
- [ ] You can sign in to `https://app.fabric.microsoft.com` with your workshop account.

## Estimated timing: 35 minutes (+ 15 min concepts intro)

## Concepts: Fabric IQ, Real-Time Intelligence & Data Agent

> **Trainer**: Use this section as the 15-minute talk before going hands-on. Cover the "why" before the "how."

### What is Fabric IQ?

Fabric IQ is Microsoft's **semantic layer for enterprise data** — it lets business users ask natural-language questions over governed data assets without writing code. It builds on:

- **Direct Lake semantic models** (you built one in Lab 01)
- **Copilot in Fabric** — NL queries over tables and reports
- **Data Agents** — grounded NL→SQL assistants (you built one in Lab 01)

**Key point for PepsiCo**: Fabric IQ is the convergence point where governed data meets natural language — the "last mile" between data engineers and business users.

### What is Real-Time Intelligence?

RTI is Fabric's streaming analytics engine — purpose-built for high-volume, low-latency event data:

| Component | What it does | Analogy (AWS) |
|---|---|---|
| **Eventstream** | Ingest + route streaming data (no-code) | Kinesis Data Firehose |
| **Eventhouse** | Columnar time-series store optimized for append-heavy writes | Amazon Timestream / Kinesis Data Analytics |
| **KQL Database** | Query engine using Kusto Query Language (filter/aggregate/render) | CloudWatch Logs Insights / Athena on streaming |
| **Real-Time Dashboard** | Live-updating visuals on top of KQL queries | CloudWatch Dashboards / Grafana |
| **Data Activator** | Rule-based alerts triggered by streaming data conditions | CloudWatch Alarms / EventBridge rules |

### How RTI fits with Data Agent + Power BI

```
Streaming source → Eventstream → Eventhouse (KQL DB)
                                       ↓
                              Real-Time Dashboard (live)
                                       ↓
                              Data Activator (alerts)

Batch source → Lakehouse (Gold) → Semantic Model → Power BI Report
                                       ↓
                              Fabric Data Agent (NL queries)
```

**RTI handles the "right now" questions; Lakehouse handles the "what happened" questions.** Together they give PepsiCo both real-time operational visibility and historical analytics.

### When to use RTI vs Lakehouse

| Use RTI when… | Use Lakehouse when… |
|---|---|
| Data arrives continuously (IoT, POS, telemetry) | Data arrives in batches (daily feeds, CSVs) |
| You need sub-second query freshness | Minutes/hours latency is acceptable |
| You need alerts on live thresholds | You need DAX measures + Power BI reports |
| Query language: KQL | Query language: Spark SQL / T-SQL / DAX |

---

## Lab scenario

Your retail operations team needs near-real-time visibility into in-store events (bike-share telemetry is used as a stand-in for any IoT signal — imagine store foot traffic, cooler temperature, or shelf-stock sensors). You will land that stream in Fabric, run analytic queries on live data, and raise an alert when a threshold is breached.

## Architecture diagram

![Diagram of the RTI tasks.](../media/lab02-architecture.png)

## Job skills

- Task 1: Create an Eventhouse and KQL database.
- Task 2: Create an Eventstream and bind it to a destination table.
- Task 3: Explore the data with KQL.
- Task 4: Build a Real-Time Dashboard and a data activator alert.
- Task 5: Validate your work.

---

## Task 1: Create an Eventhouse and KQL database

In this task, you will create an Eventhouse — the storage tier for streaming data in Fabric.

1. Sign in to the **Microsoft Fabric portal** — `https://app.fabric.microsoft.com`.

2. Open the workspace you created in Lab 01 (`ws-pepsi-<yourName>`).

3. Click **+ New item**, search for **Eventhouse**, and select it.

4. **Name** the Eventhouse `eh_pepsi_rti` and click **Create**.

    ![Screenshot of the Create Eventhouse pane.](../media/lab02-task1-create-eventhouse.png)

5. After the Eventhouse opens, the default KQL database `eh_pepsi_rti` is created automatically. Note the **Query URI** in the **Database details** card — you will use it from KQL queries.

---

## Task 2: Create an Eventstream and bind it to a destination table

In this task, you will create an Eventstream that reads from the **Bicycles** sample source and writes to a Delta-backed KQL table.

1. From the workspace, click **+ New item**, search for **Eventstream**, and select it.

2. **Name** the Eventstream `es_pepsi_bikes` and click **Create**.

3. In the Eventstream canvas, click **Use sample data**, then choose **Bicycles**. Click **Add**.

    ![Screenshot of the Eventstream sample data picker.](../media/lab02-task2-sample-source.png)

4. From the source node, drag a connection to a new **destination** node. In the destination dialog, specify:

    | Setting | Value |
    |---|---|
    | Destination type | **Eventhouse** |
    | Workspace | `ws-pepsi-<yourName>` |
    | Eventhouse | `eh_pepsi_rti` |
    | Destination table | `bikes_raw` (create new) |
    | Input data format | **JSON** |

5. Click **Save**, then **Publish** the Eventstream.

    ![Screenshot of the published Eventstream graph.](../media/lab02-task2-published.png)

6. In the Eventstream **Data preview** tab, confirm rows are arriving every few seconds.

---

## Task 3: Explore the data with KQL

In this task, you will query the streaming data with KQL.

1. From the workspace, open the `eh_pepsi_rti` Eventhouse. Click **Explore your data** to open the KQL query editor.

2. Run each query in turn and observe the result.

    ```kusto
    bikes_raw
    | take 10
    ```

    ```kusto
    bikes_raw
    | summarize Bikes = sum(No_Bikes), Empty = sum(No_Empty_Docks) by Neighbourhood
    | top 10 by Bikes desc
    ```

    ```kusto
    bikes_raw
    | summarize avg_bikes = avg(No_Bikes) by bin(EventProcessedUtcTime, 1m), Neighbourhood
    | render timechart
    ```

    ![Screenshot of a KQL timechart.](../media/lab02-task3-timechart.png)

3. Pin the third query result to a new dashboard when prompted, or save the query for Task 4.

---

## Task 4: Build a Real-Time Dashboard and a data activator alert

In this task, you will assemble a one-page dashboard and raise an alert when a neighbourhood runs out of bikes.

1. From the workspace, click **+ New item**, search for **Real-Time Dashboard**, name it `rtd_pepsi_bikes`, and click **Create**.

2. Add a **data source** pointing at the `eh_pepsi_rti` KQL database.

3. Click **+ Add tile**. Paste the following query and click **Apply**:

    ```kusto
    bikes_raw
    | summarize Bikes = sum(No_Bikes) by Neighbourhood
    | top 5 by Bikes desc
    ```

4. Change the visualization to **Bar chart**, save the tile, then add a second tile:

    ```kusto
    bikes_raw
    | summarize avg_bikes = avg(No_Bikes) by bin(EventProcessedUtcTime, 30s)
    | render timechart
    ```

5. Click **Save** to persist the dashboard.

    ![Screenshot of the published Real-Time Dashboard.](../media/lab02-task4-dashboard.png)

6. From the dashboard header, click **Set alert**. Configure:

    | Setting | Value |
    |---|---|
    | Activator | Use the default activator in this workspace |
    | Condition | When `Bikes` is **less than** `1` |
    | Action | **Email me** |

7. Click **Create**. When a neighbourhood empties, you receive an email.

    ![Screenshot of the Data Activator alert dialog.](../media/lab02-task4-alert.png)

---

## Task 5: Validate your work

Confirm each item below before moving on.

- [ ] Eventhouse `eh_pepsi_rti` exists with a KQL database.
- [ ] Eventstream `es_pepsi_bikes` is published and data is flowing (preview shows rows).
- [ ] KQL `bikes_raw | take 10` returns rows.
- [ ] Real-Time Dashboard `rtd_pepsi_bikes` shows a bar chart and a timechart.
- [ ] Data Activator alert is configured.

✅ **Lab 02 complete** — you now have a working Real-Time Intelligence pipeline. Continue to [**Lab 03 — Vector Search**](./LAB_03-Vector_Search.md).

---

## Review

In this lab you stood up an Eventhouse, ingested a live stream via Eventstream, queried it with KQL, built a Real-Time Dashboard, and wired up a Data Activator alert. The same building blocks apply to any sensor, POS, or transactional stream your team brings into Fabric.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Eventstream "no data" | Sample source paused | In the canvas, select the source node → **Start** |
| `bikes_raw` table missing | Destination not published | Re-open the Eventstream and click **Publish** |
| KQL query returns 0 rows | Table name mismatch | In the explorer, confirm the table name and quote-case match exactly |
| Alert email not received | Activator action not configured | Open the activator → confirm **Email** action is **Enabled** |

## Further reading

- [Real-Time Intelligence in Microsoft Fabric](https://learn.microsoft.com/fabric/real-time-intelligence/overview)
- [Eventhouse overview](https://learn.microsoft.com/fabric/real-time-intelligence/eventhouse)
- [KQL quick reference](https://learn.microsoft.com/kusto/query/)
- [Data Activator](https://learn.microsoft.com/fabric/data-activator/data-activator-introduction)
