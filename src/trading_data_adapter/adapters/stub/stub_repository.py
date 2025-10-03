"""Stub repository implementations for graceful degradation."""
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

import structlog

from trading_data_adapter.interfaces import (
    CacheRepository,
    OrdersRepository,
    PositionsRepository,
    ServiceDiscoveryRepository,
    ServiceInfo,
    StrategiesRepository,
    TradesRepository,
)
from trading_data_adapter.models import Order, Position, Strategy, Trade

logger = structlog.get_logger()


class StubStrategiesRepository(StrategiesRepository):
    """Stub implementation of strategies repository."""

    def __init__(self):
        self._strategies: Dict[str, Strategy] = {}
        logger.info("Initialized stub strategies repository")

    async def create(self, strategy: Strategy) -> None:
        """Create a new strategy."""
        self._strategies[strategy.strategy_id] = strategy
        logger.debug("Created strategy", strategy_id=strategy.strategy_id)

    async def get_by_id(self, strategy_id: str) -> Optional[Strategy]:
        """Get strategy by ID."""
        return self._strategies.get(strategy_id)

    async def update(self, strategy: Strategy) -> None:
        """Update an existing strategy."""
        if strategy.strategy_id in self._strategies:
            self._strategies[strategy.strategy_id] = strategy
            logger.debug("Updated strategy", strategy_id=strategy.strategy_id)

    async def delete(self, strategy_id: str) -> None:
        """Delete a strategy."""
        self._strategies.pop(strategy_id, None)
        logger.debug("Deleted strategy", strategy_id=strategy_id)

    async def query(self, query: Dict[str, Any]) -> list[Strategy]:
        """Query strategies."""
        return list(self._strategies.values())

    async def get_active_strategies(self) -> list[Strategy]:
        """Get all active strategies."""
        return [s for s in self._strategies.values() if s.status == "active"]

    async def update_status(self, strategy_id: str, status: str) -> None:
        """Update strategy status."""
        if strategy_id in self._strategies:
            self._strategies[strategy_id].status = status

    async def get_by_type(self, strategy_type: str) -> list[Strategy]:
        """Get strategies by type."""
        return [s for s in self._strategies.values() if s.strategy_type == strategy_type]

    async def update_pnl(self, strategy_id: str, pnl: float) -> None:
        """Update strategy P&L."""
        if strategy_id in self._strategies:
            from decimal import Decimal
            self._strategies[strategy_id].total_pnl = Decimal(str(pnl))

    async def count(self) -> int:
        """Count total strategies."""
        return len(self._strategies)


class StubOrdersRepository(OrdersRepository):
    """Stub implementation of orders repository."""

    def __init__(self):
        self._orders: Dict[str, Order] = {}
        logger.info("Initialized stub orders repository")

    async def create(self, order: Order) -> None:
        """Create a new order."""
        self._orders[order.order_id] = order
        logger.debug("Created order", order_id=order.order_id)

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self._orders.get(order_id)

    async def update(self, order: Order) -> None:
        """Update an existing order."""
        if order.order_id in self._orders:
            self._orders[order.order_id] = order

    async def update_status(self, order_id: str, status: str) -> None:
        """Update order status."""
        if order_id in self._orders:
            self._orders[order_id].status = status

    async def query(self, query: Dict[str, Any]) -> list[Order]:
        """Query orders."""
        return list(self._orders.values())

    async def get_active_orders(self, strategy_id: Optional[str] = None) -> list[Order]:
        """Get active orders."""
        active_statuses = {"pending", "submitted", "accepted", "partially_filled"}
        if strategy_id:
            return [o for o in self._orders.values()
                   if o.status in active_statuses and o.strategy_id == strategy_id]
        return [o for o in self._orders.values() if o.status in active_statuses]

    async def get_by_strategy(self, strategy_id: str) -> list[Order]:
        """Get orders by strategy."""
        return [o for o in self._orders.values() if o.strategy_id == strategy_id]

    async def get_by_instrument(self, instrument_id: str) -> list[Order]:
        """Get orders by instrument."""
        return [o for o in self._orders.values() if o.instrument_id == instrument_id]

    async def update_fill(self, order_id: str, filled_quantity: float, average_price: float) -> None:
        """Update order fill information."""
        if order_id in self._orders:
            from decimal import Decimal
            self._orders[order_id].filled_quantity = Decimal(str(filled_quantity))
            self._orders[order_id].average_fill_price = Decimal(str(average_price))

    async def cancel(self, order_id: str) -> None:
        """Cancel an order."""
        if order_id in self._orders:
            self._orders[order_id].status = "cancelled"

    async def get_pending_orders(self) -> list[Order]:
        """Get pending orders."""
        return [o for o in self._orders.values() if o.status == "pending"]

    async def cleanup_old_orders(self, days: int) -> int:
        """Clean up old orders."""
        return 0


