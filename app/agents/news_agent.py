from app.agents.base_agent import BaseAgent
from app.data.models import NewsOutput, Signal


class NewsAnalyst(BaseAgent):
    name = "news"
    role = "News Analyst"
    description = "Pluggable news-provider sentiment interpretation."

    def analyse(self, ticker, items):
        if not items:
            return NewsOutput(
                agent=self.name,
                ticker=ticker,
                signal=Signal.INSUFFICIENT_DATA,
                confidence=0,
                reasoning=["No news items provided."],
                status="INSUFFICIENT_DATA",
            )
        sentiment = items[0].get("sentiment", "neutral")
        sig = {"bullish": Signal.BUY, "bearish": Signal.SELL}.get(
            sentiment, Signal.HOLD
        )
        return NewsOutput(
            agent=self.name,
            ticker=ticker,
            signal=sig,
            confidence=0.55,
            sentiment=sentiment,
            event_importance=items[0].get("importance", "low"),
            affected_assets=[ticker],
            reasoning=["Mock news provider output; not a live news claim."],
        )
