import argparse, json, pytest
from app.orchestration.pipeline import Pipeline

p = argparse.ArgumentParser()
p.add_argument(
    "command",
    choices=["analyze", "pipeline", "portfolio", "performance", "trades", "test"],
)
p.add_argument("ticker", nargs="?")
args = p.parse_args()
if args.command == "test":
    raise SystemExit(pytest.main(["-q"]))
pipe = Pipeline()
if args.command in ("analyze", "pipeline"):
    if not args.ticker:
        p.error("ticker is required")
    result = pipe.run(args.ticker, execute=args.command == "pipeline")
    print(
        json.dumps(
            result,
            default=lambda x: (
                x.model_dump(mode="json") if hasattr(x, "model_dump") else str(x)
            ),
            indent=2,
        )
    )
elif args.command == "portfolio":
    print(
        json.dumps(
            {"cash": pipe.portfolio.cash, "equity": pipe.portfolio.equity()}, indent=2
        )
    )
elif args.command == "performance":
    print(json.dumps({"realized_pnl": pipe.portfolio.realized_pnl}, indent=2))
else:
    print(json.dumps(pipe.broker.trades, default=str, indent=2))
