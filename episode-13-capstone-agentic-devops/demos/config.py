"""
Configuration Management — Agentic DevOps Platform

Centralized configuration using Pydantic BaseSettings with environment variable
support. All settings use the DEVOPS_PLATFORM_ prefix and provide sensible defaults
for local development with Ollama.

AI-Assisted DevOps Workshop | Episode 13 | Sagar Utekar
"""

from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM backend providers."""

    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"


class LLMSettings(BaseSettings):
    """Configuration for the LLM backend connection.

    Attributes:
        provider: The LLM provider to use (ollama, anthropic, or bedrock).
        model_name: Model identifier passed to the provider.
        temperature: Sampling temperature for generation (0.0-1.0).
        max_tokens: Maximum number of tokens to generate per request.
        base_url: Base URL for the LLM API endpoint.
        api_key: API key for authenticated providers (Anthropic/Bedrock).
        timeout_seconds: Request timeout for LLM calls.
    """

    model_config = SettingsConfigDict(
        env_prefix="DEVOPS_PLATFORM_LLM_",
        env_file=".env",
        extra="ignore",
    )

    provider: LLMProvider = Field(
        default=LLMProvider.OLLAMA,
        description="LLM provider backend to use",
    )
    model_name: str = Field(
        default="llama3.1:8b",
        description="Model name or identifier for the provider",
    )
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for generation",
    )
    max_tokens: int = Field(
        default=4096,
        gt=0,
        le=128000,
        description="Maximum tokens to generate per request",
    )
    base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for the LLM API endpoint",
    )
    api_key: str = Field(
        default="",
        description="API key for authenticated providers",
    )
    timeout_seconds: int = Field(
        default=120,
        gt=0,
        description="Request timeout in seconds for LLM calls",
    )


class SafetySettings(BaseSettings):
    """Configuration for the safety guardrails system.

    Attributes:
        enabled: Whether safety checks are active.
        default_classification: Fallback classification when analysis is inconclusive.
        require_approval_for_restricted: Whether restricted operations need explicit approval.
        block_on_error: Whether to block requests when safety analysis fails.
    """

    model_config = SettingsConfigDict(
        env_prefix="DEVOPS_PLATFORM_SAFETY_",
        env_file=".env",
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Whether safety classification is active",
    )
    default_classification: str = Field(
        default="RESTRICTED",
        description="Fallback classification when analysis is inconclusive",
    )
    require_approval_for_restricted: bool = Field(
        default=True,
        description="Whether restricted operations require explicit approval",
    )
    block_on_error: bool = Field(
        default=True,
        description="Whether to block requests when safety check itself errors",
    )


class APISettings(BaseSettings):
    """Configuration for the FastAPI server.

    Attributes:
        host: Bind address for the API server.
        port: Port number to listen on.
        api_key_header: HTTP header name for API key authentication.
        rate_limit: Maximum requests per minute per client.
        cors_origins: Allowed CORS origins.
        docs_enabled: Whether to serve interactive API docs.
    """

    model_config = SettingsConfigDict(
        env_prefix="DEVOPS_PLATFORM_API_",
        env_file=".env",
        extra="ignore",
    )

    host: str = Field(
        default="0.0.0.0",
        description="Bind address for the API server",
    )
    port: int = Field(
        default=8000,
        gt=0,
        le=65535,
        description="Port number to listen on",
    )
    api_key_header: str = Field(
        default="X-API-Key",
        description="HTTP header name for API key authentication",
    )
    rate_limit: int = Field(
        default=60,
        gt=0,
        description="Maximum requests per minute per client",
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins",
    )
    docs_enabled: bool = Field(
        default=True,
        description="Whether to serve interactive Swagger/ReDoc docs",
    )


class AgentSettings(BaseSettings):
    """Configuration for the agent orchestration layer.

    Attributes:
        timeout_seconds: Maximum time an agent may run before being cancelled.
        max_retries: Number of retry attempts for transient failures.
        available_agents: List of agent identifiers available for routing.
        default_agent: Agent to use when no preference is specified.
        parallel_execution: Whether to allow parallel agent execution.
    """

    model_config = SettingsConfigDict(
        env_prefix="DEVOPS_PLATFORM_AGENT_",
        env_file=".env",
        extra="ignore",
    )

    timeout_seconds: int = Field(
        default=300,
        gt=0,
        description="Maximum seconds an agent may run",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retry attempts on transient failure",
    )
    available_agents: List[str] = Field(
        default=[
            "k8s-agent",
            "terraform-agent",
            "incident-agent",
            "monitoring-agent",
            "security-agent",
            "ci-cd-agent",
        ],
        description="List of available agent identifiers",
    )
    default_agent: str = Field(
        default="k8s-agent",
        description="Default agent when no preference is specified",
    )
    parallel_execution: bool = Field(
        default=True,
        description="Whether to allow parallel agent execution in workflows",
    )


class LoggingSettings(BaseSettings):
    """Configuration for structured logging and audit trails.

    Attributes:
        level: Minimum log level to emit.
        format: Log output format (json or console).
        audit_file: Path to the JSONL audit log file.
        enable_console: Whether to output logs to console.
        enable_file: Whether to write logs to file.
    """

    model_config = SettingsConfigDict(
        env_prefix="DEVOPS_PLATFORM_LOG_",
        env_file=".env",
        extra="ignore",
    )

    level: str = Field(
        default="INFO",
        description="Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    format: str = Field(
        default="json",
        description="Log output format: 'json' or 'console'",
    )
    audit_file: str = Field(
        default="audit.jsonl",
        description="Path to the JSONL audit log file",
    )
    enable_console: bool = Field(
        default=True,
        description="Whether to output logs to console/stdout",
    )
    enable_file: bool = Field(
        default=True,
        description="Whether to write logs to a file",
    )


class PlatformSettings(BaseSettings):
    """Root configuration aggregating all subsystem settings.

    This is the single entry point for loading platform configuration.
    All settings are loaded from environment variables with the
    DEVOPS_PLATFORM_ prefix, or from a .env file if present.

    Example:
        >>> settings = PlatformSettings()
        >>> print(settings.llm.provider)
        ollama
        >>> print(settings.api.port)
        8000
    """

    model_config = SettingsConfigDict(
        env_prefix="DEVOPS_PLATFORM_",
        env_file=".env",
        extra="ignore",
    )

    llm: LLMSettings = Field(default_factory=LLMSettings)
    safety: SafetySettings = Field(default_factory=SafetySettings)
    api: APISettings = Field(default_factory=APISettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)


def get_settings() -> PlatformSettings:
    """Load and return the platform settings singleton.

    Settings are loaded from environment variables and .env file.
    This function can be used as a FastAPI dependency.

    Returns:
        PlatformSettings: Fully initialized platform configuration.
    """
    return PlatformSettings()
