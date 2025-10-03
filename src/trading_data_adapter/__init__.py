"""Trading Data Adapter - Clean architecture persistence for trading system engine."""

from trading_data_adapter.config import AdapterConfig
from trading_data_adapter.factory import TradingDataAdapter, create_adapter

__version__ = "0.1.0"
__all__ = ["AdapterConfig", "TradingDataAdapter", "create_adapter"]
