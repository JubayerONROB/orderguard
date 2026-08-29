# OrderGuard

## What this is

OrderGuard is a pre-trade intent compiler and deterministic risk gate for self-directed
retail traders. A trader describes what they want to do in plain English; OrderGuard turns
that into a concrete basket of orders, checks it against a fixed set of account rules,
repairs what it safely can, blocks what it can't, and shows the trader exactly what changed
before anything reaches their broker.

## The user and the bottleneck

The target user is a self-directed retail trader on a margin account under $25,000 in
equity — the threshold below which Reg T's pattern-day-trading (PDT) rule applies. Below
that line, four constraints bite that a trader managing their own account by hand routinely
misses:

- **Pattern day trading.** A fourth same-day round trip (buy and sell, or sell and buy, on a
  position opened that same session) within a rolling five-business-day window trips a
  restriction that locks the account out of day trading for ninety days. The concrete cost
  of one miscounted trade is ninety days of reduced account access — not a warning, not a
  fee, a ninety-day lockout.
- **Stacked open orders.** An existing unfilled order on a symbol, combined with a new order
  on the same symbol, produces an ambiguous position outcome the moment both could fill.
- **Concentration drift.** A trader states a position-size cap in their head and rarely
  recomputes it precisely against current equity before every trade; a plan that "seems
  about right" can silently exceed it.
- **Wash sales.** Repurchasing a security within 30 days of realizing a loss on it disallows
  the loss for tax purposes — easy to trigger by accident when rebalancing back into a name
  you just trimmed.

None of these are exotic. They are the ordinary arithmetic of running a real account, and
they are exactly the kind of check a human skips when they're moving fast.

## Worked example

Fixture `retail_rotation` (`eval/fixtures/retail_rotation/`), account equity $18,400.00:

| Position | Qty | Price | Value | % of equity | Opened |
|---|---|---|---|---|---|
| NVDA | 12 | $170.00 | $2,040.00 | 11.1% | 2026-07-28 |
| XOM | 40 | $115.00 | $4,600.00 | 25.0% | 2026-07-16 |
| CVX | 25 | $152.00 | $3,800.00 | 20.7% | same day (this morning) |
| MSFT | 8 | $430.00 | $3,440.00 | 18.7% | 2026-06-28 |

Cash $4,520.00. Buying power $9,040.00. Day trades used: 3 of the rolling-window limit.
Open order: a limit buy for 12 more NVDA at $168.00, still unfilled. Nine days ago, 60
shares of AMD were sold at a realized loss of $1,500.00.

**Instruction:** *"Close out my energy names and put it all into NVDA and AMD, split evenly,
nothing over 15% per position."*

**What an unguarded compile produces**, taken literally: sell all 40 XOM, sell all 25 CVX,
put half the combined proceeds ($4,200.00) into NVDA, half into AMD. Four things are wrong
with this basket, and none of them are visible from reading the instruction:

1. CVX was opened this morning. Selling it today would be the fourth day trade in the
   rolling window on an account under $25,000 equity — the PDT restriction fires.
2. The new NVDA buy stacks with the existing unfilled 12-share limit order on NVDA.
3. $4,200.00 into NVDA (on top of the $2,040.00 already held) is $6,240.00 — 33.9% of
   equity, more than double the stated 15% cap. $4,200.00 into AMD alone is 22.8%, also
   over.
4. AMD was sold at a loss nine days ago; rebuying it now is inside the 30-day wash-sale
   window.

