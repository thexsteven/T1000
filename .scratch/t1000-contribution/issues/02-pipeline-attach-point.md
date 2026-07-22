# Attach point in Fatemeh's pipeline for a physical pre-stage

Type: research
Status: resolved
Blocked by: —

## Question

Where and in what form would a t1000 physical-plausibility pre-stage attach to
Fatemeh's pipeline, and what is the pipeline's input/stage interface at that
seam?

Gather, do not decide. Report with citations from `/home/ita/MasterThesis`:

- The stage sequence and where cycle boundaries / session detection / cycle
  extraction produce their outputs (Stages around 4-5 and 8-10), and which
  stage's *input* a physical floor would sit in front of.
- The concrete data contract at that point: what object/parquet/schema flows
  between stages (columns, per-cycle vs per-sample, how cycles are indexed,
  how rejections are represented — e.g. `valid_core_cycle` / `invalid_cycle`).
- How the pipeline is configured (`configs/example_pipeline.yaml`) and whether
  a new pre-stage or a flag/index hand-off is the natural extension point.
- Any existing extension/plugin seam, or the closest thing to one.
- The smallest surface a t1000 pre-stage could expose to feed the pipeline
  (e.g. a filtered pool index vs. an annotated cycle table).

This is read-only research on Fatemeh's repo; capture enough that ticket
**Integration seam / data contract** can decide the seam without re-reading.

## Answer

Resolved by the `pipeline-attach-point` research subagent (findings recorded here;
the subagent had no write tool). All citations are into `/home/ita/MasterThesis`.

**Attach point.** The pipeline is a flat 9-stage sequence with **no plugin/hook
mechanism** — stages are plain lambdas in a `stage_runners` dict iterated over
`STAGE_ORDER` (`src/pipeline.py:59-87, 1087-1194`). The only sensible seam for a
physical floor is **between Stage 5 `cycle_detection` and Stage 6
`multi_sensor_extraction`** — before the expensive extraction and before any
statistics. Data flows in-memory as `results["cycle_detection"]["cycles"]` →
extraction (`src/pipeline.py:1119-1141`).

**Seam object / data contract.** The cycle index — one row per cycle, keyed by
global integer `cycle_id`, sorted by `(session_id, start_time, cycle_id)`,
written to `cycles/cycles.parquet`. Schema (`src/storage/cycle_index_writer.py:12-24`):
`experiment, session_id, cycle_id, reference_signal_uuid, start_time, end_time,
duration_seconds, number_of_samples, minimum_position, maximum_position,
mean_position` (position-only features at this point — velocity/current/etc. are
not yet extracted).

**Rejection representation at the seam: none.** No flag/invalid column exists
here; a **filtered pool (absent rows = rejected)** is the natural hand-off form.
Rejection classes (`valid_core_cycle` / `valid_complete_multisensor_cycle` /
`invalid_cycle`) appear only later in **Stage 9 `dataset_validation`, the ONLY
rejecting stage** (`src/preprocessing/dataset_validation.py:58-60, 340-368`).
Stages 7-8 (quality profiling, rule generation) are purely descriptive.

**Documented precedent.** `src/preprocessing/cycle_selection.py` is a standalone,
opt-in filter for exactly this seam, deliberately **not** wired into `STAGE_ORDER`
(`tests/test_pipeline.py:1103-1110`; `docs/thesis_pipeline.md:436-455`). It returns
a filtered cycle-index parquet with the same schema — the pattern a t1000 pre-stage
should follow.

**Config.** Single flat YAML (`configs/example_pipeline.yaml`) → `PipelineConfig`
dataclass (`src/pipeline.py:117-144`); no key for a physical pre-stage. A new
top-level section (e.g. `physical_plausibility:`) parallel to `dataset_validation:`
is the natural extension.

**Three hand-off options for the seam decision (ticket 05):**
- **A — Filtered pool index (min coupling, zero code change to Fatemeh):** t1000
  reads `cycles.parquet`, emits `cycles_filtered.parquet` (same schema, passing
  cycles only); extraction is pointed at it.
- **B — New pipeline stage (tighter):** add a `PHYSICAL_PLAUSIBILITY` enum value +
  STAGE_DIRECTORIES entry + lambda (~4 lines in `src/pipeline.py`).
- **C — Annotated cycle table (best auditability):** add `t1000_ok: bool` +
  `t1000_reason: str` columns to the cycle index; one filter line at extraction.
  Preserves *which* cycles were rejected and *why* (fits the dashboard use case).
