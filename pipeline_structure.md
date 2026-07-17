# Preprocessing Pipeline Structure & Criteria (Stand: 2026-07-17)

Source: `/home/ita/MasterThesis/src/pipeline.py` (`PipelineStage` enum,
`STAGE_ORDER`, `IMPLEMENTED_STAGES`) and the individual stage modules under
`src/preprocessing/`. Stage numbers below match the actual code, not an
earlier draft numbering.

## 1. Pipeline overview (10 stages, 8 implemented)

```
[Raw data: Position, Velocity, Current, Vibration, Pressure, Temperature]
        |
        v
+----------------------------------------------------------------------+
| Stage 1: Metadata            metadata catalogue of raw signals       |
| Stage 2: Signal discovery    select relevant signal channels         |
| Stage 3: Timestamp analysis  gap statistics per signal                |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 4: Session detection             session_detection.py          |
| - Time gap > 3600 s (1 h) = new recording session                    |
| - Prevents cycle detection across recording interruptions            |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 5: Cycle detection               cycle_detection.py            |
| - NaN rows (time/value) removed & logged (_prepare_position_frame)   |
| - Reference signal: Position                                         |
| - is_moving = Position > 1.0 (movement_threshold)                    |
| - Cycle start: <=1.0 -> >1.0 ; Cycle end: >1.0 -> <=1.0               |
| - Incomplete edge cycles are discarded                                |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 6: Cycle selection               cycle_selection.py             |
| - mode = complete_multisensor_stratified                              |
| - Picks a representative, complete-signal subset of cycles,           |
|   distributed across sessions & time strata                           |
| - Bounded by target_cycle_count / max_cycles_to_scan (config)         |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 7: Multi-sensor extraction       multi_sensor_cycle_extraction.py|
| - All signals trimmed per selected cycle                              |
| - Native sampling rate retained (no resampling, ADR-008)              |
| - Internally selects a few cycles for HTML validation plots           |
|   via "is_validation_ready" check (validation_cycle_selection.py):     |
|   * all required_signals present                                      |
|   * >= minimum_samples per signal (config)                            |
|   * require_consecutive=True: only consecutive "good" cycles          |
|     (same session) accepted                                           |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 8: Cycle Quality Profiling       cycle_quality_profiler.py      |
| [IMPLEMENTED] currently running full-scale on the server right now    |
| - Computes exploratory, NON-rejecting quality metrics per cycle       |
|   and per signal (missing channels, timestamp consistency,            |
|   sampling behaviour, coverage ratio)                                 |
| - Outputs: signal_quality_metrics.parquet,                            |
|   cycle_quality_profile.parquet,                                      |
|   quality_metric_distribution_summary.csv                             |
| - Does NOT decide keep/reject -- this is the data basis the           |
|   decision-tree Level-4 thresholds still need to be derived from      |
+----------------------------------------------------------------------+
        |
        v
+----------------------------------------------------------------------+
| Stage 9  (PLANNED, NOT IMPLEMENTED): Feature Engineering               |
| Stage 10 (PLANNED, NOT IMPLEMENTED): Dataset Generation                |
+----------------------------------------------------------------------+
        |
        v
   [Output today: candidate cycles + quality metrics, still WITHOUT
    a final "usefulness"/reject decision -- that's the pool-filter
    module (decision tree, Levels 1-4) still to be built on top of
    Stage 8's output.]
```

## 2. Criteria used per stage - quick reference

| Stage | Criterion | Value / Rule | Status / Assessment | Source |
|---|---|---|---|---|
| 4 | Session gap | 3600 s | **Inconsistent** - ADR-006 says "Accepted", but a code comment describes the value as "exploratory" | `session_detection.py` (`DEFAULT_SESSION_GAP_SECONDS`), `scripts/analyze_recording_sessions.py:20`, ADR-006 |
| 5 | Movement threshold | Position > 1.0 | **Provisional** - explicitly marked "temporary/provisional"; technical justification missing | `cycle_detection.py`, `scripts/analyze_position_cycles.py` |
| 5 | Reference signal | Position (position-controlled actuator) | **Justified** - traceably documented | ADR-007, `docs/architecture_decisions.md` |
| 6 | Cycle selection sample size | `target_cycle_count` / `max_cycles_to_scan` (config) | **Configurable, not yet finalized** - determines how representative the quality profile is | `configs/example_pipeline.yaml`, `src/preprocessing/cycle_selection.py` |
| 7 | Minimum samples per signal | Position/Velocity/Current/Vibration >= 20; Pressure/Temperature >= 1 | **Not justified** - configured but no documented derivation | `configs/example_pipeline.yaml:41-49` |
| 7 | Consecutive-cycle block | Only consecutive "good" cycles accepted | **Structural only** - checks structural consistency, not physical signal quality | `validation_cycle_selection.py` |
| 8 | Quality metrics (missing channels, sampling rate, coverage ratio, time gaps) | Computed, not thresholded | **Exploratory / non-rejecting** - this is the data the Level-4 decision-tree thresholds must be derived from | `cycle_quality_profiler.py` |

## 3. Open questions still to clarify (see `t1000_wochenplan.md`)

- [ ] Derivation of `movement_threshold = 1.0` (duplicated 3x in code, no documented justification)
- [ ] Session-gap 3600 s: ADR-006 "Accepted" vs. code comment "exploratory" - which is current?
- [ ] Velocity scaling (blocks Variant B of the standstill/idle definition)
- [ ] Minimum session size N (proposed: 100)
- [ ] Cycle duration confirmed at ~3.1 s (older figure of 1.81 s was outdated)

## 4. Status note (2026-07-17)

Stage 8 (Cycle Quality Profiling) is currently being run at full scale
(`cycle_selection.target_cycle_count` / `max_cycles_to_scan` raised from the
default 100-cycle test values) to produce real distributions for the
Level-4 threshold derivation. Results will be added here once the run
completes.
