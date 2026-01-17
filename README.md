# SentinelNet v0.1.0: AI-Powered Multi-Cloud Resilience Platform

## 🚀 Vision: Intelligent Remediation for Cloud Infrastructure

**Prometheus alerts you when BigQuery goes down. SentinelNet tells you exactly what to do and does it for you.**

**The Problem:** SRE teams spend hours investigating alerts and manually executing remediation. During major outages, this costs millions in downtime and countless on-call hours.

**The Solution:** SentinelNet connects to your existing Grafana + Prometheus monitoring stack and adds an intelligent action layer powered by LangGraph AI agents.

**Example Flow:**
```
Prometheus Alert: "BigQuery US-east-1 High Latency"
     ↓
AlertManager → SentinelNet Webhook
     ↓
SentinelNet AI Agent: Analyzes alert + infrastructure context
     ↓
Intelligent Plan: "Switch to BigQuery US-west-2, update DNS, validate data consistency"
     ↓
Human Approval: SRE reviews cost/risk assessment in Dashboard
     ↓
Automated Execution: Terraform apply + monitoring + rollback ready
     ↓
Grafana Dashboard: Real-time execution tracking
```

**Unlike pure monitoring tools, SentinelNet transforms alerts into automated, intelligent remediation.**

---

## 🎯 Target Users

**Primary:** SRE Teams, DevOps Engineers, Platform Engineers

**Use Cases:**
- Automated incident response with human-in-the-loop approval
- Cross-cloud dependency analysis during outages
- Intelligent remediation plan generation
- Cost-benefit analysis for infrastructure changes

---

## ✨ Key Features

### 🤖 Advanced AI Agent Orchestration
- **LangGraph Workflows**: Complex multi-step remediation orchestration
- **Plugin Architecture**: Support for Microsoft AutoGen, Google Agent Kit, or LangChain
- **Intelligent Remediation**: AI-generated plans with safety validation and human oversight
- **Multi-LLM Support**: OpenAI GPT-4, Google Gemini, or Azure OpenAI

### 📊 Native Grafana + Prometheus Integration
- **Prometheus Metrics**: Real-time performance monitoring and custom metrics
- **AlertManager Webhooks**: Direct integration for alert-driven workflows
- **Grafana Dashboards**: Pre-built dashboards for SentinelNet metrics
- **OpenTelemetry**: Distributed tracing and observability

### ☁️ Multi-Cloud Intelligence
- **GCP Integration**: BigQuery, Vertex AI, Cloud Storage, Cloud Monitoring
- **Azure Integration**: Blob Storage, DevOps, Monitor, Resource Manager
- **AWS Ready**: Extensible architecture for additional cloud providers
- **Cross-Cloud Correlation**: Intelligent analysis across cloud boundaries

### 🛡️ Enterprise-Grade Security & Safety
- **Human-in-the-Loop**: All remediation plans require explicit approval
- **Safety Validation**: Automated risk assessment and rollback planning
- **Audit Logging**: Comprehensive action tracking and compliance
- **No Destructive Actions**: Demo mode prevents accidental damage

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SentinelNet Platform                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   Grafana    │    │  Prometheus  │    │ AlertManager │              │
│  │  Dashboards  │◄──►│   Metrics    │◄──►│   Webhooks   │              │
│  └──────────────┘    └──────────────┘    └──────┬───────┘              │
│                                                  │                       │
│                                                  ▼                       │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    SentinelNet API (FastAPI)                      │  │
│  │  • /webhooks/alertmanager  • /api/remediation  • /api/status     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                   AI Agent Orchestrator (LangGraph)               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │  │
│  │  │  Monitor    │  │   Impact    │  │ Remediation │              │  │
│  │  │   Agent     │  │   Analyzer  │  │   Planner   │              │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      Plugin System                                │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐    │  │
│  │  │ LangChain │  │  AutoGen  │  │  Google   │  │  Custom   │    │  │
│  │  │  (Multi)  │  │  (Azure)  │  │   (GCP)   │  │  Plugins  │    │  │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│                                    ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Cloud Integrations                             │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │  │
│  │  │      GCP        │  │     Azure       │  │      AWS        │  │  │
│  │  │ BigQuery,Vertex │  │ Blob,DevOps     │  │   (Future)      │  │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.9+ 
- **Package Manager**: UV (recommended) or pip
- **Cloud Accounts**: GCP and/or Azure (free tiers work)
- **AI API Key**: OpenAI or Google AI

