"""Auditable orchestration for deterministic mock-data paper-trading research."""

from datetime import datetime
from uuid import uuid4

from app.agents.fundamental_agent import FundamentalAnalyst
from app.agents.macro_agent import MacroAnalyst
from app.agents.news_agent import NewsAnalyst
from app.agents.portfolio_manager import PortfolioManager
from app.agents.risk_manager import RiskManager
from app.agents.technical_agent import TechnicalAnalyst
from app.config.settings import get_settings
from app.data import mock_data
from app.data.market_data import MockMarketDataProvider
from app.database.database import init_database
from app.database.repositories import audit, save_decision, save_pipeline_records
from app.portfolio.performance import metrics
from app.portfolio.portfolio import Portfolio
from app.trading.order_manager import decision_order
from app.trading.paper_broker import PaperBroker


class Pipeline:
    def __init__(self, settings=None, database_url=None):
        self.settings = settings or get_settings()
        self.provider = MockMarketDataProvider()
        self.portfolio = Portfolio(self.settings.initial_capital)
        self.broker = PaperBroker(self.portfolio, self.settings)
        self.Session = init_database(database_url)

    def run(self, ticker: str, execute: bool = True) -> dict:
        ticker = ticker.upper()
        run_id = f"RUN-{datetime.utcnow().year}-{uuid4().hex[:8].upper()}"
        session = self.Session()
        try:
            candles = self.provider.get_candles(ticker)
            technical = TechnicalAnalyst().analyse(ticker, candles)
            fundamental = FundamentalAnalyst().analyse(
                ticker, self.provider.get_fundamentals(ticker)
            )
            news = NewsAnalyst().analyse(ticker, mock_data.news(ticker))
            macro = MacroAnalyst().analyse(ticker, mock_data.macro())
            requested_size = (
                self.portfolio.equity()
                * self.settings.max_position_size
                / (technical.entry or 1)
            )
            risk = RiskManager(self.settings).analyse(
                ticker,
                technical,
                self.portfolio,
                requested_size,
                mock_data.ASSETS[ticker],
            )
            decision = PortfolioManager(self.settings).analyse(
                technical, fundamental, news, macro, risk
            )
            decision.run_id = run_id
            order = decision_order(decision)
            execution = self.broker.submit(order) if execute and order else None
            performance = metrics(
                [
                    self.portfolio.initial_capital,
                    self.portfolio.equity({ticker: candles[-1].close}),
                ],
                self.broker.trades,
            )
            outputs = {
                "technical": technical,
                "fundamental": fundamental,
                "news": news,
                "macro": macro,
                "risk": risk,
            }
            save_decision(session, decision)
            save_pipeline_records(
                session, run_id, outputs, execution, self.portfolio, performance
            )
            audit(
                session,
                run_id,
                "pipeline_completed",
                {
                    "ticker": ticker,
                    "decision": decision.action.value,
                    "execution": execution,
                },
            )
            return {
                "run_id": run_id,
                **outputs,
                "decision": decision,
                "execution": execution,
                "performance": performance,
            }
        except Exception as exc:
            audit(
                session, run_id, "pipeline_error", {"ticker": ticker, "error": str(exc)}
            )
            raise
        finally:
            session.close()
