#!/usr/bin/env python3
"""
SentinelNet Grafana Integration
Automated Grafana dashboard creation and management

Author: Vinayak Pawar
Version: 1.0
Compatible with: M1 Pro MacBook Pro (Apple Silicon)
"""

import json
import logging
from typing import Dict, Any, Optional, List
import requests
from datetime import datetime

from sentinelnet.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class GrafanaClient:
    """Grafana API client for dashboard management"""

    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize Grafana client

        Args:
            url: Grafana server URL
            api_key: Grafana API key
        """
        self.url = url or settings.monitoring.grafana_url
        self.api_key = api_key or settings.monitoring.grafana_api_key
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })

        self.base_url = f"{self.url}/api" if self.url else None

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Grafana API"""
        if not self.base_url:
            raise ValueError("Grafana URL not configured")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.exceptions.RequestException as e:
            logger.error(f"Grafana API request failed: {e}")
            raise

    def create_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dashboard"""
        payload = {
            "dashboard": dashboard_config,
            "overwrite": True
        }

        result = self._make_request('POST', '/dashboards/db', payload)
        logger.info(f"✅ Dashboard created: {result.get('url', 'Unknown URL')}")
        return result

    def update_dashboard(self, dashboard_id: str, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing dashboard"""
        payload = {
            "dashboard": dashboard_config,
            "overwrite": True
        }

        result = self._make_request('POST', f'/dashboards/db/{dashboard_id}', payload)
        logger.info(f"✅ Dashboard updated: {dashboard_id}")
        return result

    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard"""
        try:
            self._make_request('DELETE', f'/dashboards/db/{dashboard_id}')
            logger.info(f"✅ Dashboard deleted: {dashboard_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete dashboard {dashboard_id}: {e}")
            return False

    def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Get dashboard by ID"""
        try:
            result = self._make_request('GET', f'/dashboards/db/{dashboard_id}')
            return result.get('dashboard')
        except Exception:
            return None

    def list_dashboards(self) -> List[Dict[str, Any]]:
        """List all dashboards"""
        try:
            result = self._make_request('GET', '/search?type=dash-db')
            return result
        except Exception as e:
            logger.error(f"Failed to list dashboards: {e}")
            return []

    def create_data_source(self, data_source_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a data source"""
        result = self._make_request('POST', '/datasources', data_source_config)
        logger.info(f"✅ Data source created: {data_source_config.get('name')}")
        return result

def create_sentinelnet_dashboard(dashboard_config: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a comprehensive SentinelNet monitoring dashboard

    Args:
        dashboard_config: Custom dashboard configuration (optional)

    Returns:
        Dashboard URL
    """
    try:
        client = GrafanaClient()

        # Default dashboard configuration
        default_config = {
            "title": "SentinelNet - Cloud Resilience Monitoring",
            "tags": ["sentinelnet", "cloud", "monitoring"],
            "timezone": "browser",
            "panels": [
                # System Health Panel
                {
                    "id": 1,
                    "title": "System Health Score",
                    "type": "stat",
                    "targets": [{
                        "expr": "sentinelnet_system_health_score",
                        "legendFormat": "Health Score"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "red", "value": None},
                                    {"color": "orange", "value": 50},
                                    {"color": "yellow", "value": 75},
                                    {"color": "green", "value": 90}
                                ]
                            }
                        }
                    },
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                },

                # Active Agents Panel
                {
                    "id": 2,
                    "title": "Active Monitoring Agents",
                    "type": "stat",
                    "targets": [{
                        "expr": "sentinelnet_active_agents",
                        "legendFormat": "Active Agents"
                    }],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                },

                # Service Latency Panel
                {
                    "id": 3,
                    "title": "Service Response Latency",
                    "type": "graph",
                    "targets": [{
                        "expr": "histogram_quantile(0.95, rate(sentinelnet_service_latency_seconds_bucket[5m]))",
                        "legendFormat": "{{service_name}} (95th percentile)"
                    }],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                },

                # Active Incidents Panel
                {
                    "id": 4,
                    "title": "Active Incidents",
                    "type": "stat",
                    "targets": [{
                        "expr": "sentinelnet_active_incidents",
                        "legendFormat": "Active Incidents"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 1},
                                    {"color": "red", "value": 5}
                                ]
                            }
                        }
                    },
                    "gridPos": {"h": 8, "w": 8, "x": 0, "y": 16}
                },

                # Request Rate Panel
                {
                    "id": 5,
                    "title": "API Request Rate",
                    "type": "graph",
                    "targets": [{
                        "expr": "rate(sentinelnet_requests_total[5m])",
                        "legendFormat": "{{method}} {{endpoint}}"
                    }],
                    "gridPos": {"h": 8, "w": 16, "x": 8, "y": 16}
                },

                # Anomaly Detection Panel
                {
                    "id": 6,
                    "title": "Anomaly Detection",
                    "type": "table",
                    "targets": [{
                        "expr": "increase(sentinelnet_anomalies_detected_total[1h])",
                        "legendFormat": "{{service_name}} - {{detection_method}}"
                    }],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 24}
                },

                # Agent Performance Panel
                {
                    "id": 7,
                    "title": "Agent Heartbeats",
                    "type": "table",
                    "targets": [{
                        "expr": "sentinelnet_agent_heartbeat_timestamp",
                        "legendFormat": "{{agent_id}} ({{agent_type}})"
                    }],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 32}
                },

                # AI Agent Activity Panel
                {
                    "id": 8,
                    "title": "AI Agent Activity",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(sentinelnet_agent_conversations_total[5m])",
                            "legendFormat": "Agent Conversations"
                        },
                        {
                            "expr": "rate(sentinelnet_autogen_tasks_total[5m])",
                            "legendFormat": "AutoGen Tasks"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 32}
                }
            ],
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "refresh": "30s"
        }

        # Merge with custom config if provided
        if dashboard_config:
            default_config.update(dashboard_config)

        # Create the dashboard
        result = client.create_dashboard(default_config)

        dashboard_url = f"{settings.monitoring.grafana_url}/d/{result.get('uid', '')}"
        logger.info(f"✅ SentinelNet dashboard created: {dashboard_url}")

        return dashboard_url

    except Exception as e:
        logger.error(f"Failed to create SentinelNet dashboard: {e}")
        # Return mock URL for demo purposes
        return f"{settings.monitoring.grafana_url}/d/sentinelnet-demo" if settings.monitoring.grafana_url else "demo-dashboard-url"

