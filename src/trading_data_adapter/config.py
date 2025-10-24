"""Configuration for trading data adapter."""
from typing import Any, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdapterConfig(BaseSettings):
    """Configuration for trading data adapter with multi-instance support."""

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

    # Service Identity (NEW for multi-instance support)
    service_name: str = "trading-system-engine"
    service_instance_name: str = Field(default="")  # Auto-derived from service_name if empty
    environment: str = Field(default="development")  # development, testing, production, docker
    service_version: str = "0.1.0"

    # Multi-tenancy (derived from instance name)
    postgres_schema: Optional[str] = Field(default=None)  # Auto-derived if None
    redis_namespace: Optional[str] = Field(default=None)  # Auto-derived if None

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

    def model_post_init(self, __context: Any) -> None:
        """Derive instance-specific configuration after model initialization.

        This hook runs after Pydantic validation and automatically derives:
        - service_instance_name from service_name if not provided
        - postgres_schema from instance name if not explicitly set
        - redis_namespace from instance name if not explicitly set
        """
        # Auto-derive instance name from service name if not provided
        if not self.service_instance_name:
            self.service_instance_name = self.service_name

        # Auto-derive PostgreSQL schema if not explicitly set
        if not self.postgres_schema:
            self.postgres_schema = self._derive_schema_name()

        # Auto-derive Redis namespace if not explicitly set
        if not self.redis_namespace:
            self.redis_namespace = self._derive_redis_namespace()

    def _derive_schema_name(self) -> str:
        """Derive PostgreSQL schema name from service instance name.

        Derivation rules:
        - Singleton (service_name == service_instance_name):
          trading-system-engine → "trading"
          (uses first part of hyphen-separated name)

        - Multi-instance (service_name != service_instance_name):
          trading-system-engine-LH → "trading_system_engine_lh"
          trading-system-engine-Alpha → "trading_system_engine_alpha"
          (converts all hyphens to underscores, lowercase)

        Returns:
            PostgreSQL-safe schema name (lowercase, underscores)
        """
        if self.service_name == self.service_instance_name:
            # Singleton: extract first part of service name
            # "trading-system-engine" → "trading"
            return self.service_name.split('-')[0]

        # Multi-instance: convert hyphens to underscores, lowercase
        # "trading-system-engine-LH" → "trading_system_engine_lh"
        return self.service_instance_name.replace('-', '_').lower()

    def _derive_redis_namespace(self) -> str:
        """Derive Redis namespace from service instance name.

        Derivation rules:
        - Singleton (service_name == service_instance_name):
          trading-system-engine → "trading"
          (uses first part of hyphen-separated name)

        - Multi-instance (service_name != service_instance_name):
          trading-system-engine-LH → "trading_system:LH"
          trading-system-engine-Alpha → "trading_system:Alpha"
          (base service name with colon separator and suffix)

        Returns:
            Redis namespace string with colon separator for multi-instance
        """
        if self.service_name == self.service_instance_name:
            # Singleton: extract first part of service name
            # "trading-system-engine" → "trading"
            return self.service_name.split('-')[0]

        # Multi-instance: extract base and suffix with colon separator
        # "trading-system-engine-LH" → "trading_system:LH"
        parts = self.service_instance_name.split('-', 2)  # Split at most 2 times
        if len(parts) >= 3:
            # Extract everything after "engine" as suffix
            # parts[2] = "engine-LH" → extract "LH"
            suffix = parts[2].split('-', 1)[-1] if '-' in parts[2] else parts[2]
            return f"{parts[0]}_{parts[1]}:{suffix}"

        # Fallback: convert hyphens to underscores
        return self.service_instance_name.replace('-', '_')
