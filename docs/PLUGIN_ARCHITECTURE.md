# SentinelNet Plugin Architecture

## Overview

SentinelNet now uses a **plugin-based architecture** for agent frameworks to solve licensing costs and ecosystem lock-in issues. This approach allows companies to choose agent frameworks based on their existing licenses and cloud preferences, rather than being forced into expensive or incompatible solutions.

## Problem Solved

### Traditional Approach Issues
- **Licensing Costs**: Companies must buy licenses for LangChain, LangGraph, Microsoft AutoGen, etc.
- **Ecosystem Lock-in**: Teams get stuck using tools they don't prefer (e.g., PowerBI when they want Looker)
- **Vendor Dependencies**: Forced to use specific frameworks regardless of fit
- **Upgrade Complexity**: Hard to switch frameworks or add new ones

### Plugin-Based Solution
- **License Flexibility**: Companies choose plugins based on what they already own
- **Ecosystem Freedom**: Native frameworks for each cloud provider
- **Easy Switching**: Change plugins without architectural changes
- **Future-Proof**: Add new frameworks as plugins

## Architecture

### Core Components

```
sentinelnet/agents/
├── __init__.py          # Plugin manager and base classes
├── plugins/             # Plugin implementations
│   ├── autogen_azure.py     # Microsoft AutoGen for Azure
│   ├── google_gcp.py        # Google Agent Kit for GCP
│   ├── langchain_multi.py   # LangChain for multi-cloud
│   └── langgraph_multi.py   # LangGraph for complex workflows
└── remediation.py       # Framework-agnostic remediation
```

### Plugin Manager

The `PluginManager` class handles:
- **Plugin Registration**: Register plugins with capabilities
- **Plugin Activation**: Initialize plugins with configurations
- **Task Routing**: Route tasks to appropriate plugins
- **Lifecycle Management**: Start/stop plugins cleanly

### Abstract Interfaces

```python
class AgentPlugin(Protocol):
    @property
    def capabilities(self) -> AgentCapabilities: ...

    async def initialize(self, config: Dict[str, Any]) -> bool: ...

    async def execute_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]: ...

    async def analyze_issue(self, issue: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]: ...

    async def shutdown(self) -> None: ...
```

## Available Plugins

### 1. Microsoft AutoGen (Azure)
```python
# Best for: Azure-native operations
# License: Microsoft AutoGen (free for Azure users)
# Capabilities: Azure monitoring, remediation, resource management
```

### 2. Google Agent Development Kit (GCP)
```python
# Best for: Google Cloud operations
# License: Google Cloud (included with GCP)
# Capabilities: Vertex AI analysis, BigQuery optimization, Cloud Storage management
```

### 3. LangChain (Multi-Cloud)
```python
# Best for: Cross-cloud flexibility
# License: LangChain (MIT license, free)
# Capabilities: Unified analysis, cross-cloud remediation, flexible workflows
```

### 4. LangGraph (Complex Workflows)
```python
# Best for: Complex multi-step orchestrations
# License: LangGraph (MIT license, free)
# Capabilities: Advanced workflow orchestration, state management, complex AI chains
```

## Configuration

### Plugin Selection by Ecosystem

```python
# In .env or config
PLUGIN_GCP_PLUGINS=["google_agent_kit", "langchain"]
PLUGIN_AZURE_PLUGINS=["autogen", "langchain"]
PLUGIN_MULTI_CLOUD_PLUGINS=["langchain", "langgraph"]
```

### Automatic Plugin Priority

Plugins are prioritized by ecosystem preference:
1. **Native Frameworks**: AutoGen (Azure), Google Agent Kit (GCP)
2. **Cross-Platform**: LangGraph, LangChain
3. **Custom**: User-defined plugins

## Usage Examples

### For Google Cloud Company
```python
# Uses Google Agent Kit (free with GCP) + LangChain fallback
gcp_plugins = ["google_agent_kit", "langchain"]
# No licensing costs, native GCP integration
```

### For Microsoft/Azure Company
```python
# Uses Microsoft AutoGen (free for Azure users) + LangChain fallback
azure_plugins = ["autogen", "langchain"]
# No licensing costs, native Azure integration
```

### For Multi-Cloud Company
```python
# Uses flexible frameworks that work across clouds
multi_cloud_plugins = ["langchain", "langgraph"]
# Open-source, no vendor lock-in
```

## Benefits

