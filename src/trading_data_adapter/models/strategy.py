"""Trading strategy domain model."""
from datetime import datetime, UTC
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class StrategyStatus(str, Enum):
    """Strategy status levels."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class StrategyType(str, Enum):
    """Strategy type classifications."""
    MARKET_MAKING = "market_making"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    MOMENTUM = "momentum"
    CUSTOM = "custom"


class Strategy(BaseModel):
    """Trading strategy configuration and state."""

    strategy_id: str = Field(..., description="Unique strategy identifier")
    name: str = Field(..., description="Strategy name")
    strategy_type: StrategyType = Field(..., description="Strategy classification")
    status: StrategyStatus = Field(..., description="Current strategy status")

    # Configuration
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Strategy parameters as JSON")
    instruments: list[str] = Field(default_factory=list, description="Instruments traded by strategy")

    # Risk limits
    max_position_size: Optional[Decimal] = Field(None, description="Maximum position size")
    max_daily_loss: Optional[Decimal] = Field(None, description="Maximum daily loss limit")
    max_leverage: Optional[Decimal] = Field(None, description="Maximum leverage ratio")

    # Performance tracking
    total_pnl: Decimal = Field(default=Decimal("0"), description="Total P&L")
    daily_pnl: Decimal = Field(default=Decimal("0"), description="Today's P&L")
    total_trades: int = Field(default=0, description="Total number of trades executed")

    # Timestamps
    started_at: Optional[datetime] = Field(None, description="When strategy was started")
    stopped_at: Optional[datetime] = Field(None, description="When strategy was stopped")

    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"json_schema_extra": {"example": {
        "strategy_id": "strat-001",
        "name": "BTC Market Making",
        "strategy_type": "market_making",
        "status": "active",
        "parameters": {"spread": 0.001, "order_size": 0.1},
        "instruments": ["BTC-USD", "ETH-USD"],
        "max_position_size": "10.0",
        "max_daily_loss": "1000.0",
        "total_pnl": "5000.00",
        "daily_pnl": "250.00",
        "total_trades": 142
    }}}


class StrategyQuery(BaseModel):
    """Query parameters for strategies."""

    strategy_type: Optional[StrategyType] = None
    status: Optional[StrategyStatus] = None
    instrument: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
