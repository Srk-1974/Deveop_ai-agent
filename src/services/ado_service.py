import os
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.git.models import GitPullRequestCommentThread, Comment
from azure.devops.v7_1.build.build_client import BuildClient

from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation

class ADOService:
    def __init__(self):
        self.org_url = os.getenv("AZURE_DEVOPS_ORG_URL")
        self.pat = os.getenv("AZURE_DEVOPS_PAT")
        self.connection = Connection(base_url=self.org_url, creds=BasicAuthentication('', self.pat))
        self.git_client = self.connection.clients.get_git_client()
        self.build_client = self.connection.clients.get_build_client()
        self.work_item_client = self.connection.clients.get_work_item_tracking_client()

    def get_pr_changes(self, project, repo_id, pr_id):
        """Fetches the actual file changes for a Pull Request."""
        return self.git_client.get_pull_request_changes(repo_id, pr_id, project=project)

    def post_pr_comment(self, repo_id, pr_id, message):
        """Posts a top-level comment to a Pull Request."""
        thread = GitPullRequestCommentThread(
            comments=[Comment(content=message, comment_type="text")],
            status="active"
        )
        return self.git_client.create_thread(thread, repo_id, pr_id)

    def get_build_log_content(self, project, build_id):
        """Fetches the actual text content of the build logs."""
        logs = self.build_client.get_build_logs(project, build_id)
        if not logs:
            return "No logs found."
        
        # In a real scenario, we'd iterate through logs and fetch the content of the failed step
        # For now, we'll return a concatenated string of log metadata or the first log's content
        log_content = ""
        for log in logs[:3]: # Limit to first 3 log files for brevity
            content = self.build_client.get_build_log(project, build_id, log.id)
            log_content += f"--- Log {log.id} ---\n{content}\n"
        return log_content

    def get_work_item(self, id):
        """Fetches details of a work item."""
        return self.work_item_client.get_work_item(id)

    def update_work_item(self, id, priority, area_path, tags=None):
        """Updates work item priority and tags."""
        patch_document = [
            JsonPatchOperation(
                op="add",
                path="/fields/Microsoft.VSTS.Common.Priority",
                value=int(priority)
            )
        ]
        
        if tags:
            patch_document.append(
                JsonPatchOperation(
                    op="add",
                    path="/fields/System.Tags",
                    value=tags
                )
            )

        return self.work_item_client.update_work_item(patch_document, id)

    def get_environment_config(self, project, env_id):
        """Mock fetching environment variables/config for validation."""
        # In real ADO, you would call get_environment or release definitions
        return {
            "name": "Production-Retail-Web",
            "region": "East US",
            "sku": "Premium_V3",
            "settings": {
                "NODE_ENV": "production",
                "DB_PLATFORM": "AzureSQL",
                "AUTOSCALE": "Enabled"
            }
        }

    def post_deployment_report(self, project, release_id, report):
        """Mock posting a validation report back to the release/deployment."""
        # Real logic would use release_client.create_release_abandoned_comment or similar
        print(f"POSTING REPORT TO RELEASE {release_id} in {project}:\n{report}")
        return True
