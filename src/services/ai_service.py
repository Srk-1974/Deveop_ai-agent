import os
from openai import AzureOpenAI

class AIService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.model = os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4o")

    def analyze_pr(self, pr_title, pr_description, diffs):
        """Analyzes a PR diff and returns improvement suggestions."""
        prompt = f"""
        You are a senior Software Engineer and DevOps expert.
        Review the following Pull Request:
        Title: {pr_title}
        Description: {pr_description}
        
        Diff Content:
        {diffs}
        
        Provide a concise review. Focus on:
        1. Critical bugs or security issues.
        2. Performance bottlenecks.
        3. Readability and maintainability.
        
        Format your response as a markdown comment for Azure DevOps.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def diagnose_build_failure(self, error_logs):
        """Analyzes build logs to identify the root cause of a failure."""
        prompt = f"""
        Analyze the following build failure logs and identify the root cause.
        Provide a summary of the error and a suggested fix for the developer.
        
        Logs:
        {error_logs}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def triage_work_item(self, title, description):
        """Categorizes a work item and suggests an area/priority."""
        prompt = f"""
        You are a DevOps Triage Bot. Analyze the following work item:
        Title: {title}
        Description: {description}
        
        Categorize this issue into one of these areas:
        - Security
        - Infrastructure
        - Application Logic
        - Frontend
        - Documentation
        
        Also suggest a Priority (1-4) where 1 is critical.
        
        Return your response in JSON format (without markdown blocks):
        {{
            "area": "Area Name",
            "priority": number,
            "reasoning": "Brief explanation"
        }}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

    def validate_deployment(self, env_name, config_summary, logs):
        """Validates an environment before or during deployment."""
        prompt = f"""
        You are a Cloud Infrastructure Expert. Validate the following deployment:
        Environment: {env_name}
        Configuration Summary: {config_summary}
        Recent Logs/Checks: {logs}
        
        Identify any potential risks (e.g., misconfigured secrets, resource limits, region mismatches).
        Provide a "Go/No-Go" recommendation and reasoning.
        
        Format as a professional report.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
