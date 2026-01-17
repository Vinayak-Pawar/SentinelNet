#!/usr/bin/env python3
"""
SentinelNet Prometheus Monitoring
Comprehensive monitoring and metrics collection using Prometheus

Author: Vinayak Pawar
Version: 1.0
Compatible with: M1 Pro MacBook Pro (Apple Silicon)
"""

import time
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, push_to_gateway
)
from fastapi import Response
import logging

from sentinelnet.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create registry
registry = CollectorRegistry()

# Request metrics
REQUEST_COUNT = Counter(
    'sentinelnet_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

REQUEST_LATENCY = Histogram(
    'sentinelnet_request_duration_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    registry=registry
)

# System metrics
ACTIVE_AGENTS = Gauge(
    'sentinelnet_active_agents',
    'Number of active monitoring agents',
    registry=registry
)

INCIDENT_COUNT = Gauge(
    'sentinelnet_active_incidents',
    'Number of active incidents',
    registry=registry
)

SYSTEM_HEALTH_SCORE = Gauge(
    'sentinelnet_system_health_score',
    'Overall system health score (0-100)',
    registry=registry
)

# Agent metrics
AGENT_HEARTBEAT = Gauge(
    'sentinelnet_agent_heartbeat_timestamp',
    'Last heartbeat timestamp for agents',
    ['agent_id', 'agent_type'],
    registry=registry
)

# Service health metrics
SERVICE_LATENCY = Histogram(
    'sentinelnet_service_latency_seconds',
    'Service response latency',
    ['service_name', 'cloud_provider', 'region'],
    registry=registry
)

SERVICE_STATUS = Gauge(
    'sentinelnet_service_status',
    'Service status (0=unknown, 1=healthy, 2=degraded, 3=down)',
    ['service_name', 'cloud_provider'],
    registry=registry
)

# AI Agent metrics
AGENT_CONVERSATIONS = Counter(
    'sentinelnet_agent_conversations_total',
    'Total number of agent conversations',
    ['agent_type', 'outcome'],
    registry=registry
)

AUTOGEN_TASKS = Counter(
    'sentinelnet_autogen_tasks_total',
    'Total AutoGen tasks executed',
    ['task_type', 'status'],
    registry=registry
)

LANGGRAPH_WORKFLOWS = Counter(
    'sentinelnet_langgraph_workflows_total',
    'Total LangGraph workflows executed',
    ['workflow_type', 'status'],
    registry=registry
)

# Anomaly detection metrics
ANOMALIES_DETECTED = Counter(
    'sentinelnet_anomalies_detected_total',
    'Total anomalies detected',
    ['service_name', 'detection_method', 'severity'],
    registry=registry
)

# Remediation metrics
REMEDIATION_PLANS = Counter(
    'sentinelnet_remediation_plans_total',
    'Total remediation plans generated',
    ['status'],
    registry=registry
)

REMEDIATION_EXECUTIONS = Counter(
    'sentinelnet_remediation_executions_total',
    'Total remediation executions',
    ['outcome'],
    registry=registry
)

# Performance metrics
MEMORY_USAGE = Gauge(
    'sentinelnet_memory_usage_bytes',
    'Memory usage in bytes',
    registry=registry
)

CPU_USAGE = Gauge(
    'sentinelnet_cpu_usage_percent',
    'CPU usage percentage',
    registry=registry
)

# Build info
BUILD_INFO = Info(
    'sentinelnet_build_info',
    'Build information',
    registry=registry
)

# Set build info
BUILD_INFO.info({
    'version': settings.version,
    'environment': settings.environment,
    'python_version': '3.9+'
})

def update_metrics(**kwargs):
    """Update various metrics"""
    try:
        if 'orchestrator_status' in kwargs:
            # Could map status to a numeric value
            pass

        if 'active_agents' in kwargs:
            ACTIVE_AGENTS.set(kwargs['active_agents'])

        if 'incident_count' in kwargs:
            INCIDENT_COUNT.set(kwargs['incident_count'])

        if 'system_health_score' in kwargs:
            SYSTEM_HEALTH_SCORE.set(kwargs['system_health_score'])

    except Exception as e:
        logger.error(f"Failed to update metrics: {e}")

def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record request metrics"""
    try:
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
    except Exception as e:
        logger.error(f"Failed to record request metrics: {e}")

def record_service_health(service_name: str, cloud_provider: str, region: str,
                         latency: float, status: str):
    """Record service health metrics"""
    try:
        # Record latency
        SERVICE_LATENCY.labels(
            service_name=service_name,
            cloud_provider=cloud_provider,
            region=region
        ).observe(latency)

        # Map status to numeric value
        status_map = {
            'unknown': 0,
            'healthy': 1,
            'degraded': 2,
            'down': 3
        }
        status_value = status_map.get(status.lower(), 0)
        SERVICE_STATUS.labels(
            service_name=service_name,
            cloud_provider=cloud_provider
        ).set(status_value)

    except Exception as e:
        logger.error(f"Failed to record service health metrics: {e}")

def record_agent_heartbeat(agent_id: str, agent_type: str):
    """Record agent heartbeat"""
    try:
        AGENT_HEARTBEAT.labels(
            agent_id=agent_id,
            agent_type=agent_type
        ).set(time.time())
    except Exception as e:
        logger.error(f"Failed to record agent heartbeat: {e}")

def record_anomaly(service_name: str, detection_method: str, severity: str):
    """Record anomaly detection"""
    try:
        ANOMALIES_DETECTED.labels(
            service_name=service_name,
            detection_method=detection_method,
            severity=severity
        ).inc()
    except Exception as e:
        logger.error(f"Failed to record anomaly: {e}")

def record_remediation(status: str, execution_outcome: Optional[str] = None):
    """Record remediation metrics"""
    try:
        REMEDIATION_PLANS.labels(status=status).inc()

        if execution_outcome:
            REMEDIATION_EXECUTIONS.labels(outcome=execution_outcome).inc()

    except Exception as e:
        logger.error(f"Failed to record remediation metrics: {e}")

def record_agent_conversation(agent_type: str, outcome: str):
    """Record agent conversation metrics"""
    try:
        AGENT_CONVERSATIONS.labels(agent_type=agent_type, outcome=outcome).inc()
    except Exception as e:
        logger.error(f"Failed to record agent conversation: {e}")

async def get_metrics() -> Dict[str, Any]:
    """Get current metrics data"""
    try:
        # In a real implementation, you'd query Prometheus or expose metrics
        return {
            "request_count": REQUEST_COUNT._value,
            "active_agents": ACTIVE_AGENTS._value,
            "incident_count": INCIDENT_COUNT._value,
            "system_health_score": SYSTEM_HEALTH_SCORE._value,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return {}

def create_prometheus_response() -> Response:
    """Create FastAPI response with Prometheus metrics"""
    try:
        output = generate_latest(registry)
        return Response(
            content=output,
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error(f"Failed to generate Prometheus metrics: {e}")
        return Response(
            content="# Error generating metrics\n",
            media_type=CONTENT_TYPE_LATEST,
            status_code=500
        )

async def push_metrics_to_gateway(gateway_url: Optional[str] = None):
    """Push metrics to Prometheus push gateway"""
    try:
        gateway = gateway_url or "localhost:9091"
        push_to_gateway(gateway, job='sentinelnet', registry=registry)
        logger.info("✅ Metrics pushed to Prometheus gateway")
    except Exception as e:
        logger.error(f"Failed to push metrics to gateway: {e}")

def start_prometheus_server(port: int = 8001):
    """Start Prometheus metrics server"""
    try:
        from prometheus_client import start_http_server
        start_http_server(port)
        logger.info(f"✅ Prometheus metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start Prometheus server: {e}")
        raise

# FastAPI middleware for automatic metrics collection
class PrometheusMiddleware:
    """FastAPI middleware to automatically collect request metrics"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start_time = time.time()

        # Process request
        response_status = 500  # Default to error

        async def wrapped_send(message):
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            response_status = 500
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            method = scope["method"]
            path = scope["path"]

            record_request(method, path, response_status, duration)

# Health check function
def health_check():
    """Basic health check for monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.version
    }

if __name__ == "__main__":
    # Test Prometheus integration
    print("Testing Prometheus metrics...")

    # Update some test metrics
    update_metrics(active_agents=4, incident_count=2, system_health_score=95.0)
    record_service_health("BigQuery", "GCP", "us-central1", 0.045, "healthy")
    record_anomaly("BigQuery", "z_score", "medium")

    # Print current metrics
    print("Current metrics:")
    print(f"Active agents: {ACTIVE_AGENTS._value}")
    print(f"Incident count: {INCIDENT_COUNT._value}")
    print(f"System health: {SYSTEM_HEALTH_SCORE._value}")

    print("✅ Prometheus integration test completed!")
