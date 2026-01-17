"""
Alert Models for SentinelNet
Pydantic models for AlertManager webhooks and internal alert representation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AlertStatus(str, Enum):
    """Alert status enumeration"""
    FIRING = "firing"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    PENDING = "pending"


class Severity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertLabels(BaseModel):
    """AlertManager alert labels"""
    alertname: str = Field(..., description="Name of the alert")
    severity: Optional[str] = Field(None, description="Alert severity")
    service: Optional[str] = Field(None, description="Affected service")
    cloud_provider: Optional[str] = Field(None, description="Cloud provider")
    region: Optional[str] = Field(None, description="Cloud region")
    instance: Optional[str] = Field(None, description="Instance identifier")
    job: Optional[str] = Field(None, description="Job name")
    
    # Allow additional labels
    class Config:
        extra = "allow"


class AlertAnnotations(BaseModel):
    """AlertManager alert annotations"""
    summary: Optional[str] = Field(None, description="Alert summary")
    description: Optional[str] = Field(None, description="Detailed description")
    runbook_url: Optional[str] = Field(None, description="Runbook URL")
    dashboard_url: Optional[str] = Field(None, description="Dashboard URL")
    
    # Allow additional annotations
    class Config:
        extra = "allow"


class AlertManagerAlert(BaseModel):
    """Single alert from AlertManager"""
    status: str = Field(..., description="Alert status (firing/resolved)")
    labels: AlertLabels = Field(..., description="Alert labels")
    annotations: AlertAnnotations = Field(..., description="Alert annotations")
    startsAt: str = Field(..., description="Alert start time")
    endsAt: Optional[str] = Field(None, description="Alert end time")
    generatorURL: Optional[str] = Field(None, description="Prometheus generator URL")
    fingerprint: Optional[str] = Field(None, description="Alert fingerprint")


class AlertManagerPayload(BaseModel):
    """
    AlertManager webhook payload
    
    Example:
    {
        "version": "4",
        "groupKey": "{}:{alertname='HighLatency'}",
        "status": "firing",
        "receiver": "sentinelnet",
        "groupLabels": {"alertname": "HighLatency"},
        "commonLabels": {"alertname": "HighLatency", "service": "bigquery"},
        "commonAnnotations": {"summary": "High latency detected"},
        "externalURL": "http://alertmanager:9093",
        "alerts": [...]
    }
    """
    version: str = Field(..., description="AlertManager version")
    groupKey: str = Field(..., description="Alert group key")
    status: str = Field(..., description="Group status (firing/resolved)")
    receiver: str = Field(..., description="Receiver name")
    groupLabels: Dict[str, Any] = Field(..., description="Group labels")
    commonLabels: Dict[str, Any] = Field(..., description="Common labels")
    commonAnnotations: Dict[str, Any] = Field(..., description="Common annotations")
    externalURL: str = Field(..., description="AlertManager external URL")
    alerts: List[AlertManagerAlert] = Field(..., description="List of alerts")


class Alert(BaseModel):
    """
    Internal alert representation in SentinelNet
    This is our normalized format after processing AlertManager webhooks
    """
    id: str = Field(..., description="Unique alert ID")
    alertname: str = Field(..., description="Alert name")
    status: AlertStatus = Field(..., description="Alert status")
    severity: Severity = Field(default=Severity.MEDIUM, description="Alert severity")
    
    # Service information
    service: Optional[str] = Field(None, description="Affected service")
    cloud_provider: Optional[str] = Field(None, description="Cloud provider")
    region: Optional[str] = Field(None, description="Cloud region")
    
    # Alert content
    summary: Optional[str] = Field(None, description="Alert summary")
    description: Optional[str] = Field(None, description="Detailed description")
    
    # Timestamps
    starts_at: datetime = Field(..., description="Alert start time")
    ends_at: Optional[datetime] = Field(None, description="Alert end time")
    received_at: datetime = Field(default_factory=datetime.now, description="Time received by SentinelNet")
    acknowledged_at: Optional[datetime] = Field(None, description="Time acknowledged")
    resolved_at: Optional[datetime] = Field(None, description="Time resolved")
    
    # Metadata
    fingerprint: Optional[str] = Field(None, description="Alert fingerprint")
    generator_url: Optional[str] = Field(None, description="Prometheus URL")
    labels: Dict[str, Any] = Field(default_factory=dict, description="All labels")
    annotations: Dict[str, Any] = Field(default_factory=dict, description="All annotations")
    
    # Enrichment data (added during processing)
    enriched: bool = Field(default=False, description="Whether alert has been enriched")
    cloud_context: Optional[Dict[str, Any]] = Field(None, description="Cloud provider context")
    incident_id: Optional[str] = Field(None, description="Associated incident ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Incident(BaseModel):
    """
    Incident - a group of correlated alerts
    """
    id: str = Field(..., description="Unique incident ID")
    title: str = Field(..., description="Incident title")
    status: str = Field(..., description="Incident status")
    severity: Severity = Field(..., description="Highest severity of alerts")
    
    # Related alerts
    alert_ids: List[str] = Field(default_factory=list, description="IDs of related alerts")
    alert_count: int = Field(default=0, description="Number of alerts")
    
    # Affected resources
    affected_services: List[str] = Field(default_factory=list, description="Affected services")
    affected_clouds: List[str] = Field(default_factory=list, description="Affected cloud providers")
    affected_regions: List[str] = Field(default_factory=list, description="Affected regions")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Incident creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    resolved_at: Optional[datetime] = Field(None, description="Resolution time")
    
    # Analysis
    impact_analysis: Optional[str] = Field(None, description="AI-generated impact analysis")
    remediation_plan_id: Optional[str] = Field(None, description="Associated remediation plan")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertResponse(BaseModel):
    """Response for alert webhook"""
    success: bool = Field(..., description="Whether the alert was received successfully")
    message: str = Field(..., description="Response message")
    alerts_received: int = Field(..., description="Number of alerts received")
    alert_ids: List[str] = Field(default_factory=list, description="IDs of created alerts")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
