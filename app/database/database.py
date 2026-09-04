from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Float, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.config.settings import get_settings


class Base(DeclarativeBase):
    pass


class DecisionRecord(Base):
    __tablename__ = "decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(40), index=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    action: Mapped[str] = mapped_column(String(24))
    score: Mapped[float] = mapped_column(Float)
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(40), index=True)
    event: Mapped[str] = mapped_column(String(80))
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


def engine(url=None):
    return create_engine(
        url or get_settings().database_url,
        connect_args=(
            {"check_same_thread": False}
            if (url or get_settings().database_url).startswith("sqlite")
            else {}
        ),
    )


def init_database(url=None):
    e = engine(url)
    Base.metadata.create_all(e)
    return sessionmaker(bind=e, expire_on_commit=False)


# Extensible research ledger tables. Payload JSON preserves provider-specific fields without secrets.
class AssetRecord(Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True)
    sector: Mapped[str] = mapped_column(String(80), default="Unknown")


class MarketDataRecord(Base):
    __tablename__ = "market_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    payload: Mapped[str] = mapped_column(Text)


class AgentAnalysisRecord(Base):
    __tablename__ = "agent_analyses"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(40), index=True)
    agent: Mapped[str] = mapped_column(String(40))
    confidence: Mapped[float] = mapped_column(Float)
    payload: Mapped[str] = mapped_column(Text)


class OrderRecord(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(40), index=True)
    ticker: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(40))
    payload: Mapped[str] = mapped_column(Text)


class PositionRecord(Base):
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    quantity: Mapped[float] = mapped_column(Float)
    payload: Mapped[str] = mapped_column(Text)


class PortfolioSnapshotRecord(Base):
    __tablename__ = "portfolio_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(40), index=True)
    equity: Mapped[float] = mapped_column(Float)
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class TradeRecord(Base):
    __tablename__ = "trades"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    realized_pnl: Mapped[float] = mapped_column(Float)
    payload: Mapped[str] = mapped_column(Text)


class PerformanceMetricRecord(Base):
    __tablename__ = "performance_metrics"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(String(40), index=True)
    payload: Mapped[str] = mapped_column(Text)
