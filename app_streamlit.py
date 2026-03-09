import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Azure AI DevOps Agent | Management Console",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #0b1120;
        color: #f8fafc;
    }
    .stMetric {
        background-color: rgba(30, 41, 59, 0.7);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://127.0.0.1:8000"

def get_status():
    try:
        response = requests.get(f"{API_URL}/api/status", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def trigger_test(endpoint, payload):
    try:
        response = requests.post(f"{API_URL}/webhook/{endpoint}", json=payload)
        return response.status_code == 200
    except:
        return False

# Sidebar
with st.sidebar:
    st.title("🤖 Agent Settings")
    st.write("Control your autonomous DevOps agent.")
    
    server_status = get_status()
    if server_status:
        st.success("Backend: Online")
    else:
        st.error("Backend: Offline")
        st.info("Start the server using: `python -m uvicorn src.main:app --reload`")

    st.divider()
    st.subheader("Manual Actions")
    if st.button("🚀 Test All Webhooks"):
        with st.spinner("Firing webhooks..."):
            # Trigger simulations via requests
            requests.post(f"{API_URL}/webhook/pr", json={
                "resource": {"pullRequestId": 100, "repository": {"id": "repo"}, "title": "Security Fix", "description": "Fixing auth"},
                "resourceContainers": {"project": {"id": "project"}}
            })
            requests.post(f"{API_URL}/webhook/build", json={
                "resource": {"id": 200, "result": "failed"},
                "resourceContainers": {"project": {"id": "project"}}
            })
            st.toast("Tests triggered successfully!")

# Main Dashboard
st.title("Azure AI DevOps Agent Console")
st.caption("AI-powered orchestration for Pull Requests, Pipelines, and Incident Triage.")

if server_status:
    # Stats row
    activities = server_status.get("activity", [])
    pr_count = len([a for a in activities if "PR_REVIEWED" in a["type"]])
    build_count = len([a for a in activities if "BUILD_DIAGNOSED" in a["type"]])
    wi_count = len([a for a in activities if "WORKITEM_TRIAGED" in a["type"]])
    deploy_count = len([a for a in activities if "DEPLOYMENT_VALIDATED" in a["type"]])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("PRs Reviewed", pr_count)
    col2.metric("Builds Diagnosed", build_count)
    col3.metric("Incidents Triaged", wi_count)
    col4.metric("Release Validations", deploy_count)

    st.divider()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🕒 Activity Log", "📈 Analytics", "⚙️ Configuration"])

    with tab1:
        st.subheader("Real-time Activity")
        if activities:
            df = pd.DataFrame(activities).iloc[::-1] # Reverse for latest first
            for _, row in df.iterrows():
                with st.expander(f"{row['type']} - {row['timestamp']}"):
                    st.write(f"**Message:** {row['message']}")
                    st.write(f"**Status:** {row['status'].upper()}")
        else:
            st.info("No activity recorded yet. Trigger some webhooks to see data!")

    with tab2:
        st.subheader("AI Performance")
        st.info("Detailed analytics on AI accuracy and response times coming soon.")
        # Placeholder chart
        chart_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "Tasks": [12, 18, 15, 25, 20]
        })
        st.line_chart(chart_data.set_index("Day"))

    with tab3:
        st.subheader("Agent Configuration")
        st.json({
            "model": "gpt-4o",
            "temperature": 0.2,
            "max_tokens": 4096,
            "connected_services": ["PR Reviewer", "Build Monitor", "Work Item Triager", "Deployment Guard"]
        })

else:
    st.warning("Please connect the FastAPI backend to view real-time metrics.")
    st.image("https://via.placeholder.com/800x400/0b1120/f8fafc?text=Console+Offline+-+Start+FastAPI+Server", use_container_width=True)

# Polling for updates
if st.checkbox("Auto-refresh data (5s)"):
    time.sleep(5)
    st.rerun()
