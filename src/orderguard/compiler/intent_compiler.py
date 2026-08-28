"""Compiles a trader's plain-English instruction into a concrete OrderPlan.

This is one of the two places in OrderGuard allowed to call an LLM (the other is
`repair/repair_agent.py`). It resolves loose references in the instruction (e.g. "my
energy names", "split evenly") against the trader's actual `AccountState` and current
market data, and must ground every resulting order in real, current positions or
tradable symbols -- it does not invent tickers or prices.
"""

from __future__ import annotations

from orderguard.llm.client import LLMClient
from orderguard.schemas.account_state import AccountState
from orderguard.schemas.market_snapshot import MarketSnapshot
from orderguard.schemas.order_plan import OrderPlan


class IntentCompiler:
    """Turns (instruction, AccountState, MarketSnapshot) into an OrderPlan."""

    def __init__(self, llm_client: LLMClient) -> None:
        self._llm_client = llm_client

    def compile(
        self,
        instruction: str,
        account_state: AccountState,
        market_snapshot: MarketSnapshot,
    ) -> OrderPlan:
        """Compiles one instruction into an OrderPlan grounded in the given account/market state.

        Raises:
            NotImplementedError: business logic not yet implemented.
        """
        raise NotImplementedError
