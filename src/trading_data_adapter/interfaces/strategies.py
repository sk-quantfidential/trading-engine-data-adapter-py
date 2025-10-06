"""Strategy repository interface."""
from abc import ABC, abstractmethod
from typing import Optional

from trading_data_adapter.models import Strategy, StrategyQuery, StrategyStatus


class StrategiesRepository(ABC):
    """Repository interface for strategy persistence."""

    @abstractmethod
    async def create(self, strategy: Strategy) -> None:
        """Create a new strategy."""
        pass

    @abstractmethod
    async def get_by_id(self, strategy_id: str) -> Optional[Strategy]:
        """Get strategy by ID."""
        pass

    @abstractmethod
    async def update(self, strategy: Strategy) -> None:
        """Update existing strategy."""
        pass

    @abstractmethod
    async def delete(self, strategy_id: str) -> None:
        """Delete strategy by ID."""
        pass

    @abstractmethod
    async def query(self, query: StrategyQuery) -> list[Strategy]:
        """Query strategies with filters."""
        pass

    @abstractmethod
    async def get_active_strategies(self) -> list[Strategy]:
        """Get all active strategies."""
        pass

    @abstractmethod
    async def update_status(self, strategy_id: str, status: StrategyStatus) -> None:
        """Update strategy status."""
        pass

    @abstractmethod
    async def update_pnl(self, strategy_id: str, total_pnl: float, daily_pnl: float) -> None:
        """Update strategy P&L."""
        pass

    @abstractmethod
    async def increment_trade_count(self, strategy_id: str) -> None:
        """Increment total trade count."""
        pass

    @abstractmethod
    async def get_by_instrument(self, instrument_id: str) -> list[Strategy]:
        """Get all strategies trading a specific instrument."""
        pass
