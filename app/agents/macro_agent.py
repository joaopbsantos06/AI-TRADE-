from app.agents.base_agent import BaseAgent
from app.data.models import MacroOutput, Signal


class MacroAnalyst(BaseAgent):
    name = "macro"
    role = "Macro Analyst"
    description = "Pluggable macro-regime assessment."

    def analyse(self, ticker, data):
        if not data:
            return MacroOutput(
                agent=self.name,
                ticker=ticker,
                signal=Signal.INSUFFICIENT_DATA,
                confidence=0,
                reasoning=["No macro data provided."],
                status="INSUFFICIENT_DATA",
            )
        return MacroOutput(
            agent=self.name,
            ticker=ticker,
            signal=Signal.HOLD,
            confidence=0.55,
            macro_regime=data["regime"],
            risk_environment=data["risk_environment"],
            relevant_factors=data["factors"],
            affected_assets=[ticker],
            reasoning=[
                "Mock macro input is neutral and timestamped providers can replace it."
            ],
        )