### Installation

```bash
# Clone the repository
git clone https://github.com/Vinayak-Pawar/SentinelNet.git
cd SentinelNet

# Option 1: One-click setup (recommended)
chmod +x setup_and_run_v2.sh
./setup_and_run_v2.sh

# Option 2: Manual installation
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### CLI Commands

```bash
# Initialize SentinelNet
sentinelnet init

# Start the API server
sentinelnet api

# Start the dashboard
sentinelnet dashboard

# Start Prometheus metrics server
sentinelnet monitor

# Check system status
sentinelnet status

# Run tests
sentinelnet test
```

### Quick Demo

```bash
# Start all services
sentinelnet api &
sentinelnet dashboard &
sentinelnet monitor &

# Open in browser
# API Docs: http://localhost:8000/docs
# Dashboard: http://localhost:8501
# Metrics: http://localhost:8001/metrics
```

---

## 📁 Project Structure

```
sentinelnet/
├── sentinelnet/              # Main package
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # Command-line interface
│   ├── core/                 # Core components
│   │   ├── config.py         # Configuration management
│   │   └── orchestrator.py   # LangGraph orchestration
│   ├── agents/               # AI agent implementations
│   │   ├── __init__.py       # Plugin manager
│   │   ├── plugins/          # Agent plugins
│   │   │   ├── autogen_azure.py
│   │   │   ├── google_gcp.py
│   │   │   └── langchain_multi.py
│   │   ├── gcp_monitor.py    # GCP monitoring
│   │   └── azure_monitor.py  # Azure monitoring
│   ├── api/                  # FastAPI backend
│   │   └── main.py           # API endpoints
│   ├── dashboard/            # Streamlit dashboard
│   │   └── app.py            # Dashboard application
│   └── monitoring/           # Observability
│       ├── prometheus.py     # Prometheus metrics
│       └── grafana.py        # Grafana integration
├── docs/                     # Documentation
├── logs/                     # Application logs
├── pyproject.toml            # Package configuration
├── requirements.txt          # Dependencies
└── main.py                   # Application entry point
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# ===========================================
# SentinelNet Configuration
# ===========================================

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# ===========================================
# AI Services (at least one required)
# ===========================================
OPENAI_API_KEY=sk-your-openai-api-key
# OR
GOOGLE_API_KEY=your-google-ai-api-key

# ===========================================
# Google Cloud Platform (optional)
# ===========================================
GCP_ENABLED=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# ===========================================
# Microsoft Azure (optional)
# ===========================================
AZURE_ENABLED=true
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id

# ===========================================
# Monitoring (Grafana + Prometheus)
# ===========================================
MONITORING_ENABLED=true
PROMETHEUS_PORT=8001
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=your-grafana-api-key

# ===========================================
# API Configuration
# ===========================================
API_HOST=0.0.0.0
API_PORT=8000

# ===========================================
# Dashboard Configuration
# ===========================================
DASHBOARD_PORT=8501
```

---

## 📊 Grafana + Prometheus Integration

### AlertManager Configuration

Add SentinelNet as a webhook receiver in your `alertmanager.yml`:

```yaml
receivers:
  - name: 'sentinelnet'
    webhook_configs:
      - url: 'http://localhost:8000/webhooks/alertmanager'
        send_resolved: true

route:
  receiver: 'sentinelnet'
  group_by: ['alertname', 'service']
  group_wait: 10s
  group_interval: 5m
  repeat_interval: 3h
```

### Available Prometheus Metrics

SentinelNet exposes the following metrics at `/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `sentinelnet_requests_total` | Counter | Total API requests |
| `sentinelnet_request_latency_seconds` | Histogram | Request latency |
| `sentinelnet_active_agents` | Gauge | Number of active agents |
| `sentinelnet_incidents_total` | Counter | Total incidents detected |
| `sentinelnet_remediations_total` | Counter | Total remediation plans |
| `sentinelnet_remediation_success_rate` | Gauge | Success rate of remediations |

### Grafana Dashboard

Import the pre-built dashboard from `dashboards/sentinelnet.json` or create via API:

```bash
sentinelnet grafana --import-dashboard
```

---

## 🚦 API Endpoints

### Alert Integration
```
POST /webhooks/alertmanager    # Receive AlertManager webhooks
POST /webhooks/custom          # Custom alert ingestion
```

