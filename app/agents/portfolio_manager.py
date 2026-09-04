from app.agents.base_agent import BaseAgent
from app.data.models import Decision, Signal, RiskAction


class PortfolioManager(BaseAgent):
    name = "portfolio"
    role = "Portfolio Manager"
    description = "Configurable weighted score combiner, not a vote counter."

    def __init__(self, settings):
        self.settings = settings

    def analyse(self, technical, fundamental, news, macro, risk):
        outputs = [technical, fundamental, news, macro]
        if any(x.signal == Signal.INSUFFICIENT_DATA for x in outputs):
            return Decision(
                ticker=technical.ticker,
                action=Signal.HOLD,
                thesis="INSUFFICIENT_DATA",
                reasons=["One or more required analyses lack data."],
            )
        if risk.action not in (RiskAction.APPROVE, RiskAction.REDUCE_SIZE):
            return Decision(
                ticker=technical.ticker,
                action=Signal.HOLD,
                thesis="Risk manager did not approve execution.",
                reasons=risk.reasons,
            )

        def v(x):
            return 1 if x.signal == Signal.BUY else -1 if x.signal == Signal.SELL else 0

        score = (
            sum(
                v(x) * x.confidence * w
                for x, w in zip(
                    outputs,
                    [
                        self.settings.technical_weight,
                        self.settings.fundamental_weight,
                        self.settings.news_weight,
                        self.settings.macro_weight,
                    ],
                )
            )
            + risk.confidence * self.settings.risk_weight
        )
        action = (
            Signal.BUY
            if score >= 0.35 and technical.signal == Signal.BUY
            else Signal.HOLD
        )
        entry = technical.entry if action == Signal.BUY else None
        stop = technical.stop_loss if action == Signal.BUY else None
        take = technical.take_profit if action == Signal.BUY else None
        return Decision(
            ticker=technical.ticker,
            action=action,
            position_size=risk.approved_size if action == Signal.BUY else 0,
            entry=entry,
            stop_loss=stop,
            take_profit=take,
            expected_risk=(entry - stop) * risk.approved_size if entry and stop else 0,
            expected_reward=(
                (take - entry) * risk.approved_size if entry and take else 0
            ),
            confidence=min(max(score, 0), 1),
            score=score,
            thesis="Weighted, confidence-adjusted evidence score with a mandatory risk gate.",
            reasons=[
                "Weights are configurable; agent count alone does not determine action."
            ],
            risks=["Mock data must not be treated as live research."],
            invalidation_conditions=technical.invalidation_conditions,
        )
