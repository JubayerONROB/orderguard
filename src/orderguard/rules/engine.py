"""Runs all registered rules (R1-R7) over a basket and aggregates them into a RiskReport.

This module contains no rule logic itself -- it only orchestrates: collect each
`Rule.check()` result, and derive the overall `Decision` from their `passed`/`severity`
combination. Individual rule modules stay independently testable and swappable.
"""

from __future__ import annotations

from orderguard.rules.base import Rule
from orderguard.schemas.account_state import AccountState
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import RiskReport


class RuleEngine:
    """Aggregates a fixed set of `Rule` instances into one `RiskReport` per basket."""

    def __init__(self, rules: tuple[Rule, ...]) -> None:
        self._rules = rules

    def evaluate(self, plan: OrderPlan, state: AccountState) -> RiskReport:
        """Runs every rule against `plan`/`state` and returns the aggregated RiskReport.

        Raises:
            NotImplementedError: business logic not yet implemented.
        """
        raise NotImplementedError
