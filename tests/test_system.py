import pytest
from app.config.settings import Settings
from app.data.mock_data import candles, fundamentals
from app.agents.technical_agent import TechnicalAnalyst
from app.agents.fundamental_agent import FundamentalAnalyst
from app.agents.risk_manager import RiskManager
from app.portfolio.portfolio import Portfolio
from app.trading.paper_broker import PaperBroker
from app.data.models import OrderRequest, Signal, RiskAction
from app.orchestration.pipeline import Pipeline


def settings():
    return Settings(database_url="sqlite:///:memory:")


def test_technical_and_insufficient_data():
    assert TechnicalAnalyst().analyse("AAPL", candles("AAPL")).entry is not None
    assert (
        TechnicalAnalyst().analyse("AAPL", candles("AAPL", 10)).signal
        == Signal.INSUFFICIENT_DATA
    )


def test_fundamentals():
    assert (
        FundamentalAnalyst().analyse("AAPL", fundamentals("AAPL")).signal == Signal.BUY
    )


def test_invalid_stop():
    with pytest.raises(ValueError):
        OrderRequest(ticker="AAPL", side=Signal.BUY, quantity=1, price=10, stop_loss=11)


def test_paper_buy_sell_pnl():
    p = Portfolio(1000)
    b = PaperBroker(p, settings())
    b.submit(
        OrderRequest(
            ticker="AAPL", side=Signal.BUY, quantity=2, price=100, stop_loss=90
        )
    )
    b.submit(OrderRequest(ticker="AAPL", side=Signal.SELL, quantity=2, price=110))
    assert b.trades[0].realized_pnl > 0 and not p.positions


def test_paper_cash_guard():
    with pytest.raises(ValueError):
        PaperBroker(Portfolio(10), settings()).submit(
            OrderRequest(ticker="AAPL", side=Signal.BUY, quantity=1, price=100)
        )


def test_risk_rejects_low_rr():
    s = settings()
    t = TechnicalAnalyst().analyse("AAPL", candles("AAPL"))
    t.risk_reward = 1
    assert RiskManager(s).analyse("AAPL", t, Portfolio(), 1).action == RiskAction.REJECT


def test_pipeline_persists_and_executes():
    r = Pipeline(settings(), database_url="sqlite:///:memory:").run("AAPL")
    assert r["decision"].run_id and r["execution"]["status"] == "EXECUTED_PAPER"


def test_invalid_ticker():
    with pytest.raises(ValueError):
        Pipeline(settings(), database_url="sqlite:///:memory:").run("BAD")


def test_unsafe_config_fails():
    with pytest.raises(ValueError):
        Settings(paper_trading_only=False)


def test_pipeline_persists_decision_order_position_and_performance():
    from app.database.database import (
        DecisionRecord,
        OrderRecord,
        PerformanceMetricRecord,
        PositionRecord,
    )

    system = Pipeline(settings(), database_url="sqlite:///:memory:")
    result = system.run("AAPL")
    session = system.Session()
    try:
        assert (
            session.query(DecisionRecord).filter_by(run_id=result["run_id"]).count()
            == 1
        )
        assert (
            session.query(OrderRecord).filter_by(run_id=result["run_id"]).count() == 1
        )
        assert session.query(PositionRecord).filter_by(ticker="AAPL").count() == 1
        assert (
            session.query(PerformanceMetricRecord)
            .filter_by(run_id=result["run_id"])
            .count()
            == 1
        )
    finally:
        session.close()


def test_paper_trade_realized_pnl_is_recorded_on_portfolio():
    portfolio = Portfolio(1000)
    broker = PaperBroker(portfolio, settings())
    broker.submit(OrderRequest(ticker="AAPL", side=Signal.BUY, quantity=2, price=100))
    broker.submit(OrderRequest(ticker="AAPL", side=Signal.SELL, quantity=2, price=110))
    assert portfolio.realized_pnl > 0
    assert portfolio.trades[0].realized_pnl > 0