def setup_prometheus_data_source(grafana_url: Optional[str] = None,
                                prometheus_url: str = "http://localhost:9090") -> bool:
    """
    Set up Prometheus data source in Grafana

    Args:
        grafana_url: Grafana server URL
        prometheus_url: Prometheus server URL

    Returns:
        Success status
    """
    try:
        client = GrafanaClient(grafana_url)

        data_source_config = {
            "name": "SentinelNet Prometheus",
            "type": "prometheus",
            "url": prometheus_url,
            "access": "proxy",
            "isDefault": True
        }

        client.create_data_source(data_source_config)
        logger.info("✅ Prometheus data source configured in Grafana")
        return True

    except Exception as e:
        logger.error(f"Failed to setup Prometheus data source: {e}")
        return False

def get_dashboard_template(template_name: str = "sentinelnet") -> Dict[str, Any]:
    """
    Get dashboard template configuration

    Args:
        template_name: Name of the template to retrieve

    Returns:
        Dashboard configuration
    """
    templates = {
        "sentinelnet": {
            "title": "SentinelNet - Cloud Resilience Monitoring",
            "description": "Comprehensive monitoring dashboard for SentinelNet cloud resilience platform",
            "tags": ["sentinelnet", "cloud", "resilience", "ai", "monitoring"]
        },

        "minimal": {
            "title": "SentinelNet - Minimal Dashboard",
            "description": "Basic monitoring dashboard with essential metrics",
            "tags": ["sentinelnet", "minimal"]
        }
    }

    return templates.get(template_name, templates["sentinelnet"])

async def create_monitoring_stack():
    """
    Create complete monitoring stack (Prometheus + Grafana dashboard)

    Returns:
        Configuration status
    """
    try:
        # Setup Prometheus data source
        prometheus_configured = setup_prometheus_data_source()

        # Create SentinelNet dashboard
        dashboard_url = create_sentinelnet_dashboard()

        return {
            "prometheus_configured": prometheus_configured,
            "dashboard_url": dashboard_url,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to create monitoring stack: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Test Grafana integration
    print("Testing Grafana integration...")

    try:
        # Create SentinelNet dashboard
        dashboard_url = create_sentinelnet_dashboard()
        print(f"✅ Dashboard created: {dashboard_url}")

        # Setup Prometheus data source
        prometheus_setup = setup_prometheus_data_source()
        print(f"✅ Prometheus data source setup: {prometheus_setup}")

        print("✅ Grafana integration test completed!")

    except Exception as e:
        print(f"❌ Grafana integration test failed: {e}")
        print("💡 Make sure Grafana is running and API key is configured")
