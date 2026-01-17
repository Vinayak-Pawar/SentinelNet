# SentinelNet Development Roadmap

> **Target User:** SRE/DevOps Teams  
> **Product Type:** AI-Powered Remediation Platform  
> **Monitoring Stack:** Grafana + Prometheus  
> **Last Updated:** January 2026

---

## 📋 Executive Summary

SentinelNet is an AI-powered multi-cloud resilience platform that transforms Prometheus alerts into intelligent, automated remediation actions. Built for SRE teams who need faster incident response with human oversight.

**Core Value Proposition:**
```
Prometheus Alert → AI Analysis → Remediation Plan → Human Approval → Automated Execution
```

---

## 🎯 Development Phases Overview

| Phase | Focus | Duration | Status |
|-------|-------|----------|--------|
| **Phase 0** | Foundation & Setup | 1 week | ✅ Complete |
| **Phase 1** | Core Alert Pipeline | 2 weeks | 🔄 In Progress |
| **Phase 2** | AI Remediation Engine | 2 weeks | ⏳ Pending |
| **Phase 3** | Dashboard & UX | 1 week | ⏳ Pending |
| **Phase 4** | Testing & Polish | 1 week | ⏳ Pending |
| **Phase 5** | Enterprise Features | 2 weeks | ⏳ Future |

---

## ✅ Phase 0: Foundation & Setup (COMPLETE)

### Completed Items

- [x] **Project Structure**
  - [x] Create `sentinelnet/` package structure
  - [x] Setup `pyproject.toml` for pip installation
  - [x] Create CLI with Click (`sentinelnet` command)
  - [x] Setup logging and configuration management

- [x] **Core Configuration**
  - [x] Pydantic settings management (`core/config.py`)
  - [x] Environment variable support (`.env`)
  - [x] Multi-cloud provider configuration (GCP, Azure, AWS)
  - [x] AI provider configuration (OpenAI, Google AI)

- [x] **Plugin Architecture**
  - [x] Abstract plugin interface (`agents/__init__.py`)
  - [x] Plugin manager with activation/deactivation
  - [x] LangChain multi-cloud plugin
  - [x] Framework for AutoGen and Google Agent Kit plugins

- [x] **Basic Infrastructure**
  - [x] FastAPI server setup (`api/main.py`)
  - [x] Streamlit dashboard skeleton (`dashboard/app.py`)
  - [x] Prometheus metrics foundation (`monitoring/prometheus.py`)
  - [x] Basic health check endpoints

---

## 🔄 Phase 1: Core Alert Pipeline (2 WEEKS)

### Week 1: AlertManager Integration

#### Task 1.1: Webhook Receiver ✅ COMPLETE
- [x] **Create AlertManager webhook endpoint**
  - [x] `POST /webhooks/alertmanager` endpoint
  - [x] Parse AlertManager JSON payload
  - [x] Extract alert labels and annotations
  - [x] Handle `firing` and `resolved` states
  - [x] Return proper acknowledgment response

```python
# Expected endpoint signature
@app.post("/webhooks/alertmanager")
async def receive_alertmanager_webhook(payload: AlertManagerPayload):
    # Process incoming alert
    pass
```

#### Task 1.2: Alert Data Models ✅ COMPLETE
- [x] **Define Pydantic models for alerts**
  - [x] `AlertManagerPayload` model
  - [x] `Alert` model with severity, service, cloud_provider
  - [x] `AlertStatus` enum (firing, resolved, acknowledged)
  - [x] `Incident` model for grouped alerts

#### Task 1.3: Alert Storage ✅ COMPLETE
- [x] **Implement alert persistence**
  - [x] SQLite database for local development
  - [x] Alert table schema (id, timestamp, status, payload)
  - [x] Simple database wrapper (will migrate to SQLAlchemy in Phase 2)
  - [x] Basic CRUD operations

#### Task 1.4: Alert Queue
- [ ] **Create async alert processing queue**
  - [ ] In-memory queue for alert processing
  - [ ] Background task for queue processing
  - [ ] Rate limiting for AI API calls
  - [ ] Deduplication of repeated alerts

### Week 2: Alert Processing Pipeline

#### Task 1.5: Alert Enrichment
- [ ] **Add context to raw alerts**
  - [ ] Fetch service metadata from cloud providers
  - [ ] Query Prometheus for related metrics
  - [ ] Identify affected services and dependencies
  - [ ] Calculate initial severity score

#### Task 1.6: Alert Correlation
- [ ] **Group related alerts**
  - [ ] Time-window based grouping
  - [ ] Service-based correlation
  - [ ] Cross-cloud dependency mapping
  - [ ] Create incident from correlated alerts

