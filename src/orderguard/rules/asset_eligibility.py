"""R7: tradable, fractionable, and shortable flags for every symbol in the basket."""

from __future__ import annotations

from orderguard.schemas.account_state import AccountState
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import RuleResult, Severity


class AssetEligibilityRule:
    """Fails if an order requires a flag (tradable/fractionable/shortable) the asset lacks."""

    id = "R7"
    severity = Severity.BLOCKING

    def check(self, plan: OrderPlan, state: AccountState) -> RuleResult:
        raise NotImplementedError
