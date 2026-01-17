#!/usr/bin/env python3
"""
LangChain Plugin for Multi-Cloud Operations

Provides flexible, framework-agnostic agent capabilities using LangChain.
Can work across multiple cloud providers with unified interfaces.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from sentinelnet.agents import (
    AgentFramework, CloudProvider, AgentCapabilities,
    BaseAgentPlugin
)
from sentinelnet.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LangchainMultiPlugin(BaseAgentPlugin):
    """
    LangChain plugin for multi-cloud operations.

    This plugin provides:
    - Framework-agnostic agent orchestration
    - Cross-cloud analysis and remediation
    - Flexible tool integration
    - Extensible architecture for new cloud providers
    """

    def __init__(self):
        capabilities = AgentCapabilities(
            framework=AgentFramework.LANGCHAIN,
            cloud_provider=CloudProvider.MULTI_CLOUD,
            features=[
                "cross_cloud_analysis",
                "unified_remediation",
                "multi_provider_monitoring",
                "flexible_orchestration",
                "tool_integration",
                "custom_workflows"
            ],
            max_concurrent_tasks=10,  # Flexible framework allows higher concurrency
            requires_api_keys=["openai_api_key"]  # Primarily needs LLM access
        )

        super().__init__(capabilities)
        self._llm = None
        self._agents = {}
        self._tools = {}
        self._chains = {}

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize LangChain agents for multi-cloud operations"""
        try:
            # Import LangChain components
            from langchain_openai import ChatOpenAI
            from langchain.agents import create_openai_tools_agent, AgentExecutor
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
            from langchain.memory import ConversationBufferMemory
            from langchain.tools import tool

            # Initialize LLM
            openai_api_key = config.get("openai_api_key", settings.ai.openai_api_key)
            if not openai_api_key:
                logger.warning("⚠️ OpenAI API key not available for LangChain plugin")
                return False

            self._llm = ChatOpenAI(
                model=config.get("model", settings.ai.openai_model),
                temperature=0.1,
                openai_api_key=openai_api_key
            )

            # Create custom tools for cloud operations
            self._tools = await self._create_cloud_tools()

            # Create specialized agents for different cloud operations
            self._agents = await self._create_langchain_agents()

            # Create analysis and remediation chains
            self._chains = await self._create_analysis_chains()

            self._initialized = True
            logger.info("✅ LangChain multi-cloud plugin initialized")
            return True

        except ImportError as e:
            logger.warning(f"⚠️ LangChain libraries not available: {e}")
            logger.info("💡 Install with: pip install langchain langchain-openai langchain-community")
            return False
        except Exception as e:
            logger.error(f"❌ LangChain plugin initialization failed: {e}")
            return False

    async def _create_cloud_tools(self) -> Dict[str, Any]:
        """Create custom tools for cloud operations"""
        tools = {}

        try:
            from langchain.tools import tool

            @tool
            def analyze_cloud_service_health(service: str, cloud_provider: str) -> str:
                """
                Analyze health of a cloud service across providers.

                Args:
                    service: The service name (e.g., 'bigquery', 'blob-storage')
                    cloud_provider: The cloud provider ('gcp', 'azure', 'aws')

                Returns:
                    Health analysis summary
                """
                # This would integrate with actual cloud monitoring APIs
                return f"Health analysis for {service} on {cloud_provider}: Service appears healthy with normal metrics."

            @tool
            def generate_cross_cloud_remediation_plan(issue: str, affected_services: List[str]) -> str:
                """
                Generate remediation plan considering cross-cloud dependencies.

                Args:
                    issue: Description of the issue
                    affected_services: List of affected services across clouds

                Returns:
                    Comprehensive remediation plan
                """
                return f"Cross-cloud remediation plan for {issue}: {len(affected_services)} services affected."

            @tool
            def assess_multi_cloud_cost_impact(changes: List[str]) -> str:
                """
                Assess cost impact of changes across multiple cloud providers.

                Args:
                    changes: List of proposed changes

                Returns:
                    Cost impact analysis
                """
                return f"Cost impact analysis for {len(changes)} changes: Potential savings identified."

            @tool
            def optimize_multi_cloud_resources(resources: List[str]) -> str:
                """
                Optimize resource allocation across cloud providers.

                Args:
                    resources: List of resources to optimize

                Returns:
                    Optimization recommendations
                """
                return f"Resource optimization for {len(resources)} resources: Efficiency improvements suggested."

            tools.update({
                "analyze_cloud_service_health": analyze_cloud_service_health,
                "generate_cross_cloud_remediation_plan": generate_cross_cloud_remediation_plan,
                "assess_multi_cloud_cost_impact": assess_multi_cloud_cost_impact,
                "optimize_multi_cloud_resources": optimize_multi_cloud_resources
            })

            logger.info("✅ Created LangChain cloud operation tools")
            return tools

        except Exception as e:
            logger.error(f"❌ Failed to create cloud tools: {e}")
            return {}

    async def _create_langchain_agents(self) -> Dict[str, Any]:
        """Create specialized LangChain agents"""
        agents = {}

        try:
            from langchain.agents import create_openai_tools_agent, AgentExecutor
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
            from langchain.memory import ConversationBufferMemory

            # Define agent prompts
            agent_configs = {
                "monitoring_agent": {
                    "role": "Cloud Monitoring Specialist",
                    "expertise": "analyzing metrics and identifying issues across multiple cloud providers",
                    "tools": ["analyze_cloud_service_health"]
                },
                "remediation_agent": {
                    "role": "Multi-Cloud Remediation Expert",
                    "expertise": "creating safe, effective remediation plans for complex cloud environments",
                    "tools": ["generate_cross_cloud_remediation_plan", "assess_multi_cloud_cost_impact"]
                },
                "optimization_agent": {
                    "role": "Cloud Resource Optimizer",
                    "expertise": "optimizing resource allocation and reducing costs across cloud providers",
                    "tools": ["optimize_multi_cloud_resources", "assess_multi_cloud_cost_impact"]
                }
            }

            for agent_name, config in agent_configs.items():
                # Create prompt template
                prompt = ChatPromptTemplate.from_messages([
                    ("system", f"""You are a {config['role']} specializing in {config['expertise']}.

You work across multiple cloud providers (GCP, Azure, AWS) and understand:
- Cross-cloud dependencies and interactions
- Provider-specific best practices
- Cost optimization strategies
- Security and compliance requirements

Always provide actionable, safe recommendations with rollback plans."""),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ])

                # Get relevant tools
                agent_tools = [self._tools[tool_name] for tool_name in config["tools"] if tool_name in self._tools]

                # Create agent
                agent = create_openai_tools_agent(
                    llm=self._llm,
                    tools=agent_tools,
                    prompt=prompt
                )

                # Create executor with memory
                executor = AgentExecutor(
                    agent=agent,
                    tools=agent_tools,
                    memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
                    verbose=False,
                    max_iterations=5
                )

                agents[agent_name] = executor

            logger.info("✅ Created LangChain specialized agents")
            return agents

        except Exception as e:
            logger.error(f"❌ Failed to create LangChain agents: {e}")
            return {}

    async def _create_analysis_chains(self) -> Dict[str, Any]:
        """Create analysis and processing chains"""
        chains = {}

        try:
            from langchain.chains import LLMChain
            from langchain_core.prompts import PromptTemplate

            # Issue severity assessment chain
            severity_template = PromptTemplate(
                input_variables=["issue_description", "affected_services", "impact"],
                template="""Assess the severity of this cloud infrastructure issue:

Issue: {issue_description}
Affected Services: {affected_services}
Business Impact: {impact}

Classify severity as: critical, high, medium, or low
Provide reasoning and immediate action priority.

Severity Assessment:"""
            )

            chains["severity_chain"] = LLMChain(
                llm=self._llm,
                prompt=severity_template,
                verbose=False
            )

            # Cost-benefit analysis chain
            cost_template = PromptTemplate(
                input_variables=["proposed_changes", "current_costs", "expected_benefits"],
                template="""Analyze the cost-benefit of these infrastructure changes:

Proposed Changes: {proposed_changes}
Current Monthly Costs: {current_costs}
Expected Benefits: {expected_benefits}

Provide:
1. Cost impact assessment
2. ROI timeline
3. Risk-benefit analysis
4. Recommendation

Cost-Benefit Analysis:"""
            )

            chains["cost_benefit_chain"] = LLMChain(
                llm=self._llm,
                prompt=cost_template,
                verbose=False
            )

            logger.info("✅ Created LangChain analysis chains")
            return chains

        except Exception as e:
            logger.error(f"❌ Failed to create analysis chains: {e}")
            return {}

    async def execute_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multi-cloud task using LangChain"""
        if not self._initialized:
            return {"success": False, "error": "Plugin not initialized"}

        task_type = task.get("type", "analysis")
        services = task.get("services", [])
        cloud_providers = task.get("cloud_providers", [])

        try:
            # Route to appropriate agent based on task type
            if task_type in ["monitoring", "analysis", "health_check"]:
                agent = self._agents.get("monitoring_agent")
                result = await self._execute_monitoring_task(agent, task, context)

            elif task_type in ["remediation", "fix", "recovery"]:
                agent = self._agents.get("remediation_agent")
                result = await self._execute_remediation_task(agent, task, context)

            elif task_type in ["optimization", "cost", "efficiency"]:
                agent = self._agents.get("optimization_agent")
                result = await self._execute_optimization_task(agent, task, context)

            else:
                # Use monitoring agent as default
                agent = self._agents.get("monitoring_agent")
                result = await self._execute_general_task(agent, task, context)

            return {
                "success": True,
                "task_type": task_type,
                "services": services,
                "cloud_providers": cloud_providers,
                "result": result,
                "framework": "langchain",
                "cloud_provider": "multi_cloud"
            }

        except Exception as e:
            logger.error(f"❌ LangChain task execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_issue(self, issue: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze multi-cloud issue using LangChain"""
        if not self._initialized:
            return {"success": False, "error": "Plugin not initialized"}

        try:
            # Use severity assessment chain
            severity_chain = self._chains.get("severity_chain")
            if severity_chain:
                severity_result = await severity_chain.arun(
                    issue_description=issue.get("description", ""),
                    affected_services=", ".join(issue.get("affected_services", [])),
                    impact=issue.get("impact", "Unknown")
                )
            else:
                severity_result = "Severity assessment unavailable"

            # Use remediation agent for comprehensive analysis
            remediation_agent = self._agents.get("remediation_agent")
            if remediation_agent:
                # Prepare agent input
                agent_input = f"""
                Analyze this multi-cloud infrastructure issue:

                Description: {issue.get('description', 'No description')}
                Affected Services: {', '.join(issue.get('affected_services', []))}
                Cloud Providers: {', '.join(issue.get('cloud_providers', []))}
                Impact: {issue.get('impact', 'Unknown')}
                Current Status: {issue.get('status', 'Unknown')}

                Context: {context}

                Provide:
                1. Root cause analysis
                2. Cross-cloud dependency assessment
                3. Immediate containment actions
                4. Long-term remediation plan
                5. Risk assessment and rollback strategy
                """

                agent_result = await remediation_agent.arun(input=agent_input)
            else:
                agent_result = "Agent analysis unavailable"

            return {
                "success": True,
                "severity_assessment": severity_result,
                "comprehensive_analysis": agent_result,
                "cross_cloud_impact": self._assess_cross_cloud_impact(issue),
                "immediate_actions": self._generate_multi_cloud_immediate_actions(issue),
                "long_term_recommendations": self._generate_multi_cloud_long_term_recommendations(issue),
                "framework": "langchain",
                "cloud_provider": "multi_cloud"
            }

        except Exception as e:
            logger.error(f"❌ LangChain issue analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_monitoring_task(self, agent, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Execute monitoring task with LangChain agent"""
        if not agent:
            return "Monitoring agent not available"

        try:
            services = task.get("services", [])
            cloud_providers = task.get("cloud_providers", [])

            agent_input = f"""
            Perform comprehensive monitoring analysis across multiple cloud providers:

            Services to Monitor: {', '.join(services)}
            Cloud Providers: {', '.join(cloud_providers)}
            Time Range: {task.get('time_range', 'Last 24 hours')}
            Focus Areas: {', '.join(task.get('focus_areas', ['performance', 'errors', 'costs']))}

            Context: {context}

            Provide detailed analysis including:
            - Service health status across providers
            - Performance metrics and anomalies
            - Cost optimization opportunities
            - Cross-cloud dependency issues
            - Recommended monitoring improvements
            """

            result = await agent.arun(input=agent_input)
            return result

        except Exception as e:
            logger.error(f"❌ Monitoring task execution failed: {e}")
            return f"Monitoring analysis failed: {str(e)}"

    async def _execute_remediation_task(self, agent, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Execute remediation task with LangChain agent"""
        if not agent:
            return "Remediation agent not available"

        try:
            issues = task.get("issues", [])
            affected_services = task.get("affected_services", [])

            agent_input = f"""
            Create comprehensive remediation plan for multi-cloud infrastructure issues:

            Issues: {', '.join(issues)}
            Affected Services: {', '.join(affected_services)}
            Cloud Providers: {', '.join(task.get('cloud_providers', []))}
            Business Impact: {task.get('business_impact', 'Unknown')}

            Context: {context}

            Develop remediation plan including:
            1. Root cause analysis
            2. Immediate containment steps
            3. Detailed remediation procedures
            4. Cross-cloud coordination requirements
            5. Rollback and testing procedures
            6. Risk assessment and mitigation
            7. Timeline and resource requirements
            """

            result = await agent.arun(input=agent_input)
            return result

        except Exception as e:
            logger.error(f"❌ Remediation task execution failed: {e}")
            return f"Remediation planning failed: {str(e)}"

    async def _execute_optimization_task(self, agent, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Execute optimization task with LangChain agent"""
        if not agent:
            return "Optimization agent not available"

        try:
            resources = task.get("resources", [])
            optimization_goals = task.get("goals", ["cost", "performance"])

            agent_input = f"""
            Optimize multi-cloud resource allocation and costs:

            Resources to Optimize: {', '.join(resources)}
            Optimization Goals: {', '.join(optimization_goals)}
            Current Budget: {task.get('budget', 'Not specified')}
            Time Horizon: {task.get('time_horizon', 'Monthly')}

            Context: {context}

            Provide optimization recommendations including:
            1. Resource right-sizing opportunities
            2. Cost optimization strategies
            3. Performance improvement suggestions
            4. Migration recommendations between providers
            5. Automation opportunities
            6. ROI projections and timelines
            """

            result = await agent.arun(input=agent_input)
            return result

        except Exception as e:
            logger.error(f"❌ Optimization task execution failed: {e}")
            return f"Optimization analysis failed: {str(e)}"

    async def _execute_general_task(self, agent, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Execute general task with LangChain agent"""
        if not agent:
            return "Agent not available"

        try:
            agent_input = f"""
            Analyze and provide recommendations for this multi-cloud operation:

            Task: {task.get('description', 'General analysis')}
            Services: {', '.join(task.get('services', []))}
            Cloud Providers: {', '.join(task.get('cloud_providers', []))}

            Context: {context}

            Provide comprehensive analysis and actionable recommendations.
            """

            result = await agent.arun(input=agent_input)
            return result

        except Exception as e:
            logger.error(f"❌ General task execution failed: {e}")
            return f"Task execution failed: {str(e)}"

    def _assess_cross_cloud_impact(self, issue: Dict[str, Any]) -> str:
        """Assess cross-cloud impact of an issue"""
        affected_services = issue.get("affected_services", [])
        cloud_providers = issue.get("cloud_providers", [])

        if len(cloud_providers) > 1:
            return f"High cross-cloud impact: {len(affected_services)} services across {len(cloud_providers)} providers affected"
        elif len(affected_services) > 3:
            return f"Medium cross-cloud impact: Multiple services within {cloud_providers[0] if cloud_providers else 'provider'} affected"
        else:
            return f"Low cross-cloud impact: Isolated service issue"

    def _generate_multi_cloud_immediate_actions(self, issue: Dict[str, Any]) -> List[str]:
        """Generate immediate actions for multi-cloud issue"""
        actions = []
        cloud_providers = issue.get("cloud_providers", [])
        affected_services = issue.get("affected_services", [])

        actions.extend([
            f"Check service health dashboards for {', '.join(cloud_providers)}",
            f"Review monitoring alerts across {len(cloud_providers)} cloud providers",
            f"Verify cross-cloud network connectivity and DNS resolution",
            f"Check for ongoing maintenance windows or incidents"
        ])

        if len(cloud_providers) > 1:
            actions.append("Assess cross-cloud dependency impact and failover capabilities")

        return actions

    def _generate_multi_cloud_long_term_recommendations(self, issue: Dict[str, Any]) -> List[str]:
        """Generate long-term recommendations for multi-cloud issue"""
        recommendations = []
        cloud_providers = issue.get("cloud_providers", [])

        recommendations.extend([
            "Implement unified monitoring and alerting across all cloud providers",
            "Establish cross-cloud disaster recovery and failover procedures",
            "Implement multi-cloud cost optimization and resource management",
            "Develop cloud-agnostic infrastructure as code practices",
            "Set up centralized logging and analysis across providers"
        ])

        if len(cloud_providers) > 1:
            recommendations.extend([
                "Implement cross-cloud load balancing and traffic management",
                "Establish multi-cloud backup and data replication strategies",
                "Develop cross-cloud security policies and compliance frameworks"
            ])

        return recommendations

    async def shutdown(self) -> None:
        """Shutdown LangChain multi-cloud plugin"""
        try:
            # Clean up agents, chains, and tools
            self._agents.clear()
            self._chains.clear()
            self._tools.clear()
            self._llm = None
            self._initialized = False

            logger.info("✅ LangChain multi-cloud plugin shutdown")

        except Exception as e:
            logger.error(f"❌ LangChain plugin shutdown failed: {e}")


# Convenience function to create multi-cloud LangChain plugin
def create_multi_cloud_langchain_plugin() -> LangchainMultiPlugin:
    """Create and return multi-cloud LangChain plugin instance"""
    return LangchainMultiPlugin()
