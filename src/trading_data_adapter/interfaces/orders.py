"""Order repository interface."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from trading_data_adapter.models import Order, OrderQuery, OrderStatus


class OrdersRepository(ABC):
    """Repository interface for order persistence."""

    @abstractmethod
    async def create(self, order: Order) -> None:
        """Create a new order."""
        pass

    @abstractmethod
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        pass

    @abstractmethod
    async def update(self, order: Order) -> None:
        """Update existing order."""
        pass

    @abstractmethod
    async def delete(self, order_id: str) -> None:
        """Delete order by ID."""
        pass

    @abstractmethod
    async def query(self, query: OrderQuery) -> list[Order]:
        """Query orders with filters."""
        pass

    @abstractmethod
    async def get_by_strategy(self, strategy_id: str) -> list[Order]:
        """Get all orders for a strategy."""
        pass

    @abstractmethod
    async def get_active_orders(self, strategy_id: Optional[str] = None) -> list[Order]:
        """Get all active orders (optionally filtered by strategy)."""
        pass

    @abstractmethod
    async def update_status(self, order_id: str, status: OrderStatus,
                           filled_quantity: Optional[float] = None) -> None:
        """Update order status and optionally filled quantity."""
        pass

    @abstractmethod
    async def update_fill(self, order_id: str, filled_quantity: float,
                         average_fill_price: float) -> None:
        """Update order fill information."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str, cancelled_at: datetime) -> None:
        """Mark order as cancelled."""
        pass

    @abstractmethod
    async def get_by_exchange_order_id(self, exchange_order_id: str) -> Optional[Order]:
        """Get order by exchange order ID."""
        pass

    @abstractmethod
    async def get_orders_by_instrument(self, instrument_id: str,
                                      status: Optional[OrderStatus] = None) -> list[Order]:
        """Get orders for an instrument, optionally filtered by status."""
        pass
