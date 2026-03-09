# Azure AI DevOps Agent

An autonomous, AI-powered agent designed to integrate with Azure DevOps. This agent leverages Azure OpenAI to perform intelligent DevOps tasks like PR analysis, pipeline failure diagnosis, and automated incident triage.

## Features

- **PR Analysis**: Automatically reviews Pull Requests for security issues, bugs, and performance.
- **Pipeline Failure Diagnosis**: Analyzes build logs when a pipeline fails and suggests fixes.
- **Incident Triage**: Automatically categorizes and assigns new work items based on description.
- **Deployment Assistant**: Validates environments before deployment.

## Tech Stack

- **Backend**: Python (FastAPI)
- **AI**: Azure OpenAI Service (GPT-4o)
- **Identity**: Azure Managed Identity
- **Integration**: Azure DevOps REST API

## Setup

1. **Environment Variables**:
   Create a `.env` file with the following:
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your-api-key
   AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
   AZURE_DEVOPS_PAT=your-pat (for local dev, use Managed Identity in production)
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Locally**:
   ```bash
   uvicorn src.main:app --reload
   ```

## Azure Deployment

This agent is designed to run in **Azure Functions** or **Azure App Service**.
Infrastructure templates can be found in the `infra/` directory.

## Webhook Configuration

Configure Azure DevOps Webhooks to point to the `/webhook` endpoint of this agent:
- **Git Pull Request Created/Updated** -> `/webhook/pr`
- **Build Completed** -> `/webhook/build`
- **Work Item Created** -> `/webhook/workitem`
- **Deployment Validation** -> `/webhook/deployment`

## Testing

For detailed instructions on how to test the AI features locally using simulations, refer to the [HELP.md](./HELP.md) file.
