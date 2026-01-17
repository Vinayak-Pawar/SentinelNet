"""
SentinelNet Agent Framework

Plugin-based architecture for multi-framework agent orchestration.
Supports ecosystem-specific implementations while maintaining unified interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
from enum import Enum
import importlib
import logging

logger = logging.getLogger(__name__)


class AgentFramework(Enum):
    """Supported agent frameworks"""
    AUTOGEN = "autogen"
    GOOGLE_AGENT_KIT = "google_agent_kit"
    LANGCHAIN = "langchain"
    LANGGRAPH = "langgraph"
    CUSTOM = "custom"


class CloudProvider(Enum):
    """Supported cloud providers"""
    AZURE = "azure"
    GCP = "gcp"
    AWS = "aws"
    MULTI_CLOUD = "multi_cloud"


@dataclass
class AgentCapabilities:
    """Agent capabilities and features"""
    framework: AgentFramework
    cloud_provider: CloudProvider
    features: List[str]
    max_concurrent_tasks: int = 10
    supports_async: bool = True
    requires_api_keys: List[str] = None

    def __post_init__(self):
        if self.requires_api_keys is None:
            self.requires_api_keys = []


class AgentPlugin(Protocol):
    """Protocol for agent plugins"""

    @property
    def capabilities(self) -> AgentCapabilities:
        """Return agent capabilities"""
        ...

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the agent plugin"""
        ...

    async def execute_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using the agent framework"""
        ...

    async def analyze_issue(self, issue: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an issue using the agent framework"""
        ...

    async def shutdown(self) -> None:
        """Shutdown the agent plugin"""
        ...