class StubTradesRepository(TradesRepository):
    """Stub implementation of trades repository."""

    def __init__(self):
        self._trades: Dict[str, Trade] = {}
        logger.info("Initialized stub trades repository")

    async def create(self, trade: Trade) -> None:
        """Create a new trade."""
        self._trades[trade.trade_id] = trade
        logger.debug("Created trade", trade_id=trade.trade_id)

    async def get_by_id(self, trade_id: str) -> Optional[Trade]:
        """Get trade by ID."""
        return self._trades.get(trade_id)

    async def query(self, query: Dict[str, Any]) -> list[Trade]:
        """Query trades."""
        return list(self._trades.values())

    async def get_by_order(self, order_id: str) -> list[Trade]:
        """Get trades by order."""
        return [t for t in self._trades.values() if t.order_id == order_id]

    async def get_by_strategy(self, strategy_id: str) -> list[Trade]:
        """Get trades by strategy."""
        return [t for t in self._trades.values() if t.strategy_id == strategy_id]

    async def get_by_instrument(self, instrument_id: str) -> list[Trade]:
        """Get trades by instrument."""
        return [t for t in self._trades.values() if t.instrument_id == instrument_id]

    async def get_by_time_range(self, start: datetime, end: datetime) -> list[Trade]:
        """Get trades by time range."""
        return [t for t in self._trades.values()
               if start <= t.executed_at <= end]

    async def calculate_pnl(self, strategy_id: str) -> float:
        """Calculate total P&L for strategy."""
        trades = await self.get_by_strategy(strategy_id)
        total = sum(t.realized_pnl or 0 for t in trades)
        return float(total)

    async def get_recent_trades(self, limit: int = 100) -> list[Trade]:
        """Get recent trades."""
        sorted_trades = sorted(self._trades.values(),
                              key=lambda t: t.executed_at, reverse=True)
        return sorted_trades[:limit]

    async def cleanup_old_trades(self, days: int) -> int:
        """Clean up old trades."""
        return 0


class StubPositionsRepository(PositionsRepository):
    """Stub implementation of positions repository."""

    def __init__(self):
        self._positions: Dict[str, Position] = {}
        logger.info("Initialized stub positions repository")

    async def create(self, position: Position) -> None:
        """Create a new position."""
        self._positions[position.position_id] = position
        logger.debug("Created position", position_id=position.position_id)

    async def get_by_id(self, position_id: str) -> Optional[Position]:
        """Get position by ID."""
        return self._positions.get(position_id)

    async def update(self, position: Position) -> None:
        """Update an existing position."""
        if position.position_id in self._positions:
            self._positions[position.position_id] = position

    async def delete(self, position_id: str) -> None:
        """Delete a position."""
        self._positions.pop(position_id, None)

    async def query(self, query: Dict[str, Any]) -> list[Position]:
        """Query positions."""
        return list(self._positions.values())

    async def get_by_strategy(self, strategy_id: str) -> list[Position]:
        """Get positions by strategy."""
        return [p for p in self._positions.values() if p.strategy_id == strategy_id]

    async def get_by_instrument(self, instrument_id: str) -> list[Position]:
        """Get positions by instrument."""
        return [p for p in self._positions.values() if p.instrument_id == instrument_id]

    async def get_open_positions(self, strategy_id: Optional[str] = None) -> list[Position]:
        """Get open positions."""
        if strategy_id:
            return [p for p in self._positions.values()
                   if p.quantity != 0 and p.strategy_id == strategy_id]
        return [p for p in self._positions.values() if p.quantity != 0]

    async def update_price(self, position_id: str, current_price: float) -> None:
        """Update position current price."""
        if position_id in self._positions:
            from decimal import Decimal
            self._positions[position_id].current_price = Decimal(str(current_price))

    async def update_pnl(self, position_id: str, realized_pnl: float, unrealized_pnl: float) -> None:
        """Update position P&L."""
        if position_id in self._positions:
            from decimal import Decimal
            self._positions[position_id].realized_pnl = Decimal(str(realized_pnl))
            self._positions[position_id].unrealized_pnl = Decimal(str(unrealized_pnl))

    async def calculate_total_exposure(self, strategy_id: Optional[str] = None) -> float:
        """Calculate total exposure."""
        positions = await self.get_open_positions(strategy_id)
        total = sum(p.exposure for p in positions)
        return float(total)

    async def get_largest_positions(self, limit: int = 10) -> list[Position]:
        """Get largest positions by exposure."""
        sorted_positions = sorted(self._positions.values(),
                                 key=lambda p: abs(p.exposure), reverse=True)
        return sorted_positions[:limit]

    async def cleanup_closed_positions(self, days: int) -> int:
        """Clean up old closed positions."""
        return 0


