from fastapi import APIRouter, HTTPException
from app.orchestration.pipeline import Pipeline
from app.data.models import Signal

router = APIRouter()
pipeline = Pipeline()


@router.get("/health")
def health():
    return {"status": "ok", "paper_trading_only": True}


@router.get("/agents")
def agents():
    return [
        {"name": x, "mode": "deterministic/mock"}
        for x in ["technical", "fundamental", "news", "macro", "risk", "portfolio"]
    ]


@router.post("/pipeline/{ticker}")
def run(ticker: str):
    try:
        return pipeline.run(ticker)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post("/analysis/{ticker}")
def analysis(ticker: str):
    try:
        return pipeline.run(ticker, execute=False)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/portfolio")
def portfolio():
    return {
        "cash": pipeline.portfolio.cash,
        "equity": pipeline.portfolio.equity(),
        "paper_trading_only": True,
    }


@router.get("/positions")
def positions():
    return list(pipeline.portfolio.positions.values())


@router.get("/trades")
def trades():
    return pipeline.broker.trades


@router.get("/performance")
def performance():
    return {
        "realized_pnl": pipeline.portfolio.realized_pnl,
        "number_of_paper_orders": len(pipeline.broker.orders),
    }


@router.get("/decisions")
def decisions():
    from app.database.repositories import decisions

    s = pipeline.Session()
    rows = decisions(s)
    s.close()
    return [
        {
            "run_id": r.run_id,
            "ticker": r.ticker,
            "action": r.action,
            "score": r.score,
            "created_at": r.created_at,
        }
        for r in rows
    ]
