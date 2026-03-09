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
st.sidebar.subheader("🌐 Connection Settings")
api_base_url = st.sidebar.text_input("Backend API URL", value="http://127.0.0.1:8000", help="Change this if your backend is running on a different machine or in the cloud.")
API_URL = api_base_url.strip("/")

def get_status():
    try:
        response = requests.get(f"{API_URL}/api/status", timeout=3)
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
        st.info("💡 **Connection Required**: Ensure your FastAPI backend is running.")

    st.divider()
    st.subheader("Manual Actions")
    if st.button("🚀 Test All Webhooks"):
        if not server_status:
            st.error("Cannot test: Backend is offline!")
        else:
            with st.spinner("Firing webhooks..."):
                # Trigger simulations via requests
                trigger_test("pr", {"resource": {"pullRequestId": 100, "repository": {"id": "repo"}, "title": "Security Fix", "description": "Fixing auth"}, "resourceContainers": {"project": {"id": "project"}}})
                trigger_test("build", {"resource": {"id": 200, "result": "failed"}, "resourceContainers": {"project": {"id": "project"}}})
                st.toast("Tests triggered successfully!")

# Main Dashboard
st.title("Azure AI DevOps Agent Console")
st.caption("AI-powered orchestration for Pull Requests, Pipelines, and Incident Triage.")

if not server_status:
    with st.expander("🛠️ Connection Guide (System Offline)", expanded=True):
        st.markdown("""
        The Management Console needs to connect to your AI DevOps Backend to show live data.
        1.  **Start the Backend**: Run `python -m uvicorn src.main:app --reload`
        2.  **Verify URL**: Ensure the 'Backend API URL' in the sidebar matches your server.
        3.  **Check Firewall**: Ensure port 8000 is open if testing remotely.
        """)

# Data processing
activities = server_status.get("activity", []) if server_status else []
pr_count = len([a for a in activities if "PR_REVIEWED" in a["type"]])
build_count = len([a for a in activities if "BUILD_DIAGNOSED" in a["type"]])
wi_count = len([a for a in activities if "WORKITEM_TRIAGED" in a["type"]])
deploy_count = len([a for a in activities if "DEPLOYMENT_VALIDATED" in a["type"]])

# Stats row
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
        st.info("No activity recorded yet or backend disconnected.")

with tab2:
    st.subheader("AI Performance")
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
        "connected_services": ["PR Reviewer", "Build Monitor", "Work Item Triager", "Deployment Guard"]
    })

# Polling for updates
if st.checkbox("Auto-refresh data (5s)"):
    time.sleep(5)
    st.rerun()
