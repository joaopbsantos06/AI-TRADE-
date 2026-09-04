from app.data.models import Position


class Portfolio:
    def __init__(self, cash=10000):
        self.cash = cash
        self.initial_capital = cash
        self.positions: dict[str, Position] = {}
        self.realized_pnl = 0

    def market_value(self, prices: dict[str, float] | None = None):
        return sum(
            p.quantity * (prices or {}).get(t, p.average_price)
            for t, p in self.positions.items()
        )

    def equity(self, prices=None):
        return self.cash + self.market_value(prices)
