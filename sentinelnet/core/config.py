"""
SentinelNet Configuration Management

Centralized configuration management using Pydantic settings
with support for multiple environments and validation.
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class DatabaseConfig(BaseSettings):
    """Database configuration settings"""
    url: str = Field(default="sqlite:///./sentinelnet.db", env="DATABASE_URL")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")

    class Config:
        env_prefix = "DB_"


class CloudProviderConfig(BaseSettings):
    """Base configuration for cloud providers"""
    enabled: bool = True
    project_id: Optional[str] = None
    region: str = "us-central1"
    credentials_path: Optional[str] = None


class GCPConfig(CloudProviderConfig):
    """Google Cloud Platform configuration"""
    project_id: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_PROJECT")
    credentials_path: Optional[str] = Field(default=None, env="GOOGLE_APPLICATION_CREDENTIALS")
    vertex_ai_region: str = "us-central1"
    bigquery_dataset: str = "sentinelnet_monitoring"

    class Config:
        env_prefix = "GCP_"


class AzureConfig(CloudProviderConfig):
    """Microsoft Azure configuration"""
    subscription_id: Optional[str] = Field(default=None, env="AZURE_SUBSCRIPTION_ID")
    client_id: Optional[str] = Field(default=None, env="AZURE_CLIENT_ID")
    client_secret: Optional[str] = Field(default=None, env="AZURE_CLIENT_SECRET")
    tenant_id: Optional[str] = Field(default=None, env="AZURE_TENANT_ID")
    region: str = "East US"
    resource_group: str = "sentinelnet-rg"

    class Config:
        env_prefix = "AZURE_"


class AWSConfig(CloudProviderConfig):
    """Amazon Web Services configuration"""
    access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    region: str = "us-east-1"
    profile: Optional[str] = Field(default=None, env="AWS_PROFILE")

    class Config:
        env_prefix = "AWS_"


class PluginConfig(BaseSettings):
    """Agent plugin configuration"""
    # Plugin enablement by ecosystem
    gcp_plugins: List[str] = ["google_agent_kit", "langchain"]
    azure_plugins: List[str] = ["autogen", "langchain"]
    aws_plugins: List[str] = ["langchain"]  # AWS doesn't have native agent framework yet
    multi_cloud_plugins: List[str] = ["langchain", "langgraph"]

    # Plugin priority (higher priority plugins tried first)
    plugin_priority: Dict[str, int] = {
        "autogen": 10,          # Microsoft AutoGen (Azure native)
        "google_agent_kit": 10, # Google Agent Development Kit (GCP native)
        "langgraph": 8,         # LangGraph (complex workflows)
        "langchain": 5,         # LangChain (flexible, multi-cloud)
        "custom": 1             # Custom plugins (lowest priority)
    }

    # Plugin-specific configurations
    plugin_configs: Dict[str, Dict[str, Any]] = {
        "autogen": {
            "timeout": 300,
            "max_rounds": 50,
            "model": "gpt-4-turbo-preview"
        },
        "google_agent_kit": {
            "vertex_ai_region": "us-central1",
            "model": "gemini-1.5-pro"
        },
        "langchain": {
            "model": "gpt-4-turbo-preview",
            "temperature": 0.1
        },
        "langgraph": {
            "timeout": 600,
            "max_iterations": 100,
            "model": "gpt-4-turbo-preview"
        }
    }

    # Auto-selection based on available licenses
    auto_select_plugins: bool = True

    def get_plugins_for_provider(self, provider: str) -> List[str]:
        """Get enabled plugins for a specific cloud provider"""
        provider_plugins = {
            "gcp": self.gcp_plugins,
            "azure": self.azure_plugins,
            "aws": self.aws_plugins,
            "multi_cloud": self.multi_cloud_plugins
        }
        return provider_plugins.get(provider, [])

    def get_prioritized_plugins(self, provider: str) -> List[str]:
        """Get plugins sorted by priority for a provider"""
        plugins = self.get_plugins_for_provider(provider)
        return sorted(plugins, key=lambda p: self.plugin_priority.get(p, 0), reverse=True)

    class Config:
        env_prefix = "PLUGIN_"


class AIConfig(BaseSettings):
    """AI and LLM configuration"""
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.1

    # Google AI
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    google_model: str = "gemini-pro"
    vertex_ai_model: str = "text-bison@002"

    # Plugin-based agent framework configuration (replaces old strategy system)
    plugins: PluginConfig = PluginConfig()

    # Legacy compatibility (deprecated - use plugins instead)
    agent_strategy: str = Field(default="plugin_based", env="AI_AGENT_STRATEGY")
    # Options: "plugin_based" (new), "langgraph_only", "autogen_azure", "google_gcp", "hybrid"

    # Legacy framework flags (auto-migrated to plugin config)
    autogen_enabled: bool = False
    google_agent_kit_enabled: bool = False
    langgraph_enabled: bool = True

    @field_validator("autogen_enabled", "google_agent_kit_enabled", "langgraph_enabled", mode="before")
    @classmethod
    def migrate_legacy_config(cls, v, info):
        """Migrate legacy configuration to plugin system"""
        values = info.data
        strategy = values.get("agent_strategy", "plugin_based")

        # If using new plugin system, ignore legacy flags
        if strategy == "plugin_based":
            return False  # Legacy flags not used in plugin system

        # Legacy migration for backward compatibility
        if info.field_name == "autogen_enabled":
            return strategy in ["autogen_azure", "hybrid"]
        elif info.field_name == "google_agent_kit_enabled":
            return strategy in ["google_gcp", "hybrid"]
        elif info.field_name == "langgraph_enabled":
            return strategy in ["langgraph_only", "autogen_azure", "google_gcp", "hybrid"]

        return v

    class Config:
        env_prefix = "AI_"


class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration"""
    enabled: bool = True
    prometheus_port: int = 8001
    grafana_url: Optional[str] = Field(default=None, env="GRAFANA_URL")
    grafana_api_key: Optional[str] = Field(default=None, env="GRAFANA_API_KEY")

    # Metrics collection
    metrics_interval_seconds: int = 30
    retention_days: int = 30

    class Config:
        env_prefix = "MONITORING_"


