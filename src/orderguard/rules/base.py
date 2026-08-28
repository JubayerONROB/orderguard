"""The `Rule` protocol every rule module (R1-R7) implements.

A rule always sees the *whole* basket, not one order at a time -- R1 (buying_power),
R2 (pdt), R3 (concentration), and R4 (open_orders) are only meaningful at that
granularity, and giving every rule the same signature keeps `engine.py` uniform.
"""

from __future__ import annotations

from typing import Protocol

from orderguard.schemas.account_state import AccountState
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import RuleResult, Severity


class Rule(Protocol):
    """A single deterministic risk check, evaluated over an entire OrderPlan."""

    id: str
    """e.g. "R1"."""
    severity: Severity

    def check(self, plan: OrderPlan, state: AccountState) -> RuleResult:
        """Evaluates this rule against the full basket and current account state.

        Must be pure and deterministic: same `plan`/`state` in, same `RuleResult` out.
        """
        ...
