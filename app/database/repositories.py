"""Persistence helpers for the paper-research audit trail."""

import json
from typing import Any

from app.database.database import (
    AgentAnalysisRecord,
    AuditLog,
    DecisionRecord,
    OrderRecord,
    PerformanceMetricRecord,
    PortfolioSnapshotRecord,
    PositionRecord,
    TradeRecord,
)


def _payload(value: Any) -> str:
    """Serialize structured data without logging environment variables or secrets."""
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, default=str)


def save_decision(session, decision) -> None:
    session.add(
        DecisionRecord(
            run_id=decision.run_id or "",
            ticker=decision.ticker,
            action=decision.action.value,
            score=decision.score,
            payload=decision.model_dump_json(),
        )
    )
    session.commit()


def save_pipeline_records(
    session, run_id: str, outputs: dict, execution, portfolio, performance
) -> None:
    """Record all observable results from a completed pipeline run."""
    for agent, output in outputs.items():
        session.add(
            AgentAnalysisRecord(
                run_id=run_id,
                agent=agent,
                confidence=output.confidence,
                payload=_payload(output),
            )
        )
    if execution:
        session.add(
            OrderRecord(
                run_id=run_id,
                ticker=execution["ticker"],
                status=execution["status"],
                payload=_payload(execution),
            )
        )
    for position in portfolio.positions.values():
        session.add(
            PositionRecord(
                ticker=position.ticker,
                quantity=position.quantity,
                payload=_payload(position),
            )
        )
    for trade in getattr(portfolio, "trades", []):
        session.add(
            TradeRecord(
                ticker=trade.ticker,
                realized_pnl=trade.realized_pnl,
                payload=_payload(trade),
            )
        )
    session.add(
        PortfolioSnapshotRecord(
            run_id=run_id,
            equity=portfolio.equity(),
            payload=_payload(
                {"cash": portfolio.cash, "realized_pnl": portfolio.realized_pnl}
            ),
        )
    )
    session.add(PerformanceMetricRecord(run_id=run_id, payload=_payload(performance)))
    session.commit()


def audit(session, run_id: str, event: str, payload: dict) -> None:
    session.add(AuditLog(run_id=run_id, event=event, payload=_payload(payload)))
    session.commit()


def decisions(session):
    return list(session.query(DecisionRecord).order_by(DecisionRecord.id.desc()).all())
