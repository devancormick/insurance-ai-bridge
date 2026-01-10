"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Insurance AI Bridge API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/insurance_bridge"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    
    # Security (with defaults for development)
    secret_key: str = "dev-secret-key-change-in-production-min-32-chars-long"
    encryption_key: str = "dev-encryption-key-32-bytes-long-key-for-fernet"
    jwt_secret: str = "dev-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Legacy System Integration
    legacy_db_host: Optional[str] = None
    legacy_db_port: int = 1433
    legacy_db_name: Optional[str] = None
    legacy_db_user: Optional[str] = None
    legacy_db_password: Optional[str] = None
    soap_api_url: Optional[str] = None
    sharepoint_url: Optional[str] = None
    sharepoint_client_id: Optional[str] = None
    sharepoint_client_secret: Optional[str] = None
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    log_level: str = "INFO"
    
    # HIPAA Compliance
    pii_retention_days: int = 0
    audit_log_retention_days: int = 2555
    enable_encryption_at_rest: bool = True


# Create settings instance (will use defaults if env vars not set)
try:
    settings = Settings()
except Exception as e:
    # Fallback to defaults if loading fails
    settings = Settings(
        database_url="postgresql+asyncpg://user:password@localhost:5432/insurance_bridge",
        secret_key="dev-secret-key-change-in-production-min-32-chars-long",
        encryption_key="dev-encryption-key-32-bytes-long-key-for-fernet",
        jwt_secret="dev-jwt-secret-change-in-production"
    )

