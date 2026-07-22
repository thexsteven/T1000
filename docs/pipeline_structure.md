# Preprocessing Pipeline Structure & Criteria (Stand: 2026-07-22)

Source of truth: `/home/ita/MasterThesis/docs/thesis_pipeline.md` (Version 2.1,
2026-07-22), cross-checked against `src/pipeline.py` (`PipelineStage` enum,
`STAGE_ORDER`, `IMPLEMENTED_STAGES`) and the stage modules under
`src/preprocessing/`. Stage numbers below follow the authoritative
`thesis_pipeline.md` V2.1 numbering.

> **What changed since the 2026-07-17 version of this file.** Fatemeh's pipeline
> has advanced. It now implements **Stage 8 Cycle Quality Profiling**
> (descriptive, non-rejecting), **Stage 9 Validation Rule Generation** (robust,
> data-driven thresholds) and **Stage 10 Dataset Validation** (the *only* stage
> that rejects cycles). The earlier assumption that "the pipeline only profiles
> and never decides — the t1000 thesis builds the missing validation/decision
> layer" is therefore **no longer true**: statistical validation and cycle
> rejection now live inside the pipeline. See §5 for how the t1000 contribution
> is repositioned around this.

## 1. Pipeline overview (13 stages, 10 implemented)

```
[Raw data: Position, Velocity, Current, Vibration, Pressure, Temperature]
        |
        v
+----------------------------------------------------------------------+
| Stage 1: Metadata Integration   metadata catalogue of raw signals    |
| Stage 2: Signal discovery       resolve signal by experiment + type  |
| Stage 3: Efficient loading      PyArrow predicate pushdown / pruning  |
| Stage 4: Timestamp analysis     gap statistics per signal            |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 5: Session detection             session_detection.py          |
| - Time gap > 3600 s (1 h) = new recording session (PROVISIONAL)      |
| - Prevents cycle detection across recording interruptions            |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 6: Position-based cycle detection    cycle_detection.py         |
| - NaN rows (time/value) removed & logged (_prepare_position_frame)   |
| - Reference signal: Position                                         |
| - is_moving = Position > 1.0 (movement_threshold, PROVISIONAL)       |
| - Cycle start: <=1.0 -> >1.0 ; Cycle end: >1.0 -> <=1.0               |
| - Incomplete edge cycles are discarded                                |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 7: Multi-sensor extraction       multi_sensor_cycle_extraction.py|
| - All signals sliced per detected cycle (session-level signal cache) |
| - Native sampling rate retained (no resampling, ADR-008)             |
| - Extraction NEVER rejects on a missing optional signal (vibration)  |
| - Standalone utility cycle_selection.py can pick a complete-          |
|   multisensor subset, but is NOT part of the default sequence        |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 8: Cycle Quality Profiling       cycle_quality_profiler.py      |
| [IMPLEMENTED, non-rejecting]                                          |
| - Computes exploratory, NON-rejecting quality metrics per cycle       |
|   and per signal (missing channels, timestamp consistency,            |
|   sampling behaviour, coverage ratio) at whole-cycle level            |
| - Outputs: signal_quality_metrics.parquet,                            |
|   cycle_quality_profile.parquet,                                      |
|   quality_metric_distribution_summary.csv                             |
| - Deliberately does NOT reject -- it is the unbiased data basis for   |
|   the data-driven rules generated in Stage 9                          |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 9: Validation Rule Generation   validation_rule_generation.py   |
| [IMPLEMENTED]                                                         |
| - Derives robust, data-driven thresholds from the Stage-8 population  |
|   BEFORE any rejection (avoids circular validation)                   |
| - Hard rules (logical/domain constraints) vs. learned rules          |
|   (median/MAD, quantile fallback); rules marked `provisional` when    |
|   the reference population is limited                                 |
| - Vibration thresholds derived only from the vibration_complete subset|
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 10: Dataset Validation           dataset_validation.py          |
| [IMPLEMENTED -- the ONLY stage that rejects cycles]                   |
| - Applies the frozen Stage-9 rules to every profiled cycle           |
| - Classes: valid_core_cycle / valid_complete_multisensor_cycle /     |
|   invalid_cycle, with reason codes                                    |
| - Absence of (duty-cycled) vibration alone NEVER invalidates a cycle  |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 11 (PLANNED): Feature Engineering  (partial time-domain util)   |
| Stage 12 (PLANNED): Dataset Generation                                |
| Stage 13 (PLANNED): Machine Learning & Anomaly Detection              |
+----------------------------------------------------------------------+
        |
        v
   [Output today: cycles classified valid_core / valid_complete_multisensor
    / invalid, with per-cycle rejection reason codes. The pipeline already
    performs statistical validation AND rejection. The t1000 thesis does NOT
    build that -- it adds a PHYSICAL-plausibility floor and in-cycle
    standstill detection on top, and re-derives the two provisional
    segmentation thresholds (see §5).]
```

## 2. Criteria used per stage - quick reference

