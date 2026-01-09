"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Insurance AI Bridge API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # Database
    database_url: str
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
    
    # Security
    secret_key: str
    encryption_key: str
    jwt_secret: str
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

