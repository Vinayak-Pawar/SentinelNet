#!/bin/bash

# SentinelNet v0.1.0 Setup and Run Script
# Enhanced version with Python package installation and advanced AI agents
# Version: 2.0
# Author: Vinayak Pawar
# Description: Complete setup and execution for SentinelNet with advanced AI capabilities
# Compatible with: M1 Pro MacBook Pro (Apple Silicon)

set -e  # Exit on any error

echo "🚀 SentinelNet v0.1.0 - Advanced AI-Powered Multi-Cloud Resilience Platform"
echo "=========================================================================="
echo "✨ Features:"
echo "   • Microsoft AutoGen for Azure cloud operations"
echo "   • Google Agent Development Kit for GCP intelligence"
echo "   • LangGraph for complex workflow orchestration"
echo "   • Grafana + Prometheus comprehensive monitoring"
echo "   • High-performance async task processing"
echo "   • Advanced anomaly detection and remediation"
echo ""

# Check if running on macOS with Apple Silicon
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS. Please run on macOS."
    exit 1
fi

# Check for Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "⚠️  Warning: Not running on Apple Silicon. Some optimizations may not work."
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command_exists uv; then
    echo "❌ UV is not installed. Please install it first: https://github.com/astral-sh/uv"
    echo "   Run: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3."
    exit 1
fi

if ! command_exists docker; then
    echo "⚠️  Docker not found. Some features may be limited."
    echo "   Install Docker Desktop for Mac for full functionality."
fi

echo "✅ Prerequisites check passed!"

# Create Python environment
echo "🐍 Creating Python UV environment..."
uv venv sentinelnet_env_v2

# Activate environment
echo "🔄 Activating environment..."
source sentinelnet_env_v2/bin/activate

# Install the package in development mode
echo "📦 Installing SentinelNet package..."
if [ -f "pyproject.toml" ]; then
    uv pip install -e .
    echo "✅ Package installed in development mode!"
else
    echo "⚠️  pyproject.toml not found. Installing basic dependencies..."
    uv pip install langchain langchain-community langgraph openai fastapi uvicorn streamlit
fi

# Create .env file if it doesn't exist
echo "🔐 Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# SentinelNet v0.1.0 Configuration
# IMPORTANT: Edit this file with your actual API keys before running the project

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Google Cloud Platform (GCP)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
GCP_REGION=us-central1

# Microsoft Azure
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_REGION=East US

# Azure DevOps
AZURE_DEVOPS_ORGANIZATION=your-organization
AZURE_DEVOPS_PAT=your-personal-access-token

# AI Agent Strategy Configuration
# Choose your preferred agent framework strategy:
# - "langgraph_only": Use LangChain/LangGraph only (no vendor lock-in)
# - "autogen_azure": Use Microsoft AutoGen for Azure operations
# - "google_gcp": Use Google Agent Development Kit for GCP operations
# - "hybrid": Combine multiple frameworks (requires multiple licenses)
AI_AGENT_STRATEGY=langgraph_only

# AI Services - OpenAI (Primary - works with all strategies)
OPENAI_API_KEY=your-openai-api-key
AI_OPENAI_MODEL=gpt-4-turbo-preview

# AI Services - Google AI (Required for google_gcp or hybrid strategies)
GOOGLE_API_KEY=your-google-api-key
AI_GOOGLE_MODEL=gemini-pro

# Vertex AI (Google Cloud AI - for google_gcp or hybrid strategies)
AI_VERTEX_AI_MODEL=text-bison@002

# AutoGen Configuration (for autogen_azure or hybrid strategies)
AI_AUTOGEN_TIMEOUT=300
AI_AUTOGEN_MAX_ROUNDS=50

# LangGraph Configuration (always used for orchestration)
AI_LANGGRAPH_TIMEOUT=600
AI_LANGGRAPH_MAX_ITERATIONS=100

# Application Settings
API_HOST=0.0.0.0
API_PORT=8000
DASHBOARD_PORT=8501
AGENT_DISCOVERY_PORT=8080

