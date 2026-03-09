import json
from fastapi import FastAPI, Request, BackgroundTasks
import logging
from dotenv import load_dotenv

load_dotenv()

from .services.ado_service import ADOService
from .services.ai_service import AIService

from fastapi.responses import FileResponse
import os

app = FastAPI(title="Azure AI DevOps Agent")

# Initialize services with error handling
try:
    ado_service = ADOService()
except Exception as e:
    logging.warning(f"Could not initialize ADOService: {e}")
    ado_service = None

try:
    ai_service = AIService()
except Exception as e:
    logging.warning(f"Could not initialize AIService: {e}")
    ai_service = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory storage for frontend activity log
activity_log = []

def log_activity(event_type, message, status="info"):
    activity_log.append({
        "type": event_type,
        "message": message,
        "status": status,
        "timestamp": "Just now" # Replace with real time if needed
    })
    if len(activity_log) > 50:
        activity_log.pop(0)

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/api/status")
def get_status():
    return {"status": "online", "agent": "Azure AI DevOps Agent", "activity": activity_log}

@app.post("/webhook/pr")
async def handle_pr_webhook(request: Request, background_tasks: BackgroundTasks):
    """Triggered when a PR is created or updated."""
    payload = await request.json()
    resource = payload.get("resource", {})
    pr_id = resource.get("pullRequestId")
    repo_id = resource.get("repository", {}).get("id")
    title = resource.get("title")
    description = resource.get("description", "")

    if pr_id and repo_id:
        project = payload.get("resourceContainers", {}).get("project", {}).get("id")
        logger.info(f"Processing PR #{pr_id} in repo {repo_id}")
        log_activity("PR_RECEIVED", f"New PR #{pr_id}: {title}", "success")
        background_tasks.add_task(process_pr_review, project, repo_id, pr_id, title, description)
    
    return {"status": "accepted"}

async def process_pr_review(project, repo_id, pr_id, title, description):
    try:
        changes = ado_service.get_pr_changes(project, repo_id, pr_id)
        # Simplify changes for the AI (convert to a string description)
        change_summary = str(changes.changes)[:5000] # Truncate for safety
        
        analysis = ai_service.analyze_pr(title, description, change_summary)
        ado_service.post_pr_comment(repo_id, pr_id, analysis)
        
        logger.info(f"Commented on PR #{pr_id}")
        log_activity("PR_REVIEWED", f"AI Review posted for PR #{pr_id}", "success")
    except Exception as e:
        logger.error(f"Error processing PR review: {e}")
        log_activity("PR_ERROR", f"Failed to review PR #{pr_id}: {str(e)}", "error")

@app.post("/webhook/build")
async def handle_build_webhook(request: Request, background_tasks: BackgroundTasks):
    """Triggered when a build completes (on failure)."""
    payload = await request.json()
    resource = payload.get("resource", {})
    status = resource.get("status")
    result = resource.get("result")
    build_id = resource.get("id")
    project = payload.get("resourceContainers", {}).get("project", {}).get("id")

    if result == "failed":
        logger.info(f"Build #{build_id} failed. Starting diagnosis...")
        log_activity("BUILD_FAILED", f"Build failure detected: #{build_id}", "warning")
        background_tasks.add_task(process_build_failure, project, build_id)

    return {"status": "accepted"}

async def process_build_failure(project, build_id):
    try:
        logs = ado_service.get_build_log_content(project, build_id)
        diagnosis = ai_service.diagnose_build_failure(logs)
        # In a real app, we'd post this diagnosis back to ADO
        logger.info(f"Diagnosis for Build #{build_id}: {diagnosis}")
        log_activity("BUILD_DIAGNOSED", f"AI diagnosed failure in build #{build_id}", "success")
    except Exception as e:
        logger.error(f"Error diagnosing build: {e}")
        log_activity("BUILD_ERROR", f"Failed to diagnose build #{build_id}", "error")

@app.post("/webhook/workitem")
async def handle_workitem_webhook(request: Request, background_tasks: BackgroundTasks):
    """Triggered when a work item is created."""
    payload = await request.json()
    resource = payload.get("resource", {})
    wi_id = resource.get("id")
    fields = resource.get("fields", {})
    title = fields.get("System.Title")
    description = fields.get("System.Description", "")

    if wi_id:
        logger.info(f"Processing Work Item #{wi_id}: {title}")
        log_activity("WORKITEM_RECEIVED", f"New Work Item #{wi_id}: {title}", "success")
        background_tasks.add_task(process_workitem_triage, wi_id, title, description)
    
    return {"status": "accepted"}

async def process_workitem_triage(wi_id, title, description):
    try:
        triage_json = ai_service.triage_work_item(title, description)
        triage_data = json.loads(triage_json)
        
        priority = triage_data.get("priority", 3)
        area = triage_data.get("area", "General")
        reasoning = triage_data.get("reasoning", "")
        
        # Update work item in ADO
        tags = f"AI_Triaged; {area}"
        ado_service.update_work_item(wi_id, priority, area, tags)
        
        logger.info(f"Triaged Work Item #{wi_id} as {area} (P{priority})")
        log_activity("WORKITEM_TRIAGED", f"Work Item #{wi_id} triaged: {area} (P{priority})", "success")
    except Exception as e:
        logger.error(f"Error triaging work item: {e}")
        log_activity("WORKITEM_ERROR", f"Failed to triage Work Item #{wi_id}", "error")

@app.post("/webhook/deployment")
async def handle_deployment_webhook(request: Request, background_tasks: BackgroundTasks):
    """Triggered when a deployment approval is requested or started."""
    payload = await request.json()
    resource = payload.get("resource", {})
    release_id = resource.get("release", {}).get("id")
    project = payload.get("resourceContainers", {}).get("project", {}).get("id")
    env_id = resource.get("environment", {}).get("id")

    if release_id:
        logger.info(f"Deployment validation requested for Release #{release_id}")
        log_activity("DEPLOYMENT_STARTED", f"Validation started for Release #{release_id}", "info")
        background_tasks.add_task(process_deployment_validation, project, release_id, env_id)
    
    return {"status": "accepted"}

async def process_deployment_validation(project, release_id, env_id):
    try:
        config = ado_service.get_environment_config(project, env_id)
        # Combine config into a string for AI
        config_summary = json.dumps(config, indent=2)
        
        # Mocking some recent logs for the AI to "analyze"
        mock_logs = "Health check: PASS. Traffic spike: NONE. Database Latency: 45ms. Security Patch Level: Current."
        
        validation_report = ai_service.validate_deployment(config.get("name"), config_summary, mock_logs)
        ado_service.post_deployment_report(project, release_id, validation_report)
        
        logger.info(f"Deployment validated for Release #{release_id}")
        status = "success" if "Go" in validation_report[:20] else "warning"
        log_activity("DEPLOYMENT_VALIDATED", f"AI Validation complete for Release #{release_id}", status)
    except Exception as e:
        logger.error(f"Error validating deployment: {e}")
        log_activity("DEPLOYMENT_ERROR", f"Failed to validate Release #{release_id}", "error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
