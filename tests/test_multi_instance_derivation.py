"""Tests for multi-instance configuration derivation logic.

This test suite validates that the trading-data-adapter-py correctly derives
PostgreSQL schema names and Redis namespaces from service instance names,
enabling multi-instance deployment patterns.

Test Coverage:
- Singleton derivation (trading-system-engine → "trading" schema/namespace)
- Multi-instance derivation (trading-system-engine-LH → "trading_system_engine_lh" schema)
- Explicit override behavior
- Instance name auto-derivation
- Complex instance name patterns
"""

import pytest
from trading_data_adapter.config import AdapterConfig


class TestSingletonDerivation:
    """Test schema/namespace derivation for singleton instances."""

    def test_singleton_schema_derivation(self):
        """Singleton instance should derive schema from first part of service name."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="trading-system-engine",
        )
        assert config.postgres_schema == "trading"

    def test_singleton_namespace_derivation(self):
        """Singleton instance should derive Redis namespace from first part."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="trading-system-engine",
        )
        assert config.redis_namespace == "trading"

    def test_singleton_auto_instance_name(self):
        """When instance name not provided, should auto-derive from service name."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="",  # Empty triggers auto-derivation
        )
        assert config.service_instance_name == "trading-system-engine"
        assert config.postgres_schema == "trading"
        assert config.redis_namespace == "trading"


class TestMultiInstanceDerivation:
    """Test schema/namespace derivation for multi-instance deployments."""

    def test_multi_instance_schema_derivation_lh(self):
        """Multi-instance should convert hyphens to underscores for schema."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="trading-system-engine-LH",
        )
        assert config.postgres_schema == "trading_system_engine_lh"

    def test_multi_instance_namespace_derivation_lh(self):
        """Multi-instance should use colon separator for Redis namespace."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="trading-system-engine-LH",
        )
        assert config.redis_namespace == "trading_system:LH"

    def test_multi_instance_schema_derivation_alpha(self):
        """Test schema derivation for Alpha instance."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="trading-system-engine-Alpha",
        )
        assert config.postgres_schema == "trading_system_engine_alpha"

    def test_multi_instance_namespace_derivation_alpha(self):
        """Test namespace derivation for Alpha instance."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="trading-system-engine-Alpha",
        )
        assert config.redis_namespace == "trading_system:Alpha"

    def test_multi_instance_complex_name(self):
        """Test derivation for complex instance names with multiple parts."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="trading-system-engine-Alpha-2",
        )
        # Schema: all hyphens to underscores, lowercase
        assert config.postgres_schema == "trading_system_engine_alpha_2"
        # Namespace: base + colon + suffix
        assert config.redis_namespace == "trading_system:Alpha-2"


class TestExplicitOverrides:
    """Test that explicit schema/namespace settings override derivation."""

    def test_explicit_schema_override(self):
        """Explicit schema should override derivation."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="trading-system-engine-LH",
            postgres_schema="custom_schema",
        )
        assert config.postgres_schema == "custom_schema"

    def test_explicit_namespace_override(self):
        """Explicit namespace should override derivation."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="trading-system-engine-LH",
            redis_namespace="custom:namespace",
        )
        assert config.redis_namespace == "custom:namespace"

    def test_both_explicit_overrides(self):
        """Both explicit settings should override derivation."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            service_instance_name="trading-system-engine-LH",
            postgres_schema="custom_schema",
            redis_namespace="custom:namespace",
        )
        assert config.postgres_schema == "custom_schema"
        assert config.redis_namespace == "custom:namespace"


class TestEnvironmentField:
    """Test environment field integration."""

    def test_environment_default(self):
        """Environment should default to development."""
        config = AdapterConfig(
            service_name="trading-system-engine",
        )
        assert config.environment == "development"

    def test_environment_docker(self):
        """Environment can be set to docker."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            environment="docker",
        )
        assert config.environment == "docker"

    def test_environment_production(self):
        """Environment can be set to production."""
        config = AdapterConfig(
            service_name="trading-system-engine",
            environment="production",
        )
        assert config.environment == "production"


class TestBackwardCompatibility:
    """Test that changes maintain backward compatibility."""

    def test_default_behavior_preserved(self):
        """Default config should work without any new fields."""
        config = AdapterConfig()
        # Should have defaults
        assert config.service_name == "trading-system-engine"
        assert config.service_instance_name == "trading-system-engine"
        assert config.postgres_schema == "trading"  # Derived from singleton
        assert config.redis_namespace == "trading"

    def test_existing_tests_unaffected(self):
        """Existing test patterns should continue working."""
        config = AdapterConfig(
            postgres_url="postgresql+asyncpg://user:pass@host:5432/db",
            redis_url="redis://user:pass@host:6379/0",
        )
        # All original fields should work
        assert config.postgres_url
        assert config.redis_url
        assert config.service_name
        # New fields should have defaults
        assert config.service_instance_name
        assert config.postgres_schema
        assert config.redis_namespace
