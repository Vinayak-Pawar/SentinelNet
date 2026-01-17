"""
SentinelNet - AI-Powered Multi-Cloud Resilience Platform

A comprehensive platform for intelligent cloud monitoring, incident response,
and automated remediation using advanced AI agents and multi-cloud orchestration.

Features:
- Multi-cloud service monitoring (GCP, Azure, AWS)
- Advanced AI agent orchestration (LangGraph, AutoGen, Google Agent Kit)
- Intelligent incident detection and impact analysis
- Automated remediation planning with human validation
- Grafana + Prometheus monitoring integration
- High-performance FastAPI backend

Author: Vinayak Pawar
Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "Vinayak Pawar"
__email__ = "vinayak@example.com"
__license__ = "MIT"

# Optional imports to avoid dependency issues during package import
try:
    from sentinelnet.core.orchestrator import SentinelNetOrchestrator
    _orchestrator_available = True
except Exception:
    SentinelNetOrchestrator = None
    _orchestrator_available = False

try:
    from sentinelnet.api.main import create_app
    _api_available = True
except Exception:
    create_app = None
    _api_available = False

from sentinelnet.core.config import get_settings

# Get settings instance for convenience
settings = get_settings()

__all__ = [
    "SentinelNetOrchestrator",
    "get_settings",
    "settings",
    "create_app",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]
