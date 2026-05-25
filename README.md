# PepsiCo × Microsoft — Data & AI Workshop (Day 1)

This repository contains the hands-on labs and demos for the **Day 1 Data + Data Science** track of the PepsiCo × Microsoft technical workshop. The site is published to GitHub Pages and rendered with Jekyll, in the same style as the Microsoft Learning catalogs (e.g. AZ-104).

🌐 **Live site:** `https://<your-org>.github.io/pepsico-msft-workshop/`

## Repository layout

```
workshop/
├── index.md                       # Landing page (catalog of labs)
├── _config.yml                    # Jekyll config
├── Gemfile
├── .github/workflows/pages.yml    # Build + deploy to GitHub Pages
├── Instructions/
│   ├── Labs/
│   │   ├── LAB_01-Fabric_Lakehouse_Data_Agent.md
│   │   ├── LAB_02-Real_Time_Intelligence.md
│   │   ├── LAB_03-Vector_Search_Azure_SQL.md
│   │   └── LAB_04-Azure_ML_Agent_Tool.md
│   ├── Demos/
│   │   ├── DEMO_00-Pre_flight.md
│   │   └── DEMO_01-Purview_Fabric_IQ.md
│   └── media/                     # Screenshots referenced by labs
├── Allfiles/                      # Sample CSVs, notebooks, scripts
│   ├── lab01/
│   ├── lab03/
│   └── lab04/
└── infra/                         # Bicep templates (one team per deployment)
    ├── main.bicep
    └── modules/
```

## Run the site locally

```bash
cd workshop
bundle install
bundle exec jekyll serve
# → http://127.0.0.1:4000/
```

## Provision a team environment

```bash
az login
az account set --subscription <subId>

az deployment sub create \
  --name pepsi-ws-team01 \
  --location eastus2 \
  --template-file infra/main.bicep \
  --parameters team=team01 location=eastus2
```

## Hand-off to Day 2 (Sandeep)

| From | Artifact | Used in Day 2 lab |
|---|---|---|
| LAB 01 | Fabric Data Agent grounded on curated Lakehouse | *Agentic RAG with Foundry IQ + Data Agent + Tools* |
| LAB 03 | `retrieve_documents` over Azure SQL VECTOR | *Create an MCP Server* |
| LAB 04 | `predict_quality` over AML managed online endpoint | *Multi-Agent Orchestration with MAF* |

## License

Workshop content © Microsoft. Sample data is synthetic.
