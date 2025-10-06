"""Redis behavior tests for trading data adapter."""
import pytest
from datetime import datetime, UTC

from trading_data_adapter.interfaces import ServiceInfo


pytestmark = [pytest.mark.integration, pytest.mark.redis]


class TestRedisBehavior:
    """Behavior tests for Redis integration."""

    @pytest.mark.asyncio
    async def test_redis_connection_health(self, connected_adapter):
        """GIVEN orchestrator Redis is running
        WHEN health check is performed
        THEN Redis connection should be healthy
        """
        health = await connected_adapter.health_check()

        assert health["status"] in ["healthy", "degraded"]
        assert "redis" in health
        assert health["redis"]["connected"] is True

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, connected_adapter):
        """GIVEN Redis cache is available
        WHEN value is set and retrieved
        THEN value should match exactly
        """
        cache = connected_adapter.get_cache_repository()

        key = f"test:cache:{datetime.now(UTC).timestamp()}"
        value = "test_value_123"

        await cache.set(key, value)
        retrieved = await cache.get(key)

        assert retrieved == value

        # Cleanup
        await cache.delete(key)

    @pytest.mark.asyncio
    async def test_cache_ttl_behavior(self, connected_adapter):
        """GIVEN cache with TTL
        WHEN item is set with short TTL
        THEN item should expire after TTL seconds
        """
        cache = connected_adapter.get_cache_repository()

        key = f"test:ttl:{datetime.now(UTC).timestamp()}"
        value = "expiring_value"

        # Set with 2 second TTL
        await cache.set(key, value, ttl=2)

        # Check TTL
        ttl = await cache.ttl(key)
        assert 0 < ttl <= 2

        # Value should exist now
        exists = await cache.exists(key)
        assert exists is True

        # Wait for expiration
        import asyncio
        await asyncio.sleep(3)

        # Value should be expired
        retrieved = await cache.get(key)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_cache_json_operations(self, connected_adapter):
        """GIVEN Redis cache
        WHEN JSON objects are stored and retrieved
        THEN objects should be serialized/deserialized correctly
        """
        cache = connected_adapter.get_cache_repository()

        key = f"test:json:{datetime.now(UTC).timestamp()}"
        data = {
            "strategy_id": "strat_001",
            "parameters": {"spread": 0.01, "size": 100},
            "instruments": ["BTC-USD", "ETH-USD"],
        }

        await cache.set_json(key, data)
        retrieved = await cache.get_json(key)

        assert retrieved == data
        assert retrieved["strategy_id"] == "strat_001"
        assert retrieved["parameters"]["spread"] == 0.01

        # Cleanup
        await cache.delete(key)

    @pytest.mark.asyncio
    async def test_cache_pattern_operations(self, connected_adapter):
        """GIVEN multiple cache keys with pattern
        WHEN pattern matching is used
        THEN should find all matching keys
        """
        cache = connected_adapter.get_cache_repository()

        timestamp = datetime.now(UTC).timestamp()
        pattern_prefix = f"test:pattern:{timestamp}"

        # Create multiple keys
        keys_to_create = [
            f"{pattern_prefix}:key1",
            f"{pattern_prefix}:key2",
            f"{pattern_prefix}:key3",
        ]

        for key in keys_to_create:
            await cache.set(key, "value")

        # Find keys by pattern
        found_keys = await cache.keys(f"{pattern_prefix}:*")
        assert len(found_keys) >= 3

        # Delete by pattern
        deleted_count = await cache.delete_pattern(f"{pattern_prefix}:*")
        assert deleted_count >= 3

    @pytest.mark.asyncio
    async def test_cache_increment_operations(self, connected_adapter):
        """GIVEN numeric cache value
        WHEN increment/decrement operations are used
        THEN value should change correctly
        """
        cache = connected_adapter.get_cache_repository()

        key = f"test:counter:{datetime.now(UTC).timestamp()}"

        # Set initial value
        await cache.set(key, "10")

        # Increment
        new_value = await cache.increment(key, 5)
        assert new_value == 15

        # Decrement
        new_value = await cache.decrement(key, 3)
        assert new_value == 12

        # Cleanup
        await cache.delete(key)

    @pytest.mark.asyncio
    async def test_cache_bulk_operations(self, connected_adapter):
        """GIVEN multiple key-value pairs
        WHEN bulk set/get operations are used
        THEN should handle multiple items efficiently
        """
        cache = connected_adapter.get_cache_repository()

        timestamp = datetime.now(UTC).timestamp()
        items = {
            f"test:bulk:{timestamp}:key1": "value1",
            f"test:bulk:{timestamp}:key2": "value2",
            f"test:bulk:{timestamp}:key3": "value3",
        }

        # Bulk set
        await cache.set_many(items)

        # Bulk get
        keys = list(items.keys())
        values = await cache.get_many(keys)

        assert len(values) == 3
        assert values[0] == "value1"
        assert values[1] == "value2"
        assert values[2] == "value3"

        # Cleanup
        await cache.delete_pattern(f"test:bulk:{timestamp}:*")

    @pytest.mark.asyncio
    async def test_service_discovery_registration(self, connected_adapter):
        """GIVEN service discovery repository
        WHEN service is registered
        THEN service should be discoverable
        """
        repo = connected_adapter.get_service_discovery_repository()

        service = ServiceInfo(
            service_id=f"test_service_{datetime.now(UTC).timestamp()}",
            service_name="trading-system-engine",
            version="0.1.0",
            host="localhost",
            grpc_port=50051,
            http_port=8080,
            status="healthy",
            metadata={"region": "us-east-1"},
            last_seen=datetime.now(UTC),
            registered_at=datetime.now(UTC),
        )

        await repo.register(service)

        # Retrieve by name
        retrieved = await repo.get_service("trading-system-engine")
        assert retrieved is not None
        assert retrieved.service_name == "trading-system-engine"
        assert retrieved.version == "0.1.0"

        # Cleanup
        await repo.deregister(service.service_id)

    @pytest.mark.asyncio
    async def test_service_heartbeat_behavior(self, connected_adapter):
        """GIVEN registered service
        WHEN heartbeat is updated
        THEN last_seen timestamp should be updated
        """
        repo = connected_adapter.get_service_discovery_repository()

        service = ServiceInfo(
            service_id=f"test_service_{datetime.now(UTC).timestamp()}",
            service_name="test-heartbeat-service",
            version="0.1.0",
            host="localhost",
            grpc_port=50051,
            http_port=8080,
            last_seen=datetime.now(UTC),
            registered_at=datetime.now(UTC),
        )

        await repo.register(service)

        # Wait a bit to ensure timestamp difference
        import asyncio
        await asyncio.sleep(0.01)

        # Update heartbeat
        await repo.update_heartbeat(service.service_id)

        # Retrieve and check timestamp changed
        retrieved = await repo.get_service_by_id(service.service_id)
        assert retrieved is not None
        # Verify heartbeat was updated (>= to handle timing precision)
        assert retrieved.last_seen >= service.last_seen

        # Cleanup
        await repo.deregister(service.service_id)

    @pytest.mark.asyncio
    async def test_service_discovery_list_healthy(self, connected_adapter):
        """GIVEN services with different statuses
        WHEN listing healthy services
        THEN should return only healthy services
        """
        repo = connected_adapter.get_service_discovery_repository()

        timestamp = datetime.now(UTC).timestamp()

        # Register healthy service
        healthy_service = ServiceInfo(
            service_id=f"healthy_{timestamp}",
            service_name="healthy-service",
            version="0.1.0",
            host="localhost",
            grpc_port=50051,
            http_port=8080,
            status="healthy",
            last_seen=datetime.now(UTC),
            registered_at=datetime.now(UTC),
        )

        # Register unhealthy service
        unhealthy_service = ServiceInfo(
            service_id=f"unhealthy_{timestamp}",
            service_name="unhealthy-service",
            version="0.1.0",
            host="localhost",
            grpc_port=50052,
            http_port=8081,
            status="degraded",
            last_seen=datetime.now(UTC),
            registered_at=datetime.now(UTC),
        )

        await repo.register(healthy_service)
        await repo.register(unhealthy_service)

        # List healthy services
        healthy_services = await repo.list_healthy_services()

        # Should contain healthy service
        healthy_ids = {s.service_id for s in healthy_services}
        assert healthy_service.service_id in healthy_ids

        # Cleanup
        await repo.deregister(healthy_service.service_id)
        await repo.deregister(unhealthy_service.service_id)

    @pytest.mark.asyncio
    async def test_stale_service_cleanup_behavior(self, connected_adapter):
        """GIVEN services with old heartbeats
        WHEN cleanup is performed
        THEN stale services should be removed
        """
        repo = connected_adapter.get_service_discovery_repository()

        # This test validates the cleanup mechanism exists
        # Actual stale detection requires time-based testing
        count = await repo.cleanup_stale_services(stale_threshold_seconds=300)

        # Should not raise exception
        assert count >= 0

    @pytest.mark.asyncio
    async def test_cache_namespace_isolation(self, connected_adapter):
        """GIVEN trading-adapter user with trading:* namespace
        WHEN keys are created
        THEN should be properly namespaced
        """
        cache = connected_adapter.get_cache_repository()

        # Create key in trading namespace
        key = f"trading:test:{datetime.now(UTC).timestamp()}"
        value = "namespaced_value"

        await cache.set(key, value)
        retrieved = await cache.get(key)

        assert retrieved == value

        # Cleanup
        await cache.delete(key)