class APIConfig(BaseSettings):
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    workers: int = 1
    reload: bool = False

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    class Config:
        env_prefix = "API_"


class AgentConfig(BaseSettings):
    """Agent orchestration configuration"""
    max_concurrent_agents: int = 10
    heartbeat_interval_seconds: int = 30
    agent_timeout_seconds: int = 300

    # Communication
    websocket_port: int = 8080
    p2p_enabled: bool = True
    sms_enabled: bool = False
    email_enabled: bool = False

    class Config:
        env_prefix = "AGENT_"


class SecurityConfig(BaseSettings):
    """Security configuration"""
    jwt_secret_key: str = Field(default="your-secret-key-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Encryption
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")

    # API Keys
    api_key_required: bool = False
    api_keys: List[str] = []

    class Config:
        env_prefix = "SECURITY_"


class LoggingConfig(BaseSettings):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = "logs/sentinelnet.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5

    # Structured logging
    structured: bool = True

    class Config:
        env_prefix = "LOG_"


class Settings(BaseSettings):
    """Main application settings"""

    # Application
    app_name: str = "SentinelNet"
    version: str = "0.1.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    config_dir: Path = base_dir / "config"
    data_dir: Path = base_dir / "data"
    logs_dir: Path = base_dir / "logs"
    models_dir: Path = base_dir / "models"

    # Sub-configurations
    database: DatabaseConfig = DatabaseConfig()
    gcp: GCPConfig = GCPConfig()
    azure: AzureConfig = AzureConfig()
    aws: AWSConfig = AWSConfig()
    ai: AIConfig = AIConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    api: APIConfig = APIConfig()
    agents: AgentConfig = AgentConfig()
    security: SecurityConfig = SecurityConfig()
    logging: LoggingConfig = LoggingConfig()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("data_dir", "logs_dir", "models_dir", mode="before")
    @classmethod
    def create_directories(cls, v):
        """Ensure required directories exist"""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() in ["production", "prod"]

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment.lower() in ["development", "dev"]

    def get_cloud_providers(self) -> List[str]:
        """Get list of enabled cloud providers"""
        providers = []
        if self.gcp.enabled:
            providers.append("gcp")
        if self.azure.enabled:
            providers.append("azure")
        if self.aws.enabled:
            providers.append("aws")
        return providers

    def validate_cloud_configs(self) -> Dict[str, bool]:
        """Validate cloud provider configurations"""
        validation = {}

        # GCP validation
        gcp_valid = bool(
            self.gcp.project_id and
            (self.gcp.credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        )
        validation["gcp"] = gcp_valid

        # Azure validation
        azure_valid = bool(
            self.azure.subscription_id and
            self.azure.client_id and
            self.azure.client_secret and
            self.azure.tenant_id
        )
        validation["azure"] = azure_valid

        # AWS validation
        aws_valid = bool(
            (self.aws.access_key_id and self.aws.secret_access_key) or
            self.aws.profile
        )
        validation["aws"] = aws_valid

        return validation


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()


# Global settings instance
settings = get_settings()
