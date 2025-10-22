"""Order domain model."""
from datetime import datetime, UTC
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    """Order side."""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(str, Enum):
    """Order status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimeInForce(str, Enum):
    """Time in force options."""
    GTC = "gtc"  # Good Till Cancel
    IOC = "ioc"  # Immediate Or Cancel
    FOK = "fok"  # Fill Or Kill
    DAY = "day"  # Day order


class Order(BaseModel):
    """Order lifecycle tracking."""

    order_id: str = Field(..., description="Unique order identifier")
    strategy_id: str = Field(..., description="Strategy that created this order")
    instrument_id: str = Field(..., description="Instrument being traded")

    # Order details
    side: OrderSide = Field(..., description="Buy or sell")
    order_type: OrderType = Field(..., description="Order type")
    status: OrderStatus = Field(..., description="Current order status")
    time_in_force: TimeInForce = Field(default=TimeInForce.GTC, description="Time in force")

    # Quantities and prices
    quantity: Decimal = Field(..., description="Ordered quantity")
    filled_quantity: Decimal = Field(default=Decimal("0"), description="Filled quantity")
    remaining_quantity: Decimal = Field(..., description="Remaining quantity")

    price: Optional[Decimal] = Field(None, description="Limit price (for limit orders)")
    stop_price: Optional[Decimal] = Field(None, description="Stop price (for stop orders)")
    average_fill_price: Optional[Decimal] = Field(None, description="Average execution price")

    # Execution tracking
    exchange_order_id: Optional[str] = Field(None, description="Exchange order ID")
    execution_venue: Optional[str] = Field(None, description="Execution venue/exchange")

    # Financial tracking
    commission: Decimal = Field(default=Decimal("0"), description="Commission paid")
    realized_pnl: Optional[Decimal] = Field(None, description="Realized P&L from this order")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    submitted_at: Optional[datetime] = Field(None, description="When submitted to exchange")
    filled_at: Optional[datetime] = Field(None, description="When fully filled")
    cancelled_at: Optional[datetime] = Field(None, description="When cancelled")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Error tracking
    error_message: Optional[str] = Field(None, description="Error message if rejected")

    model_config = {"json_schema_extra": {"example": {
        "order_id": "ord-001",
        "strategy_id": "strat-001",
        "instrument_id": "BTC-USD",
        "side": "buy",
        "order_type": "limit",
        "status": "filled",
        "time_in_force": "gtc",
        "quantity": "1.5",
        "filled_quantity": "1.5",
        "remaining_quantity": "0.0",
        "price": "50000.00",
        "average_fill_price": "49995.50",
        "exchange_order_id": "EX-12345",
        "execution_venue": "exchange-simulator",
        "commission": "15.00",
        "realized_pnl": "250.00"
    }}}


class OrderQuery(BaseModel):
    """Query parameters for orders."""

    strategy_id: Optional[str] = None
    instrument_id: Optional[str] = None
    side: Optional[OrderSide] = None
    order_type: Optional[OrderType] = None
    status: Optional[OrderStatus] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