#### Task 1.7: Prometheus Integration
- [ ] **Query Prometheus for context**
  - [ ] Prometheus client library integration
  - [ ] Query recent metrics for affected services
  - [ ] Fetch alert history
  - [ ] Get resource utilization data

#### Task 1.8: API Endpoints for Alerts ✅ COMPLETE
- [x] **Expose alert management API**
  - [x] `GET /api/alerts` - List active alerts
  - [x] `GET /api/alerts/{id}` - Get alert details
  - [x] `POST /api/alerts/{id}/acknowledge` - Acknowledge alert
  - [x] `GET /api/stats` - Get system statistics

### Phase 1 Deliverables
- [ ] Working AlertManager webhook integration
- [ ] Alert storage and retrieval
- [ ] Basic alert correlation
- [ ] API endpoints for alert management

### Phase 1 Success Criteria
- [ ] Can receive alerts from AlertManager
- [ ] Alerts persisted to database
- [ ] Related alerts grouped into incidents
- [ ] API returns alert data correctly

---

## ⏳ Phase 2: AI Remediation Engine (2 WEEKS)

### Week 3: LangGraph Workflow Implementation

#### Task 2.1: Incident Analysis Workflow
- [ ] **Create LangGraph workflow for incident analysis**
  - [ ] Define workflow state schema
  - [ ] Implement `analyze_incident` node
  - [ ] Implement `assess_impact` node
  - [ ] Implement `identify_dependencies` node
  - [ ] Connect nodes with conditional edges

```python
# Workflow structure
workflow = StateGraph(IncidentState)
workflow.add_node("analyze", analyze_incident)
workflow.add_node("assess_impact", assess_impact)
workflow.add_node("identify_deps", identify_dependencies)
workflow.add_node("generate_plan", generate_remediation_plan)
```

#### Task 2.2: Impact Analysis Agent
- [ ] **Build AI agent for impact assessment**
  - [ ] System prompt for impact analysis
  - [ ] Context gathering from cloud providers
  - [ ] Business impact scoring
  - [ ] Affected service enumeration

#### Task 2.3: Remediation Plan Generator
- [ ] **Create AI-powered plan generation**
  - [ ] Define remediation action types
  - [ ] Generate step-by-step plans
  - [ ] Include estimated time and risk
  - [ ] Add rollback procedures

#### Task 2.4: Plan Data Models
- [ ] **Define remediation plan structures**
  - [ ] `RemediationPlan` model
  - [ ] `RemediationStep` model
  - [ ] `RiskAssessment` model
  - [ ] `RollbackProcedure` model

### Week 4: Safety & Execution

#### Task 2.5: Safety Validation
- [ ] **Implement safety checks for plans**
  - [ ] Destructive action detection
  - [ ] Cost estimation
  - [ ] Risk scoring algorithm
  - [ ] Required approval level determination

#### Task 2.6: Human Approval Flow
- [ ] **Create approval workflow**
  - [ ] Pending approval queue
  - [ ] Approval API endpoints
  - [ ] Approval notification system
  - [ ] Approval timeout handling

#### Task 2.7: Execution Engine
- [ ] **Build plan execution system**
  - [ ] Step-by-step execution
  - [ ] Progress tracking
  - [ ] Error handling and rollback
  - [ ] Execution logging

#### Task 2.8: Cloud Provider Actions
- [ ] **Implement cloud-specific actions**
  - [ ] GCP: BigQuery region switching
  - [ ] GCP: Vertex AI endpoint failover
  - [ ] Azure: Blob Storage geo-redundancy
  - [ ] Azure: Resource scaling

### Phase 2 Deliverables
- [ ] Working LangGraph remediation workflow
- [ ] AI-generated remediation plans
- [ ] Safety validation system
- [ ] Human approval flow
- [ ] Basic execution engine

### Phase 2 Success Criteria
- [ ] AI generates valid remediation plans
- [ ] Safety validation catches risky actions
- [ ] Approval flow works end-to-end
- [ ] Demo execution completes successfully

---

## ⏳ Phase 3: Dashboard & UX (1 WEEK)

#### Task 3.1: Alert Dashboard
- [ ] **Build alert monitoring view**
  - [ ] Active alerts list with filtering
  - [ ] Alert details panel
  - [ ] Severity indicators
  - [ ] Real-time updates

#### Task 3.2: Incident Triage View
- [ ] **Create incident management interface**
  - [ ] Incident timeline
  - [ ] Correlated alerts view
  - [ ] Impact summary
  - [ ] Quick actions

#### Task 3.3: Remediation Plan Review
- [ ] **Build plan approval interface**
  - [ ] Plan details with steps
  - [ ] Risk assessment display
  - [ ] Cost estimation
  - [ ] Approve/Reject buttons
  - [ ] Feedback input

