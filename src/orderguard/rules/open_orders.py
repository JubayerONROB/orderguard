"""R4: conflicts and stacking between the basket and existing unfilled orders on the account.

REPAIR: cancel-and-resize is arithmetically unique -- see CLAUDE.md's repair principle.
Cancelling the stale open order removes the ambiguity and always succeeds; there is no
"deferring would empty the basket" failure mode like R2/R6, since cancelling never
removes a basket order.
"""

from __future__ import annotations

from orderguard.schemas.account_state import AccountState
from orderguard.schemas.market_snapshot import MarketSnapshot
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import RuleResult, Severity
from orderguard.schemas.user_constraints import UserConstraints


def _stacking_open_order_ids(plan: OrderPlan, state: AccountState) -> list[str]:
    """Open order ids that stack with a basket order on the same symbol and aren't
    already cancelled by this basket.

    Any side combination counts as stacking: an unfilled order on a symbol makes that
    symbol's position outcome ambiguous the moment a new basket order also touches it,
    regardless of whether the two orders are the same side.
    """
    cancelled = set(plan.cancellations)
    basket_symbols = {o.symbol for o in plan.orders}
    return [oo.order_id for oo in state.open_orders if oo.symbol in basket_symbols and oo.order_id not in cancelled]


class OpenOrdersRule:
    """Fails if the basket conflicts with (or double-stacks) an existing open order on a symbol."""

    id = "R4"
    name = "open_orders"
    severity = Severity.BLOCKING

    def check(
        self,
        plan: OrderPlan,
        state: AccountState,
        market: MarketSnapshot,
        constraints: UserConstraints,
    ) -> RuleResult:
        stacking_ids = _stacking_open_order_ids(plan, state)
        if not stacking_ids:
            return RuleResult(
                rule_id=self.id,
                rule_name=self.name,
                passed=True,
                severity=self.severity,
                explanation="no basket order shares a symbol with an uncancelled open order",
            )

        stacking_id = stacking_ids[0]
        open_order = next(oo for oo in state.open_orders if oo.order_id == stacking_id)
        order_index = next(i for i, o in enumerate(plan.orders) if o.symbol == open_order.symbol)
        return RuleResult(
            rule_id=self.id,
            rule_name=self.name,
            passed=False,
            severity=self.severity,
            order_index=order_index,
            explanation=(
                f"{open_order.symbol} has an existing open order ({open_order.order_type} {open_order.side}, "
                f"id {open_order.order_id}, submitted {open_order.submitted_at}) not yet cancelled; a new "
                f"{open_order.symbol} order in this basket would stack with it"
            ),
        )

    def repair(
        self,
        plan: OrderPlan,
        state: AccountState,
        market: MarketSnapshot,
        constraints: UserConstraints,
        result: RuleResult,
    ) -> OrderPlan:
        stacking_ids = _stacking_open_order_ids(plan, state)
        if not stacking_ids:
            return plan
        new_cancellations = tuple(plan.cancellations) + tuple(stacking_ids)
        return plan.model_copy(update={"cancellations": new_cancellations})
