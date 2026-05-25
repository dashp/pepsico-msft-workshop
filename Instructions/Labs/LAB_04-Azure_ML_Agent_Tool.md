# Lab 04: Azure Machine Learning — Train, Deploy & Wrap as Agent Tool

## Lab introduction

In this lab you learn to train a classical machine-learning model in **Azure Machine Learning (AML)**, register it in the **model registry**, deploy it to a **managed online endpoint**, and finally wrap the scoring call as a Python function that Day 2 exposes as the `predict_quality` agent tool.

This lab requires an Azure subscription. The steps are written using **East US 2**.

## Estimated timing: 50 minutes

## Lab scenario

Your data-science team has a small tabular model that predicts product-quality class from process telemetry. The model is realistic but the dataset is intentionally tiny so you can train it in a few minutes. The end goal is not the model — it is the **deployment contract**: a stable, authenticated REST endpoint your agents can call from anywhere.

> **Time-saver**: If your endpoint deployment is still rolling out at the 35-minute mark, switch to the shared endpoint `mlep-pepsi-quality-shared` provided by the workshop team. The contract is identical.

## Architecture diagram

![Diagram of the AML tasks.](../media/lab04-architecture.png)

## Job skills

- Task 1: Connect to the shared AML workspace.
- Task 2: Train and register a model from a notebook.
- Task 3: Deploy a managed online endpoint.
- Task 4: Score the endpoint from CLI and Python.
- Task 5: Wrap scoring as the `predict_quality` agent tool.

---

## Task 1: Connect to the shared AML workspace

In this task, you will attach to the shared AML workspace pre-provisioned for the workshop (each team trains and deploys into the same workspace under a team-scoped name).

1. Sign in to **Azure Machine Learning Studio** — `https://ml.azure.com`.

2. From the workspace picker, select:

    | Setting | Value |
    |---|---|
    | Subscription | the workshop subscription |
    | Resource group | `rg-pepsi-shared` |
    | Workspace | `aml-pepsi-shared` |

3. Confirm the **Overview** blade loads and **Compute** shows at least one running cluster (`cpu-cluster`).

    ![Screenshot of the AML workspace overview.](../media/lab04-task1-workspace.png)

4. From a terminal on your laptop, log in and bind the AML CLI extension:

    ```bash
    az login
    az account set --subscription <subId>
    az extension add -n ml -y
    az configure --defaults group=rg-pepsi-shared workspace=aml-pepsi-shared
    ```

---

## Task 2: Train and register a model from a notebook

1. In the AML Studio, open **Notebooks** and upload `Allfiles/lab04/train_register.ipynb` from the workshop repo (or create a new notebook with the same content).

2. Attach the notebook to a **compute instance** (create one if needed; the smallest SKU is fine).

3. Run all cells. The notebook does the following:

    ```python
    from sklearn.datasets import load_wine
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    import joblib, mlflow

    X, y = load_wine(return_X_y=True, as_frame=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    mlflow.sklearn.autolog()
    with mlflow.start_run(run_name="rf-wine-quality"):
        model = RandomForestClassifier(n_estimators=120, max_depth=8, random_state=42)
        model.fit(X_tr, y_tr)
        acc = model.score(X_te, y_te)
        mlflow.log_metric("test_accuracy", acc)
        joblib.dump(model, "model.joblib")
    print(f"test accuracy: {acc:.3f}")
    ```

4. After the run completes, register the model from the notebook (or with the CLI):

    ```bash
    az ml model create \
      --name quality-model-team01 \
      --version 1 \
      --path model.joblib \
      --type custom_model
    ```

5. In the Studio, navigate to **Models** and confirm `quality-model-team01` is listed at version 1.

    ![Screenshot of the registered model.](../media/lab04-task2-model.png)

---

## Task 3: Deploy a managed online endpoint

