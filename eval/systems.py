"""Systems the eval harness can run: `null`, `baseline`, `agent`.

Each implements `System.run(case, fixture) -> SystemResult`. `NullSystem` is the only
one implemented here -- it exists purely to prove the harness runs end to end and to
establish the scoring floor. `baseline` (single-prompt) and `agent` (full OrderGuard
pipeline: compiler -> rule engine -> repair) are wired into `run_eval.py`'s CLI but
raise `NotImplementedError` until those components exist.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol

from eval.cases import EvalCase
from eval.fixtures import Fixture
from orderguard.rules.engine import RuleEngine
from orderguard.schemas.order_plan import OrderPlan
from orderguard.schemas.risk_report import Decision, RiskReport


@dataclass(frozen=True)
class SystemResult:
    """One system's output for one case, plus the metadata the scorer aggregates."""

    plan: OrderPlan
    report: RiskReport
    latency_s: float
    llm_calls: int


class System(Protocol):
    """A thing the eval harness can run one case through."""

    def run(self, case: EvalCase, fixture: Fixture) -> SystemResult: ...


class NullSystem:
    """Always returns ALLOW with an empty basket and no rule evaluations.

    Calls no LLM, evaluates no rules, makes no network call. This is the harness's
    floor: any real system should score far above what NullSystem achieves, since
    NullSystem is right only on cases whose expected decision is also ALLOW with
    zero orders.
    """

    def run(self, case: EvalCase, fixture: Fixture) -> SystemResult:
        start = time.perf_counter()
        plan = OrderPlan(
            account_id=fixture.account.account_id,
            source_instruction=case.instruction,
            orders=(),
        )
        report = RiskReport(plan_id=plan.plan_id, decision=Decision.ALLOW, rule_results=())
        latency_s = time.perf_counter() - start
        return SystemResult(plan=plan, report=report, latency_s=latency_s, llm_calls=0)


class RuleEngineSystem:
    """Runs `case.naive_plan` through `RuleEngine` directly, skipping the LLM compiler.

    Isolates rule-engine accuracy from compiler accuracy: `naive_plan` is what an
    unguarded single-pass system would have produced from the instruction, so this
    system answers "given that basket, does the deterministic rule engine reach the
    right decision?" independent of whether an LLM would compile the instruction
    correctly in the first place.
    """

    def __init__(self) -> None:
        self._engine = RuleEngine()

    def run(self, case: EvalCase, fixture: Fixture) -> SystemResult:
        start = time.perf_counter()
        naive = OrderPlan(
            account_id=fixture.account.account_id,
            source_instruction=case.instruction,
            orders=case.naive_plan,
        )
        final_plan, report = self._engine.evaluate(naive, fixture.account, fixture.market, case.user_constraints)
        latency_s = time.perf_counter() - start
        return SystemResult(plan=final_plan, report=report, latency_s=latency_s, llm_calls=0)


class BaselineSystem:
    """Single-prompt baseline: one model call with broker tools, no rule engine.

    Not implemented yet -- see `eval/baselines/single_prompt.py`.
    """

    def run(self, case: EvalCase, fixture: Fixture) -> SystemResult:
        raise NotImplementedError("baseline system is not implemented yet")


class AgentSystem:
    """Full OrderGuard pipeline: IntentCompiler -> RuleEngine -> RepairAgent.

    Not implemented yet -- rule logic, the compiler, and the repair agent are all
    still `NotImplementedError` stubs.
    """

    def run(self, case: EvalCase, fixture: Fixture) -> SystemResult:
        raise NotImplementedError("agent system is not implemented yet")
