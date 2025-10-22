"""Position repository interface."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from trading_data_adapter.models import Position, PositionQuery


class PositionsRepository(ABC):
    """Repository interface for position persistence."""

    @abstractmethod
    async def create(self, position: Position) -> None:
        """Create a new position."""
        pass

    @abstractmethod
    async def get_by_id(self, position_id: str) -> Optional[Position]:
        """Get position by ID."""
        pass

    @abstractmethod
    async def update(self, position: Position) -> None:
        """Update existing position."""
        pass

    @abstractmethod
    async def delete(self, position_id: str) -> None:
        """Delete position by ID."""
        pass

    @abstractmethod
    async def query(self, query: PositionQuery) -> list[Position]:
        """Query positions with filters."""
        pass

    @abstractmethod
    async def get_by_strategy(self, strategy_id: str) -> list[Position]:
        """Get all positions for a strategy."""
        pass

    @abstractmethod
    async def get_open_positions(self, strategy_id: Optional[str] = None) -> list[Position]:
        """Get all open positions (optionally filtered by strategy)."""
        pass

    @abstractmethod
    async def get_by_instrument(self, strategy_id: str, instrument_id: str) -> Optional[Position]:
        """Get position for a specific strategy and instrument."""
        pass

    @abstractmethod
    async def update_market_data(self, position_id: str, current_price: float) -> None:
        """Update position with current market price and recalculate P&L."""
        pass

    @abstractmethod
    async def close_position(self, position_id: str, closed_at: datetime) -> None:
        """Mark position as closed."""
        pass

    @abstractmethod
    async def calculate_total_exposure(self, strategy_id: Optional[str] = None) -> float:
        """Calculate total exposure across positions."""
        pass

    @abstractmethod
    async def calculate_total_unrealized_pnl(self, strategy_id: Optional[str] = None) -> float:
        """Calculate total unrealized P&L across positions."""
        pass
