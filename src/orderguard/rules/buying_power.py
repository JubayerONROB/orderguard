"""R1: basket notional, summed across all orders, vs available buying power."""

from __future__ import annotations

from orderguard.schemas.account_state import AccountState
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import RuleResult, Severity


class BuyingPowerRule:
    """Fails if the summed notional of buy orders in the basket exceeds buying power."""

    id = "R1"
    severity = Severity.BLOCKING

    def check(self, plan: OrderPlan, state: AccountState) -> RuleResult:
        raise NotImplementedError