1. From the workshop repo `Allfiles/lab04/`, open the two deployment files:

    `endpoint.yml`
    ```yaml
    $schema: https://azuremlschemas.azureedge.net/latest/managedOnlineEndpoint.schema.json
    name: mlep-pepsi-quality-team01
    auth_mode: key
    ```

    `deployment.yml`
    ```yaml
    $schema: https://azuremlschemas.azureedge.net/latest/managedOnlineDeployment.schema.json
    name: blue
    endpoint_name: mlep-pepsi-quality-team01
    model: azureml:quality-model-team01:1
    code_configuration:
      code: ./
      scoring_script: score.py
    environment:
      conda_file: env.yml
      image: mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04
    instance_type: Standard_DS2_v2
    instance_count: 1
    ```

2. Create the endpoint and deployment:

    ```bash
    az ml online-endpoint create -f endpoint.yml
    az ml online-deployment create -f deployment.yml --all-traffic
    ```

    > **Note**: The first deployment takes 8–12 minutes (image pull + container start). If you are short on time, switch to `mlep-pepsi-quality-shared` for Task 4.

3. After provisioning, confirm:

    ```bash
    az ml online-endpoint show -n mlep-pepsi-quality-team01 \
        --query "{state:provisioning_state,uri:scoring_uri}"
    ```

    ![Screenshot of the deployed online endpoint.](../media/lab04-task3-endpoint.png)

---

## Task 4: Score the endpoint from CLI and Python

1. **CLI smoke test**:

    ```bash
    az ml online-endpoint invoke \
      --name mlep-pepsi-quality-team01 \
      --request-file sample_request.json
    ```

    Expected output:

    ```json
    { "predictions": [1] }
    ```

2. **Python client**: from `Allfiles/lab04/`, run:

    ```bash
    python score_client.py
    ```

    The script reads the endpoint URI + key from environment variables and prints a class label for a fixed payload.

    ![Screenshot of score_client.py output.](../media/lab04-task4-score.png)

3. Open `score_client.py` and note the function signature — it is the **tool contract**:

    ```python
    def predict_quality(features: dict) -> dict:
        """Returns {'prediction': int, 'probability': float}."""
    ```

---

## Task 5: Wrap scoring as the `predict_quality` agent tool

In this task, you will produce the function and metadata that Day 2's **Multi-Agent Orchestration with MAF** lab will consume.

1. Open `predict_quality.py` in `Allfiles/lab04/`. Confirm:
    - It reads endpoint URI + key from environment variables (no hard-coded secrets).
    - It validates that the input dict contains the 13 expected wine features.
    - It returns a stable JSON shape `{"prediction": int, "probability": float}`.

2. Run the unit smoke-test:

    ```bash
    python -m pytest tests/test_predict_quality.py -q
    ```

3. Export the tool metadata that Day 2 expects:

    ```bash
    python predict_quality.py --emit-schema > predict_quality.schema.json
    ```

    The emitted JSON conforms to the OpenAI function-calling schema and is the exact file Day 2 registers as an MCP tool.

    ![Screenshot of the generated tool schema.](../media/lab04-task5-schema.png)

---

## Review

In this lab you trained a model, registered it, deployed it to a managed online endpoint, and produced a Python function + JSON schema that Day 2 turns into a callable agent tool. The artefact that matters for the workshop is the **endpoint URI + the function contract**, both of which Sandeep's Day 2 labs will consume verbatim.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `az ml` command not found | CLI extension missing | `az extension add -n ml -y` |
| Deployment stuck at `Creating` >15 min | Image pull from MCR slow | Cancel and re-issue; or switch to the shared endpoint |
| `403 Forbidden` from endpoint | Wrong key / wrong endpoint URI | `az ml online-endpoint get-credentials -n <name>`; refresh env vars |
| `score_client.py` says "missing feature" | Payload column names don't match | Inspect `score.py` for expected column order; use the sample payload first |
| Model accuracy looks low (~0.6) | `random_state` not set | Re-run the notebook with `random_state=42` |

## Further reading

- [Azure ML — Managed online endpoints](https://learn.microsoft.com/azure/machine-learning/concept-endpoints)
- [Azure ML CLI v2 reference](https://learn.microsoft.com/cli/azure/ml)
- [MLflow with Azure ML](https://learn.microsoft.com/azure/machine-learning/how-to-use-mlflow-cli-runs)
- [Model deployment best practices](https://learn.microsoft.com/azure/machine-learning/how-to-deploy-online-endpoints)
