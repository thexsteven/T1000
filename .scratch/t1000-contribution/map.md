# Map: t1000 as a defended, additive contribution

Label: `wayfinder:map`
Tracker: local-markdown (no `docs/agents/issue-tracker.md`; wayfinder default)

## Destination

A **locked, defended plan** (a hand-off spec, not built code) that pins down
exactly what value t1000 adds — as a **physical-plausibility pre-stage
integrated into Fatemeh's ERA pipeline** — and a **gap-closure plan** that
closes the credibility gaps (provisional thresholds, redundancy-vs-Stage-9/10,
"value on paper vs in implementation") so the contribution holds up, in
priority order, to:

1. **DHBW T1000 examiners** — academic defensibility as an independent contribution.
2. **Fatemeh / the master thesis** — t1000 must actually plug into and improve her pipeline's outcome.
3. **Emerson test engineers** — the floor/dashboard must be usable and trusted in daily practice.

Done = every credibility gap has an agreed closure decision, and the seam into
Fatemeh's pipeline is specified — nothing left to *decide* before someone goes
and does the re-derivation/integration work.

## Notes

- **Domain.** Fatemeh's pipeline = *statistical* anomaly detection (Median/MAD,
  Stages 8-10, Stage 10 the only rejecting stage). t1000 = a *physical-
  plausibility* floor (absolute physical values, no healthy reference
  population) + in-cycle standstill detection, run *before* the statistics.
  See `docs/approach_comparison.md`, `docs/pipeline_structure.md`,
  `docs/MasterThesis_usefulness_criteria_analysis.md`.
- **Chosen path.** Integration (t1000 becomes a physical pre-stage feeding
  Fatemeh's pipeline), not a standalone parallel layer.
- **This map plans, it does not do.** Tickets produce *decisions*. Actually
  running the threshold re-derivation or writing the integration code is
  execution that happens *after* the plan (see Out of scope).
- **Skills to consult per ticket:** `/grilling` + `/domain-modeling` (default),
  `/research` (AFK facts), `/prototype` (fidelity when "how should it look/behave").
- **Tooling.** Any parquet/pandas work uses `/home/ita/ERA-NAS/.venv/bin/python`
  (system Python lacks pyarrow/pandas). External data is read-only; all
  generated files stay inside `t1000/`.

## Decisions so far

<!-- one line per resolved ticket: gist + link -->

- [Attach point in Fatemeh's pipeline](issues/02-pipeline-attach-point.md) — seam is between Stage 5 `cycle_detection` and Stage 6 `multi_sensor_extraction`; the object is the per-cycle `cycles.parquet` index (position-only, keyed by `cycle_id`); no rejection flag exists there, so hand-off is a filtered pool or an annotated table; `cycle_selection.py` is the documented opt-in precedent. Three seam options (A filtered index / B new stage / C annotated table) for ticket 05.
- [Prior evidence for re-deriving the provisional thresholds](issues/01-threshold-derivation-evidence.md) — all three thresholds are provisional in Fatemeh's source; **session-gap 3600 s** and **movement threshold >1.0** are cheaply re-derivable from existing `outputs/D63_Nr7_8/…` artifacts (`timestamp_analysis/statistics.csv`, `cycles.parquet`); **velocity scaling** is blocked on a unit/spec question (declared `m/s` but values physically impossible) → graduated new task ticket **Confirm velocity-signal unit & actuator spec**.
- [Justification strategy for the three thresholds](issues/03-threshold-justification-strategy.md) — **one empirical pillar** (one position-signal study, ~3 days) re-derives BOTH session-gap 3600 s (timestamp-gap distribution break) and movement >1.0 (min-position noise floor), on D63_Nr7_8 + a cheap cross-dataset sanity check; the position unit is left unresolved as an explicit caveat; **velocity stays openly provisional**, deferred to ticket 08. Canonical physical-contamination classes locked (non-finite / frozen / incomplete-stroke / implausible duration / implausible sample-count), all computable at the position-only seam. Anti-circularity rebuttal banked for 07: the floor removes *contamination* (physics-defined, distribution-independent), not statistical outliers, so it cleans Stage 9's input population without biasing its median/MAD.

## Not yet specified

<!-- in-scope fog, graduates as the frontier advances -->

- **Final hand-off spec assembly** — the single document that states t1000's
  defended contribution + gap-closure plan. Pure assembly; blocked by every
  decision below, so not yet sharp.
- **Engineer-usability / dashboard-trust criteria** (audience #3) — what makes
  a `rejection_reason` actionable and trusted in daily practice. Sharpens once
  the seam and the additive-value evidence are settled.
- **Prototype of the integrated pre-stage** — a rough stub of the seam to react
  to. Only specifiable after the seam contract and threshold strategy land.

## Out of scope

<!-- ruled beyond the destination; closed, never graduates -->

- **Executing the threshold re-derivation** (running the data analysis to fix
  3600 s / Position>1.0 / velocity scaling) — that is post-plan *doing*; the map
  decides the strategy, not the number.
- **Writing the integration code** into Fatemeh's pipeline — post-plan doing.
- **Rebuilding or modifying Fatemeh's statistical pipeline (Stages 8-10)** —
  belongs to the master thesis, not t1000.
