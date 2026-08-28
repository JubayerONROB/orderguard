"""Append-only JSONL audit log: every prompt, tool call, rule result, and retry.

One line per event, written in order, never rewritten. This is the record that lets a
judge (or a debugging session) reconstruct exactly what the compiler, rule engine, and
repair agent did for a given instruction, in what order.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TrajectoryLogger:
    """Appends structured events to a per-run JSONL audit log."""

    def __init__(self, log_path: Path) -> None:
        self._log_path = log_path

    def log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Appends one timestamped event to the trajectory log.

        Args:
            event_type: e.g. "llm_call", "rule_result", "repair_attempt", "human_approval".
            payload: event-specific structured data.
        """
        raise NotImplementedError

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
