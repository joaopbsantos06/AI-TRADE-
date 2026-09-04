from app.agents.base_agent import BaseAgent
from app.analysis.technical_indicators import calculate
from app.data.models import Signal, TechnicalOutput


class TechnicalAnalyst(BaseAgent):
    name = "technical"
    role = "Technical Analyst"
    description = "Deterministic price/volume analysis."

    def analyse(self, ticker, candles):
        ind = calculate(candles)
        if not ind:
            return TechnicalOutput(
                agent=self.name,
                ticker=ticker,
                signal=Signal.INSUFFICIENT_DATA,
                confidence=0,
                reasoning=["At least 30 candles are required."],
                status="INSUFFICIENT_DATA",
            )
        price = candles[-1].close
        bullish = price > ind["sma_20"] and ind["macd"] > 0
        signal = Signal.BUY if bullish else Signal.HOLD
        atr = ind["atr_14"]
        stop = price - 2 * atr
        take = price + 4 * atr
        return TechnicalOutput(
            agent=self.name,
            ticker=ticker,
            signal=signal,
            confidence=0.72 if bullish else 0.45,
            reasoning=[
                "Price is above/below 20-period SMA based on deterministic mock candles.",
                "MACD direction is included in the score.",
            ],
            trend="uptrend" if bullish else "range/downtrend",
            entry=price,
            stop_loss=stop,
            take_profit=take,
            risk_reward=2.0,
            indicators=ind,
            invalidation_conditions=["Close below proposed stop loss."],
        )
