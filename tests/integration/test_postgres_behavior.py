"""PostgreSQL behavior tests for trading data adapter."""
import pytest
from decimal import Decimal
from datetime import datetime, UTC

from trading_data_adapter.models import (
    StrategyStatus,
    StrategyType,
    OrderSide,
    OrderType,
    OrderStatus,
    TradeSide,
)


pytestmark = [pytest.mark.integration, pytest.mark.postgres]


class TestPostgresBehavior:
    """Behavior tests for PostgreSQL integration."""

    @pytest.mark.asyncio
    async def test_connection_health_check(self, connected_adapter):
        """GIVEN orchestrator PostgreSQL is running
        WHEN health check is performed
        THEN connection should be healthy and trading schema accessible
        """
        health = await connected_adapter.health_check()

        assert health["status"] in ["healthy", "degraded"]
        assert "postgres" in health
        assert health["postgres"]["connected"] is True

        if "schema_check" in health["postgres"]:
            schema_check = health["postgres"]["schema_check"]
            assert schema_check["schema"] == "trading"
            assert schema_check["status"] == "healthy"
            assert "tables" in schema_check

    @pytest.mark.asyncio
    async def test_connection_status_tracking(self, connected_adapter):
        """GIVEN adapter has connected
        WHEN connection status is checked
        THEN status should show PostgreSQL connected with timestamp
        """
        assert connected_adapter.connection_status.postgres_connected is True
        assert connected_adapter.connection_status.last_postgres_check is not None
        assert connected_adapter.connection_status.postgres_error is None

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_connection_failure(self):
        """GIVEN PostgreSQL is unavailable
        WHEN adapter connects
        THEN should degrade gracefully and allow stub operations
        """
        # Use invalid connection
        config = AdapterConfig(postgres_url="postgresql+asyncpg://invalid:invalid@localhost:9999/invalid")
        adapter = await create_adapter(config)

        # Should not raise exception
        assert connected_adapter.connection_status.postgres_connected is False
        assert connected_adapter.connection_status.postgres_error is not None

        # Stub should still work
        repo = connected_adapter.get_strategies_repository()
        assert repo is not None

        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_strategy_persistence_behavior(self, connected_adapter):
        """GIVEN trading schema exists
        WHEN strategy is created, updated, and queried
        THEN operations should persist correctly in PostgreSQL
        """
        # This test will initially fail until we implement PostgreSQL repositories
        # For now, we're using stub which keeps data in memory
        repo = connected_adapter.get_strategies_repository()

        # Create strategy
        strategy = Strategy(
            strategy_id=f"test_strat_{datetime.now(UTC).timestamp()}",
            name="Test PostgreSQL Strategy",
            strategy_type=StrategyType.MARKET_MAKING,
            status=StrategyStatus.ACTIVE,
            parameters={"spread": 0.01, "size": 100},
            instruments=["BTC-USD"],
            max_position_size=Decimal("10000.00"),
        )

        await repo.create(strategy)

        # Retrieve and verify
        retrieved = await repo.get_by_id(strategy.strategy_id)
        assert retrieved is not None
        assert retrieved.name == "Test PostgreSQL Strategy"
        assert retrieved.status == StrategyStatus.ACTIVE

        # Update
        strategy.status = StrategyStatus.PAUSED
        await repo.update(strategy)

        # Verify update
        updated = await repo.get_by_id(strategy.strategy_id)
        assert updated.status == StrategyStatus.PAUSED

        # Cleanup
        await repo.delete(strategy.strategy_id)

    @pytest.mark.asyncio
    async def test_order_lifecycle_behavior(self, connected_adapter):
        """GIVEN trading schema with orders table
        WHEN order goes through lifecycle (pending -> submitted -> filled)
        THEN state transitions should persist correctly
        """
        repo = connected_adapter.get_orders_repository()

        # Create order
        order = Order(
            order_id=f"test_order_{datetime.now(UTC).timestamp()}",
            strategy_id="test_strategy",
            instrument_id="BTC-USD",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            status=OrderStatus.PENDING,
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
        )

        await repo.create(order)

        # Update to submitted
        await repo.update_status(order.order_id, OrderStatus.SUBMITTED)
        submitted = await repo.get_by_id(order.order_id)
        assert submitted.status == OrderStatus.SUBMITTED

        # Update fill information
        await repo.update_fill(order.order_id, Decimal("0.5"), Decimal("50100.00"))
        partially_filled = await repo.get_by_id(order.order_id)
        assert partially_filled.filled_quantity == Decimal("0.5")
        assert partially_filled.average_fill_price == Decimal("50100.00")

    @pytest.mark.asyncio
    async def test_trade_recording_behavior(self, connected_adapter):
        """GIVEN trading schema with trades table
        WHEN trades are executed
        THEN trade details should be recorded with P&L calculation
        """
        repo = connected_adapter.get_trades_repository()

        # Create trade
        trade = Trade(
            trade_id=f"test_trade_{datetime.now(UTC).timestamp()}",
            order_id="test_order",
            strategy_id="test_strategy",
            instrument_id="BTC-USD",
            side=TradeSide.BUY,
            quantity=Decimal("1.5"),
            price=Decimal("50000.00"),
            gross_value=Decimal("75000.00"),
            commission=Decimal("7.50"),
            net_value=Decimal("74992.50"),
            realized_pnl=Decimal("100.00"),
            executed_at=datetime.now(UTC),
        )

        await repo.create(trade)

        # Retrieve and verify
        retrieved = await repo.get_by_id(trade.trade_id)
        assert retrieved is not None
        assert retrieved.quantity == Decimal("1.5")
        assert retrieved.commission == Decimal("7.50")
        assert retrieved.realized_pnl == Decimal("100.00")

    @pytest.mark.asyncio
    async def test_position_aggregation_behavior(self, connected_adapter):
        """GIVEN trading schema with positions table
        WHEN positions are updated with market prices
        THEN unrealized P&L should be calculated correctly
        """
        repo = connected_adapter.get_positions_repository()

        # Create position
        position = Position(
            position_id=f"test_pos_{datetime.now(UTC).timestamp()}",
            strategy_id="test_strategy",
            instrument_id="BTC-USD",
            quantity=Decimal("2.0"),
            average_entry_price=Decimal("49000.00"),
            current_price=Decimal("50000.00"),
            market_value=Decimal("100000.00"),
            unrealized_pnl=Decimal("2000.00"),
            realized_pnl=Decimal("0"),
            total_pnl=Decimal("2000.00"),
            exposure=Decimal("100000.00"),
            opened_at=datetime.now(UTC),
        )

        await repo.create(position)

        # Update price
        await repo.update_price(position.position_id, Decimal("51000.00"))
        updated = await repo.get_by_id(position.position_id)
        assert updated.current_price == Decimal("51000.00")

        # Update P&L
        await repo.update_pnl(position.position_id, Decimal("100.00"), Decimal("4000.00"))
        updated_pnl = await repo.get_by_id(position.position_id)
        assert updated_pnl.realized_pnl == Decimal("100.00")
        assert updated_pnl.unrealized_pnl == Decimal("4000.00")

    @pytest.mark.asyncio
    async def test_query_by_strategy_behavior(self, connected_adapter):
        """GIVEN multiple orders and positions exist
        WHEN querying by strategy_id
        THEN should return only items for that strategy
        """
        orders_repo = adapter.get_orders_repository()
        positions_repo = adapter.get_positions_repository()

        strategy_id = f"test_strategy_{datetime.now(UTC).timestamp()}"

        # Create orders for strategy
        for i in range(3):
            order = Order(
                order_id=f"order_{strategy_id}_{i}",
                strategy_id=strategy_id,
                instrument_id=f"INST_{i}",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                status=OrderStatus.PENDING,
                quantity=Decimal("1.0"),
                price=Decimal("100.00"),
            )
            await orders_repo.create(order)

        # Query by strategy
        orders = await orders_repo.get_by_strategy(strategy_id)
        assert len(orders) == 3
        assert all(o.strategy_id == strategy_id for o in orders)

    @pytest.mark.asyncio
    async def test_active_orders_filtering_behavior(self, connected_adapter):
        """GIVEN orders in various states
        WHEN requesting active orders
        THEN should return only pending/submitted/partially_filled orders
        """
        repo = connected_adapter.get_orders_repository()

        strategy_id = f"test_strategy_{datetime.now(UTC).timestamp()}"

        # Create orders in different states
        statuses = [
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.PARTIALLY_FILLED,
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
        ]

        for i, status in enumerate(statuses):
            order = Order(
                order_id=f"order_{strategy_id}_{i}",
                strategy_id=strategy_id,
                instrument_id="BTC-USD",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                status=status,
                quantity=Decimal("1.0"),
                price=Decimal("100.00"),
            )
            await repo.create(order)

        # Get active orders
        active = await repo.get_active_orders(strategy_id)

        # Should have 3 active (pending, submitted, partially_filled)
        assert len(active) == 3
        assert all(o.status in {OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED} for o in active)

    @pytest.mark.asyncio
    async def test_exposure_calculation_behavior(self, connected_adapter):
        """GIVEN multiple open positions
        WHEN calculating total exposure
        THEN should sum all position exposures correctly
        """
        repo = connected_adapter.get_positions_repository()

        strategy_id = f"test_strategy_{datetime.now(UTC).timestamp()}"

        # Create positions
        exposures = [Decimal("10000.00"), Decimal("20000.00"), Decimal("15000.00")]

        for i, exposure in enumerate(exposures):
            position = Position(
                position_id=f"pos_{strategy_id}_{i}",
                strategy_id=strategy_id,
                instrument_id=f"INST_{i}",
                quantity=Decimal("1.0"),
                average_entry_price=Decimal("100.00"),
                current_price=Decimal("100.00"),
                market_value=exposure,
                unrealized_pnl=Decimal("0"),
                realized_pnl=Decimal("0"),
                total_pnl=Decimal("0"),
                exposure=exposure,
                opened_at=datetime.now(UTC),
            )
            await repo.create(position)

        # Calculate total exposure
        total_exposure = await repo.calculate_total_exposure(strategy_id)
        assert total_exposure == float(sum(exposures))
