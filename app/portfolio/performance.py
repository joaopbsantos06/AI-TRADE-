import numpy as np


def metrics(equity_history: list[float], trades: list):
    if not equity_history:
        return {}
    arr = np.array(equity_history, float)
    returns = np.diff(arr) / arr[:-1] if len(arr) > 1 else np.array([])
    peak = np.maximum.accumulate(arr)
    dd = (arr - peak) / peak
    wins = [t.realized_pnl for t in trades if t.realized_pnl > 0]
    losses = [t.realized_pnl for t in trades if t.realized_pnl < 0]
    return {
        "total_return": float(arr[-1] / arr[0] - 1),
        "daily_return": float(returns[-1]) if len(returns) else 0.0,
        "annualized_return": float(
            (arr[-1] / arr[0]) ** (252 / max(len(arr) - 1, 1)) - 1
        ),
        "win_rate": len(wins) / max(len(wins) + len(losses), 1),
        "average_win": float(np.mean(wins)) if wins else 0.0,
        "average_loss": float(np.mean(losses)) if losses else 0.0,
        "profit_factor": sum(wins) / abs(sum(losses)) if losses else 0.0,
        "maximum_drawdown": float(abs(dd.min())),
        "sharpe_ratio": (
            float(returns.mean() / returns.std() * np.sqrt(252))
            if len(returns) > 1 and returns.std() > 0
            else 0.0
        ),
        "volatility": float(returns.std() * np.sqrt(252)) if len(returns) > 1 else 0.0,
        "number_of_trades": len(trades),
        "average_holding_period": 0.0,
    }
