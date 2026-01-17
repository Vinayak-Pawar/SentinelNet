#!/usr/bin/env python3
"""
SentinelNet - AI-Powered Multi-Cloud Resilience Platform
Main entry point using the new package structure

Author: Vinayak Pawar
Version: 0.1.0
Compatible with: M1 Pro MacBook Pro (Apple Silicon)
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/sentinelnet.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add project root to path for backward compatibility
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    """Main application entry point using the new package structure"""
    logger.info("🚀 Starting SentinelNet v0.1.0...")

    # Import from new package structure
    try:
        from sentinelnet.core.orchestrator import SentinelNetOrchestrator, AgentInfo, AgentStatus
        from sentinelnet.core.config import get_settings
        from sentinelnet.agents.gcp_monitor import get_gcp_monitor
        from sentinelnet.agents.azure_monitor import get_azure_monitor
        from sentinelnet.agents.communication import initialize_communication
        from sentinelnet.dashboard.app import run_dashboard
        from sentinelnet.monitoring.prometheus import start_prometheus_server
        from datetime import datetime

        settings = get_settings()

        # Check environment
        if not settings.ai.openai_api_key and not settings.ai.google_api_key:
            logger.warning("⚠️  No AI API keys found - some features may be limited")
            logger.warning("Please edit the .env file with your API keys")

        # Check if we're in demo mode
        demo_mode = settings.is_development()

        if demo_mode:
            logger.info("🎯 Running in demo mode - using mock data and emulators")

        # Initialize communication layer
        logger.info("📡 Initializing communication layer...")
        comm_manager = await initialize_communication()

        # Initialize orchestrator with plugin-based AI agents
        logger.info("🎯 Initializing SentinelNet orchestrator with plugin-based AI...")
        orchestrator = SentinelNetOrchestrator()
        await orchestrator.initialize_plugins()

        # Register plugin-based agents with orchestrator
        for plugin_name, plugin_info in orchestrator.active_plugins.items():
            # Create agent info for plugin
            agent_info = AgentInfo(
                agent_id=f"plugin_{plugin_name}",
                agent_type="plugin",
                cloud_provider=plugin_info["capabilities"].get("cloud_provider", "multi_cloud"),
                services=plugin_info["capabilities"].get("features", []),
                status=AgentStatus.HEALTHY,
                last_heartbeat=datetime.now(),
                capabilities=plugin_info["capabilities"].get("features", [])
            )
            await orchestrator.register_agent(agent_info)
            logger.info(f"✅ Registered plugin agent: {plugin_name}")

        # Start monitoring in background
        monitor_tasks = []
        if settings.gcp.enabled and demo_mode:
            logger.info("🎮 Starting GCP monitoring in demo mode...")
            monitor_tasks.append(asyncio.create_task(gcp_monitor.start_monitoring()))

        if settings.azure.enabled and demo_mode:
            logger.info("🎮 Starting Azure monitoring in demo mode...")
            monitor_tasks.append(asyncio.create_task(azure_monitor.start_monitoring()))

        # Start Prometheus monitoring in background
        if settings.monitoring.enabled:
            logger.info("📊 Starting Prometheus monitoring...")
            prometheus_task = asyncio.create_task(start_prometheus_server_async(settings.monitoring.prometheus_port))
            monitor_tasks.append(prometheus_task)

        # Start dashboard
        logger.info("📊 Starting dashboard...")
        run_dashboard()

    except ImportError as e:
        logger.error(f"❌ Failed to import required modules: {e}")
        logger.info("💡 Make sure all requirements are installed: uv pip install -r requirements.txt")
        logger.info("💡 Or run: pip install -e .")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down SentinelNet...")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

async def start_prometheus_server_async(port: int):
    """Start Prometheus server asynchronously"""
    try:
        from sentinelnet.monitoring.prometheus import start_prometheus_server
        # Note: This would need to be made async-compatible
        start_prometheus_server(port)
    except Exception as e:
        logger.error(f"Failed to start Prometheus server: {e}")

def check_environment():
    """Check if the environment is properly configured"""
    from sentinelnet.core.config import get_settings

    settings = get_settings()

    # Check required AI keys
    ai_keys_missing = not (settings.ai.openai_api_key or settings.ai.google_api_key)

    if ai_keys_missing:
        print("⚠️  Missing AI API keys (OpenAI or Google AI required):")
        print("   - OPENAI_API_KEY or GOOGLE_API_KEY")
        print("Please edit the .env file with your actual API keys")

    # Check cloud configurations
    cloud_validation = settings.validate_cloud_configs()

    print("📊 Cloud Provider Status:")
    for provider, configured in cloud_validation.items():
        status = "✅ Configured" if configured else "⚠️ Not configured"
        print(f"   - {provider.upper()}: {status}")

    if ai_keys_missing:
        return False

    print("✅ Environment configuration looks good!")
    return True

if __name__ == "__main__":
    print("🚀 SentinelNet v0.1.0 - AI-Powered Multi-Cloud Resilience Platform")
    print("=" * 70)
    print("✨ Enhanced with Advanced AI Agents:")
    print("   • Microsoft AutoGen for Azure operations")
    print("   • Google Agent Development Kit for GCP")
    print("   • LangGraph for complex workflow orchestration")
    print("   • Grafana + Prometheus for comprehensive monitoring")
    print("=" * 70)

    # Check environment before starting
    if not check_environment():
        print("\n💡 Tips:")
        print("   • Edit the .env file with your API keys")
        print("   • Run: sentinelnet init (to initialize)")
        print("   • Run: sentinelnet api (to start API server)")
        print("   • Run: sentinelnet dashboard (to start dashboard)")
        sys.exit(1)

    # Run the main application
    asyncio.run(main())
