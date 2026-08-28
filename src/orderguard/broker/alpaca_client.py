"""Live Alpaca paper-trading implementation of `BrokerClient`.

Reads `alpaca_endpoint` / `alpaca_api_key` / `alpaca_secret_key` from `Settings`
(`config.py`). Never used by `eval/` or `tests/` -- those use `fixture_client.py`
so that no test run makes a network call.
"""

from __future__ import annotations

from orderguard.config import Settings
from orderguard.schemas.account_state import AccountState
from orderguard.schemas.order_plan import Order


class AlpacaClient:
    """`BrokerClient` backed by the live Alpaca paper-trading API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def get_account_state(self) -> AccountState:
        raise NotImplementedError

    def submit_order(self, order: Order) -> str:
        raise NotImplementedError

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError
