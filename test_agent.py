
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_pr_webhook():
    print("Testing PR Webhook...")
    payload = {
        "resource": {
            "pullRequestId": 123,
            "repository": {"id": "test-repo-id"},
            "title": "Fix: Critical security vulnerability in auth.py",
            "description": "This PR fixes a bug where users could bypass authentication by sending an empty token."
        },
        "resourceContainers": {
            "project": {"id": "test-project-id"}
        }
    }
    response = requests.post(f"{BASE_URL}/webhook/pr", json=payload)
    print(f"Response: {response.json()}")

def test_build_webhook():
    print("Testing Build Webhook...")
    payload = {
        "resource": {
            "id": 456,
            "status": "completed",
            "result": "failed"
        },
        "resourceContainers": {
            "project": {"id": "test-project-id"}
        }
    }
    response = requests.post(f"{BASE_URL}/webhook/build", json=payload)
    print(f"Response: {response.json()}")

def test_workitem_webhook():
    print("Testing Work Item Webhook...")
    payload = {
        "resource": {
            "id": 789,
            "fields": {
                "System.Title": "Database connection timeout in production",
                "System.Description": "We are seeing many timeout errors when trying to connect to the SQL database from the web app."
            }
        }
    }
    response = requests.post(f"{BASE_URL}/webhook/workitem", json=payload)
    print(f"Response: {response.json()}")

def test_deployment_webhook():
    print("Testing Deployment Webhook...")
    payload = {
        "resource": {
            "release": {"id": 101},
            "environment": {"id": 202}
        },
        "resourceContainers": {
            "project": {"id": "test-project-id"}
        }
    }
    response = requests.post(f"{BASE_URL}/webhook/deployment", json=payload)
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    try:
        test_pr_webhook()
        test_build_webhook()
        test_workitem_webhook()
        test_deployment_webhook()
        print("\nAll tests sent! Check the dashboard or logs.")
    except Exception as e:
        print(f"Error: {e}. Is the server running?")
