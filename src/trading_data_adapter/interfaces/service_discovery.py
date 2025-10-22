"""Service discovery repository interface."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class ServiceInfo(BaseModel):
    """Service registration information."""
    service_id: str
    service_name: str
    version: str
    host: str
    grpc_port: int
    http_port: int
    status: str = "healthy"
    metadata: Dict[str, str] = {}
    last_seen: datetime
    registered_at: datetime


class ServiceDiscoveryRepository(ABC):
    """Repository interface for service discovery operations."""

    @abstractmethod
    async def register(self, service: ServiceInfo) -> None:
        """Register a service."""
        pass

    @abstractmethod
    async def deregister(self, service_id: str) -> None:
        """Deregister a service."""
        pass

    @abstractmethod
    async def update_heartbeat(self, service_id: str) -> None:
        """Update service heartbeat timestamp."""
        pass

    @abstractmethod
    async def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service information by name."""
        pass

    @abstractmethod
    async def get_service_by_id(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service information by ID."""
        pass

    @abstractmethod
    async def list_services(self) -> List[ServiceInfo]:
        """List all registered services."""
        pass

    @abstractmethod
    async def list_healthy_services(self) -> List[ServiceInfo]:
        """List all healthy services."""
        pass

    @abstractmethod
    async def cleanup_stale_services(self, stale_threshold_seconds: int = 300) -> int:
        """Remove services that haven't sent heartbeat, return count removed."""
        pass

    @abstractmethod
    async def update_status(self, service_id: str, status: str) -> None:
        """Update service status."""
        pass
