from typing import Protocol
from app.data.models import Candle, FundamentalData
from app.data import mock_data


class MarketDataProvider(Protocol):
    def get_candles(self, ticker: str) -> list[Candle]: ...
    def get_fundamentals(self, ticker: str) -> FundamentalData | None: ...
class MockMarketDataProvider:
    def get_candles(self, ticker: str) -> list[Candle]:
        return mock_data.candles(ticker)

    def get_fundamentals(self, ticker: str) -> FundamentalData | None:
        return mock_data.fundamentals(ticker)
