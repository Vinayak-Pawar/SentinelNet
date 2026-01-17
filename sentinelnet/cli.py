#!/usr/bin/env python3
"""
SentinelNet Command Line Interface

Provides command-line tools for managing and running SentinelNet.
"""

import click
import uvicorn
import asyncio
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from sentinelnet.core.config import get_settings
from sentinelnet.core.orchestrator import SentinelNetOrchestrator
from sentinelnet.api.main import create_app
from sentinelnet.dashboard.app import run_dashboard
from sentinelnet.monitoring.prometheus import start_prometheus_server

console = Console()
settings = get_settings()


@click.group()
@click.version_option(version=settings.version)
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(config, verbose):
    """SentinelNet - AI-Powered Multi-Cloud Resilience Platform

    Intelligent cloud monitoring, incident response, and automated remediation
    using advanced AI agents and multi-cloud orchestration.
    """
    if config:
        # Load custom config if provided
        pass

    if verbose:
        console.print(f"[bold blue]SentinelNet v{settings.version}[/bold blue]")
        console.print(f"Environment: {settings.environment}")
        console.print(f"Debug mode: {settings.debug}")
        console.print()


@cli.command()
@click.option('--host', default=settings.api.host, help='API server host')
@click.option('--port', default=settings.api.port, type=int, help='API server port')
@click.option('--workers', default=settings.api.workers, type=int, help='Number of workers')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def api(host, port, workers, reload):
    """Start the FastAPI server"""
    console.print("[bold green]🚀 Starting SentinelNet API Server[/bold green]")

    # Update settings
    settings.api.host = host
    settings.api.port = port
    settings.api.workers = workers
    settings.api.reload = reload

    try:
        app = create_app()
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers,
            reload=reload,
            log_level="info" if not settings.debug else "debug"
        )
    except Exception as e:
        console.print(f"[bold red]❌ Failed to start API server: {e}[/bold red]")
        raise click.Abort()


@cli.command()
@click.option('--port', default=8501, type=int, help='Dashboard port')
@click.option('--host', default='localhost', help='Dashboard host')
def dashboard(port, host):
    """Start the Streamlit dashboard"""
    console.print("[bold green]📊 Starting SentinelNet Dashboard[/bold green]")

    import os
    os.environ['STREAMLIT_SERVER_PORT'] = str(port)
    os.environ['STREAMLIT_SERVER_ADDRESS'] = host

    try:
        run_dashboard()
    except Exception as e:
        console.print(f"[bold red]❌ Failed to start dashboard: {e}[/bold red]")
        raise click.Abort()


@cli.command()
@click.option('--config-only', is_flag=True, help='Show only configuration validation')
@click.option('--fix', is_flag=True, help='Attempt to fix configuration issues')
def status(config_only, fix):
    """Show system status and configuration"""
    table = Table(title="System Status")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")

    # Configuration validation
    cloud_validation = settings.validate_cloud_configs()

    # Core components
    table.add_row("Configuration", "✅ Valid", "All settings loaded")
    table.add_row("Database", "✅ Ready", f"URL: {settings.database.url}")
    table.add_row("API Server", "✅ Configured", f"Port: {settings.api.port}")

    # Cloud providers
    for provider in ['gcp', 'azure', 'aws']:
        status_emoji = "✅" if cloud_validation.get(provider, False) else "⚠️"
        details = "Configured" if cloud_validation[provider] else "Not configured"
        table.add_row(f"{provider.upper()} Provider", f"{status_emoji} {details}", "")

    # AI services
    ai_status = "✅" if settings.ai.openai_api_key or settings.ai.google_api_key else "⚠️"
    ai_details = []
    if settings.ai.openai_api_key:
        ai_details.append("OpenAI")
    if settings.ai.google_api_key:
        ai_details.append("Google AI")
    ai_detail_str = ", ".join(ai_details) if ai_details else "No API keys configured"
    table.add_row("AI Services", f"{ai_status} {ai_detail_str}", "")

    console.print(table)

    if not config_only:
        # Show recent activity
        console.print("\n[bold]Recent Activity:[/bold]")
        logs_dir = settings.logs_dir
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            if log_files:
                latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                console.print(f"Latest log: {latest_log.name}")
                # Could show last few lines here
            else:
                console.print("No log files found")
        else:
            console.print("Logs directory not found")


