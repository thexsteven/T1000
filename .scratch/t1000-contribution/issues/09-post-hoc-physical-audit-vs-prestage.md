# Post-hoc physical-limits audit layer vs. the pre-stage seam (ticket 02)

Type: grilling
Status: open
Blocked by: —

## Question

User raised a second placement idea for the physical-plausibility check: a
layer running **after Stage 10 `dataset_generation`** in Fatemeh's pipeline
(`/home/ita/MasterThesis/src/pipeline.py`) — i.e. proving/auditing physical
limits against the *finished* dataset, rather than filtering contamination
*before* Stage 9's statistics as ticket 02 decided.

This was raised while asking a purely informational question — "does the
physical-conditions proof also need to live in `pipeline.py`?" — not as a
request to change code. No code or pipeline changes have been made. This
ticket exists to hold the open design tension so it isn't lost, and to be
resolved (via `/grilling`) before the final hand-off spec assembly.

**Key facts surfaced while answering the question (2026-07-23):**

- Stage 10 `dataset_generation` is **not implemented** in Fatemeh's pipeline
  (`NotImplementedError`; excluded from `IMPLEMENTED_STAGES`,
  `src/pipeline.py:88-100`). "After stage 10" today means "after nothing
  exists yet" — this placement is contingent on Fatemeh building that stage.
- The two placements serve **different goals**, not two implementations of
  the same thing:
  - **Pre-stage (ticket 02, locked):** before Stage 6, feeds a *cleaner input
    population* into Stage 9's Median/MAD statistics. This is what the
    anti-circularity argument (ticket 03) and the additive-value evidence
    plan (ticket 06) were built around — value = better stats, demonstrated
    by masking a contamination class.
  - **Post-hoc audit (new idea):** after the pipeline finishes, reports
    physical-limit violations against the already-validated output. Cannot
    prevent contamination from reaching Stage 9; is a trust/QA report, not a
    filter.
- **Whether it needs to live in `pipeline.py` differs by placement:**
  - Pre-stage: needs a small orchestration hook in `pipeline.py` (new
    `PipelineStage` enum value + `STAGE_ORDER`/`STAGE_DIRECTORIES`/
    `IMPLEMENTED_STAGES` entries + a `stage_runners` lambda, ~4 lines per
    ticket 02 option B). Limit-checking logic itself still lives in its own
    module, as every other stage does.
  - Post-hoc: does **not** need to touch `pipeline.py` at all — it can read
    finished Parquet outputs (`dataset_validation/valid_*.parquet`, or future
    Stage 10 output) from disk as a fully standalone script/module.
    `src/preprocessing/cycle_selection.py` is the existing precedent for an
    opt-in module deliberately **not** wired into `STAGE_ORDER`
    (`docs/thesis_pipeline.md:436-455`).
- The excalidraw source (`notes/datenpipeline.excalidraw`) names 7 signals
  with physical units that any physical-limits layer — pre-stage or post-hoc —
  would need bounds for: `Counter_force (N)`, `Counter_pressure (bar)`,
  `Cycle_count (#)`, `D_position (mm)`, `D_torque (Nm)`, `D_velocity (mm/s)`,
  `Temperature (degC)`. Today ticket 01/03's threshold work only covers
  position and session-gap; velocity is blocked on ticket 08.

## To resolve

Decide, via `/grilling`, whether:

(a) the post-hoc audit is added as a **second, additional** contribution
    alongside the locked pre-stage filter (different purpose, both defensible,
    both need separate additive-value arguments to audiences 1-3 in
    `map.md`), or
(b) ticket 02's seam decision should be **reopened** and replaced, or
(c) the post-hoc idea is dropped as out of scope for this contribution.

Whichever is chosen, update `map.md`'s "Decisions so far" / "Not yet
specified" sections accordingly, and, if (a), extend ticket 06's additive-value
plan to cover the audit layer's own value case (an audit that can't prevent
contamination needs a different justification than "cleans Stage 9's input").

## Answer

(not yet resolved)
