"""Shared test fixtures for trading data adapter tests."""
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


@pytest.fixture
def config():
    """Create test configuration."""
    return AdapterConfig()


@pytest.fixture
async def adapter(config):
    """Create adapter without connections (for unit tests)."""
    adapter = TradingDataAdapter(config)
    yield adapter
    # No connections to disconnect in unit tests


@pytest.fixture
async def connected_adapter(config):
    """Create adapter with connections (for integration tests)."""
    adapter = await create_adapter(config)
    yield adapter
    await adapter.disconnect()


@pytest.fixture
def sample_strategy():
    """Create sample strategy for testing."""
    return Strategy(
        strategy_id="test_strat_001",
        name="Test Strategy",
        strategy_type=StrategyType.MARKET_MAKING,
        status=StrategyStatus.ACTIVE,
        parameters={"spread": 0.01, "size": 100},
        instruments=["BTC-USD", "ETH-USD"],
        max_position_size=Decimal("10000.00"),
        total_pnl=Decimal("1500.50"),
    )


@pytest.fixture
def sample_order():
    """Create sample order for testing."""
    return Order(
        order_id="test_order_001",
        strategy_id="test_strat_001",
        instrument_id="BTC-USD",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        status=OrderStatus.PENDING,
        quantity=Decimal("1.5"),
        remaining_quantity=Decimal("1.5"),
        price=Decimal("50000.00"),
    )


@pytest.fixture
def sample_trade():
    """Create sample trade for testing."""
    return Trade(
        trade_id="test_trade_001",
        order_id="test_order_001",
        strategy_id="test_strat_001",
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


@pytest.fixture
def sample_position():
    """Create sample position for testing."""
    now = datetime.now(UTC)
    return Position(
        position_id="test_pos_001",
        strategy_id="test_strat_001",
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


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (requires services)"
    )
    config.addinivalue_line(
        "markers", "postgres: mark test as requiring PostgreSQL"
    )
    config.addinivalue_line(
        "markers", "redis: mark test as requiring Redis"
    )
