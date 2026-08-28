"""R5: repurchase within 30 days of a realized loss on the same security."""

from __future__ import annotations

from orderguard.schemas.account_state import AccountState
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import RuleResult, Severity


class WashSaleRule:
    """Fails if a buy order in the basket would repurchase a symbol sold at a loss within 30 days."""

    id = "R5"
    severity = Severity.WARNING

    def check(self, plan: OrderPlan, state: AccountState) -> RuleResult:
        raise NotImplementedError