| Stage | Criterion | Value / Rule | Status / Assessment | Source |
|---|---|---|---|---|
| 5 | Session gap | 3600 s | **Provisional / inconsistent** - ADR-006 says "Accepted", but a code comment describes the value as "exploratory". One of the two thresholds the t1000 thesis re-derives from data. | `session_detection.py` (`DEFAULT_SESSION_GAP_SECONDS`), `scripts/analyze_recording_sessions.py:20`, ADR-006 |
| 6 | Movement threshold | Position > 1.0 | **Provisional** - explicitly marked "temporary/provisional"; technical justification missing. The second threshold the t1000 thesis re-derives from data. | `cycle_detection.py`, `scripts/analyze_position_cycles.py` |
| 6 | Reference signal | Position (position-controlled actuator) | **Justified** - traceably documented | ADR-007, `docs/architecture_decisions.md` |
| 7 | Multi-sensor extraction | Native rate, no resampling; never rejects on a missing optional signal | **Justified** - ADR-008; duty-cycled vibration handled as legitimately absent | `multi_sensor_cycle_extraction.py`, ADR-008 |
| 7* | Cycle selection sample size (standalone utility) | `target_cycle_count` / `max_cycles_to_scan` (config) | **Optional utility, not the default sequence** - `cycle_selection.py` picks a complete-multisensor subset; not required for profiling/validation | `configs/example_pipeline.yaml`, `src/preprocessing/cycle_selection.py` |
| 8 | Quality metrics (missing channels, sampling rate, coverage ratio, time gaps) | Computed, not thresholded | **Exploratory / non-rejecting** - the unbiased data basis for the Stage-9 rules | `cycle_quality_profiler.py` |
| 9 | Validation rule generation | Hard rules + learned median/MAD (z-limit) / quantile-fallback bounds; `provisional` flag when reference population limited | **Statistically derived (not health-validated)** - robust method, but reference population not confirmed as healthy | `validation_rule_generation.py`, `validation_thresholds.json` |
| 10 | Dataset validation (only rejecting stage) | `valid_core_cycle` / `valid_complete_multisensor_cycle` / `invalid_cycle` with reason codes; absent vibration never invalidates a core cycle | **Justified core logic** - applies frozen Stage-9 rules; reference population still not verified as a health baseline | `dataset_validation.py` |

## 3. Open questions still to clarify (see `weekly_plan.md`)

- [ ] Derivation of `movement_threshold = 1.0` (duplicated 3x in code, no documented justification)
- [ ] Session-gap 3600 s: ADR-006 "Accepted" vs. code comment "exploratory" - which is current?
- [ ] Velocity scaling (blocks Variant B of the standstill/idle definition)
- [ ] Minimum session size N (proposed: 100)
- [ ] Cycle duration confirmed at ~3.1 s (older figure of 1.81 s was outdated)

## 4. Status note (2026-07-22)

Stages 8-10 are now **implemented and complete** in Fatemeh's pipeline:
Stage 8 (Cycle Quality Profiling, non-rejecting), Stage 9 (Validation Rule
Generation, robust data-driven thresholds) and Stage 10 (Dataset Validation,
the only rejecting stage). A full-scale Stage-8 profiling run
(`20260717_101103`, ~107,555 cycles) produced the real metric distributions
that Stage 9 uses to derive its rules. Feature Engineering (Stage 11),
Dataset Generation (Stage 12) and Machine Learning / Anomaly Detection
(Stage 13) remain planned.

## 5. Positioning of the t1000 contribution (relative to the pipeline above)

Because Stages 8-10 now perform statistical validation *and* cycle rejection
inside the pipeline, the t1000 thesis is **not** the "missing decision layer".
It contributes, on top of the pipeline:

- **Physical cross-check (absolute floor)** — full mechanical stroke,
  physically-plausible duration, expected sample count and per-signal sanity,
  checked against *absolute physical* values rather than the learned
  population range. Rationale: the statistical "normal" is learned from a
  population that mixes healthy and degraded cycles, so it can drift as faults
  grow and can mask whole-batch faults; an absolute physical floor cannot
  (physics needs no healthy reference population).
- **In-cycle standstill / frozen-segment detection** — genuinely new; the
  pipeline's `constant_signal` metric is whole-cycle only. A sliding window
  (ideally on velocity) catches a frozen segment *inside* an otherwise moving
  cycle.
- **Minimum session size** — not present in the pipeline.
- **Criteria Maturity rating** across all criteria (including the pipeline's),
  for transparency about how well each threshold is grounded.
- **Re-derivation of the two provisional segmentation thresholds**
  (`session gap 3600 s`, `Position > 1.0`) from data, handed back to the
  pipeline to apply at the source. The t1000 work does **not** re-implement
  segmentation.

Integration framing: the physical floor runs **first**, then the pipeline's
statistics run on the cleaned pool — the two theses combine into one pipeline,
they do not compete (see `docs/approach_comparison.md`).

