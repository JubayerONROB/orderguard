"""R2: day trades this basket creates, plus existing count, vs the $25k PDT equity rule."""

from __future__ import annotations

from orderguard.schemas.account_state import AccountState
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import RuleResult, Severity


class PdtRule:
    """Fails if the basket would push a sub-$25k account over 3 day trades in 5 days."""

    id = "R2"
    severity = Severity.BLOCKING

    def check(self, plan: OrderPlan, state: AccountState) -> RuleResult:
        raise NotImplementedError
