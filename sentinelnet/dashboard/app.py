#!/usr/bin/env python3
"""
SentinelNet Dashboard
Interactive dashboard for monitoring cloud services and viewing remediation plans

Author: Vinayak Pawar
Version: 1.0
Compatible with: M1 Pro MacBook Pro (Apple Silicon)
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="SentinelNet - Cloud Resilience Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import from new package structure
try:
    from sentinelnet.core.orchestrator import get_orchestrator
    from sentinelnet.core.config import get_settings
    from sentinelnet.monitoring.prometheus import get_metrics
    from sentinelnet.agents.gcp_monitor import get_gcp_monitor
    from sentinelnet.agents.azure_monitor import get_azure_monitor
except ImportError:
    # Fallback for development
    get_orchestrator = lambda: None
    get_settings = lambda: type('obj', (object,), {'version': '0.1.0'})()
    get_metrics = lambda: {}
    get_gcp_monitor = lambda: None
    get_azure_monitor = lambda: None

# Enhanced mock data for demo purposes
def generate_service_data():
    """Generate service health data from real monitors or mock data"""
    services = []

    # Try to get real data from monitors
    try:
        gcp_monitor = get_gcp_monitor()
        if gcp_monitor:
            for service_name in ["BigQuery", "Vertex AI"]:
                status = gcp_monitor.get_service_status(getattr(gcp_monitor, f'GCPService.{service_name.upper().replace(" ", "_")}', None))
                if status:
                    services.append({
                        "name": service_name,
                        "cloud": "GCP",
                        "status": status.status.value,
                        "latency": int(status.latency_ms),
                        "last_checked": status.timestamp.isoformat() if status.timestamp else datetime.now().isoformat()
                    })
    except Exception:
        pass

    try:
        azure_monitor = get_azure_monitor()
        if azure_monitor:
            for service_name in ["Blob Storage", "DevOps"]:
                status = azure_monitor.get_service_status(getattr(azure_monitor, f'AzureService.{service_name.upper().replace(" ", "_")}', None))
                if status:
                    services.append({
                        "name": service_name,
                        "cloud": "Azure",
                        "status": status.status.value,
                        "latency": int(status.latency_ms),
                        "last_checked": status.timestamp.isoformat() if status.timestamp else datetime.now().isoformat()
                    })
    except Exception:
        pass

    # Fallback to mock data if no real data
    if not services:
        services = [
            {"name": "BigQuery", "cloud": "GCP", "status": "healthy", "latency": 45, "last_checked": datetime.now().isoformat()},
            {"name": "Vertex AI", "cloud": "GCP", "status": "healthy", "latency": 67, "last_checked": datetime.now().isoformat()},
            {"name": "Blob Storage", "cloud": "Azure", "status": "warning", "latency": 234, "last_checked": datetime.now().isoformat()},
            {"name": "DevOps", "cloud": "Azure", "status": "healthy", "latency": 89, "last_checked": datetime.now().isoformat()}
        ]

        # Randomly simulate some issues for demo
        if random.random() < 0.3:  # 30% chance of issues
            affected = random.choice(services)
            affected["status"] = "error" if random.random() < 0.5 else "warning"
            affected["latency"] = random.randint(500, 2000)

    return services

def get_system_metrics():
    """Get system metrics from orchestrator or mock data"""
    try:
        orchestrator = get_orchestrator()
        if orchestrator:
            return asyncio.run(orchestrator.get_system_status())
    except Exception:
        pass

    # Mock system metrics
    return {
        "system_health_score": 95.0,
        "active_agents": 4,
        "total_agents": 4,
        "services_monitored": 4,
        "active_alerts": 1,
        "pending_remediations": 0,
        "communication_status": "healthy",
        "autogen_agents": 1,
        "google_agents": 1,
        "last_updated": datetime.now()
    }

def run_dashboard():
    """Main dashboard application with enhanced AI agent features"""
    st.title("🛡️ SentinelNet v0.1.0 - Cloud Resilience Dashboard")
    st.markdown("*AI-Powered Multi-Cloud Outage Detection & Remediation*")
    st.markdown("*✨ Enhanced with Microsoft AutoGen, Google Agent Kit & Advanced Monitoring*")

    # Get system metrics
    system_metrics = get_system_metrics()

    # Sidebar
    with st.sidebar:
        st.header("🔧 Controls")

        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()

        st.divider()

        st.subheader("🎯 Quick Actions")
        if st.button("🚨 Simulate Outage"):
            st.session_state.simulate_outage = True

        if st.button("📋 Generate Remediation Plan"):
            st.session_state.show_remediation = True

        if st.button("🤖 AutoGen Azure Analysis"):
            st.session_state.show_autogen = True

        if st.button("🌐 Google Agent Analysis"):
            st.session_state.show_google_agent = True

        st.divider()

        st.subheader("⚙️ Settings")
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=True)
        demo_mode = st.checkbox("Demo Mode", value=True)

        st.divider()

        st.subheader("📊 System Status")
        health_score = system_metrics.get("system_health_score", 95.0)
        active_agents = system_metrics.get("active_agents", 4)
        total_agents = system_metrics.get("total_agents", 4)

        st.metric("System Health", f"{health_score:.1f}%", "🟢" if health_score > 90 else "🟡")
        st.metric("Active Agents", f"{active_agents}/{total_agents}", "🟢" if active_agents == total_agents else "🟡")
        st.metric("Services Monitored", system_metrics.get("services_monitored", 4), "🟢")

        st.divider()

        st.subheader("🤖 AI Agents")
        autogen_count = system_metrics.get("autogen_agents", 0)
        google_count = system_metrics.get("google_agents", 0)

        st.metric("AutoGen Agents", autogen_count, "🤖" if autogen_count > 0 else "⚪")
        st.metric("Google Agents", google_count, "🌐" if google_count > 0 else "⚪")

    # Main content
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🌐 Service Health Overview")
        services = generate_service_data()

        # Service status cards
        for service in services:
            status_color = {
                "healthy": "🟢",
                "warning": "🟡",
                "error": "🔴"
            }

            with st.container():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.write(f"{status_color[service['status']]} {service['name']} ({service['cloud']})")
                with col_b:
                    st.metric("Latency", f"{service['latency']}ms")
                with col_c:
                    st.write(service['status'].title())

    with col2:
        st.subheader("📈 Real-time Metrics")

        # Mock metrics chart
        hours = list(range(24))
        healthy_count = [4 - random.randint(0, 1) for _ in hours]

        chart_data = pd.DataFrame({
            'Hour': hours,
            'Healthy Services': healthy_count
        })

        st.line_chart(chart_data.set_index('Hour'))

        # Current stats
        st.metric("Current Health Score", "95%", "🟢")

    with col3:
        st.subheader("🚨 Active Alerts")

        # Mock alerts
        alerts = [
            {"level": "warning", "service": "Blob Storage", "message": "High latency detected", "time": "2 min ago"},
            {"level": "info", "service": "System", "message": "Agent health check passed", "time": "5 min ago"}
        ]

        for alert in alerts:
            with st.container():
                if alert["level"] == "warning":
                    st.warning(f"⚠️ {alert['service']}: {alert['message']}")
                elif alert["level"] == "error":
                    st.error(f"❌ {alert['service']}: {alert['message']}")
                else:
                    st.info(f"ℹ️ {alert['service']}: {alert['message']}")
                st.caption(alert['time'])

    st.divider()

    # Remediation Planning Section
    if st.session_state.get('show_remediation', False):
        st.header("🛠️ AI-Generated Remediation Plan")

        with st.container():
            st.subheader("📋 Incident Analysis")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Affected Services", "1", "🔴")
                st.metric("Estimated Impact", "Medium", "🟡")

            with col2:
                st.metric("Recovery Time", "~15 min", "🟢")
                st.metric("Risk Level", "Low", "🟢")

            st.markdown("**Detected Issue:** High latency on Azure Blob Storage")
            st.markdown("**Root Cause:** Potential regional network congestion")

            st.subheader("🎯 Recommended Actions")

            actions = [
                {
                    "priority": "High",
                    "action": "Switch to geo-redundant storage (RA-GRS)",
                    "estimated_time": "5 minutes",
                    "risk": "Low",
                    "automated": True
                },
                {
                    "priority": "Medium",
                    "action": "Scale up compute resources in secondary region",
                    "estimated_time": "10 minutes",
                    "risk": "Medium",
                    "automated": False
                },
                {
                    "priority": "Low",
                    "action": "Update traffic routing policies",
                    "estimated_time": "2 minutes",
                    "risk": "Low",
                    "automated": True
                }
            ]

            for action in actions:
                with st.expander(f"{action['priority']} Priority: {action['action']}", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Time", action['estimated_time'])
                    with col2:
                        st.metric("Risk", action['risk'])
                    with col3:
                        st.write("🤖 Auto" if action['automated'] else "👤 Manual")
                    with col4:
                        if st.button("Execute", key=f"execute_{action['action'][:20]}"):
                            st.success("✅ Action executed successfully!")

        # Close remediation view
        if st.button("❌ Close Remediation Plan"):
            st.session_state.show_remediation = False
            st.rerun()

    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🛡️ SentinelNet v1.0 - MVP")
    with col2:
        st.caption("Built on M1 Pro MacBook Pro")
    with col3:
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

    # Auto-refresh
    if auto_refresh:
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    run_dashboard()
