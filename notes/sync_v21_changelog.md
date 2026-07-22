# Sync to pipeline V2.1 — changelog (2026-07-22)

Task: `notes/copilot_prompt_sync_t1000_docs.md`. Brought every `t1000/` document
into line with Fatemeh's current pipeline (`MasterThesis/docs/thesis_pipeline.md`,
**V2.1, 2026-07-22**) and repositioned this thesis's contribution around the fact
that the pipeline now performs statistical validation **and** cycle rejection
itself (Stage 9 Validation Rule Generation, Stage 10 Dataset Validation — the only
rejecting stage; Stage 8 Cycle Quality Profiling stays descriptive/non-rejecting).

All edits are inside `t1000/`. `MasterThesis/` was read-only and untouched.

## 1. Files changed

- **`docs/pipeline_structure.md`** — Biggest change. Removed the false premise
  ("the pipeline only profiles / never decides — the pool-filter module is still to
  be built on top of Stage 8"). Renumbered the stage map to V2.1 (13 stages, 10
  implemented): inserted Stage 3 Efficient Measurement Loading, promoted the former
  "cycle selection" to a standalone utility, added Stage 9 Validation Rule
  Generation and Stage 10 Dataset Validation (only rejecting stage), and Stage 13
  Machine Learning & Anomaly Detection. Updated the criteria table (new stage
  numbers + Stage 9/10 rows), the status note (Stages 8–10 now complete), and added
  a new **§5 "Positioning of the t1000 contribution"** (physical floor + in-cycle
  standstill + minimum session size + criteria-maturity rating + re-deriving the two
  provisional segmentation thresholds).

- **`docs/MasterThesis_usefulness_criteria_analysis.md`** (EN) — Added a V2.1 update
  banner. Marked the now-superseded current-state claims inline: "not yet a
  usefulness classifier", "no usefulness score beyond structural completeness"
  (now Stage 10), and "Signal Quality Assessment not implemented" (now Stage 8).
  Annotated the Section-5 "extend Stage 8 into a filter" suggestion as largely
  realised by the pipeline, with the physical floor as the distinct t1000 addition.

- **`docs/MasterThesis_usefulness_criteria_analysis_de.md`** (DE) — Mirror of the EN
  corrections in German.

- **`deliverables/pipeline_stage_overview.html`** — Renumbered from V2.0 (11 stages)
  to V2.1 (13 stages): inserted Stage 3 Efficient Measurement Loading and Stage 13
  ML & Anomaly Detection; Cycle Quality Profiling = Stage 8, Validation Rule
  Generation = Stage 9, Dataset Validation = Stage 10 (labelled "the only pipeline
  stage that rejects cycles"). Updated meta line (V2.0/2026-07-20 → V2.1/2026-07-22,
  source = `thesis_pipeline.md`), the "bottom line" summary (the pipeline now
  validates+rejects; only the two segmentation values are the t1000 re-derivation),
  and the footer count (13 stages · 10 implemented, 3 planned). Div-balanced.

- **`deliverables/preprocessing_decision_tree.html`** — Reframed the intro/TL;DR:
  this tree is a **physical-plausibility floor** running first, not a missing
  decision layer; the pipeline's Stages 9–10 already do the statistics/rejection.
  Added a **Level-4 overlap note** (its per-signal statistical bounds overlap Stage 9
  → defer or re-express as absolute physical guards — `TODO(confirm)`). Added an
  optional-vibration note at check 3.1 (all-8 requirement = intentionally selecting
  the complete-multisensor subset, not treating absent duty-cycled vibration as a
  failure — `TODO(confirm)`). Bumped version to Draft v0.3.

- **`deliverables/decision_tree_simple.html`** — Fixed Station 3, which wrongly
  implied missing vibration = "recording failed". Clarified vibration is
  duty-cycled/optional per V2.1 Stage 10, so most cycles have none by design;
  requiring it is a stricter pool choice (`TODO(confirm)` with the team).

- **`README.md`** — Sharpened the contribution description to the physical-floor-
  vs-statistical split; noted the pipeline (V2.1) already validates and rejects
  (Stages 9–10) and that this thesis adds the absolute physical floor + in-cycle
  standstill running first, and re-derives the two provisional segmentation
  thresholds.

- **`notes/weekly_plan.md`** — Added a dated "Update (2026-07-22) — Pipeline V2.1"
  note repositioning the planned "Pool-Filter-Modul" as a physical floor (not the
  missing decision layer) and flagging the Level-4/Stage-9 overlap.

## 2. Files reviewed but intentionally NOT changed

- **`docs/approach_comparison.md`** — Already aligned with the target split
  (physical plausibility vs. statistical outlier detection; physical floor first,
  then statistics). No premise to fix.
- **`notes/meeting_questions.md`** — Already written in the V2.1 framing (physical
  layer complementary to Fatemeh's statistical detection; references optional-
  vibration handling in dataset validation). No change needed.
- **`deliverables/source_guide.html`** — Thesis writing-guide scaffolding; does not
  assert the old premise. Left as-is.
- **`docs/dashboard_architecture.md`, `docs/dashboard_visualization_review.md`,
  `src/cycle_overlay/*` docstrings** — Concern the dashboard/cycle-overlay build,
  not the pipeline premise. No outdated framing found.

## 3. Places where a fix would require editing OUTSIDE `t1000/` (NOT done)

- None required. The source of truth (`MasterThesis/docs/thesis_pipeline.md`) was
  read-only and consistent; all corrections were within `t1000/`.

## 4. `TODO(confirm)` items inserted (source did not settle the fact)

- **Level-4 vs. Stage-9 de-duplication** (`preprocessing_decision_tree.html`,
  `weekly_plan.md`): whether Level-4's per-signal statistical bounds should defer to
  the pipeline's Stage 9 or be re-expressed as absolute physical guards. To agree
  with Fatemeh.
- **Vibration requirement for the pool** (`preprocessing_decision_tree.html` check
  3.1, `decision_tree_simple.html` Station 3): whether the useful pool must contain
  vibration (complete-multisensor only) or may also admit `valid_core_cycle`
  cycles without duty-cycled vibration. To confirm with the supervisors.

## 5. Out-of-scope staleness observed (not part of this task, left alone)

- **`docs/PROJECT_FILE_DOCUMENTATION.md`** predates the `docs/` and `deliverables/`
  additions and still says "the repository is not a git repository" and describes
  only the `src/cycle_overlay/` subproject. It does not assert the pipeline premise,
  so it was left unchanged; it would benefit from a separate refresh.
