# 🧪 Testing & Operation Guide

This guide explains how to verify and test the **Azure AI DevOps Agent**.

## 1. Quick Start (Simulation Mode)

If you want to see the agent in action without connecting it to a live Azure DevOps project:

1.  **Start the Server**:
    ```powershell
    python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
    ```
2.  **Open Dashboard**: Go to [http://127.0.0.1:8000](http://127.0.0.1:8000).
3.  **Run Simulation Subscript**: In a separate terminal, run:
    ```powershell
    python test_agent.py
    ```
    *This script sends mock webhooks for PRs, Builds, Work Items, and Deployments. You will see the dashboard update immediately.*

---

## 2. Testing Specific Features

### Pull Request Analysis
*   **Endpoint**: `POST /webhook/pr`
*   **Test Script**: `test_pr_webhook()` in `test_agent.py`
*   **Expected Result**: AI analyzes the code diff and posts a markdown review.

### Build Failure Diagnosis
*   **Endpoint**: `POST /webhook/build`
*   **Test Script**: `test_build_webhook()` in `test_agent.py`
*   **Expected Result**: AI reads failed logs and suggests a fix in the Activity Log.

### Work Item Triage
*   **Endpoint**: `POST /webhook/workitem`
*   **Test Script**: `test_workitem_webhook()` in `test_agent.py`
*   **Expected Result**: AI categorizes the issue (e.g., "Security") and updates the priority.

### Deployment Validation
*   **Endpoint**: `POST /webhook/deployment`
*   **Test Script**: `test_deployment_webhook()` in `test_agent.py`
*   **Expected Result**: AI performs a "Go/No-Go" check on environment configuration.

---

## 3. Production Testing (Azure DevOps Integration)

To test with a real project:

1.  **Expose your Localhost**: Use a tool like `ngrok` to make your agent reachable from the internet:
    ```bash
    ngrok http 8000
    ```
2.  **Configure Service Hooks**:
    *   In Azure DevOps, go to **Project Settings > Service Hooks**.
    *   Create a new **Webhooks** subscription.
    *   Point it to your ngrok URL (e.g., `https://xyz.ngrok.app/webhook/pr`).
3.  **Trigger Actions**: Create a PR or fail a build in your ADO project to see the real AI response.

---

## 4. Troubleshooting

*   **App won't start?** Ensure your `.env` file exists (even with mock values).
*   **Dashboard missing data?** Check the terminal logs. If `ado_service` or `ai_service` failed to initialize, they will log a warning but the dashboard will still work.
*   **Port 8000 in use?** Run `taskkill /F /IM python.exe /T` to clear stuck processes.
