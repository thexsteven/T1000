# Prior evidence for re-deriving the provisional thresholds

Type: research
Status: resolved
Blocked by: —

## Question

What do the available ERA data and the already-written docs/reports say about
deriving or justifying the three provisional thresholds t1000's physical floor
depends on — **session-gap `3600 s`**, **movement threshold `Position > 1.0`**,
and **velocity scaling** — so a later decision can pick a justification strategy
without re-deriving from scratch?

Gather, do not decide. Report with citations:

- What existing t1000/ERA docs already establish: `docs/approach_comparison.md`
  (honest caveat), `docs/MasterThesis_usefulness_criteria_analysis*.md`
  (§3 rationale-per-criterion), `docs/pipeline_structure.md`, and in
  `/home/ita/ERA`: `V1_V2_DATA_COMPARISON.md`, `lazy_load_example.md`.
- What the stop-analysis tooling/reports under `/home/ita/ERA-NAS`
  (`run_stop_analysis.py`, `reports/`) already computed that bears on these
  thresholds (cycle durations, session gaps, standstill).
- Whether the raw data under `/home/ita/ERA` (which roots, size, columns) makes
  data-driven re-derivation of each threshold feasible, and how expensive.
- For each of the three thresholds: what evidence exists today vs. what is
  missing to justify it.

Use `/home/ita/ERA-NAS/.venv/bin/python` for any parquet inspection; prefer
lazy loads. Do not run a full re-derivation — just scope feasibility.

## Answer

Resolved by the `threshold-evidence` research subagent (findings recorded here;
the subagent had no write tool). Citations span `/home/ita/MasterThesis`,
`/home/ita/t1000`, and `/home/ita/ERA-NAS`.

**Headline.** All three thresholds are flagged provisional in Fatemeh's own
source; none has a formal derivation. Feasibility to re-derive differs sharply:
session-gap = easy (data present), movement threshold = easy (data present),
velocity scaling = **blocked on a unit/spec question**, not just compute.

**Session-gap 3600 s — most defensible.**
- ADR-006 (`MasterThesis/docs/architecture_decisions.md`) claims an "empirical
  basis" but attaches no numbers; `scripts/analyze_recording_sessions.py:20-21`
  calls the 1 h gap "exploratory … must be validated" — contradicting the ADR's
  "Accepted" status.
- Existing artifact `outputs/D63_Nr7_8/Versuch1/20260720_080516/timestamp_analysis/statistics.csv`
  already shows `gaps_gt_1_hour: 5`, `maximum_gap_seconds: 531462`,
  `median_gap_seconds: 0.05` (~20 Hz). ERA-NAS stop-analysis (counter-based, not
  position) confirms a clear separation between frequent short stops (median
  ~200–700 s) and multi-hour/day interruptions.
- **Missing:** an explicit gap-distribution histogram/percentile table showing
  the break-point; the derivation script has never been run and saved.
- **Feasibility: very low cost** — stats already computed; a full histogram is
  one lazy pyarrow scan of the time column.

**Movement threshold Position > 1.0 — feasible, has a unit ambiguity.**
- `cycle_detection.py:74` `value > movement_threshold` (default 1.0);
  `configs/example_pipeline.yaml:6` — no derivation comment. Provisional per
  `implementation_log.md` §15 and `analyze_position_cycles.py:23-25`.
- Existing `outputs/D63_Nr7_8/Versuch1/…/cycles/cycles.parquet` (4.6 M cycles)
  has `minimum_position` ranging ~0.06–0.85 at rest vs peak ~85 — the threshold
  sits just above the observed rest floor (~1% of peak).
- **Missing:** a min-position histogram proving the noise floor is consistently
  <1.0; the position unit is labelled "m" but values reach ~85 (implies mm or
  scaled) — ambiguity unresolved; no actuator stroke spec cited.
- **Feasibility: low cost** — lazy read of 2 columns × 4.6 M rows, <30 s. Always
  read `cycles.parquet`, not the 819 MB `cycles.csv`.

**Velocity scaling — weakest; blocked on external input.**
- `implementation_log.md` §15 verbatim: "physical scaling and unit
  interpretation of the Velocity signal still require verification."
- Velocity declared unit `m/s` (`selected_signals.csv`), yet per-cycle
  `std_value` min = 156.1 (`preprocessing_decision_tree.html` check 4.4,
  n=107,555) — physically impossible for a rod-style actuator if truly m/s →
  probable **unit-metadata error**. `weekly_plan.md:36` lists it as an open
  question to Fatemeh.
- **Missing:** an actuator velocity spec/datasheet or supervisor confirmation to
  interpret raw values. Until the unit is resolved, no physically meaningful
  epsilon can be set.
- **Feasibility: moderate compute but BLOCKED** — needs the spec first, so it is
  a decision/task dependency, not a pure data exercise.

**Available raw data** under `/home/ita/ERA`: `ERAP_EXT_003`(+V2–V6),
`ERAP_EXT_004/D63`, `ERAP_EXT_005/D100` (parquet, MB–hundreds of MB). Primary
NAS datasets (`D32/D63…`, 36–52 GB, 10–13 B rows) drive the big pipeline runs.
The already-produced `outputs/D63_Nr7_8/…` pipeline artifacts are the cheapest
re-derivation inputs.

**Implication for ticket 03 (justification strategy):** session-gap and movement
threshold can plausibly be *re-derived from existing artifacts*; velocity scaling
likely must be *declared provisional / deferred to a spec question* — surfacing a
possible new task ticket (obtain actuator spec / confirm velocity unit).
