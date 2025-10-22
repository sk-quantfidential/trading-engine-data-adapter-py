"""Position tracking domain model."""
from datetime import datetime, UTC
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class Position(BaseModel):
    """Aggregated position for an instrument."""

    position_id: str = Field(..., description="Unique position identifier")
    strategy_id: str = Field(..., description="Strategy owning this position")
    instrument_id: str = Field(..., description="Instrument identifier")

    # Position details
    quantity: Decimal = Field(..., description="Current position quantity (positive=long, negative=short)")
    average_entry_price: Decimal = Field(..., description="Average entry price")

    # Market value
    current_price: Decimal = Field(..., description="Current market price")
    market_value: Decimal = Field(..., description="Current market value (quantity * current_price)")

    # P&L tracking
    unrealized_pnl: Decimal = Field(..., description="Unrealized profit/loss")
    realized_pnl: Decimal = Field(default=Decimal("0"), description="Realized P&L from closed portions")
    total_pnl: Decimal = Field(..., description="Total P&L (realized + unrealized)")

    # Cost basis
    cost_basis: Decimal = Field(..., description="Total cost basis")

    # Risk metrics
    exposure: Decimal = Field(..., description="Total exposure (abs(quantity) * current_price)")

    # Position lifecycle
    opened_at: datetime = Field(..., description="When position was opened")
    last_updated: datetime = Field(..., description="Last update timestamp")
    closed_at: Optional[datetime] = Field(None, description="When position was closed (if closed)")

    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Metadata
    notes: Optional[str] = Field(None, description="Additional notes")

    model_config = {"json_schema_extra": {"example": {
        "position_id": "pos-001",
        "strategy_id": "strat-001",
        "instrument_id": "BTC-USD",
        "quantity": "2.5",
        "average_entry_price": "48000.00",
        "current_price": "50000.00",
        "market_value": "125000.00",
        "unrealized_pnl": "5000.00",
        "realized_pnl": "1500.00",
        "total_pnl": "6500.00",
        "cost_basis": "120000.00",
        "exposure": "125000.00",
        "opened_at": "2025-10-01T10:00:00Z",
        "last_updated": "2025-10-03T12:00:00Z"
    }}}


class PositionQuery(BaseModel):
    """Query parameters for positions."""

    strategy_id: Optional[str] = None
    instrument_id: Optional[str] = None
    is_open: Optional[bool] = None  # None = all, True = open only, False = closed only
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="last_updated")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