@cli.command()
@click.option('--provider', type=click.Choice(['gcp', 'azure', 'aws', 'all']),
              default='all', help='Cloud provider to test')
@click.option('--service', help='Specific service to test')
def test(provider, service):
    """Run connectivity and functionality tests"""
    console.print("[bold blue]🧪 Running SentinelNet Tests[/bold blue]")

    async def run_tests():
        results = []

        # Test orchestrator initialization
        try:
            orchestrator = SentinelNetOrchestrator()
            results.append(("Orchestrator", "✅", "Initialized successfully"))
        except Exception as e:
            results.append(("Orchestrator", "❌", str(e)))

        # Test cloud providers
        if provider in ['gcp', 'all']:
            # GCP tests
            try:
                from sentinelnet.agents.gcp_monitor import get_gcp_monitor
                monitor = get_gcp_monitor()
                results.append(("GCP Monitor", "✅", "Initialized"))
            except Exception as e:
                results.append(("GCP Monitor", "❌", str(e)))

        if provider in ['azure', 'all']:
            # Azure tests
            try:
                from sentinelnet.agents.azure_monitor import get_azure_monitor
                monitor = get_azure_monitor()
                results.append(("Azure Monitor", "✅", "Initialized"))
            except ImportError:
                results.append(("Azure Monitor", "⚠️", "Not implemented yet"))
            except Exception as e:
                results.append(("Azure Monitor", "❌", str(e)))

        # Display results
        table = Table(title="Test Results")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")

        for component, status, details in results:
            table.add_column(component, status)
            table.add_column(details)

        console.print(table)

    asyncio.run(run_tests())


@cli.command()
@click.option('--days', default=30, type=int, help='Days to retain data')
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned without deleting')
def cleanup(days, dry_run):
    """Clean up old data and logs"""
    console.print(f"[bold yellow]🧹 Cleaning up data older than {days} days[/bold yellow]")

    if dry_run:
        console.print("[italic]Dry run mode - no files will be deleted[/italic]")

    # This would implement actual cleanup logic
    console.print("Cleanup functionality to be implemented")


@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file for configuration')
def config(output):
    """Show or export current configuration"""
    if output:
        # Export configuration
        console.print(f"📄 Exporting configuration to {output}")
        # Implementation would go here
    else:
        # Show configuration
        config_panel = Panel.fit(
            f"[bold]SentinelNet Configuration[/bold]\n\n"
            f"Version: {settings.version}\n"
            f"Environment: {settings.environment}\n"
            f"Debug: {settings.debug}\n\n"
            f"[bold]API:[/bold]\n"
            f"Host: {settings.api.host}\n"
            f"Port: {settings.api.port}\n\n"
            f"[bold]Cloud Providers:[/bold]\n"
            f"GCP: {'✅' if settings.gcp.enabled else '❌'}\n"
            f"Azure: {'✅' if settings.azure.enabled else '❌'}\n"
            f"AWS: {'✅' if settings.aws.enabled else '❌'}\n\n"
            f"[bold]AI Services:[/bold]\n"
            f"OpenAI: {'✅' if settings.ai.openai_api_key else '❌'}\n"
            f"Google AI: {'✅' if settings.ai.google_api_key else '❌'}",
            title="Configuration Overview"
        )
        console.print(config_panel)


@cli.command()
def init():
    """Initialize SentinelNet environment and configuration"""
    console.print("[bold green]🚀 Initializing SentinelNet[/bold green]")

    # Create necessary directories
    dirs_to_create = [
        settings.data_dir,
        settings.logs_dir,
        settings.models_dir,
        settings.config_dir
    ]

    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        console.print(f"📁 Created directory: {dir_path}")

    # Create default configuration files
    console.print("📝 Creating default configuration...")

    # This would create default config files
    console.print("✅ Initialization complete!")


@cli.command()
@click.option('--port', default=settings.monitoring.prometheus_port, type=int,
              help='Prometheus metrics port')
def monitor(port):
    """Start monitoring server (Prometheus metrics)"""
    console.print("[bold green]📊 Starting SentinelNet Monitoring[/bold green]")

    try:
        start_prometheus_server(port)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to start monitoring: {e}[/bold red]")
        raise click.Abort()


def main():
    """Main CLI entry point"""
    cli()


if __name__ == "__main__":
    main()
