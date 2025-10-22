"""Configuration for trading data adapter."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdapterConfig(BaseSettings):
    """Configuration for trading data adapter."""

    # Database connection
    postgres_url: str = "postgresql+asyncpg://trading_adapter:trading-adapter-db-pass@localhost:5432/trading_ecosystem"
    redis_url: str = "redis://trading-adapter:trading-pass@localhost:6379/0"

    # PostgreSQL pool settings
    postgres_pool_size: int = 10
    postgres_max_overflow: int = 20
    postgres_pool_timeout: int = 30
    postgres_pool_recycle: int = 3600

    # Redis pool settings
    redis_pool_size: int = 10
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5

    # Cache TTLs (seconds)
    cache_ttl_default: int = 300  # 5 minutes
    cache_ttl_strategies: int = 600  # 10 minutes
    cache_ttl_positions: int = 60  # 1 minute
    cache_ttl_orders: int = 120  # 2 minutes

    # Service information
    service_name: str = "trading-system-engine"
    service_version: str = "0.1.0"

    # Service discovery
    heartbeat_interval: int = 30
    stale_service_threshold: int = 300

    # Query settings
    batch_size: int = 100
    query_timeout: int = 30

    # Retention periods (days)
    orders_retention_days: int = 90
    trades_retention_days: int = 365
    positions_retention_days: int = 180
    strategies_retention_days: int = 365

    # Logging
    log_level: str = "INFO"
    log_sql_queries: bool = False

    # Health checks
    health_check_timeout: int = 5

    model_config = SettingsConfigDict(
        env_prefix="TRADING_ADAPTER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
