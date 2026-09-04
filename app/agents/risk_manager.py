from app.agents.base_agent import BaseAgent
from app.data.models import RiskOutput, RiskAction, Signal


class RiskManager(BaseAgent):
    name = "risk"
    role = "Risk Manager"
    description = "Guardrail-only proposal validation; never seeks opportunities."

    def __init__(self, settings):
        self.settings = settings

    def analyse(
        self,
        ticker,
        technical,
        portfolio,
        proposed_size,
        sector="Unknown",
        drawdown=0.0,
    ):
        reasons = []
        if (
            technical.signal == Signal.INSUFFICIENT_DATA
            or not technical.entry
            or not technical.stop_loss
        ):
            return RiskOutput(
                agent=self.name,
                ticker=ticker,
                signal=Signal.HOLD,
                confidence=1,
                action=RiskAction.REQUEST_MORE_DATA,
                reasoning=["Technical entry/stop missing."],
                reasons=["Insufficient data."],
            )
        if drawdown >= self.settings.max_drawdown:
            return RiskOutput(
                agent=self.name,
                ticker=ticker,
                signal=Signal.HOLD,
                confidence=1,
                action=RiskAction.REJECT,
                reasoning=["Drawdown limit breached."],
                reasons=["Maximum drawdown breached."],
            )
        equity = portfolio.equity()
        max_notional = equity * self.settings.max_position_size
        requested = proposed_size * technical.entry
        risk = (technical.entry - technical.stop_loss) * proposed_size
        if (
            technical.risk_reward is None
            or technical.risk_reward < self.settings.min_risk_reward
        ):
            reasons.append("Risk/reward below configured minimum.")
        if risk > equity * self.settings.max_portfolio_risk:
            reasons.append("Risk per trade exceeds configured maximum.")
        if (
            len(portfolio.positions) >= self.settings.max_open_positions
            and ticker not in portfolio.positions
        ):
            reasons.append("Maximum open positions reached.")
        if reasons:
            return RiskOutput(
                agent=self.name,
                ticker=ticker,
                signal=Signal.HOLD,
                confidence=0.95,
                action=RiskAction.REJECT,
                reasoning=reasons,
                reasons=reasons,
            )
        approved = min(proposed_size, max_notional / technical.entry)
        action = (
            RiskAction.REDUCE_SIZE if approved < proposed_size else RiskAction.APPROVE
        )
        return RiskOutput(
            agent=self.name,
            ticker=ticker,
            signal=Signal.BUY,
            confidence=0.9,
            action=action,
            approved_size=approved,
            risk_amount=(technical.entry - technical.stop_loss) * approved,
            reasoning=["Proposal meets configured paper-risk limits."],
            reasons=[],
        )