# Monitoring & Observability
MONITORING_ENABLED=true
MONITORING_PROMETHEUS_PORT=8001
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=your-grafana-api-key

# Database Configuration
DATABASE_URL=sqlite:///./sentinelnet.db
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Security Settings
SECURITY_API_KEY_REQUIRED=false
JWT_SECRET_KEY=your-secret-key-change-in-production

# Safety Settings
ALLOW_AUTOMATED_ACTIONS=false
REQUIRE_HUMAN_APPROVAL=true

# Communication Settings
AGENT_MAX_CONCURRENT=10
AGENT_HEARTBEAT_INTERVAL=30
COMMUNICATION_USE_P2P=true
WEBRTC_SIGNALING_SERVER=ws://localhost:8080

# Cloud Provider Settings
GCP_ENABLED=true
AZURE_ENABLED=true
AWS_ENABLED=false

EOF
    echo "✅ Created enhanced .env file with placeholder values."
    echo "⚠️  IMPORTANT: Please edit the .env file with your actual API keys!"
    echo "   Required: OPENAI_API_KEY or GOOGLE_API_KEY"
    echo "   Optional: GCP and Azure credentials for real cloud monitoring"
else
    echo "ℹ️  .env file already exists. Skipping creation."
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs data models/saved_models sentinelnet.egg-info

# Initialize database
echo "🗄️  Initializing database..."
python -c "
from sentinelnet.data.processor import DataProcessor
processor = DataProcessor()
print('✅ Database initialized')
" 2>/dev/null || echo "⚠️  Database initialization skipped (may require additional setup)"

# Setup complete message
echo ""
echo "🎉 SentinelNet v0.1.0 Setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. ✏️  Edit the .env file with your actual API keys (OpenAI or Google AI required)"
echo "2. 🏃 Run the project with: python main.py"
echo "3. 🌐 Open your browser to:"
echo "   • Dashboard: http://localhost:8501"
echo "   • API docs: http://localhost:8000/docs"
echo "   • Prometheus: http://localhost:8001"
echo ""
echo "🛠️  Available commands:"
echo "   • sentinelnet api          # Start FastAPI server"
echo "   • sentinelnet dashboard    # Start Streamlit dashboard"
echo "   • sentinelnet monitor      # Start Prometheus monitoring"
echo "   • sentinelnet status       # Show system status"
echo "   • sentinelnet test         # Run connectivity tests"
echo ""
echo "🤖 Advanced AI Features:"
echo "   • POST /agents/autogen/azure/execute - Execute AutoGen Azure tasks (if enabled)"
echo "   • POST /agents/google/gcp/analyze - Google Agent analysis (if enabled)"
echo "   • POST /agents/langgraph/workflow - Custom LangGraph workflows (always available)"
echo "   • POST /monitoring/grafana/dashboard - Create Grafana dashboards"
echo ""
echo "💰 Licensing Information:"
echo "   • LangGraph: Commercial license required (~$100-500/user/year)"
echo "   • AutoGen: MIT License (free, requires Azure subscription)"
echo "   • Google Agent Kit: Included with GCP (requires GCP subscription)"
echo "   • Recommendation: Start with langgraph_only to avoid lock-in"
echo ""
echo "📖 For detailed documentation, see README.md"
echo "🆘 If you encounter issues, run: sentinelnet status"
echo ""

# Optional: Ask if user wants to run the project immediately
read -p "❓ Would you like to start the SentinelNet dashboard now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting SentinelNet Dashboard..."
    if [ -f "sentinelnet/dashboard/app.py" ]; then
        streamlit run sentinelnet/dashboard/app.py
    elif [ -f "main.py" ]; then
        python main.py
    else
        echo "⚠️  No main application file found. Please run manually after setup."
    fi
fi

echo ""
echo "💡 Pro tip: Run 'sentinelnet --help' to see all available commands"
echo "🎯 SentinelNet v0.1.0 is ready for advanced AI-powered cloud resilience! 🚀"
