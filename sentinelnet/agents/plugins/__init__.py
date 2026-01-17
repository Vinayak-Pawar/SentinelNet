"""
SentinelNet Agent Plugins

Modular plugin system for different agent frameworks.
Each plugin provides ecosystem-specific agent capabilities.
"""

from sentinelnet.agents import (
    AgentFramework, CloudProvider, AgentCapabilities,
    BaseAgentPlugin, AgentPlugin
)

__all__ = [
    "AgentFramework",
    "CloudProvider",
    "AgentCapabilities",
    "BaseAgentPlugin",
    "AgentPlugin"
]
