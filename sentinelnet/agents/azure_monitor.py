#!/usr/bin/env python3
"""
SentinelNet Azure Service Monitor
Monitoring agents for Microsoft Azure services with AutoGen integration

Author: Vinayak Pawar
Version: 1.0
Compatible with: M1 Pro MacBook Pro (Apple Silicon)

This module provides monitoring for:
- Azure Blob Storage: Container accessibility, throughput metrics
- Azure DevOps: Pipeline status, build health, deployment monitoring
- Cross-service health correlation with AutoGen agent assistance
- Intelligent remediation suggestions using Azure AutoGen agents
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Azure imports (optional - will work without them for demo)
try:
    from azure.storage.blob import BlobServiceClient
    from azure.devops.connection import Connection
    from azure.devops.v7_1.build import BuildClient
    from azure.devops.v7_1.core import CoreClient
    from azure.monitor.query import LogsQueryClient
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    BlobServiceClient = None
    Connection = None
    BuildClient = None
    CoreClient = None
    LogsQueryClient = None
    DefaultAzureCredential = None

# Local imports
from sentinelnet.core.config import get_settings
from sentinelnet.data.processor import DataProcessor, MetricData
from sentinelnet.models.anomaly_detector import AnomalyDetector, AnomalyResult
from sentinelnet.core.orchestrator import AgentInfo, AgentStatus, ServiceStatus, ServiceHealth

# Configure logging
logger = logging.getLogger(__name__)

class AzureService(Enum):
    """Azure services monitored by this agent"""
    BLOB_STORAGE = "blob_storage"
    DEVOPS = "devops"
    MONITOR = "monitor"

@dataclass
class AzureServiceConfig:
    """Configuration for Azure service monitoring"""
    service: AzureService
    subscription_id: str
    resource_group: str = "sentinelnet-rg"
    region: str = "East US"
    check_interval_seconds: int = 60
    timeout_seconds: int = 30

@dataclass
class MonitoringResult:
    """Result of a service health check"""
    service: AzureService
    status: ServiceStatus
    latency_ms: float
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = None
    timestamp: datetime = None

class AzureMonitorAgent:
    """
    Azure service monitoring agent for SentinelNet
    Monitors Azure services with AutoGen agent assistance
    """

    def __init__(self, agent_id: str = "azure_monitor_001", subscription_id: Optional[str] = None):
        """
        Initialize the Azure monitoring agent

        Args:
            agent_id: Unique identifier for this agent
            subscription_id: Azure subscription ID to monitor
        """
        self.settings = get_settings()
        self.agent_id = agent_id
        self.subscription_id = subscription_id or self.settings.azure.subscription_id

        # Service configurations
        self.service_configs = self._load_service_configs()

        # Monitoring state
        self.last_checks: Dict[AzureService, datetime] = {}
        self.health_history: Dict[AzureService, List[MonitoringResult]] = {
            service: [] for service in AzureService
        }

        # Components
        self.data_processor = DataProcessor()
        self.anomaly_detector = AnomalyDetector()

        # Agent info for orchestrator
        self.agent_info = AgentInfo(
            agent_id=self.agent_id,
            agent_type="monitor",
            cloud_provider="Azure",
            services=["Blob Storage", "DevOps", "Monitor"],
            status=AgentStatus.INITIALIZING,
            region=self.settings.azure.region
        )

        # Azure clients (initialized when needed)
        self.blob_client = None
        self.devops_connection = None
        self.monitor_client = None

        # AutoGen integration
        self.autogen_agent = None

        logger.info(f"🔍 Azure Monitor Agent {agent_id} initialized for subscription: {self.subscription_id}")

    def _load_service_configs(self) -> Dict[AzureService, AzureServiceConfig]:
        """Load service monitoring configurations"""
        return {
            AzureService.BLOB_STORAGE: AzureServiceConfig(
                service=AzureService.BLOB_STORAGE,
                subscription_id=self.subscription_id or "demo-subscription",
                resource_group=self.settings.azure.resource_group,
                region=self.settings.azure.region,
                check_interval_seconds=60
            ),
            AzureService.DEVOPS: AzureServiceConfig(
                service=AzureService.DEVOPS,
                subscription_id=self.subscription_id or "demo-subscription",
                resource_group=self.settings.azure.resource_group,
                region=self.settings.azure.region,
                check_interval_seconds=120  # Less frequent for DevOps
            ),
            AzureService.MONITOR: AzureServiceConfig(
                service=AzureService.MONITOR,
                subscription_id=self.subscription_id or "demo-subscription",
                resource_group=self.settings.azure.resource_group,
                region=self.settings.azure.region,
                check_interval_seconds=300  # Much less frequent for monitoring
            )
        }

    async def initialize_clients(self):
        """Initialize Azure client libraries"""
        try:
            if not AZURE_AVAILABLE:
                logger.warning("⚠️ Azure libraries not available - running in demo mode")
                return

            if self.subscription_id and self.settings.azure.client_id:
                # Initialize Azure credentials
                credential = DefaultAzureCredential()

                # Initialize Blob Storage client
                # Note: Would need actual storage account details
                # self.blob_client = BlobServiceClient(account_url="...", credential=credential)

                # Initialize DevOps connection
                if hasattr(self.settings.azure, 'devops_organization'):
                    organization_url = f"https://dev.azure.com/{self.settings.azure.devops_organization}"
                    self.devops_connection = Connection(
                        base_url=organization_url,
                        creds=credential
                    )

                # Initialize Monitor client
                self.monitor_client = LogsQueryClient(credential)

                logger.info("✅ Azure clients initialized successfully")
            else:
                logger.warning("⚠️ Azure credentials not provided - using demo mode")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure clients: {e}")
            logger.info("💡 Running in demo mode without real Azure access")

    def initialize_autogen_agent(self):
        """Initialize AutoGen agent for Azure operations"""
        try:
            from autogen import AssistantAgent

            if self.settings.ai.openai_api_key:
                self.autogen_agent = AssistantAgent(
                    name="AzureOperationsAgent",
                    system_message="""You are an expert Azure cloud engineer specializing in Azure services monitoring, diagnostics, and remediation.
                    Help analyze Azure service issues, suggest remediation steps, and provide operational guidance.

                    Focus areas:
                    - Azure Blob Storage performance and availability
                    - Azure DevOps pipeline and deployment monitoring
                    - Azure Monitor logs and metrics analysis
                    - Cross-service dependency analysis
                    - Cost-effective remediation strategies""",
                    llm_config={
                        "model": self.settings.ai.openai_model,
                        "api_key": self.settings.ai.openai_api_key,
                        "temperature": 0.1,
                    },
                    max_consecutive_auto_reply=15,
                    human_input_mode="NEVER",
                )
                logger.info("✅ Azure AutoGen agent initialized")
            else:
                logger.warning("⚠️ OpenAI API key not available - AutoGen agent disabled")

        except ImportError:
            logger.warning("⚠️ AutoGen not available - Azure agent features limited")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AutoGen agent: {e}")

    async def start_monitoring(self):
        """Start the monitoring loop"""
        logger.info("🚀 Starting Azure service monitoring...")

        # Initialize clients and agents
        await self.initialize_clients()
        self.initialize_autogen_agent()

        # Update agent status
        self.agent_info.status = AgentStatus.HEALTHY

        # Start monitoring tasks
        tasks = []
        for service in AzureService:
            task = asyncio.create_task(self._monitor_service_loop(service))
            tasks.append(task)

        # Wait for all monitoring tasks
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _monitor_service_loop(self, service: AzureService):
        """Monitoring loop for a specific service"""
        config = self.service_configs[service]

        while True:
            try:
                # Check if it's time for monitoring
                now = datetime.now()
                last_check = self.last_checks.get(service)

                if last_check and (now - last_check).total_seconds() < config.check_interval_seconds:
                    await asyncio.sleep(10)  # Wait before checking again
                    continue

                # Perform health check
                start_time = time.time()
                result = await self._check_service_health(service)
                end_time = time.time()

                result.latency_ms = (end_time - start_time) * 1000
                result.timestamp = now

                # Store result
                self.last_checks[service] = now
                self.health_history[service].append(result)

                # Keep only recent history (last 100 checks)
                if len(self.health_history[service]) > 100:
                    self.health_history[service] = self.health_history[service][-100:]

                # Process metrics and detect anomalies
                await self._process_monitoring_result(result)

                # Log result
                status_emoji = "🟢" if result.status == ServiceStatus.HEALTHY else "🔴"
                logger.info(f"{status_emoji} Azure {service.value}: {result.status.value} ({result.latency_ms:.1f}ms)")

                # Wait before next check
                await asyncio.sleep(config.check_interval_seconds)

            except Exception as e:
                logger.error(f"❌ Error monitoring Azure {service.value}: {e}")
                await asyncio.sleep(30)  # Wait longer on error

    async def _check_service_health(self, service: AzureService) -> MonitoringResult:
        """Check health of a specific Azure service"""
        config = self.service_configs[service]

        try:
            if service == AzureService.BLOB_STORAGE:
                return await self._check_blob_storage_health(config)
            elif service == AzureService.DEVOPS:
                return await self._check_devops_health(config)
            elif service == AzureService.MONITOR:
                return await self._check_monitor_health(config)
            else:
                return MonitoringResult(
                    service=service,
                    status=ServiceStatus.UNKNOWN,
                    latency_ms=0.0,
                    error_message=f"Unsupported service: {service}"
                )

        except Exception as e:
            logger.error(f"❌ Health check failed for Azure {service.value}: {e}")
            return MonitoringResult(
                service=service,
                status=ServiceStatus.DOWN,
                latency_ms=0.0,
                error_message=str(e)
            )

    async def _check_blob_storage_health(self, config: AzureServiceConfig) -> MonitoringResult:
        """Check Azure Blob Storage health"""
        try:
            if not self.blob_client or not AZURE_AVAILABLE:
                # Demo mode - simulate health check
                await asyncio.sleep(0.1)  # Simulate network delay

                import random
                if random.random() < 0.1:  # 10% chance of issues
                    return MonitoringResult(
                        service=AzureService.BLOB_STORAGE,
                        status=ServiceStatus.DEGRADED,
                        latency_ms=random.randint(200, 1000),
                        error_message="Simulated Blob Storage performance degradation",
                        metrics={
                            "container_count": random.randint(5, 20),
                            "total_blobs": random.randint(1000, 10000),
                            "error_rate": random.uniform(0.02, 0.08),
                            "throughput_mbps": random.uniform(50, 200)
                        }
                    )
                else:
                    return MonitoringResult(
                        service=AzureService.BLOB_STORAGE,
                        status=ServiceStatus.HEALTHY,
                        latency_ms=random.randint(50, 150),
                        metrics={
                            "container_count": random.randint(10, 30),
                            "total_blobs": random.randint(5000, 50000),
                            "error_rate": random.uniform(0.001, 0.01),
                            "throughput_mbps": random.uniform(100, 500)
                        }
                    )

            # Real Blob Storage health check would go here
            # This would check container accessibility, list blobs, etc.

        except Exception as e:
            error_msg = str(e)
            status = ServiceStatus.DOWN

            if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                status = ServiceStatus.DEGRADED

            return MonitoringResult(
                service=AzureService.BLOB_STORAGE,
                status=status,
                latency_ms=0.0,
                error_message=error_msg
            )

    async def _check_devops_health(self, config: AzureServiceConfig) -> MonitoringResult:
        """Check Azure DevOps health"""
        try:
            if not self.devops_connection or not AZURE_AVAILABLE:
                # Demo mode - simulate health check
                await asyncio.sleep(0.15)  # Simulate network delay

                import random
                if random.random() < 0.05:  # 5% chance of issues (less frequent)
                    return MonitoringResult(
                        service=AzureService.DEVOPS,
                        status=ServiceStatus.DEGRADED,
                        latency_ms=random.randint(500, 2000),
                        error_message="Simulated DevOps pipeline delays",
                        metrics={
                            "active_pipelines": random.randint(1, 10),
                            "build_success_rate": random.uniform(0.85, 0.95),
                            "deployment_count": random.randint(5, 50),
                            "average_build_time": random.randint(300, 1200)  # seconds
                        }
                    )
                else:
                    return MonitoringResult(
                        service=AzureService.DEVOPS,
                        status=ServiceStatus.HEALTHY,
                        latency_ms=random.randint(100, 300),
                        metrics={
                            "active_pipelines": random.randint(5, 20),
                            "build_success_rate": random.uniform(0.95, 0.99),
                            "deployment_count": random.randint(20, 100),
                            "average_build_time": random.randint(180, 600)  # seconds
                        }
                    )

            # Real DevOps health check would go here
            # This would check pipeline status, build health, etc.

        except Exception as e:
            error_msg = str(e)
            status = ServiceStatus.DOWN

            return MonitoringResult(
                service=AzureService.DEVOPS,
                status=status,
                latency_ms=0.0,
                error_message=error_msg
            )

    async def _check_monitor_health(self, config: AzureServiceConfig) -> MonitoringResult:
        """Check Azure Monitor health"""
        try:
            if not self.monitor_client or not AZURE_AVAILABLE:
                # Demo mode - simulate health check
                await asyncio.sleep(0.05)  # Quick check

                import random
                return MonitoringResult(
                    service=AzureService.MONITOR,
                    status=ServiceStatus.HEALTHY,
                    latency_ms=random.randint(20, 100),
                    metrics={
                        "log_ingestion_rate": random.uniform(1000, 10000),
                        "query_success_rate": random.uniform(0.98, 0.999),
                        "alert_count": random.randint(0, 50),
                        "data_retention_days": 90
                    }
                )

            # Real Monitor health check would go here
            # This would query logs, check metrics availability, etc.

        except Exception as e:
            return MonitoringResult(
                service=AzureService.MONITOR,
                status=ServiceStatus.DEGRADED,
                latency_ms=0.0,
                error_message=str(e)
            )

    async def _process_monitoring_result(self, result: MonitoringResult):
        """Process monitoring result and store metrics"""
        try:
            # Convert to MetricData
            metric_data = MetricData(
                timestamp=result.timestamp,
                service_name=f"Azure {result.service.value.replace('_', ' ').title()}",
                cloud_provider="Azure",
                metric_name="latency",
                value=result.latency_ms,
                unit="ms",
                region=self.service_configs[result.service].region,
                metadata={
                    "status": result.status.value,
                    "error_message": result.error_message,
                    **(result.metrics or {})
                }
            )

            # Store metric
            success = await self.data_processor.store_metric(metric_data)
            if success:
                # Check for anomalies
                recent_metrics = await self.data_processor.get_metrics(
                    metric_data.service_name,
                    metric_data.cloud_provider,
                    metric_data.metric_name,
                    hours=1
                )

                if len(recent_metrics) >= 10:
                    anomaly_result = await self.anomaly_detector.detect_anomaly(recent_metrics)

                    if anomaly_result and anomaly_result.is_anomaly:
                        logger.warning(f"🚨 Anomaly detected in Azure {result.service.value}: {anomaly_result.description}")

                        # Get AutoGen analysis if available
                        if self.autogen_agent:
                            await self._analyze_issue_with_autogen(result, anomaly_result)

                        # Report to orchestrator
                        await self._report_anomaly_to_orchestrator(result.service, anomaly_result)

        except Exception as e:
            logger.error(f"❌ Failed to process Azure monitoring result: {e}")

    async def _analyze_issue_with_autogen(self, result: MonitoringResult, anomaly: AnomalyResult):
        """Analyze issue using AutoGen agent"""
        try:
            if not self.autogen_agent:
                return

            analysis_prompt = f"""
            Analyze this Azure service issue and provide remediation recommendations:

            Service: Azure {result.service.value.replace('_', ' ').title()}
            Status: {result.status.value}
            Latency: {result.latency_ms:.1f}ms
            Anomaly: {anomaly.description}
            Error: {result.error_message or 'None'}
            Metrics: {result.metrics or {}}

            Please provide:
            1. Root cause analysis
            2. Immediate remediation steps
            3. Preventive measures
            4. Azure-specific recommendations
            5. Cost implications
            """

            # Note: In a real implementation, you'd initiate an AutoGen conversation
            # For now, we'll just log that analysis would happen
            logger.info(f"🤖 AutoGen analysis would be performed for: {result.service.value}")

        except Exception as e:
            logger.error(f"❌ AutoGen analysis failed: {e}")

    async def _report_anomaly_to_orchestrator(self, service: AzureService, anomaly: AnomalyResult):
        """Report anomaly to the orchestrator"""
        logger.warning(f"📢 Reporting Azure anomaly for {service.value}: {anomaly.description}")

    def get_service_status(self, service: AzureService) -> Optional[MonitoringResult]:
        """Get the latest status for a service"""
        history = self.health_history.get(service, [])
        return history[-1] if history else None

    def get_service_health_history(self, service: AzureService, hours: int = 1) -> List[MonitoringResult]:
        """Get health history for a service"""
        history = self.health_history.get(service, [])
        cutoff_time = datetime.now() - timedelta(hours=hours)

        return [result for result in history
                if result.timestamp and result.timestamp > cutoff_time]

    async def force_health_check(self, service: AzureService) -> MonitoringResult:
        """Force an immediate health check for a service"""
        logger.info(f"🔍 Forcing health check for Azure {service.value}")
        result = await self._check_service_health(service)
        result.timestamp = datetime.now()

        # Update history
        self.health_history[service].append(result)
        if len(self.health_history[service]) > 100:
            self.health_history[service] = self.health_history[service][-100:]

        # Process result
        await self._process_monitoring_result(result)

        return result

    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        return {
            'agent_id': self.agent_id,
            'status': self.agent_info.status.value,
            'services_monitored': len(AzureService),
            'last_checks': {
                service.value: self.last_checks.get(service).isoformat()
                if self.last_checks.get(service) else None
                for service in AzureService
            },
            'health_summary': {
                service.value: {
                    'latest_status': self.get_service_status(service).status.value
                    if self.get_service_status(service) else 'unknown',
                    'checks_in_last_hour': len(self.get_service_health_history(service, 1)),
                    'average_latency': sum(r.latency_ms for r in self.get_service_health_history(service, 1))
                                    / max(1, len(self.get_service_health_history(service, 1)))
                }
                for service in AzureService
            },
            'azure_available': AZURE_AVAILABLE,
            'autogen_enabled': self.autogen_agent is not None,
            'subscription_id': self.subscription_id
        }

# Global Azure monitor instance
_azure_monitor_instance: Optional[AzureMonitorAgent] = None

def get_azure_monitor(agent_id: str = "azure_monitor_001") -> AzureMonitorAgent:
    """Get the global Azure monitor instance"""
    global _azure_monitor_instance
    if _azure_monitor_instance is None:
        _azure_monitor_instance = AzureMonitorAgent(agent_id=agent_id)
    return _azure_monitor_instance

# Convenience functions
async def start_azure_monitoring(agent_id: str = "azure_monitor_001"):
    """Start Azure service monitoring"""
    monitor = get_azure_monitor(agent_id)
    await monitor.start_monitoring()

async def check_blob_storage_health() -> MonitoringResult:
    """Check Azure Blob Storage health"""
    monitor = get_azure_monitor()
    return await monitor.force_health_check(AzureService.BLOB_STORAGE)

async def check_devops_health() -> MonitoringResult:
    """Check Azure DevOps health"""
    monitor = get_azure_monitor()
    return await monitor.force_health_check(AzureService.DEVOPS)

if __name__ == "__main__":
    # Test the Azure monitor
    async def test_azure_monitor():
        monitor = AzureMonitorAgent()

        print("Testing Azure Blob Storage health check...")
        blob_result = await monitor._check_blob_storage_health(monitor.service_configs[AzureService.BLOB_STORAGE])
        print(f"Blob Storage: {blob_result.status.value} ({blob_result.latency_ms:.1f}ms)")

        print("Testing Azure DevOps health check...")
        devops_result = await monitor._check_devops_health(monitor.service_configs[AzureService.DEVOPS])
        print(f"DevOps: {devops_result.status.value} ({devops_result.latency_ms:.1f}ms)")

        print("Azure Monitor test completed!")

    asyncio.run(test_azure_monitor())
