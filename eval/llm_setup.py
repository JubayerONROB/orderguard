"""Constructs the cassette-cached Agnes client eval systems share.

Loads real settings from `.env` (base URL, API key, model) but every call goes through
`CachedLLMClient`, so the mode (`live`/`replay`/`auto`) governs whether the network is
ever actually touched.
"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from orderguard.config import get_settings
from orderguard.llm.cassette import CachedLLMClient, CassetteMode, resolve_mode
from orderguard.llm.client import AGNES_DEFAULT_TEMPERATURE, AgnesClient, LLMClient

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class CountingLLMClient:
    """Wraps an `LLMClient`, counting every `complete()` call (cache hit or miss).

    Used by eval systems to report `total_llm_calls` -- a logical count of how many
    times the system invoked the LLM interface, independent of whether the cassette
    cache actually touched the network.
    """

    def __init__(self, inner: LLMClient) -> None:
        self._inner = inner
        self.call_count = 0

    def complete(self, system: str, user: str, response_schema: type[SchemaT]) -> SchemaT:
        self.call_count += 1
        return self._inner.complete(system, user, response_schema)


def build_llm_client(mode: CassetteMode | None = None) -> CachedLLMClient:
    """Builds the shared cached Agnes client for eval systems.

    Args:
        mode: overrides the resolved mode (CLI flag > env var > "auto") when given.
    """
    settings = get_settings()
    inner = AgnesClient(
        base_url=settings.agnes_base_url,
        api_key=settings.agnes_api_key,
        model=settings.agnes_default_model,
        timeout=settings.agnes_timeout,
        max_retries=settings.agnes_max_retries,
        temperature=AGNES_DEFAULT_TEMPERATURE,
    )
    return CachedLLMClient(
        inner=inner,
        model=settings.agnes_default_model,
        temperature=AGNES_DEFAULT_TEMPERATURE,
        mode=mode if mode is not None else resolve_mode(),
    )
