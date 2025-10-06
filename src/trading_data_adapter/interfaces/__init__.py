"""Repository interfaces for trading data adapter."""

from trading_data_adapter.interfaces.strategies import StrategiesRepository
from trading_data_adapter.interfaces.orders import OrdersRepository
from trading_data_adapter.interfaces.trades import TradesRepository
from trading_data_adapter.interfaces.positions import PositionsRepository
from trading_data_adapter.interfaces.service_discovery import ServiceDiscoveryRepository, ServiceInfo
from trading_data_adapter.interfaces.cache import CacheRepository

__all__ = [
    "StrategiesRepository",
    "OrdersRepository",
    "TradesRepository",
    "PositionsRepository",
    "ServiceDiscoveryRepository",
    "ServiceInfo",
    "CacheRepository",
]