class BaseAgentPlugin(ABC):
    """Base class for agent plugins"""

    def __init__(self, capabilities: AgentCapabilities):
        self._capabilities = capabilities
        self._initialized = False

    @property
    def capabilities(self) -> AgentCapabilities:
        return self._capabilities

    @property
    def initialized(self) -> bool:
        return self._initialized

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the agent plugin"""
        pass

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using the agent framework"""
        pass

    @abstractmethod
    async def analyze_issue(self, issue: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an issue using the agent framework"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the agent plugin"""
        pass


class PluginManager:
    """Manages agent plugins and their lifecycle"""

    def __init__(self):
        self._plugins: Dict[str, AgentPlugin] = {}
        self._active_plugins: Dict[str, AgentPlugin] = {}
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}

    def register_plugin(self, name: str, plugin: AgentPlugin, config: Optional[Dict[str, Any]] = None):
        """Register a plugin"""
        self._plugins[name] = plugin
        if config:
            self._plugin_configs[name] = config
        logger.info(f"✅ Registered plugin: {name} ({plugin.capabilities.framework.value})")

    def unregister_plugin(self, name: str):
        """Unregister a plugin"""
        if name in self._active_plugins:
            # Shutdown active plugin
            import asyncio
            asyncio.create_task(self._active_plugins[name].shutdown())

        if name in self._plugins:
            del self._plugins[name]
            logger.info(f"✅ Unregistered plugin: {name}")

    async def activate_plugin(self, name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Activate a plugin"""
        if name not in self._plugins:
            logger.error(f"❌ Plugin not found: {name}")
            return False

        plugin = self._plugins[name]
        plugin_config = config or self._plugin_configs.get(name, {})

        try:
            success = await plugin.initialize(plugin_config)
            if success:
                self._active_plugins[name] = plugin
                logger.info(f"✅ Activated plugin: {name}")
                return True
            else:
                logger.error(f"❌ Failed to initialize plugin: {name}")
                return False
        except Exception as e:
            logger.error(f"❌ Plugin activation failed: {name} - {e}")
            return False

    async def deactivate_plugin(self, name: str):
        """Deactivate a plugin"""
        if name in self._active_plugins:
            try:
                await self._active_plugins[name].shutdown()
                del self._active_plugins[name]
                logger.info(f"✅ Deactivated plugin: {name}")
            except Exception as e:
                logger.error(f"❌ Plugin deactivation failed: {name} - {e}")

    def get_plugin_for_task(self, task_type: str, cloud_provider: Optional[str] = None) -> Optional[AgentPlugin]:
        """Get the best plugin for a task type"""
        # Priority: cloud-specific plugins, then general plugins
        cloud_specific = []
        general = []

        for name, plugin in self._active_plugins.items():
            if cloud_provider and plugin.capabilities.cloud_provider.value == cloud_provider:
                cloud_specific.append(plugin)
            elif plugin.capabilities.cloud_provider == CloudProvider.MULTI_CLOUD:
                general.append(plugin)

        # Return cloud-specific plugin if available, otherwise general
        candidates = cloud_specific + general

        for plugin in candidates:
            if task_type in plugin.capabilities.features:
                return plugin

        return None

    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all registered plugins"""
        return {
            name: {
                "capabilities": plugin.capabilities.__dict__,
                "active": name in self._active_plugins,
                "initialized": plugin.initialized if hasattr(plugin, 'initialized') else False
            }
            for name, plugin in self._plugins.items()
        }

    async def execute_task_with_plugin(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using the appropriate plugin"""
        task_type = task.get("type", "analysis")
        cloud_provider = task.get("cloud_provider")

        plugin = self.get_plugin_for_task(task_type, cloud_provider)

        if not plugin:
            return {
                "success": False,
                "error": f"No suitable plugin found for task type: {task_type}",
                "available_plugins": list(self._active_plugins.keys())
            }

        try:
            result = await plugin.execute_task(task, context)
            result["plugin_used"] = plugin.capabilities.framework.value
            return result
        except Exception as e:
            logger.error(f"❌ Task execution failed with plugin {plugin.capabilities.framework.value}: {e}")
            return {
                "success": False,
                "error": str(e),
                "plugin_used": plugin.capabilities.framework.value
            }

    async def shutdown_all(self):
        """Shutdown all active plugins"""
        shutdown_tasks = []
        for name, plugin in self._active_plugins.items():
            shutdown_tasks.append(self.deactivate_plugin(name))

        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        logger.info("✅ All plugins shutdown")


# Global plugin manager instance
_plugin_manager = PluginManager()

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance"""
    return _plugin_manager


# Export key functions
__all__ = [
    "AgentFramework",
    "CloudProvider",
    "AgentCapabilities",
    "BaseAgentPlugin",
    "AgentPlugin",
    "PluginManager",
    "get_plugin_manager",
    "create_plugin_from_framework",
    "setup_gcp_plugins",
    "setup_azure_plugins",
    "setup_multi_cloud_plugins"
]


def create_plugin_from_framework(framework: AgentFramework, cloud_provider: CloudProvider) -> Optional[AgentPlugin]:
    """
    Create a plugin instance from framework and cloud provider

    This factory function loads the appropriate plugin module dynamically.
    """
    try:
        # Framework-specific plugin modules
        framework_modules = {
            AgentFramework.AUTOGEN: f"sentinelnet.agents.plugins.autogen_{cloud_provider.value}",
            AgentFramework.GOOGLE_AGENT_KIT: f"sentinelnet.agents.plugins.google_{cloud_provider.value}",
            AgentFramework.LANGCHAIN: f"sentinelnet.agents.plugins.langchain_{cloud_provider.value}",
            AgentFramework.LANGGRAPH: f"sentinelnet.agents.plugins.langgraph_{cloud_provider.value}",
        }

        module_path = framework_modules.get(framework)
        if not module_path:
            logger.warning(f"⚠️ No plugin module found for framework: {framework.value}")
            return None

        # Dynamically import the plugin module
        module = importlib.import_module(module_path)

        # Get the plugin class (assumes class name follows convention)
        class_name = f"{framework.value.title()}{cloud_provider.value.title()}Plugin"
        plugin_class = getattr(module, class_name, None)

        if not plugin_class:
            logger.warning(f"⚠️ Plugin class not found: {class_name} in {module_path}")
            return None

        # Create and return plugin instance
        plugin = plugin_class()
        logger.info(f"✅ Created plugin: {framework.value} for {cloud_provider.value}")
        return plugin

    except ImportError as e:
        logger.warning(f"⚠️ Plugin module not available: {framework.value} for {cloud_provider.value} - {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to create plugin: {framework.value} for {cloud_provider.value} - {e}")
        return None


# Convenience functions for common plugin setups
async def setup_gcp_plugins() -> bool:
    """Setup Google Cloud Platform plugins"""
    manager = get_plugin_manager()

    # Try Google Agent Kit first (preferred for GCP)
    gcp_plugin = create_plugin_from_framework(AgentFramework.GOOGLE_AGENT_KIT, CloudProvider.GCP)
    if gcp_plugin:
        manager.register_plugin("gcp_google_agent_kit", gcp_plugin)
        success = await manager.activate_plugin("gcp_google_agent_kit")
        if success:
            logger.info("✅ GCP Google Agent Kit plugin activated")
            return True

    # Fallback to LangChain for GCP
    langchain_plugin = create_plugin_from_framework(AgentFramework.LANGCHAIN, CloudProvider.GCP)
    if langchain_plugin:
        manager.register_plugin("gcp_langchain", langchain_plugin)
        success = await manager.activate_plugin("gcp_langchain")
        if success:
            logger.info("✅ GCP LangChain plugin activated")
            return True

    logger.warning("⚠️ No GCP plugins available")
    return False


async def setup_azure_plugins() -> bool:
    """Setup Azure plugins"""
    manager = get_plugin_manager()

    # Try AutoGen first (preferred for Azure)
    azure_plugin = create_plugin_from_framework(AgentFramework.AUTOGEN, CloudProvider.AZURE)
    if azure_plugin:
        manager.register_plugin("azure_autogen", azure_plugin)
        success = await manager.activate_plugin("azure_autogen")
        if success:
            logger.info("✅ Azure AutoGen plugin activated")
            return True

    # Fallback to LangChain for Azure
    langchain_plugin = create_plugin_from_framework(AgentFramework.LANGCHAIN, CloudProvider.AZURE)
    if langchain_plugin:
        manager.register_plugin("azure_langchain", langchain_plugin)
        success = await manager.activate_plugin("azure_langchain")
        if success:
            logger.info("✅ Azure LangChain plugin activated")
            return True

    logger.warning("⚠️ No Azure plugins available")
    return False


async def setup_multi_cloud_plugins() -> bool:
    """Setup multi-cloud plugins"""
    manager = get_plugin_manager()

    # LangGraph for complex multi-cloud workflows
    langgraph_plugin = create_plugin_from_framework(AgentFramework.LANGGRAPH, CloudProvider.MULTI_CLOUD)
    if langgraph_plugin:
        manager.register_plugin("multi_cloud_langgraph", langgraph_plugin)
        success = await manager.activate_plugin("multi_cloud_langgraph")
        if success:
            logger.info("✅ Multi-cloud LangGraph plugin activated")
            return True

    # LangChain as general multi-cloud fallback
    langchain_plugin = create_plugin_from_framework(AgentFramework.LANGCHAIN, CloudProvider.MULTI_CLOUD)
    if langchain_plugin:
        manager.register_plugin("multi_cloud_langchain", langchain_plugin)
        success = await manager.activate_plugin("multi_cloud_langchain")
        if success:
            logger.info("✅ Multi-cloud LangChain plugin activated")
            return True

    logger.warning("⚠️ No multi-cloud plugins available")
    return False
