from app.data.models import OrderRequest, Signal


def decision_order(decision):
    if decision.action != Signal.BUY or not decision.entry:
        return None
    return OrderRequest(
        ticker=decision.ticker,
        side=Signal.BUY,
        quantity=decision.position_size,
        price=decision.entry,
        stop_loss=decision.stop_loss,
        take_profit=decision.take_profit,
    )
