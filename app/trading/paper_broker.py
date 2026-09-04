from abc import ABC, abstractmethod
from datetime import datetime, timezone
from app.data.models import OrderRequest, Position, Trade, Signal


class Broker(ABC):
    @abstractmethod
    def submit(self, order: OrderRequest): ...
class PaperBroker(Broker):
    """Only executable broker implementation. Performs simulated fills only."""

    def __init__(self, portfolio, settings):
        if not settings.paper_trading_only:
            raise RuntimeError("Real trading is unsupported and blocked.")
        self.portfolio = portfolio
        self.settings = settings
        self.trades = []
        self.portfolio.trades = self.trades
        self.orders = []

    def submit(self, order):
        if order.side not in (Signal.BUY, Signal.SELL):
            raise ValueError("Only BUY and SELL paper orders are supported.")
        fill = order.price * (
            1 + self.settings.slippage_rate
            if order.side == Signal.BUY
            else 1 - self.settings.slippage_rate
        )
        value = fill * order.quantity
        commission = value * self.settings.commission_rate
        if order.side == Signal.BUY:
            if value + commission > self.portfolio.cash:
                raise ValueError("Insufficient paper cash.")
            p = self.portfolio.positions.get(order.ticker)
            old_qty = p.quantity if p else 0
            avg = ((p.average_price * old_qty if p else 0) + value) / (
                old_qty + order.quantity
            )
            self.portfolio.positions[order.ticker] = Position(
                ticker=order.ticker,
                quantity=old_qty + order.quantity,
                average_price=avg,
                stop_loss=order.stop_loss,
                take_profit=order.take_profit,
            )
            self.portfolio.cash -= value + commission
        else:
            p = self.portfolio.positions.get(order.ticker)
            if not p or order.quantity > p.quantity:
                raise ValueError("Cannot sell more than the paper position.")
            pnl = (fill - p.average_price) * order.quantity - commission
            self.portfolio.cash += value - commission
            self.portfolio.realized_pnl += pnl
            p.quantity -= order.quantity
            if p.quantity == 0:
                del self.portfolio.positions[order.ticker]
            self.trades.append(
                Trade(
                    ticker=order.ticker,
                    quantity=order.quantity,
                    entry_price=p.average_price,
                    exit_price=fill,
                    realized_pnl=pnl,
                    closed_at=datetime.now(timezone.utc),
                )
            )
        self.orders.append(
            {
                "ticker": order.ticker,
                "side": order.side,
                "fill_price": fill,
                "quantity": order.quantity,
                "commission": commission,
                "status": "EXECUTED_PAPER",
            }
        )
        return self.orders[-1]

    def evaluate_exits(self, prices):
        for t, p in list(self.portfolio.positions.items()):
            price = prices.get(t)
            if price and (
                (p.stop_loss and price <= p.stop_loss)
                or (p.take_profit and price >= p.take_profit)
            ):
                self.submit(
                    OrderRequest(
                        ticker=t, side=Signal.SELL, quantity=p.quantity, price=price
                    )
                )
