from app.agents.base_agent import BaseAgent
from app.data.models import Signal, FundamentalOutput


class FundamentalAnalyst(BaseAgent):
    name = "fundamental"
    role = "Fundamental Analyst"
    description = "Rule-based fundamental quality assessment."

    def analyse(self, ticker, data):
        required = (
            [
                data.revenue_growth,
                data.earnings_growth,
                data.pe,
                data.net_margin,
                data.roe,
            ]
            if data
            else []
        )
        if not data or any(v is None for v in required):
            return FundamentalOutput(
                agent=self.name,
                ticker=ticker,
                signal=Signal.INSUFFICIENT_DATA,
                confidence=0,
                reasoning=["Required fundamental fields are unavailable."],
                status="INSUFFICIENT_DATA",
            )
        good = (
            data.revenue_growth > 0
            and data.earnings_growth > 0
            and data.net_margin > 0
            and data.roe > 0
        )
        return FundamentalOutput(
            agent=self.name,
            ticker=ticker,
            signal=Signal.BUY if good else Signal.HOLD,
            confidence=0.70 if good else 0.4,
            reasoning=["Assessment uses supplied metrics only."],
            valuation_view=(
                "reasonable"
                if data.forward_pe and data.forward_pe < data.pe
                else "unknown"
            ),
            business_quality="high" if data.roe > 0.15 else "moderate",
            growth_quality="positive" if data.revenue_growth > 0 else "negative",
            financial_health=(
                "sound"
                if data.debt_to_equity is not None and data.debt_to_equity < 1
                else "unknown"
            ),
            bull_case=["Positive revenue and earnings growth."],
            bear_case=[
                "Valuation and supplied mock inputs require external verification."
            ],
        )
