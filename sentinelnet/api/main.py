#!/usr/bin/env python3
"""
SentinelNet API
FastAPI backend for SentinelNet services

Author: Vinayak Pawar
Version: 1.0
Compatible with: M1 Pro MacBook Pro (Apple Silicon)
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

from sentinelnet.core.config import get_settings
from sentinelnet.core.orchestrator import SentinelNetOrchestrator
from sentinelnet.monitoring.prometheus import (
    REQUEST_COUNT, REQUEST_LATENCY,
    ACTIVE_AGENTS, INCIDENT_COUNT
)
from sentinelnet.models import (
    AlertManagerPayload, AlertResponse, Alert as AlertModel, 
    AlertStatus, Severity
)
from sentinelnet.database import get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global settings
settings = get_settings()

# Global orchestrator instance
orchestrator_instance: Optional[SentinelNetOrchestrator] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator_instance

    # Startup
    logger.info("🚀 Starting SentinelNet API")
    orchestrator_instance = SentinelNetOrchestrator()

    # Start background tasks
    await orchestrator_instance.start_orchestration_loop()

    yield

    # Shutdown
    logger.info("🛑 Shutting down SentinelNet API")
    if orchestrator_instance:
        await orchestrator_instance.shutdown()

# Create FastAPI app with lifespan
app = FastAPI(
    title="SentinelNet API",
    description="AI-Powered Multi-Cloud Resilience Platform API with Advanced Agent Orchestration",
    version=settings.version,
    lifespan=lifespan
)

# Security middleware
if settings.security.api_key_required:
    security = HTTPBearer()

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=settings.api.cors_allow_credentials,
    allow_methods=settings.api.cors_allow_methods,
    allow_headers=settings.api.cors_allow_headers,
)

if not settings.is_development():
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure properly in production
    )

# Pydantic models
class ServiceStatus(BaseModel):
    name: str
    cloud: str
    status: str  # healthy, warning, error
    latency: int
    last_checked: datetime
    region: Optional[str] = None

class Alert(BaseModel):
    id: str
    level: str  # info, warning, error
    service: str
    message: str
    timestamp: datetime

class RemediationPlan(BaseModel):
    id: str
    incident_id: str
    actions: List[dict]
    estimated_time: str
    risk_level: str
    generated_at: datetime
    approved: bool = False

# Mock data
def get_mock_services():
    """Get mock service data for demo"""
    return [
        ServiceStatus(
            name="BigQuery",
            cloud="GCP",
            status="healthy",
            latency=45,
            last_checked=datetime.now(),
            region="us-east1"
        ),
        ServiceStatus(
            name="Vertex AI",
            cloud="GCP",
            status="healthy",
            latency=67,
            last_checked=datetime.now(),
            region="us-central1"
        ),
        ServiceStatus(
            name="Blob Storage",
            cloud="Azure",
            status="warning",
            latency=234,
            last_checked=datetime.now(),
            region="East US"
        ),
        ServiceStatus(
            name="DevOps",
            cloud="Azure",
            status="healthy",
            latency=89,
            last_checked=datetime.now(),
            region="Global"
        )
    ]

def get_mock_alerts():
    """Get mock alerts for demo"""
    return [
        Alert(
            id="alert_001",
            level="warning",
            service="Blob Storage",
            message="High latency detected (234ms > 200ms threshold)",
            timestamp=datetime.now()
        ),
        Alert(
            id="alert_002",
            level="info",
            service="System",
            message="All monitoring agents health check passed",
            timestamp=datetime.now()
        )
    ]

# API Routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "SentinelNet API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

# ============================================================================
# PHASE 1: AlertManager Webhook Integration
# ============================================================================

@app.post("/webhooks/alertmanager", response_model=AlertResponse)
async def receive_alertmanager_webhook(
    payload: AlertManagerPayload,
    background_tasks: BackgroundTasks
):
    """
    Receive AlertManager webhook and process alerts.
    
    This endpoint receives alerts from Prometheus AlertManager and:
    1. Parses the AlertManager payload
    2. Converts alerts to internal format
    3. Stores alerts in database
    4. Queues alerts for AI processing
    5. Returns acknowledgment
    
    Args:
        payload: AlertManager webhook payload
        background_tasks: FastAPI background tasks
        
    Returns:
        AlertResponse with processing status
    """
    try:
        logger.info(f"📨 Received AlertManager webhook: {payload.groupKey}")
        logger.info(f"   Status: {payload.status}, Alerts: {len(payload.alerts)}")
        
        # Get database instance
        db = get_database()
        
        # Process each alert in the payload
        processed_alerts = []
        alert_ids = []
        
        for am_alert in payload.alerts:
            try:
                # Convert AlertManager alert to internal format
                alert = _convert_alertmanager_alert(am_alert, payload)
                
                # Store in database
                alert_dict = alert.dict()
                if db.store_alert(alert_dict):
                    processed_alerts.append(alert)
                    alert_ids.append(alert.id)
                    logger.info(f"✅ Processed alert: {alert.id} - {alert.alertname}")
                else:
                    logger.error(f"❌ Failed to store alert: {alert.id}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing alert: {e}")
                continue
        
        # Queue alerts for AI processing in background
        if processed_alerts:
            background_tasks.add_task(
                _process_alerts_async,
                processed_alerts
            )
        
        # Update Prometheus metrics
        INCIDENT_COUNT.inc(len(processed_alerts))
        
        return AlertResponse(
            success=True,
            message=f"Successfully received and queued {len(processed_alerts)} alerts",
            alerts_received=len(processed_alerts),
            alert_ids=alert_ids,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ AlertManager webhook error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process AlertManager webhook: {str(e)}"
        )


def _convert_alertmanager_alert(
    am_alert,
    payload: AlertManagerPayload
) -> AlertModel:
    """
    Convert AlertManager alert to internal format.
    
    Args:
        am_alert: AlertManager alert
        payload: Full AlertManager payload for context
        
    Returns:
        Internal Alert model
    """
    # Extract key information
    alertname = am_alert.labels.alertname
    fingerprint = am_alert.fingerprint or f"fp_{datetime.now().timestamp()}"
    
    # Determine severity
    severity_str = am_alert.labels.severity or "medium"
    try:
        severity = Severity(severity_str.lower())
    except ValueError:
        severity = Severity.MEDIUM
    
    # Determine status
    status = AlertStatus.FIRING if am_alert.status == "firing" else AlertStatus.RESOLVED
    
    # Create internal alert
    alert = AlertModel(
        id=f"alert_{fingerprint}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        alertname=alertname,
        status=status,
        severity=severity,
        service=am_alert.labels.service,
        cloud_provider=am_alert.labels.cloud_provider,
        region=am_alert.labels.region,
        summary=am_alert.annotations.summary,
        description=am_alert.annotations.description,
        starts_at=datetime.fromisoformat(am_alert.startsAt.replace('Z', '+00:00')),
        ends_at=datetime.fromisoformat(am_alert.endsAt.replace('Z', '+00:00')) if am_alert.endsAt else None,
        received_at=datetime.now(),
        fingerprint=fingerprint,
        generator_url=am_alert.generatorURL,
        labels=am_alert.labels.dict(),
        annotations=am_alert.annotations.dict()
    )
    
    return alert


async def _process_alerts_async(alerts: List[AlertModel]):
    """
    Process alerts asynchronously (background task).
    
    This will be expanded in Phase 2 to include:
    - Alert enrichment with cloud context
    - Alert correlation
    - Incident creation
    - AI analysis trigger
    
    Args:
        alerts: List of alerts to process
    """
    try:
        logger.info(f"🔄 Processing {len(alerts)} alerts in background...")
        
        # TODO: Phase 2 - Add alert enrichment
        # TODO: Phase 2 - Add alert correlation
        # TODO: Phase 2 - Trigger AI analysis
        
        logger.info(f"✅ Background processing complete for {len(alerts)} alerts")
        
    except Exception as e:
        logger.error(f"❌ Background processing error: {e}")


@app.get("/api/alerts")
async def get_all_alerts(
    status: Optional[str] = None,
    service: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Get all alerts with optional filtering.
    
    Args:
        status: Filter by status (firing, resolved, acknowledged)
        service: Filter by service name
        limit: Maximum number of results
        offset: Offset for pagination
        
    Returns:
        List of alerts
    """
    try:
        db = get_database()
        alerts = db.get_alerts(status=status, service=service, limit=limit, offset=offset)
        
        return {
            "success": True,
            "count": len(alerts),
            "alerts": alerts,
            "filters": {
                "status": status,
                "service": service,
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts/{alert_id}")
async def get_alert_details(alert_id: str):
    """
    Get details of a specific alert.
    
    Args:
        alert_id: Alert identifier
        
    Returns:
        Alert details
    """
    try:
        db = get_database()
        alert = db.get_alert(alert_id)
        
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        return {
            "success": True,
            "alert": alert
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """
    Acknowledge an alert.
    
    Args:
        alert_id: Alert identifier
        
    Returns:
        Acknowledgment status
    """
    try:
        db = get_database()
        
        # Check if alert exists
        alert = db.get_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
        # Update status
        if db.update_alert_status(alert_id, "acknowledged"):
            return {
                "success": True,
                "message": f"Alert {alert_id} acknowledged",
                "alert_id": alert_id,
                "timestamp": datetime.now()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to acknowledge alert")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_statistics():
    """
    Get system statistics.
    
    Returns:
        System statistics including alert counts
    """
    try:
        db = get_database()
        stats = db.get_stats()
        
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# End of Phase 1 AlertManager Integration
# ============================================================================

@app.get("/health/services", response_model=List[ServiceStatus])
async def get_services():
    """Get all monitored services status"""
    return get_mock_services()

@app.get("/health/services/{service_name}", response_model=ServiceStatus)
async def get_service(service_name: str):
    """Get specific service status"""
    services = get_mock_services()
    for service in services:
        if service.name.lower() == service_name.lower():
            return service
    raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

@app.post("/health/check")
async def manual_health_check():
    """Trigger manual health check for all services"""
    # In real implementation, this would trigger actual checks
    return {
        "message": "Health check initiated",
        "services_checked": 4,
        "timestamp": datetime.now()
    }

@app.get("/alerts", response_model=List[Alert])
async def get_alerts():
    """Get active alerts"""
    return get_mock_alerts()

@app.post("/remediation/plan")
async def generate_remediation_plan(incident_description: str):
    """Generate AI-powered remediation plan"""
    # Mock remediation plan generation
    plan = RemediationPlan(
        id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        incident_id="incident_001",
        actions=[
            {
                "priority": "high",
                "action": "Switch to geo-redundant storage",
                "estimated_time": "5 minutes",
                "risk": "low",
                "automated": True
            },
            {
                "priority": "medium",
                "action": "Scale up compute resources",
                "estimated_time": "10 minutes",
                "risk": "medium",
                "automated": False
            }
        ],
        estimated_time="15 minutes",
        risk_level="low",
        generated_at=datetime.now(),
        approved=False
    )

    return {
        "message": "Remediation plan generated",
        "plan": plan,
        "ai_insights": "Based on historical patterns, this appears to be regional network congestion. Geo-redundant failover should resolve within 5 minutes."
    }

@app.get("/remediation/{plan_id}")
async def get_remediation_plan(plan_id: str):
    """Get details of a specific remediation plan"""
    # Mock plan retrieval
    return {
        "id": plan_id,
        "status": "generated",
        "actions": [
            {
                "step": 1,
                "action": "Enable geo-redundant storage",
                "status": "pending",
                "requires_approval": True
            }
        ]
    }

@app.post("/remediation/{plan_id}/approve")
async def approve_remediation_plan(plan_id: str):
    """Approve a remediation plan for execution"""
    # In real implementation, this would trigger safety checks
    return {
        "message": f"Remediation plan {plan_id} approved",
        "approved_by": "human_operator",
        "timestamp": datetime.now(),
        "safety_checks": "passed",
        "execution_ready": True
    }

@app.get("/dashboard/metrics")
async def get_dashboard_metrics():
    """Get metrics for dashboard display"""
    return {
        "services_healthy": 3,
        "services_warning": 1,
        "services_error": 0,
        "active_alerts": 2,
        "uptime_percentage": 99.9,
        "average_latency": 108.75,
        "last_updated": datetime.now()
    }

@app.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    if not orchestrator_instance:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    system_status = await orchestrator_instance.get_system_status()

    # Update Prometheus metrics
    ACTIVE_AGENTS.set(system_status.get('active_agents', 0))
    INCIDENT_COUNT.set(system_status.get('active_alerts', 0))

    return {
        **system_status,
        "autogen_agents": len(orchestrator_instance.autogen_agents) if orchestrator_instance.autogen_agents else 0,
        "google_agents": len(orchestrator_instance.google_agents) if orchestrator_instance.google_agents else 0,
        "cloud_providers": settings.get_cloud_providers(),
        "timestamp": datetime.now()
    }

# Advanced Agent Endpoints

@app.post("/agents/autogen/azure/execute")
async def execute_autogen_azure_task(task: str, background_tasks: BackgroundTasks):
    """Execute a task using AutoGen Azure agents"""
    if not orchestrator_instance or not orchestrator_instance.autogen_agents.get("azure"):
        raise HTTPException(status_code=503, detail="AutoGen Azure agents not available")

    try:
        azure_agent = orchestrator_instance.autogen_agents["azure"]["agent"]
        azure_proxy = orchestrator_instance.autogen_agents["azure"]["proxy"]

        # Execute task in background
        background_tasks.add_task(_execute_autogen_task, azure_agent, azure_proxy, task)

        return {
            "message": "AutoGen Azure task started",
            "task_id": f"autogen_azure_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "running"
        }

    except Exception as e:
        logger.error(f"AutoGen Azure task failed: {e}")
        raise HTTPException(status_code=500, detail=f"AutoGen execution failed: {str(e)}")

@app.post("/agents/google/gcp/analyze")
async def analyze_with_google_agent(service: str, issue: str):
    """Analyze an issue using Google Agent Development Kit"""
    if not orchestrator_instance or not orchestrator_instance.google_agents.get("gcp"):
        raise HTTPException(status_code=503, detail="Google GCP agents not available")

    try:
        model = orchestrator_instance.google_agents["gcp"]["model"]

        prompt = f"""
        Analyze this cloud service issue and provide recommendations:

        Service: {service}
        Issue: {issue}

        Please provide:
        1. Root cause analysis
        2. Immediate remediation steps
        3. Preventive measures
        4. Impact assessment
        """

        response = model.generate_content(prompt)

        return {
            "analysis": response.text,
            "agent_type": "google_gemini",
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"Google agent analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Google agent analysis failed: {str(e)}")

@app.post("/agents/langgraph/workflow")
async def execute_langgraph_workflow(workflow_config: Dict[str, Any], background_tasks: BackgroundTasks):
    """Execute a custom LangGraph workflow"""
    if not orchestrator_instance:
        raise HTTPException(status_code=503, detail="Orchestrator not available")

    try:
        # This would execute a custom workflow based on the config
        background_tasks.add_task(_execute_custom_workflow, workflow_config)

        return {
            "message": "LangGraph workflow started",
            "workflow_id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "running"
        }

    except Exception as e:
        logger.error(f"LangGraph workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@app.get("/monitoring/metrics")
async def get_monitoring_metrics():
    """Get comprehensive monitoring metrics"""
    from sentinelnet.monitoring.prometheus import get_metrics

    return await get_metrics()

@app.post("/monitoring/grafana/dashboard")
async def create_grafana_dashboard(dashboard_config: Dict[str, Any]):
    """Create a Grafana dashboard for SentinelNet monitoring"""
    try:
        from sentinelnet.monitoring.grafana import create_sentinelnet_dashboard

        dashboard_url = await create_sentinelnet_dashboard(dashboard_config)

        return {
            "message": "Grafana dashboard created",
            "dashboard_url": dashboard_url,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"Grafana dashboard creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Grafana integration failed: {str(e)}")

# Background task functions
async def _execute_autogen_task(agent, proxy, task):
    """Execute AutoGen task in background"""
    try:
        # This is a simplified implementation
        # In practice, you'd implement proper AutoGen conversation flow
        logger.info(f"Executing AutoGen task: {task}")

        # Simulate task execution
        await asyncio.sleep(2)  # Simulate processing time

        logger.info("AutoGen task completed")

    except Exception as e:
        logger.error(f"AutoGen task execution failed: {e}")

async def _execute_custom_workflow(workflow_config):
    """Execute custom LangGraph workflow"""
    try:
        logger.info(f"Executing custom workflow: {workflow_config}")

        # This would implement custom workflow execution
        # based on the provided configuration

        await asyncio.sleep(1)  # Simulate execution

        logger.info("Custom workflow completed")

    except Exception as e:
        logger.error(f"Custom workflow execution failed: {e}")

# Dependency injection
def get_orchestrator() -> SentinelNetOrchestrator:
    """Dependency injection for orchestrator"""
    if not orchestrator_instance:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    return orchestrator_instance

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security if settings.security.api_key_required else None)):
    """Verify API key if required"""
    if settings.security.api_key_required:
        if credentials.credentials not in settings.security.api_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")
    return True

def create_app() -> FastAPI:
    """Create and return FastAPI app instance"""
    return app

def run_api():
    """Run the FastAPI server"""
    port = int(os.getenv("API_PORT", 8000))
    logger.info(f"Starting SentinelNet API on port {port}")

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_api()
