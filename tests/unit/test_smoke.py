"""Smoke tests for trading data adapter."""
import pytest
from decimal import Decimal
from datetime import datetime, UTC

from trading_data_adapter import AdapterConfig, TradingDataAdapter, create_adapter
from trading_data_adapter.models import (
    Strategy,
    StrategyStatus,
    StrategyType,
    Order,
    OrderSide,
    OrderType,
    OrderStatus,
    Trade,
    TradeSide,
    Position,
)


class TestSmokeTests:
    """Smoke tests to verify basic functionality without external dependencies."""

    def test_config_creation(self):
        """Test that config can be created with defaults."""
        config = AdapterConfig()
        assert config.service_name == "trading-system-engine"
        assert config.postgres_pool_size == 10
        assert config.cache_ttl_strategies == 600

    def test_config_from_env(self, monkeypatch):
        """Test config loading from environment variables."""
        monkeypatch.setenv("TRADING_ADAPTER_SERVICE_NAME", "test-service")
        monkeypatch.setenv("TRADING_ADAPTER_POSTGRES_POOL_SIZE", "20")

        config = AdapterConfig()
        assert config.service_name == "test-service"
        assert config.postgres_pool_size == 20

    @pytest.mark.asyncio
    async def test_adapter_creation(self):
        """Test adapter can be created."""
        config = AdapterConfig()
        adapter = TradingDataAdapter(config)
        assert adapter is not None
        assert adapter.config == config

    @pytest.mark.asyncio
    async def test_stub_repositories(self):
        """Test that stub repositories work without connections."""
        config = AdapterConfig()
        adapter = TradingDataAdapter(config)

        # Get all repositories
        strategies_repo = adapter.get_strategies_repository()
        orders_repo = adapter.get_orders_repository()
        trades_repo = adapter.get_trades_repository()
        positions_repo = adapter.get_positions_repository()
        service_discovery_repo = adapter.get_service_discovery_repository()
        cache_repo = adapter.get_cache_repository()

        # Verify they're not None
        assert strategies_repo is not None
        assert orders_repo is not None
        assert trades_repo is not None
        assert positions_repo is not None
        assert service_discovery_repo is not None
        assert cache_repo is not None

    @pytest.mark.asyncio
    async def test_strategy_model(self):
        """Test strategy domain model."""
        strategy = Strategy(
            strategy_id="strat_001",
            name="Test Strategy",
            strategy_type=StrategyType.MARKET_MAKING,
            status=StrategyStatus.ACTIVE,
            parameters={"param1": "value1"},
            instruments=["BTC-USD", "ETH-USD"],
            max_position_size=Decimal("10000.00"),
            total_pnl=Decimal("1500.50"),
        )

        assert strategy.strategy_id == "strat_001"
        assert strategy.name == "Test Strategy"
        assert strategy.strategy_type == StrategyType.MARKET_MAKING
        assert strategy.status == StrategyStatus.ACTIVE
        assert strategy.max_position_size == Decimal("10000.00")
        assert isinstance(strategy.created_at, datetime)

    @pytest.mark.asyncio
    async def test_order_model(self):
        """Test order domain model."""
        order = Order(
            order_id="order_001",
            strategy_id="strat_001",
            instrument_id="BTC-USD",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            status=OrderStatus.PENDING,
            quantity=Decimal("1.5"),
            remaining_quantity=Decimal("1.5"),
            price=Decimal("50000.00"),
        )

        assert order.order_id == "order_001"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.LIMIT
        assert order.quantity == Decimal("1.5")
        assert order.filled_quantity == Decimal("0")
        assert order.remaining_quantity == Decimal("1.5")

    @pytest.mark.asyncio
    async def test_trade_model(self):
        """Test trade domain model."""
        trade = Trade(
            trade_id="trade_001",
            order_id="order_001",
            strategy_id="strat_001",
            instrument_id="BTC-USD",
            side=TradeSide.BUY,
            quantity=Decimal("1.5"),
            price=Decimal("50000.00"),
            gross_value=Decimal("75000.00"),
            commission=Decimal("7.50"),
            net_value=Decimal("74992.50"),
            execution_venue="exchange-simulator",
            executed_at=datetime.now(UTC),
        )

        assert trade.trade_id == "trade_001"
        assert trade.quantity == Decimal("1.5")
        assert trade.commission == Decimal("7.50")
        assert trade.net_value == Decimal("74992.50")
        assert trade.execution_venue == "exchange-simulator"

    @pytest.mark.asyncio
    async def test_position_model(self):
        """Test position domain model."""
        now = datetime.now(UTC)
        position = Position(
            position_id="pos_001",
            strategy_id="strat_001",
            instrument_id="BTC-USD",
            quantity=Decimal("2.0"),
            average_entry_price=Decimal("49000.00"),
            current_price=Decimal("50000.00"),
            market_value=Decimal("100000.00"),
            unrealized_pnl=Decimal("2000.00"),
            realized_pnl=Decimal("500.00"),
            total_pnl=Decimal("2500.00"),
            cost_basis=Decimal("98000.00"),
            exposure=Decimal("100000.00"),
            opened_at=now,
            last_updated=now,
        )

        assert position.position_id == "pos_001"
        assert position.quantity == Decimal("2.0")
        assert position.unrealized_pnl == Decimal("2000.00")
        assert position.total_pnl == Decimal("2500.00")
        assert position.cost_basis == Decimal("98000.00")

    @pytest.mark.asyncio
    async def test_stub_strategy_operations(self):
        """Test stub strategy repository operations."""
        config = AdapterConfig()
        adapter = TradingDataAdapter(config)
        repo = adapter.get_strategies_repository()

        # Create strategy
        strategy = Strategy(
            strategy_id="strat_001",
            name="Test Strategy",
            strategy_type=StrategyType.MARKET_MAKING,
            status=StrategyStatus.ACTIVE,
        )
        await repo.create(strategy)

        # Get strategy
        retrieved = await repo.get_by_id("strat_001")
        assert retrieved is not None
        assert retrieved.strategy_id == "strat_001"
        assert retrieved.name == "Test Strategy"

        # Update status
        await repo.update_status("strat_001", StrategyStatus.PAUSED)
        updated = await repo.get_by_id("strat_001")
        assert updated.status == StrategyStatus.PAUSED

        # Get active strategies
        active = await repo.get_active_strategies()
        assert len(active) == 0  # Paused, not active

        # Count
        count = await repo.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_stub_cache_operations(self):
        """Test stub cache repository operations."""
        config = AdapterConfig()
        adapter = TradingDataAdapter(config)
        repo = adapter.get_cache_repository()

        # Set and get
        await repo.set("test_key", "test_value")
        value = await repo.get("test_key")
        assert value == "test_value"

        # Exists
        exists = await repo.exists("test_key")
        assert exists is True

        # Delete
        await repo.delete("test_key")
        value = await repo.get("test_key")
        assert value is None

        # JSON operations
        await repo.set_json("json_key", {"field": "value"})
        json_value = await repo.get_json("json_key")
        assert json_value == {"field": "value"}

        # Increment
        await repo.set("counter", "10")
        new_value = await repo.increment("counter", 5)
        assert new_value == 15
