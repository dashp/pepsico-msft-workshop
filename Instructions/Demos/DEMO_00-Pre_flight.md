# Demonstration 00: Pre-flight (instructor setup)

## Demonstration introduction

This is an **instructor-only** pre-flight, run **at least 24 hours before delivery**. It provisions the Azure resources every team will use during the workshop, validates the Fabric capacity, and seeds shared Azure OpenAI and Azure Machine Learning artefacts.

Attendees do **not** run this; they receive a team id (`team01`, `team02`, …) and use the resources you create here.

## Estimated timing: 60 minutes (mostly waiting on Bicep + AML deploy)

## What you will set up

| Tier | Resource | Per team or shared |
|---|---|---|
| Per team | Resource group `rg-pepsi-ws-<team>` | per team |
| Per team | Storage (ADLS Gen2) `stpepsiws<team>` | per team |
| Per team | Azure SQL server + db | per team |
| Per team | Key Vault `kv-pepsi-ws-<team>` | per team |
| Shared | Azure OpenAI account `aoai-pepsi-shared` | shared |
| Shared | AML workspace `aml-pepsi-shared` | shared |
| Shared | AML fallback endpoint `mlep-pepsi-quality-shared` | shared |
| Shared | Fabric capacity (F2 or F4) | shared |

---

## Task 1: Prerequisites on the instructor laptop

1. Install the tools (or confirm versions):

    ```bash
    az --version              # 2.60+
    az extension add -n ml -y
    az bicep upgrade
    python --version          # 3.11+
    ```

2. Log in and select the workshop subscription:

    ```bash
    az login
    az account set --subscription <subId>
    az account show --query "{name:name, id:id}"
    ```

---

## Task 2: Provision per-team resources with Bicep

1. From the workshop repo, run the Bicep deployment **once per team** (loop is fine):

    ```bash
    cd workshop/infra

    for team in team01 team02 team03 team04 team05; do
      az deployment sub create \
        --name "pepsi-ws-$team" \
        --location eastus2 \
        --template-file main.bicep \
        --parameters team=$team location=eastus2 \
                     aadAdminLogin="<your-upn>" \
                     aadAdminObjectId="<your-objectId>"
    done
    ```

2. After all deployments succeed, confirm:

    ```bash
    az group list --query "[?starts_with(name,'rg-pepsi-ws-')].name" -o table
    ```

3. For each team, push the connection string and AOAI key into the team's Key Vault. The Bicep already created the secret slots — you only need to set the values:

    ```bash
    for team in team01 team02 team03 team04 team05; do
      kv="kv-pepsi-ws-$team"
      az keyvault secret set --vault-name $kv --name aoai-endpoint   --value "https://aoai-pepsi-shared.openai.azure.com"
      az keyvault secret set --vault-name $kv --name aoai-key        --value "<aoai-key>"
      az keyvault secret set --vault-name $kv --name sql-server-fqdn --value "sql-pepsi-ws-$team.database.windows.net"
    done
    ```

---

## Task 3: Validate the Fabric capacity

1. In the Fabric admin portal, open **Capacities** and confirm a running capacity with at least **F4** size (workshop default).

2. Assign the workshop capacity to the workspace template, or pre-create five workspaces (`ws-pepsi-ws-team01` … `team05`) and assign each to the capacity.

3. In each workspace, add the team's instructor email as **Admin** and the attendee group as **Contributor**.

---

## Task 4: Seed shared Azure OpenAI deployments

1. In the shared AOAI account `aoai-pepsi-shared`, confirm these deployments exist:

    | Deployment name | Model | Capacity (TPM) |
    |---|---|---|
    | `text-embedding-3-small` | text-embedding-3-small | 60 K |
    | `gpt-4o-mini` | gpt-4o-mini (2024-07-18) | 60 K |

2. If missing, create them:

    ```bash
    az cognitiveservices account deployment create \
      --name aoai-pepsi-shared \
      --resource-group rg-pepsi-shared \
      --deployment-name text-embedding-3-small \
      --model-name text-embedding-3-small \
      --model-version "1" \
      --model-format OpenAI \
      --sku-capacity 60 --sku-name Standard
    ```

---

## Task 5: Pre-deploy the AML fallback endpoint

The shared endpoint is a safety net for Lab 04 if a team's per-team deployment stalls.

1. From `Allfiles/lab04/`:

    ```bash
    az configure --defaults group=rg-pepsi-shared workspace=aml-pepsi-shared

    az ml model create --name quality-model-shared --version 1 \
        --path model.joblib --type custom_model
    az ml online-endpoint create -f endpoint-shared.yml
    az ml online-deployment create -f deployment-shared.yml --all-traffic
    ```

2. Smoke-test:

    ```bash
    az ml online-endpoint invoke \
      --name mlep-pepsi-quality-shared \
      --request-file sample_request.json
    ```

3. Publish the endpoint URI + key into every team's Key Vault as `aml-shared-uri` and `aml-shared-key`.

---

## Task 6: Final go / no-go checklist

- [ ] All teams' Bicep deployments finished without errors.
- [ ] `gold_sales` source CSVs are reachable from `raw.githubusercontent.com` (test with `curl`).
- [ ] AOAI shared deployments respond to a smoke `chat/completions` call.
- [ ] AML shared endpoint scores `sample_request.json` → returns `{ "predictions": [...] }`.
- [ ] Fabric capacity is running and the workspaces are visible to attendees.
- [ ] Every team's Key Vault has the four secrets populated.
- [ ] Day 2 owner (Sandeep) has been given the Fabric workspace IDs and the AML endpoint URIs.

If any item is **red**, escalate before the workshop opens.

## Further reading

- [Azure CLI for ML](https://learn.microsoft.com/cli/azure/ml)
- [Fabric admin portal & capacity management](https://learn.microsoft.com/fabric/admin/admin-overview)
- [Azure OpenAI quotas and limits](https://learn.microsoft.com/azure/ai-services/openai/quotas-limits)
