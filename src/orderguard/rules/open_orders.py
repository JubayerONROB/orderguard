"""R4: conflicts and stacking between the basket and existing unfilled orders on the account."""

from __future__ import annotations

from orderguard.schemas.account_state import AccountState
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import RuleResult, Severity


class OpenOrdersRule:
    """Fails if the basket conflicts with (or double-stacks) an existing open order on a symbol."""

    id = "R4"
    severity = Severity.BLOCKING

    def check(self, plan: OrderPlan, state: AccountState) -> RuleResult:
        raise NotImplementedError
