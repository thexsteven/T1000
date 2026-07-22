# Copilot Task — Sync all `t1000/` docs to the current pipeline state (V2.1)

## What this is

Fatemeh's preprocessing pipeline has advanced. Several `t1000/` documents were
written against an older assumption — *"the pipeline only profiles cycles, it
never decides; I build the missing validation/decision layer."* **That is no
longer true.** This task reads the current pipeline, then brings every document
in `t1000/` into line with it and repositions this thesis's contribution
accordingly.

---

## HARD RULES — read before doing anything

1. **Work only inside `t1000/`.** You may create, edit, or delete files *only*
   within the `t1000/` directory.
2. **`MasterThesis/` is READ-ONLY.** It is another author's (Fatemeh's) prior
   work. Read it to understand the pipeline; **never** modify, rename, move, or
   delete anything inside it.
3. **Do not touch any other top-level folder** (`data/`, `DQC/`, `ERA/`,
   `ERA-NAS/`, …). Only `t1000/`.
4. If any correction seems to require a change outside `t1000/`, **stop and note
   it in your summary** — do not make the change.
5. **Do not invent facts.** If the source docs don't support a claim, mark it
   `TODO(confirm)` rather than guessing.
6. **Do not commit, push, or run the pipeline.** Documentation edits only.

---

## Step 0 — Read first (both folders, read-only)

Before editing anything:

1. Read all of `MasterThesis/docs/`, especially:
   - `thesis_pipeline.md` — the authoritative current pipeline (note the
     version/date at the top).
   - `architecture_decisions.md`
   - `implementation_log.md`

   Goal: know exactly what the pipeline does **today**, stage by stage.

2. Read all of `t1000/` — `docs/`, `notes/`, `README.md`, `AGENTS.md`,
   `deliverables/`, and any doc-style comments/docstrings in `src/`.

   Goal: find every place that still assumes the old premise.

---

## Step 1 — The current state to align to

Treat `MasterThesis/docs/thesis_pipeline.md` as the **source of truth** and
verify the following against it. Known key facts as of pipeline **V2.1
(2026-07-22)**:

- **Stage 9 — Validation Rule Generation**: derives data-driven thresholds
  automatically (robust Median/MAD, quantile fallback), separating **hard rules**
  (logical/domain constraints) from **learned rules** (statistical bounds), and
  marks rules `provisional` when the reference population is limited.
- **Stage 10 — Dataset Validation**: the **only stage that rejects cycles**.
  Classifies each cycle as `valid_core_cycle`,
  `valid_complete_multisensor_cycle`, or `invalid_cycle`, with reason codes
  (e.g. `duration_below_lower_bound`, `position_stroke_out_of_range`,
  `vibration_unavailable`).
- **Stage 8 — Cycle Quality Profiling**: stays descriptive / non-rejecting;
  profiles `constant_signal`, `coverage_ratio`, `non_finite_count`, sample
  counts, gaps, etc. — at whole-cycle level.
- **Segmentation thresholds remain provisional**: session gap (`3600 s`) and
  cycle-detection cut-off (`position > 1.0`).

**Implication:** the pipeline already performs statistical validation *and*
rejection. This thesis does **not** build that.

---

## Step 2 — How to reposition this thesis's contribution

Everywhere the docs describe what this (t1000) thesis contributes, align to this
split.

**This thesis adds (keep / emphasize):**

- **Physical cross-check (absolute floor)** on top of the pipeline's statistical
  validation — full mechanical stroke, physically-plausible duration, expected
  sample count, per-signal sanity — checked against *absolute* physical values,
  not the learned population range. Rationale: statistical "normal" is learned
  from a population that mixes healthy + degraded cycles, so it can drift as
  faults grow and can mask whole-batch faults; an absolute physical floor does
  not (physics needs no healthy reference population).
- **In-cycle standstill / frozen-segment detection** — genuinely new; the
  pipeline's `constant_signal` is whole-cycle only. A sliding window (ideally on
  velocity) catches a frozen segment *inside* an otherwise moving cycle.
- **Minimum session size** — not in the pipeline.
- **Criteria Maturity rating** across all criteria (the pipeline's included) —
  transparency about how well each threshold is grounded.
- **Re-derivation of the two provisional segmentation thresholds** (`3600 s`,
  `position > 1.0`) — re-derived from data and handed to the pipeline to apply
  at the source. **Do not re-implement segmentation inside `t1000/`.**
- **Deliverables:** (1) decision tree = the accept/reject logic; (2) data pool =
  an index of passing cycles + a rejection log, raw files untouched
  (non-destructive); (3) HTML cycle dashboard for daily engineer use.
- **Integration framing:** the physical floor runs **first**, then the
  pipeline's statistics run on the cleaned pool — the two theses combine into one
  pipeline, they do **not** compete.

**Explicitly out of scope (state as NOT this thesis):**

- Building/rewriting the pipeline, cycle detection, extraction, or the
  segmentation thresholds.
- Data-driven statistical validation and cycle rejection (Stages 9–10 — now
  Fatemeh's prior work).
- Machine-learning / feature-engineering / RUL modelling.

**Find and rewrite any wording like:**

- "the pipeline does not decide / only profiles" stated as a *current* fact,
- "I build the missing validation/decision layer",
- listing full-stroke / duration / sample-count / per-signal quality as purely
  this thesis's own gates **without** the physical-vs-statistical distinction.

---

## Step 3 — Consistency rules

- Keep the terminology already used in `t1000/` (e.g. ERA, Versuch names, signal
  names). Do not introduce new terms where an established one exists.
- Keep each document's existing purpose and structure; change only what is needed
  for correctness. Do not rewrite wholesale.
- Where a stage number or stage count appears, make it match
  `thesis_pipeline.md`.
- If two `t1000/` docs disagree after your edits, make them agree. Source of
  truth = `thesis_pipeline.md` for the pipeline; the Step 2 split for the
  contribution.
- For source files: update only doc comments / docstrings / README-type text
  that state the outdated framing. **Do not change code logic.** List every code
  file you touch.

---

## Step 4 — Output

When done, write a summary file `t1000/notes/sync_v21_changelog.md` containing:

1. A bullet list of every file changed, each with a one-line note of what was
   corrected.
2. Any place where a fix would have required editing **outside** `t1000/` (which
   you did NOT do).
3. Any `TODO(confirm)` items you inserted because the source did not settle a
   fact.

Do not commit or push unless explicitly asked.