### Cost Savings
- **Google Cloud**: Use Google Agent Kit (free) instead of LangChain ($)
- **Azure**: Use Microsoft AutoGen (free) instead of LangChain ($)
- **Multi-Cloud**: Use MIT-licensed LangChain/LangGraph (free)

### Ecosystem Alignment
- **Google Teams**: Google Agent Kit + Vertex AI
- **Microsoft Teams**: Microsoft AutoGen + Azure OpenAI
- **Independent Teams**: LangChain/LangGraph for flexibility

### Future-Proofing
- **Easy Upgrades**: Add new framework plugins without core changes
- **A/B Testing**: Run multiple frameworks simultaneously
- **Gradual Migration**: Switch frameworks incrementally

## Migration Guide

### From Legacy Strategy System

```python
# Old: Hardcoded strategy
agent_strategy = "autogen_azure"  # Forces AutoGen everywhere

# New: Plugin-based
azure_plugins = ["autogen", "langchain"]  # Choice + fallback
gcp_plugins = ["google_agent_kit", "langchain"]  # Different for each cloud
```

### Backward Compatibility

Legacy configurations are automatically migrated:
- `agent_strategy = "autogen_azure"` → `azure_plugins = ["autogen"]`
- `agent_strategy = "google_gcp"` → `gcp_plugins = ["google_agent_kit"]`
- `agent_strategy = "hybrid"` → All plugins enabled

## Implementation Details

### Plugin Discovery
```python
# Automatic plugin loading
plugin = create_plugin_from_framework(AgentFramework.AUTOGEN, CloudProvider.AZURE)
manager.register_plugin("azure_autogen", plugin)
await manager.activate_plugin("azure_autogen")
```

### Task Routing
```python
# Automatic framework selection
result = await plugin_manager.execute_task_with_plugin(task, context)
# Uses best available plugin for the task type and cloud provider
```

### Error Handling
```python
# Graceful fallback
try:
    result = await primary_plugin.execute_task(task, context)
except Exception:
    result = await fallback_plugin.execute_task(task, context)
```

## Best Practices

### Plugin Selection Guidelines

1. **Primary Plugin**: Choose based on company licenses
   - GCP license → Google Agent Kit
   - Azure license → Microsoft AutoGen
   - No preference → LangChain

2. **Fallback Plugin**: Always include LangChain
   - Cross-cloud compatibility
   - Open-source and free
   - Flexible architecture

3. **Specialized Plugins**: Add for specific needs
   - LangGraph for complex workflows
   - Custom plugins for unique requirements

### Configuration Management

```python
# Environment-based configuration
PLUGIN_AUTO_SELECT_PLUGINS=true  # Auto-detect available frameworks
PLUGIN_PLUGIN_PRIORITY='{"autogen": 10, "google_agent_kit": 10, "langchain": 5}'
```

### Monitoring and Observability

```python
# Plugin performance tracking
plugin_metrics = plugin_manager.list_plugins()
# Track which plugins are active, their performance, and usage patterns
```

## Future Extensions

### Planned Plugins
- **AWS Agent Framework**: When AWS releases native agent tools
- **Custom Plugins**: Company-specific agent implementations
- **Third-Party Integrations**: Support for additional frameworks

### Advanced Features
- **Plugin Marketplace**: Community-contributed plugins
- **Dynamic Loading**: Load plugins at runtime
- **Plugin Versioning**: Support multiple versions of same framework

## Troubleshooting

### Common Issues

**Plugin Not Loading**
```bash
# Check plugin availability
python -c "from sentinelnet.agents.plugins import autogen_azure; print('Available')"
```

**License Issues**
```bash
# Verify plugin requirements
python -c "from sentinelnet.agents import create_plugin_from_framework; print('Requirements met')"
```

**Configuration Errors**
```bash
# Validate plugin configuration
python -c "from sentinelnet.core.config import get_settings; print(settings.ai.plugins)"
```

## Conclusion

The plugin-based architecture solves the core licensing and ecosystem issues by:

1. **Freedom of Choice**: Companies use what they already own
2. **Cost Optimization**: Leverage existing licenses instead of buying new ones
3. **Ecosystem Alignment**: Native tools for each cloud provider
4. **Future Flexibility**: Easy to add new frameworks as they emerge

This approach ensures SentinelNet can be adopted by companies regardless of their current technology stack and licensing agreements, while maintaining the flexibility to evolve with the AI agent ecosystem.