#### Task 3.4: Execution Monitoring
- [ ] **Create execution tracking view**
  - [ ] Step progress indicator
  - [ ] Real-time logs
  - [ ] Rollback button
  - [ ] Success/failure status

#### Task 3.5: System Status Page
- [ ] **Build observability dashboard**
  - [ ] Agent health status
  - [ ] Cloud provider connections
  - [ ] AI service status
  - [ ] Recent activity log

### Phase 3 Deliverables
- [ ] Functional Streamlit dashboard
- [ ] Alert and incident views
- [ ] Plan approval interface
- [ ] Execution monitoring

---

## ⏳ Phase 4: Testing & Polish (1 WEEK)

#### Task 4.1: Unit Tests
- [ ] **Write comprehensive unit tests**
  - [ ] Alert processing tests
  - [ ] Workflow node tests
  - [ ] API endpoint tests
  - [ ] Plugin tests

#### Task 4.2: Integration Tests
- [ ] **End-to-end workflow tests**
  - [ ] Alert → Plan generation
  - [ ] Approval → Execution
  - [ ] Rollback scenarios
  - [ ] Error handling

#### Task 4.3: Demo Scenarios
- [ ] **Create demo scripts**
  - [ ] BigQuery outage scenario
  - [ ] Azure Blob latency scenario
  - [ ] Cross-cloud incident
  - [ ] Successful remediation

#### Task 4.4: Documentation
- [ ] **Complete documentation**
  - [ ] API documentation (OpenAPI)
  - [ ] Setup guide
  - [ ] Configuration reference
  - [ ] Demo walkthrough

#### Task 4.5: Grafana Integration
- [ ] **Create Grafana dashboards**
  - [ ] SentinelNet metrics dashboard JSON
  - [ ] Import script
  - [ ] Dashboard provisioning

### Phase 4 Deliverables
- [ ] Test coverage > 70%
- [ ] Working demo scenarios
- [ ] Complete documentation
- [ ] Grafana dashboard templates

---

## ⏳ Phase 5: Enterprise Features (FUTURE)

### Planned Features

- [ ] **Multi-tenancy Support**
- [ ] **RBAC and Team Management**
- [ ] **Slack/PagerDuty Integration**
- [ ] **Custom Plugin Development**
- [ ] **ML-based Prediction**
- [ ] **Terraform Automation**
- [ ] **Kubernetes Operator**

---

## 📊 Progress Tracking

### Current Sprint Focus

```
Phase 1, Week 1: AlertManager Integration
├── Task 1.1: Webhook Receiver      [ ] Not Started
├── Task 1.2: Alert Data Models     [ ] Not Started
├── Task 1.3: Alert Storage         [ ] Not Started
└── Task 1.4: Alert Queue           [ ] Not Started
```

### Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Test Coverage | 70% | 0% |
| API Endpoints | 15 | 8 |
| Documentation Pages | 10 | 2 |
| Demo Scenarios | 4 | 0 |

---

## 🛠️ Technical Decisions

### Confirmed Stack
- **Language:** Python 3.9+
- **Web Framework:** FastAPI
- **Dashboard:** Streamlit
- **AI Orchestration:** LangGraph + LangChain
- **Monitoring:** Prometheus + Grafana
- **Database:** SQLite (dev), PostgreSQL (prod)
- **Package Management:** UV / pip

### Architecture Principles
1. **Plugin-based AI agents** - Avoid vendor lock-in
2. **Human-in-the-loop** - All actions require approval
3. **Safety first** - No destructive actions without safeguards
4. **Observable** - Full metrics and logging
5. **Testable** - Modular design for easy testing

---

## 📝 Notes

### Dependencies to Watch
- `langgraph` - Core workflow engine
- `langchain` - AI agent framework
- `prometheus-client` - Metrics
- `grafana-api` - Dashboard automation

### Known Risks
1. **AI API costs** - Implement caching and rate limiting
2. **Cloud API limits** - Use exponential backoff
3. **Complexity creep** - Stay focused on MVP

### Success Definition

**MVP is complete when:**
1. ✅ AlertManager webhook receives alerts
2. ✅ AI generates remediation plans
3. ✅ Human can approve/reject plans
4. ✅ Demo execution works
5. ✅ Dashboard shows full workflow
6. ✅ Grafana displays SentinelNet metrics

---

## 🚀 Getting Started with Development

### Start Here:
1. Review Phase 1, Task 1.1
2. Create the AlertManager webhook endpoint
3. Test with sample AlertManager payload
4. Move to next task

### Daily Workflow:
1. Pick one task from current sprint
2. Implement with tests
3. Update this roadmap (check the box)
4. Commit changes
5. Move to next task

---

*Last Updated: January 2026*
*Author: Vinayak Pawar*
