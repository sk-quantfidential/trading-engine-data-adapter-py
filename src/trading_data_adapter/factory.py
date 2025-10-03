"""Factory for creating trading data adapter instances."""
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional

import structlog

from trading_data_adapter.config import AdapterConfig
from trading_data_adapter.interfaces import (
    CacheRepository,
    OrdersRepository,
    PositionsRepository,
    StrategiesRepository,
    TradesRepository,
    ServiceDiscoveryRepository,
)

logger = structlog.get_logger()


@dataclass
class ConnectionStatus:
    """Connection status tracking."""
    postgres_connected: bool = False
    redis_connected: bool = False
    last_postgres_check: Optional[datetime] = None
    last_redis_check: Optional[datetime] = None
    postgres_error: Optional[str] = None
    redis_error: Optional[str] = None


class TradingDataAdapter:
    """Main data adapter facade providing access to all repositories."""

    def __init__(self, config: AdapterConfig):
        """Initialize the trading data adapter.

        Args:
            config: Adapter configuration
        """
        self.config = config
        self.connection_status = ConnectionStatus()

        # Repository instances (lazy initialization)
        self._strategies_repo: Optional[StrategiesRepository] = None
        self._orders_repo: Optional[OrdersRepository] = None
        self._trades_repo: Optional[TradesRepository] = None
        self._positions_repo: Optional[PositionsRepository] = None
        self._service_discovery_repo: Optional[ServiceDiscoveryRepository] = None
        self._cache_repo: Optional[CacheRepository] = None

        # Connection objects (to be initialized)
        self._postgres_engine = None
        self._redis_client = None

        logger.info("Trading data adapter initialized", config=config.model_dump(exclude={"postgres_url", "redis_url"}))

    async def connect(self) -> None:
        """Establish database connections."""
        try:
            # Import here to avoid circular dependencies and allow graceful degradation
            from sqlalchemy.ext.asyncio import create_async_engine
            import redis.asyncio as aioredis

            # PostgreSQL connection
            try:
                self._postgres_engine = create_async_engine(
                    self.config.postgres_url,
                    pool_size=self.config.postgres_pool_size,
                    max_overflow=self.config.postgres_max_overflow,
                    pool_timeout=self.config.postgres_pool_timeout,
                    pool_recycle=self.config.postgres_pool_recycle,
                    echo=self.config.log_sql_queries,
                )

                # Test connection
                from sqlalchemy import text
                async with self._postgres_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))

                self.connection_status.postgres_connected = True
                self.connection_status.last_postgres_check = datetime.now(UTC)
                logger.info("PostgreSQL connection established")

            except Exception as e:
                self.connection_status.postgres_error = str(e)
                logger.warning("PostgreSQL connection failed", error=str(e))

            # Redis connection
            try:
                self._redis_client = await aioredis.from_url(
                    self.config.redis_url,
                    max_connections=self.config.redis_pool_size,
                    socket_timeout=self.config.redis_socket_timeout,
                    socket_connect_timeout=self.config.redis_socket_connect_timeout,
                )

                # Test connection
                await self._redis_client.ping()

                self.connection_status.redis_connected = True
                self.connection_status.last_redis_check = datetime.now(UTC)
                logger.info("Redis connection established")

            except Exception as e:
                self.connection_status.redis_error = str(e)
                logger.warning("Redis connection failed", error=str(e))

        except Exception as e:
            logger.error("Failed to initialize database connections", error=str(e))

    async def disconnect(self) -> None:
        """Close database connections."""
        if self._postgres_engine:
            await self._postgres_engine.dispose()
            self.connection_status.postgres_connected = False
            logger.info("PostgreSQL connection closed")

        if self._redis_client:
            await self._redis_client.aclose()
            self.connection_status.redis_connected = False
            logger.info("Redis connection closed")

    async def health_check(self) -> dict:
        """Perform health check on all connections.

        Returns:
            dict: Health status information
        """
        health = {
            "status": "healthy",
            "postgres": {"connected": False, "error": None},
            "redis": {"connected": False, "error": None},
        }

        # Check PostgreSQL
        if self._postgres_engine:
            try:
                from sqlalchemy import text
                async with self._postgres_engine.connect() as conn:
                    result = await conn.execute(text("SELECT trading.health_check()"))
                    row = result.fetchone()
                    # The function returns JSON, asyncpg automatically parses it
                    schema_check = row[0] if row else None
                    health["postgres"] = {"connected": True, "schema_check": schema_check}
            except Exception as e:
                health["postgres"]["error"] = str(e)
                health["status"] = "degraded"
                logger.warning("PostgreSQL health check failed", error=str(e))

        # Check Redis
        if self._redis_client:
            try:
                await self._redis_client.ping()
                health["redis"] = {"connected": True}
            except Exception as e:
                health["redis"]["error"] = str(e)
                health["status"] = "degraded"

        return health

    def get_strategies_repository(self) -> StrategiesRepository:
        """Get strategies repository instance."""
        if self._strategies_repo is None:
            from trading_data_adapter.adapters.stub.stub_repository import StubStrategiesRepository
            self._strategies_repo = StubStrategiesRepository()
            logger.info("Using stub strategies repository")
        return self._strategies_repo

    def get_orders_repository(self) -> OrdersRepository:
        """Get orders repository instance."""
        if self._orders_repo is None:
            from trading_data_adapter.adapters.stub.stub_repository import StubOrdersRepository
            self._orders_repo = StubOrdersRepository()
            logger.info("Using stub orders repository")
        return self._orders_repo

    def get_trades_repository(self) -> TradesRepository:
        """Get trades repository instance."""
        if self._trades_repo is None:
            from trading_data_adapter.adapters.stub.stub_repository import StubTradesRepository
            self._trades_repo = StubTradesRepository()
            logger.info("Using stub trades repository")
        return self._trades_repo

    def get_positions_repository(self) -> PositionsRepository:
        """Get positions repository instance."""
        if self._positions_repo is None:
            from trading_data_adapter.adapters.stub.stub_repository import StubPositionsRepository
            self._positions_repo = StubPositionsRepository()
            logger.info("Using stub positions repository")
        return self._positions_repo

    def get_service_discovery_repository(self) -> ServiceDiscoveryRepository:
        """Get service discovery repository instance."""
        if self._service_discovery_repo is None:
            from trading_data_adapter.adapters.stub.stub_repository import StubServiceDiscoveryRepository
            self._service_discovery_repo = StubServiceDiscoveryRepository()
            logger.info("Using stub service discovery repository")
        return self._service_discovery_repo

    def get_cache_repository(self) -> CacheRepository:
        """Get cache repository instance."""
        if self._cache_repo is None:
            from trading_data_adapter.adapters.stub.stub_repository import StubCacheRepository
            self._cache_repo = StubCacheRepository()
            logger.info("Using stub cache repository")
        return self._cache_repo


async def create_adapter(config: AdapterConfig) -> TradingDataAdapter:
    """Factory function to create and initialize adapter.

    Args:
        config: Adapter configuration

    Returns:
        TradingDataAdapter: Initialized adapter instance
    """
    adapter = TradingDataAdapter(config)
    await adapter.connect()
    return adapter
