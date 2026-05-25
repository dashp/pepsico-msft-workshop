## Content Directory

Required lab files can be [DOWNLOADED HERE](https://github.com/pradiptadash/pepsico-msft-workshop/archive/main.zip)

## Labs

| Module | Lab |
|---|---|
| Microsoft Fabric Unified Platform | [Lab 01: Fabric Lakehouse + Data Agent](Instructions/Labs/LAB_01-Fabric_Lakehouse_Data_Agent.md) |
| Fabric IQ + RTI + Data Agent | [Lab 02: Real-Time Intelligence](Instructions/Labs/LAB_02-Real_Time_Intelligence.md) |
| Data Services + AI Integration | [Lab 03: Vector Search on Azure SQL](Instructions/Labs/LAB_03-Vector_Search_Azure_SQL.md) |
| Azure Machine Learning | [Lab 04: Azure ML — Train, Deploy & Wrap as Agent Tool](Instructions/Labs/LAB_04-Azure_ML_Agent_Tool.md) |

## Demonstrations

| Module | Demonstration |
|---|---|
| All | [Pre-flight (instructor setup)](Instructions/Demos/DEMO_00-Pre_flight.md) |
| Data Governance, Security & Fabric IQ | [Demonstration 01: Purview + Fabric IQ](Instructions/Demos/DEMO_01-Purview_Fabric_IQ.md) |

## Provisioning

A single Bicep deployment provisions all per-team Azure resources used by Labs 01–04. See [`infra/`](infra/) for the templates.

```bash
az login
az account set --subscription <subId>

az deployment sub create \
  --name pepsi-ws-team01 \
  --location eastus2 \
  --template-file infra/main.bicep \
  --parameters team=team01 location=eastus2
```

## Day 1 timing

| Block | Item | Duration |
|---|---|---:|
| Lecture | Microsoft Fabric Unified Platform | 25 m |
| **LAB 01** | Fabric Lakehouse + Data Agent | **60 m** |
| Lecture | Fabric IQ + RTI + Data Agent | 15 m |
| **LAB 02** | Real-Time Intelligence | **35 m** |
| Lecture | Data Services + AI Integration | 25 m |
| **LAB 03** | Vector search on Azure SQL | **50 m** |
| Lecture | Data Governance, Security & Fabric IQ | 20 m |
| **DEMO** | Purview + Fabric IQ | **25 m** |
| Lecture | Data Science Landscape | 15 m |
| Lecture | Azure Machine Learning | 20 m |
| **LAB 04** | Azure ML — agent tool | **50 m** |
| Lecture | MLOps, LLMops & Model Lifecycle | 20 m |
| | **Total** | **360 m** |

---

Sample data in this workshop is synthetic. No real PepsiCo data is used.
