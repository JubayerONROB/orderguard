"""CLI entrypoint for the eval harness: `python -m eval.run_eval --system null|baseline|agent`.

Loads cases from `eval/cases/`, resolves each case's fixture from `eval/fixtures/` (pure
disk I/O, no network), runs the selected system, scores the result, prints a per-case
table plus summary, and writes a timestamped JSON result file under `--out`.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from eval.cases import CASES_DIR, CaseLoadError, load_all_cases, load_case
from eval.fixtures import FIXTURES_DIR, FixtureLoadError, load_fixture
from eval.scorer import CaseScore, aggregate, format_report, score_case
from eval.systems import AgentSystem, BaselineSystem, NullSystem, System

SYSTEMS: dict[str, System] = {
    "null": NullSystem(),
    "baseline": BaselineSystem(),
    "agent": AgentSystem(),
}

DEFAULT_OUT_DIR = Path(__file__).parent / "runs"


def _case_score_to_dict(score: CaseScore) -> dict:
    d = asdict(score)
    d["expected_decision"] = score.expected_decision.value
    d["actual_decision"] = score.actual_decision.value
    return d


def run(system_name: str, case_id: str | None, out_dir: Path) -> int:
    """Runs `system_name` over all (or one) case(s), prints and persists the results.

    Returns:
        Process exit code: 0 if every case scored (regardless of pass/fail), 1 if a
        case or fixture failed to *load*.
    """
    system = SYSTEMS[system_name]

    try:
        if case_id is not None:
            cases = [load_case(CASES_DIR / f"{case_id}.json")]
        else:
            cases = load_all_cases()
    except CaseLoadError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    scores: list[CaseScore] = []
    for case in cases:
        try:
            fixture = load_fixture(case.fixture, fixtures_dir=FIXTURES_DIR)
        except FixtureLoadError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1

        result = system.run(case, fixture)
        scores.append(score_case(case, result.plan, result.report, result.latency_s, result.llm_calls))

    summary = aggregate(scores)
    report_text = format_report(scores, summary)
    print(report_text)

    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"{system_name}_{timestamp}.json"
    out_path.write_text(
        json.dumps(
            {
                "system": system_name,
                "timestamp": timestamp,
                "cases": [_case_score_to_dict(s) for s in scores],
                "summary": asdict(summary),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nwrote {out_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the OrderGuard eval harness.")
    parser.add_argument(
        "--system",
        choices=sorted(SYSTEMS),
        required=True,
        help="Which system to evaluate.",
    )
    parser.add_argument(
        "--case",
        default=None,
        help="Run a single case by id (e.g. case_003) instead of the full suite.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Directory to write the timestamped JSON result file into.",
    )
    args = parser.parse_args()
    sys.exit(run(args.system, args.case, args.out))


if __name__ == "__main__":
    main()
