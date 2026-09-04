from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from pydantic import BaseModel, Field, model_validator


class Signal(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class RiskAction(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REDUCE_SIZE = "REDUCE_SIZE"
    REQUEST_MORE_DATA = "REQUEST_MORE_DATA"


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class FundamentalData(BaseModel):
    ticker: str
    revenue_growth: float | None = None
    earnings_growth: float | None = None
    eps: float | None = None
    pe: float | None = None
    forward_pe: float | None = None
    ps: float | None = None
    debt_to_equity: float | None = None
    free_cash_flow: float | None = None
    net_margin: float | None = None
    roe: float | None = None
    roic: float | None = None


class AgentOutput(BaseModel):
    agent: str
    ticker: str
    signal: Signal
    confidence: float = Field(ge=0, le=1)
    reasoning: list[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "OK"


class TechnicalOutput(AgentOutput):
    timeframe: str = "1D"
    trend: str = "unknown"
    entry: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    risk_reward: float | None = None
    invalidation_conditions: list[str] = []
    indicators: dict[str, float] = {}


class FundamentalOutput(AgentOutput):
    valuation_view: str = "unknown"
    business_quality: str = "unknown"
    growth_quality: str = "unknown"
    financial_health: str = "unknown"
    bull_case: list[str] = []
    bear_case: list[str] = []


class NewsOutput(AgentOutput):
    sentiment: str = "neutral"
    event_importance: str = "low"
    affected_assets: list[str] = []


class MacroOutput(AgentOutput):
    macro_regime: str = "unknown"
    risk_environment: str = "unknown"
    relevant_factors: list[str] = []
    affected_assets: list[str] = []


class RiskOutput(AgentOutput):
    action: RiskAction
    approved_size: float = 0
    risk_amount: float = 0
    reasons: list[str] = []


class Decision(BaseModel):
    ticker: str
    action: Signal
    position_size: float = 0
    entry: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    expected_risk: float = 0
    expected_reward: float = 0
    confidence: float = 0
    score: float = 0
    thesis: str
    reasons: list[str] = []
    risks: list[str] = []
    invalidation_conditions: list[str] = []
    run_id: str | None = None


class OrderRequest(BaseModel):
    ticker: str
    side: Signal
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    stop_loss: float | None = None
    take_profit: float | None = None

    @model_validator(mode="after")
    def valid_stops(self):
        if (
            self.side == Signal.BUY
            and self.stop_loss is not None
            and self.stop_loss >= self.price
        ):
            raise ValueError("BUY stop loss must be below entry price")
        if (
            self.side == Signal.BUY
            and self.take_profit is not None
            and self.take_profit <= self.price
        ):
            raise ValueError("BUY take profit must be above entry price")
        return self


class Position(BaseModel):
    ticker: str
    quantity: float
    average_price: float
    stop_loss: float | None = None
    take_profit: float | None = None
    sector: str = "Unknown"


class Trade(BaseModel):
    ticker: str
    quantity: float
    entry_price: float
    exit_price: float | None = None
    realized_pnl: float = 0
    opened_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: datetime | None = None
