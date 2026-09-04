# AI Multi-Agent Financial Analysis & Paper Trading

> **Experimental research software. It uses paper trading only and never sends real orders, connects to brokers, accesses real money, or accepts brokerage credentials.**

## Purpose
A modular, auditable research pipeline evaluates deterministic technical, fundamental, news, macro, risk, and portfolio signals. Its aim is to compare recorded signals with later outcomes—not to promise returns.

## Architecture
`mock market data → technical + fundamental → news → macro → risk gate → weighted portfolio decision → PaperBroker → SQLite audit/decision record → performance`

All development inputs are explicitly **MOCK DATA**, deterministic, and fictional—not current prices or investment advice. Providers, the `LLMProvider` protocol, and `BacktestRunner` are extension points for future timestamp-bounded real/historical sources.

## Setup

For exact Windows PowerShell commands, see [SETUP_WINDOWS.md](SETUP_WINDOWS.md).

Python 3.11+ is required. This repository deliberately uses `requirements.txt`: it is a compact, broadly compatible dependency manifest for this small FastAPI application.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # optional; never add secrets
pytest -q
```

`PAPER_TRADING_ONLY=true` is mandatory. Setting it false fails at configuration load. `.env.example` has empty API-key fields and no credentials.

## Run
```bash
python -m app analyze AAPL       # analyses only, no simulated fill
python -m app pipeline AAPL      # may submit a simulated PaperBroker order
python -m app portfolio
python -m app performance
python -m app trades
python -m app test
uvicorn app.main:app --reload
```

API: `GET /health`, `/portfolio`, `/positions`, `/trades`, `/performance`, `/decisions`, `/agents`; `POST /analysis/{ticker}` and `POST /pipeline/{ticker}`. There is no real-trading endpoint.

## Risk and decision controls
`RiskManager` is a mandatory gate: it rejects insufficient data, drawdown, risk/reward, per-trade-risk, and open-position breaches. It can approve, reject, reduce size, or request more data. `PortfolioManager` uses configurable confidence-weighted evidence (`technical`, `fundamental`, `news`, `macro`, `risk`) rather than counting BUY votes; it holds whenever inputs are insufficient or risk is unapproved.

## Persistence and audit
SQLite is created at `DATABASE_URL` (default `data/ai_trade.db`). Each pipeline writes a unique `RUN-YYYY-...` decision JSON and structured audit event. The schema is intentionally lean in v1 and can be extended with assets, candles, snapshots, trades, and outcome labels as real providers are introduced.

## Project map
- `app/agents`: structured Pydantic agents and mandatory risk/portfolio stages.
- `app/data`, `app/analysis`: provider protocol, deterministic mock fixtures, indicators.
- `app/trading`: abstract broker boundary and only `PaperBroker` implementation.
- `app/database`, `app/orchestration`, `app/api`: SQLite audit, pipeline, FastAPI.
- `app/backtesting`, `app/llm`: safe future extension interfaces.

## Limitations / next steps
No live market/fundamental/news/macro feed, LLM, dashboard, broker, real execution, or production-grade backtest is included. Before research results are relied upon, implement timestamped sources, outcome labelling, additional persistence tables, correlation/sector calculation from verified classifications, and walk-forward backtests that pass only data available at each timestamp.
