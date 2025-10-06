"""Trade repository interface."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from trading_data_adapter.models import Trade, TradeQuery


class TradesRepository(ABC):
    """Repository interface for trade persistence."""

    @abstractmethod
    async def create(self, trade: Trade) -> None:
        """Create a new trade."""
        pass

    @abstractmethod
    async def get_by_id(self, trade_id: str) -> Optional[Trade]:
        """Get trade by ID."""
        pass

    @abstractmethod
    async def query(self, query: TradeQuery) -> list[Trade]:
        """Query trades with filters."""
        pass

    @abstractmethod
    async def get_by_order(self, order_id: str) -> list[Trade]:
        """Get all trades for an order."""
        pass

    @abstractmethod
    async def get_by_strategy(self, strategy_id: str,
                              from_date: Optional[datetime] = None,
                              to_date: Optional[datetime] = None) -> list[Trade]:
        """Get all trades for a strategy within date range."""
        pass

    @abstractmethod
    async def get_by_instrument(self, instrument_id: str,
                               from_date: Optional[datetime] = None,
                               to_date: Optional[datetime] = None) -> list[Trade]:
        """Get all trades for an instrument within date range."""
        pass

    @abstractmethod
    async def get_daily_trades(self, strategy_id: str, date: datetime) -> list[Trade]:
        """Get all trades for a strategy on a specific date."""
        pass

    @abstractmethod
    async def calculate_total_volume(self, strategy_id: str,
                                    from_date: Optional[datetime] = None,
                                    to_date: Optional[datetime] = None) -> float:
        """Calculate total trading volume for a strategy."""
        pass

    @abstractmethod
    async def calculate_total_pnl(self, strategy_id: str,
                                 from_date: Optional[datetime] = None,
                                 to_date: Optional[datetime] = None) -> float:
        """Calculate total realized P&L from trades."""
        pass

    @abstractmethod
    async def get_by_exchange_trade_id(self, exchange_trade_id: str) -> Optional[Trade]:
        """Get trade by exchange trade ID."""
        pass