**What OrderGuard produces instead:** sell 40 XOM (unaffected — it wasn't opened today);
defer the CVX sale to a later session (day trade avoided); cancel the stale NVDA limit
order; buy 4 NVDA ($680.00, bringing the position to 14.8% of equity — the largest whole
share count that stays under the cap); buy 16 AMD ($2,624.00, 14.3% of equity, flagged as a
wash sale for tax awareness but not blocked, since severity there is a warning, not a
block); leave $1,296.00 in cash, because the 15% cap doesn't allow the full XOM proceeds to
be redeployed into just two names. Every one of those four findings is shown to the trader,
with the specific numbers above, before anything is submitted.

## How it works

```
instruction --> intent compiler (LLM) --> unguarded OrderPlan
                                                |
                                                v
                                          rule engine (deterministic)
                                                |
                                                v
                                    RiskReport: decision + findings
                                                |
                                                v
                                      human approval (required)
                                                |
                                                v
                                            broker
```

The intent compiler is the only component that turns natural language into a proposed
basket, and it is deliberately literal: it does not pre-emptively resize, skip, or hedge
anything, because that is the rule engine's job, not its own. The **rule engine is 100%
deterministic Python with zero LLM calls** — same input, same output, every run, no
sampling, no drift. This is a hard architectural boundary: nothing a language model wrote
reaches the broker unchecked, because the component that decides whether a basket is safe
never asks a model anything.

Every cancellation, resize, and deferral the rule engine proposes goes through human
approval before submission — the approval screen (`ui/app.py`) shows the decision, every
rule that fired and what happened to it, the final basket with repairs marked, proposed
cancellations listed separately, and any cash left undeployed. Nothing is sent to a broker
without an explicit approve click.

## The repair principle

Repair only when the correction is uniquely determined by a constraint the user themselves
stated, or by a pure timing shift that preserves the rest of the basket. Otherwise block.

    R3 CONCENTRATION  -> REPAIR. The user stated the cap; rounding down enforces their words.
    R4 OPEN_ORDERS    -> REPAIR. Cancel-and-resize is arithmetically unique.
    R2 PDT            -> REPAIR by deferral IF other orders in the basket still execute today.
                         If deferral would empty the basket, BLOCK. (case_003 vs case_002.)
    R6 SESSION        -> Identical logic to R2. (case_013 blocks: single order, empty basket.)
    R1 BUYING_POWER   -> BLOCK. An external limit, not user intent. No principled resize exists.
    R7 ELIGIBILITY    -> BLOCK. Nothing to repair.
    R5 WASH_SALE      -> WARN. A tax consequence the user may knowingly accept.

## Results

Three systems: `rules_only` (the deterministic engine alone, given a pre-compiled basket —
isolates rule-engine accuracy), `baseline` (one Agnes call, given the same account/market
context and told all seven rules by name and definition, asked to compile AND self-check in
one pass, no engine behind it), `agent` (the full pipeline: compiler then rule engine).

**Main suite** — 18 cases, the set that drove two rounds of iteration (see
`docs/IMPROVEMENT_CHANGELOG.md`):

| System | primary_score | catch_rate | false_block_rate | mean latency | LLM calls |
|---|---|---|---|---|---|
| rules_only | 100.0% | 100.0% | 0.0% | <0.001s | 0 |
| baseline | 66.7% | 54.5% | 0.0% | 38.0s | 18 |
| agent | 100.0% | 100.0% | 0.0% | 20.4s | 18 |

**Held-out suite** — 4 cases (`case_101`-`case_104`), written after the main suite drove
those two fixes, from the case format and the seven rule definitions only, without reading
the rule implementations or the compiler prompt. Run once each, live, no iteration
afterward — these numbers are as-is:

| System | primary_score | catch_rate | false_block_rate | mean latency | LLM calls |
|---|---|---|---|---|---|
| rules_only | 100.0% | 100.0% | 0.0% | <0.001s | 0 |
| baseline | 50.0% | 66.7% | 0.0% | 46.2s | 4 |
| agent | 100.0% | 100.0% | 0.0% | 28.8s | 4 |

The main suite drove development; the held-out suite did not. `docs/IMPROVEMENT_CHANGELOG.md`
records every iteration, including one held-out case's ground truth being corrected before
its first live run (a case-authoring arithmetic error caught by the free, deterministic
`rules_only` pass, not a system defect).

## Quick start

```
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
python -m eval.run_eval --system agent --llm-mode replay
```

See `docs/REPRODUCTION.md` for the full command set (baseline, rules_only, both suites, the
UI) and for what replay mode does and doesn't need.

## What was pre-existing

`.claude/agents/`, `.claude/rules/`, `.claude/commands/`, and `.claude/skills/` were copied
from an external toolkit ([WorldFlowAI/everything-claude-code](https://github.com/WorldFlowAI/everything-claude-code),
MIT licensed) before any OrderGuard-specific code was written, then pruned. See
`.claude/PROVENANCE.md` for the exact commit, license, and the list of what was kept versus
removed. Everything else in this repository — `src/`, `api/`, `ui/`, `eval/`, `tests/`,
schemas, and project docs — was written for OrderGuard.

## Scope

OrderGuard does not pick trades, predict prices, or give tax advice. It does not decide
what a trader should buy or sell, and the wash-sale check is a timing flag, not tax
guidance. What it checks is execution safety: given an instruction a trader has already
decided on, does the resulting basket violate a rule that would cost them access, money, or
an unintended tax consequence, and if so, is there a principled fix or does a human need to
see it before anything is sent.
