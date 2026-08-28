"""R3: resulting position weight vs the user's cap, evaluated against post-trade equity."""

from __future__ import annotations

from orderguard.schemas.account_state import AccountState
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import RuleResult, Severity


class ConcentrationRule:
    """Fails if any resulting position would exceed the configured max weight of equity."""

    id = "R3"
    severity = Severity.BLOCKING

    def check(self, plan: OrderPlan, state: AccountState) -> RuleResult:
        raise NotImplementedError
