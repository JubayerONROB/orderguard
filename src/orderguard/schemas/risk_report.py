"""The rule engine's output: a per-rule verdict on a basket, plus the trader-facing decision.

`RiskReport` is what the approval UI renders. `explanation` on each `RuleResult` is not a
debug string -- it is read by the trader before they approve real (paper) orders, so every
rule implementation must name the specific value that triggered or cleared it (e.g. "NVDA
would be 18.4% of post-trade equity, cap is 15%"), not a generic pass/fail label.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from orderguard.schemas.order_plan import Order


class Severity(str, Enum):
    """How serious a rule failure is."""

    INFO = "info"
    """Worth surfacing to the trader but never blocks or triggers a repair."""
    WARNING = "warning"
    """Allowed to proceed, but flagged -- e.g. a repair was applied."""
    BLOCKING = "blocking"
    """Cannot proceed without the trader changing the instruction; the repair agent may
    still attempt a fix, but if it fails to clear this rule the basket is BLOCKed."""


class Decision(str, Enum):
    """The overall, trader-facing verdict on a basket."""

    ALLOW = "allow"
    """Every rule passed on the original basket; nothing was repaired."""
    ALLOW_WITH_REPAIRS = "allow_with_repairs"
    """One or more rules initially failed; the repair agent produced a basket that
    now passes all rules. The trader approves the repaired basket, not the original."""
    BLOCK = "block"
    """One or more BLOCKING rules failed and no repair (or no successful repair
    attempt) resolved them. No order in this basket may be submitted."""


class RuleResult(BaseModel):
    """The outcome of one rule (R1-R7) evaluated against one basket."""

    model_config = ConfigDict(frozen=True)

    rule_id: str = Field(min_length=1)
    """e.g. "R1", "R3"."""
    rule_name: str = Field(min_length=1)
    """e.g. "buying_power", "concentration"."""
    passed: bool
    severity: Severity
    order_index: int | None = None
    """Index into the evaluated `OrderPlan.orders` for the offending order, if the
    failure is attributable to one order rather than the basket as a whole."""
    explanation: str = Field(min_length=1)
    """Human-readable, trader-facing string naming the specific value that triggered
    or cleared this rule. Required even when `passed` is True."""


class Repair(BaseModel):
    """One proposed change the repair agent made to a basket to clear a rule failure."""

    model_config = ConfigDict(frozen=True)

    rule_id: str = Field(min_length=1)
    """The rule that motivated this repair, e.g. "R3"."""
    order_index: int | None = None
    """Index into the repaired `OrderPlan.orders` for the affected order, if applicable."""
    description: str = Field(min_length=1)
    """Human-readable summary of what changed, e.g. "reduced NVDA qty from 120 to 96 to
    stay under the 15% concentration cap"."""
    original_order: Order | None = None
    """The order as it stood before this repair, if a specific order was changed."""
    repaired_order: Order | None = None
    """The order as it stands after this repair, if a specific order was changed."""


class RiskReport(BaseModel):
    """Full result of running the rule engine over a basket: per-rule detail plus verdict."""

    model_config = ConfigDict(frozen=True)

    plan_id: str = Field(min_length=1)
    """The `OrderPlan.plan_id` this report was evaluated against."""
    decision: Decision
    rule_results: tuple[RuleResult, ...] = ()
    """May be empty for a system that evaluates no rules (e.g. NullSystem)."""
    repairs: tuple[Repair, ...] = ()
    """Empty when `decision` is ALLOW or BLOCK; non-empty only for ALLOW_WITH_REPAIRS."""