### AI Analysis
```
POST /api/analysis/impact      # Analyze alert impact
POST /api/analysis/plan        # Generate remediation plan
GET  /api/analysis/{plan_id}   # Get plan details
```

### Remediation
```
POST /api/remediation/{plan_id}/approve   # Approve plan
POST /api/remediation/{plan_id}/execute   # Execute plan
POST /api/remediation/{plan_id}/rollback  # Rollback execution
GET  /api/remediation/{plan_id}/status    # Execution status
```

### System
```
GET  /health                   # Health check
GET  /api/system/status        # System status
GET  /api/system/metrics       # Metrics summary
GET  /metrics                  # Prometheus metrics
```

---

## 🔄 Workflow Example

### BigQuery Regional Failover

```
1. Alert Received: BigQuery US-east-1 unavailable
   └─► AlertManager webhook → SentinelNet API

2. AI Analysis: 
   └─► Identifies 15 applications using this region
   └─► Maps cross-cloud dependencies
   └─► Calculates business impact score

3. Remediation Plan Generated:
   ├─► Step 1: Validate BigQuery US-west-2 availability
   ├─► Step 2: Generate dataset replication commands
   ├─► Step 3: Create Terraform config for region switch
   ├─► Step 4: Estimate costs ($50 downtime vs $200 transfer)
   └─► Step 5: Prepare rollback procedure

4. Human Approval:
   └─► SRE reviews plan in Dashboard
   └─► Approves execution with one click

5. Automated Execution:
   └─► Terraform apply with monitoring
   └─► Real-time progress in Grafana

6. Verification:
   └─► Confirm applications working
   └─► Auto-rollback if issues detected
```

---

## 🤖 AI Agent Framework

### Plugin System

SentinelNet supports multiple AI agent frameworks through its plugin architecture:

| Plugin | Best For | License |
|--------|----------|---------|
| `langchain` | Multi-cloud, flexibility | MIT (Free) |
| `langgraph` | Complex workflows | MIT (Free) |
| `autogen` | Azure-native operations | MIT (Free) |
| `google_agent_kit` | GCP-native operations | Included with GCP |

### Configuration

```bash
# Use LangChain for everything (recommended for most users)
PLUGIN_MULTI_CLOUD_PLUGINS=["langchain", "langgraph"]

# Azure-focused (if you have Azure licenses)
PLUGIN_AZURE_PLUGINS=["autogen", "langchain"]

# GCP-focused (if you use Google Cloud)
PLUGIN_GCP_PLUGINS=["google_agent_kit", "langchain"]
```

---

## 🔒 Safety & Security

### Safety Measures
- **Human Approval Required**: All remediation plans require explicit approval
- **Risk Assessment**: Automated risk scoring for every action
- **Rollback Planning**: Every plan includes rollback procedures
- **Demo Mode**: Default mode prevents real infrastructure changes
- **Audit Logging**: Complete action history for compliance

### What We Automate (with approval)
- Dataset replication
- Endpoint switching
- Configuration updates
- DNS changes

### What We Never Touch
- Production databases without explicit approval
- Customer data
- Billing configurations
- Security credentials

---

## 📈 Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for the complete development plan.

### Current Status: v0.1.0 (MVP)
- [x] Core package structure
- [x] Plugin-based agent architecture
- [x] FastAPI backend
- [x] Streamlit dashboard
- [x] Prometheus metrics
- [ ] AlertManager webhook integration
- [ ] Complete LangGraph workflows
- [ ] Grafana dashboard templates
- [ ] End-to-end testing

---

## 🧪 Development

### Running Tests

```bash
# Run all tests
sentinelnet test

# Or using pytest directly
pytest tests/ -v --cov=sentinelnet
```

### Code Quality

```bash
# Format code
black sentinelnet/
isort sentinelnet/

# Lint
flake8 sentinelnet/
mypy sentinelnet/
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`sentinelnet test`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## ⚖️ Disclaimer

**Educational/Portfolio Project**: This project is designed for educational purposes and portfolio demonstration. It implements safety measures to prevent unintended actions, but should never be used in production environments without enterprise-grade security reviews and liability assessments.

**No Warranty**: The software is provided "as is" without warranty of any kind.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/Vinayak-Pawar/SentinelNet/issues)
- **Author**: Vinayak Pawar

---

**Built with ❤️ for SRE teams everywhere**

*Transforming alerts into intelligent action*
