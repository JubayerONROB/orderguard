"""The fair baseline: one model call with broker tools, no rule engine, no repair step.

Exists so `run_eval.py --system baseline` can be scored against `run_eval.py --system
agent` on the same cases -- this is the comparison the eval harness exists to make.
"""

from __future__ import annotations

from orderguard.broker.base import BrokerClient
from orderguard.llm.client import LLMClient
from orderguard.schemas.order_plan import OrderPlan


def run_single_prompt_baseline(
    instruction: str,
    llm_client: LLMClient,
    broker_client: BrokerClient,
) -> OrderPlan:
    """Asks the model to produce an OrderPlan directly from the instruction and broker tools.

    Raises:
        NotImplementedError: business logic not yet implemented.
    """
    raise NotImplementedError
