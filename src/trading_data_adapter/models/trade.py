"""Trade execution domain model."""
from datetime import datetime, UTC
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TradeSide(str, Enum):
    """Trade side."""
    BUY = "buy"
    SELL = "sell"


class Trade(BaseModel):
    """Executed trade with fill information."""

    trade_id: str = Field(..., description="Unique trade identifier")
    order_id: str = Field(..., description="Order that generated this trade")
    strategy_id: str = Field(..., description="Strategy that originated the trade")
    instrument_id: str = Field(..., description="Instrument traded")

    # Trade details
    side: TradeSide = Field(..., description="Buy or sell")
    quantity: Decimal = Field(..., description="Quantity executed")
    price: Decimal = Field(..., description="Execution price")

    # Financial details
    gross_value: Decimal = Field(..., description="Gross trade value (quantity * price)")
    commission: Decimal = Field(default=Decimal("0"), description="Commission paid")
    net_value: Decimal = Field(..., description="Net trade value after commission")

    # Execution details
    exchange_trade_id: Optional[str] = Field(None, description="Exchange trade ID")
    execution_venue: str = Field(..., description="Execution venue/exchange")
    liquidity_flag: Optional[str] = Field(None, description="Maker/taker flag")

    # P&L tracking (if closing position)
    realized_pnl: Optional[Decimal] = Field(None, description="Realized P&L from this trade")

    # Timestamps
    executed_at: datetime = Field(..., description="When trade was executed")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Metadata
    notes: Optional[str] = Field(None, description="Additional notes or metadata")

    model_config = {"json_schema_extra": {"example": {
        "trade_id": "trade-001",
        "order_id": "ord-001",
        "strategy_id": "strat-001",
        "instrument_id": "BTC-USD",
        "side": "buy",
        "quantity": "0.5",
        "price": "50000.00",
        "gross_value": "25000.00",
        "commission": "7.50",
        "net_value": "25007.50",
        "exchange_trade_id": "EX-TRADE-789",
        "execution_venue": "exchange-simulator",
        "liquidity_flag": "taker",
        "realized_pnl": "150.00",
        "executed_at": "2025-10-03T12:00:00Z"
    }}}


class TradeQuery(BaseModel):
    """Query parameters for trades."""

    strategy_id: Optional[str] = None
    order_id: Optional[str] = None
    instrument_id: Optional[str] = None
    side: Optional[TradeSide] = None
    execution_venue: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="executed_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
