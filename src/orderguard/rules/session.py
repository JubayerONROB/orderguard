"""R6: market clock, extended-hours eligibility, and order-type validity for the session."""

from __future__ import annotations

from orderguard.schemas.account_state import AccountState
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import RuleResult, Severity


class SessionRule:
    """Fails if an order's type/extended-hours flag is invalid for the current market session."""

    id = "R6"
    severity = Severity.BLOCKING

    def check(self, plan: OrderPlan, state: AccountState) -> RuleResult:
        raise NotImplementedError