class StubServiceDiscoveryRepository(ServiceDiscoveryRepository):
    """Stub implementation of service discovery repository."""

    def __init__(self):
        self._services: Dict[str, ServiceInfo] = {}
        logger.info("Initialized stub service discovery repository")

    async def register(self, service: ServiceInfo) -> None:
        """Register a service."""
        self._services[service.service_id] = service
        logger.debug("Registered service", service_id=service.service_id)

    async def deregister(self, service_id: str) -> None:
        """Deregister a service."""
        self._services.pop(service_id, None)

    async def update_heartbeat(self, service_id: str) -> None:
        """Update service heartbeat."""
        if service_id in self._services:
            self._services[service_id].last_seen = datetime.now(UTC)

    async def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service by name."""
        for service in self._services.values():
            if service.service_name == service_name:
                return service
        return None

    async def get_service_by_id(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service by ID."""
        return self._services.get(service_id)

    async def list_services(self) -> List[ServiceInfo]:
        """List all services."""
        return list(self._services.values())

    async def list_healthy_services(self) -> List[ServiceInfo]:
        """List healthy services."""
        return [s for s in self._services.values() if s.status == "healthy"]

    async def cleanup_stale_services(self, stale_threshold_seconds: int = 300) -> int:
        """Clean up stale services."""
        now = datetime.now(UTC)
        stale_ids = [
            sid for sid, svc in self._services.items()
            if (now - svc.last_seen).total_seconds() > stale_threshold_seconds
        ]
        for sid in stale_ids:
            del self._services[sid]
        return len(stale_ids)

    async def update_status(self, service_id: str, status: str) -> None:
        """Update service status."""
        if service_id in self._services:
            self._services[service_id].status = status


class StubCacheRepository(CacheRepository):
    """Stub implementation of cache repository."""

    def __init__(self):
        self._cache: Dict[str, tuple[str, Optional[datetime]]] = {}
        logger.info("Initialized stub cache repository")

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if key in self._cache:
            value, expires_at = self._cache[key]
            if expires_at is None or datetime.now(UTC) < expires_at:
                return value
            del self._cache[key]
        return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        expires_at = None
        if ttl:
            from datetime import timedelta
            expires_at = datetime.now(UTC) + timedelta(seconds=ttl)
        self._cache[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        self._cache.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self.get(key) is not None

    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache."""
        value = await self.get(key)
        if value:
            import json
            return json.loads(value)
        return None

    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set JSON value in cache."""
        import json
        await self.set(key, json.dumps(value), ttl)

    async def get_many(self, keys: List[str]) -> List[Optional[str]]:
        """Get multiple values."""
        return [await self.get(key) for key in keys]

    async def set_many(self, items: dict[str, str], ttl: Optional[int] = None) -> None:
        """Set multiple values."""
        for key, value in items.items():
            await self.set(key, value, ttl)

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        import fnmatch
        matching_keys = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
        for key in matching_keys:
            del self._cache[key]
        return len(matching_keys)

    async def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        import fnmatch
        return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]

    async def ttl(self, key: str) -> int:
        """Get TTL for key."""
        if key in self._cache:
            _, expires_at = self._cache[key]
            if expires_at is None:
                return -1
            remaining = (expires_at - datetime.now(UTC)).total_seconds()
            return int(remaining) if remaining > 0 else -2
        return -2

    async def expire(self, key: str, ttl: int) -> None:
        """Set expiration for key."""
        if key in self._cache:
            value, _ = self._cache[key]
            from datetime import timedelta
            expires_at = datetime.now(UTC) + timedelta(seconds=ttl)
            self._cache[key] = (value, expires_at)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment value."""
        current = await self.get(key)
        new_value = int(current or 0) + amount
        await self.set(key, str(new_value))
        return new_value

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement value."""
        return await self.increment(key, -amount)
