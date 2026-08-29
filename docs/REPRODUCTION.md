# Reproduction

## The reproducible path: replay mode

`eval/cassettes/` holds one JSON file per LLM call ever made against the eval case
set, keyed on a hash of `(model, temperature, system prompt, user prompt)`, and is
committed to this repo. **Judges do not need an Agnes API key** to reproduce the
headline numbers:

```
python -m eval.run_eval --system rules_only
python -m eval.run_eval --system agent    --llm-mode replay
python -m eval.run_eval --system baseline --llm-mode replay
```

`--llm-mode replay` only ever reads a cassette; a miss is a loud `CassetteMissError`,
never a silent fall-through to a live call. Because the compiler and baseline both run
at `temperature=0` (see `AGNES_DEFAULT_TEMPERATURE` in `src/orderguard/llm/client.py`)
and every call is cached, a replayed run is fully deterministic -- same scores, every
time, regardless of what the live provider would return today.

`rules_only` never touches an LLM at all (`--llm-mode` is accepted but ignored for it).

## Other modes

- `--llm-mode live` -- always calls Agnes, writes every response to its cassette.
  Requires `AGNES_API_KEY` set in `.env`. Used to populate cassettes in the first
  place; not needed for reproduction.
- `--llm-mode auto` (default) -- replays on a cache hit, calls live (and writes) on a
  miss. Convenient for local development when adding new cases, but not the
  reproducible path since it can silently touch the network.

## Environment

```
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
python -m pytest -q
```

Python 3.10+. See `pyproject.toml` for the full dependency list.
