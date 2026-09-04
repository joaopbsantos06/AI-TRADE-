"""Deterministic fictional development fixtures, never live market data."""

from datetime import datetime, timedelta, timezone
import numpy as np
from app.data.models import Candle, FundamentalData

ASSETS = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "NVDA": "Technology",
    "SPY": "Index",
    "QQQ": "Index",
}


def candles(ticker: str, periods: int = 90) -> list[Candle]:
    if ticker.upper() not in ASSETS:
        raise ValueError(f"Unknown mock ticker: {ticker}")
    seed = sum(map(ord, ticker.upper()))
    rng = np.random.default_rng(seed)
    base = 80 + (seed % 90)
    trend = 0.25 + (seed % 5) * 0.03
    closes = (
        base + np.arange(periods) * trend + rng.normal(0, 1.2, periods).cumsum() * 0.15
    )
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [
        Candle(
            timestamp=now + timedelta(days=i),
            open=float(c - 0.3),
            high=float(c + 0.8),
            low=float(c - 0.9),
            close=float(c),
            volume=float(1_000_000 + rng.integers(0, 300_000)),
        )
        for i, c in enumerate(closes)
    ]


def fundamentals(ticker: str) -> FundamentalData | None:
    if ticker.upper() not in ASSETS:
        return None
    return FundamentalData(
        ticker=ticker.upper(),
        revenue_growth=0.12,
        earnings_growth=0.14,
        eps=5.2,
        pe=24,
        forward_pe=21,
        ps=6,
        debt_to_equity=0.7,
        free_cash_flow=9_000_000_000,
        net_margin=0.22,
        roe=0.28,
        roic=0.19,
    )


def news(ticker: str) -> list[dict]:
    return [
        {
            "headline": f"{ticker.upper()} mock development update",
            "sentiment": "neutral",
            "importance": "medium",
        }
    ]


def macro() -> dict:
    return {
        "regime": "disinflationary expansion",
        "risk_environment": "neutral",
        "factors": [
            "Mock data only; replace with timestamped economic provider before production research."
        ],
    }
