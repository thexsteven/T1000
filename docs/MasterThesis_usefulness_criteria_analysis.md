# Analysis: "Pool of Useful Data" Criteria in MasterThesis Repo

Source repository analyzed: `/home/ita/MasterThesis`
Author of analyzed thesis code: Fatemeh Heydari

**Note:** No repo-wide term "standstill" exists. This is a preprocessing/cycle-extraction
pipeline (not yet an ML "usefulness" classifier), authored by Fatemeh Heydari. Below is the
evidence-based breakdown, structured by the 5 requested points.

---

## 1. Filter Criteria (all found "usefulness"/validity logic)

| Criterion | Location | Logic |
|---|---|---|
| **Movement threshold (cycle boundary)** | `src/preprocessing/cycle_detection.py:56,74` `detect_candidate_cycles()` | Position `value > 1.0` (default `movement_threshold`) = "moving"; a cycle starts on the `<=1.0 → >1.0` crossing, ends on `>1.0 → <=1.0`. Incomplete edge cycles are dropped (lines 60-63, 91-92). |
| **Recording-session gap** | `src/preprocessing/session_detection.py:28,140` | `DEFAULT_SESSION_GAP_SECONDS = 3600.0` (1 hr). Timestamp gap `> threshold` starts a new session; used to prevent cycle detection spanning recording interruptions. |
| **Multi-sensor validation readiness** | `src/preprocessing/validation_cycle_selection.py:38-89` `_evaluate_cycle_quality()` | A cycle is `is_validation_ready` only if every `required_signals` entry exists (non-empty) AND has `>= minimum_samples[signal]` rows (configured in `configs/example_pipeline.yaml:41-49`, e.g. position/velocity/current/vibration ≥20 samples, pressure/temperature ≥1). |
| **Consecutive-block selection** | `validation_cycle_selection.py:101,166-186` | `require_consecutive=True` resets the candidate block on any failed cycle — only contiguous "good" cycles (same session) are accepted for the validation subset. |
| **Exactly-one-signal sanity check** | `scripts/analyze_position_cycles.py:49-52`, `src/analysis/analyze_dataset.py:212-215` | Experiments are skipped/raise if `len(position_signals) != 1`. |
| **Missing/invalid row drop** | `cycle_detection.py:39-45` `_prepare_position_frame()` | Rows with NaN `time`/`value` are dropped before detection (logged, not silently kept). |

---

## 2. Standstill Detection

No dedicated "standstill" concept (no velocity-near-zero window detector, no explicit
rest-phase labeling). The only related mechanism is the **binary moving/not-moving
classification inside `detect_candidate_cycles`** (`cycle_detection.py:74`,
`is_moving = prepared_df["value"] > movement_threshold`). This is used purely to find
cycle start/end edges on the Position signal, not to characterize or filter out standstill
segments as "useless." Velocity and Current signals exist and are extracted
(`multi_sensor_cycle_extraction.py`) but are never used for a stationary/idle detection.

---

## 3. Rationale Provided per Criterion

- **Movement threshold = 1.0**: No numeric justification anywhere. Explicitly flagged as
  provisional: `scripts/analyze_position_cycles.py:23-25` — *"Temporary exploratory
  threshold that must be validated from the observed cycle statistics and annotated plots
  before it becomes a final rule."* Same value repeated in
  `scripts/analyze_multi_sensor_cycle.py:32` and `configs/example_pipeline.yaml:6` with no
  derivation.
- **Position as reference signal for cycles**: Justified by supervisor input — ADR-007 in
  `docs/architecture_decisions.md` (lines 374-413) and `docs/thesis_pipeline.md:295-303`:
  *"the electrical actuator is position-controlled and follows a predefined position
  trajectory."*
- **1-hour session gap threshold**: Flagged as exploratory too —
  `scripts/analyze_recording_sessions.py:20-21` — *"This 1 hour gap threshold is
  exploratory and must be validated using the resulting session statistics before it is
  treated as a final rule."* ADR-006 (`architecture_decisions.md:341-370`) claims it is
  "based on the empirical timestamp analysis," but no analysis output/threshold-derivation
  number is shown in the ADR itself.
- **No interpolation/resampling ("native sampling")**: ADR-008
  (`architecture_decisions.md:416-464`) — decision to preserve native timestamps rather
  than resample, justified only by differing per-sensor sample counts, not tested against
  feature-engineering needs yet.
- **Minimum sample counts per signal (20 vs 1)**: `configs/example_pipeline.yaml:41-49` —
  no comment/rationale for why position/velocity/current/vibration need ≥20 but
  pressure/temperature only ≥1 (likely reflects their lower native sampling rate noted in
  `implementation_log.md:332-352`, but this link is never stated explicitly in code or
  docs).

---

## 4. Gaps & Ambiguities

- **`movement_threshold=1.0`** is a magic number duplicated in 3 places
  (`cycle_detection.py` default, `analyze_position_cycles.py`,
  `analyze_multi_sensor_cycle.py`, `example_pipeline.yaml`) with zero unit/physical
  justification (position unit isn't stated — likely mm or similar) and explicitly marked
  "temporary."
- **Session gap = 3600s** also explicitly marked exploratory but is already the hard-coded
  default used in production stages (`pipeline.py`, `analyze_dataset.py`) — i.e., an
  unvalidated threshold has propagated into the "accepted" pipeline (ADR-006 marks it
  "Accepted" while the script comment calls it exploratory — inconsistency between ADR
  status and script wording).
- **No "usefulness" score for cycles beyond structural completeness** — a cycle is
  currently judged "ready" only by *signal presence/sample count*
  (`validation_cycle_selection.py`), not by physical plausibility (e.g., does position
  actually change, is duration in a sane range, are there sensor saturation/outlier
  values). Cycle duration/position-range statistics are computed (`cycle_detection.py`
  columns) but never used as a filter — they're descriptive only.
- **Standstill/idle phases are not distinguished from valid short cycles** — a "cycle" as
  short as one sample above threshold would be accepted; no minimum-duration or
  minimum-displacement filter exists.
- **Signal Quality Assessment stage is "In Progress"/undefined** —
  `docs/thesis_pipeline.md:366-384` (Stage 8) lists intended checks (missing channels,
  timestamp consistency, sampling behaviour) but no implementation exists yet in `src/` for
  this stage beyond the validation-selection sample-count check.
- **Inconsistent unit/threshold semantics**: `movement_threshold` compares raw Position
  value to an absolute number without reference to the signal's dynamic range
  (`implementation_log.md` reports peak Position ≈85), so "moving" vs "not moving" is a
  fixed cutoff at ~1% of typical peak, chosen arbitrarily.

---

## 5. Suggestions for Refinement

Special focus on the "running" vs. "standstill" data problem:

- **Define standstill explicitly via a windowed criterion**, not just a static Position
  threshold: e.g., over a sliding window of *N* samples or *T* seconds, standstill =
  `max(position) - min(position) < Δ_pos` AND/OR `|velocity| < ε_v` for the whole window.
  This directly targets "position values staying constant" and is more robust than a
  single-sample threshold crossing.
- **Use Velocity (already extracted) as a corroborating signal** rather than relying
  solely on Position — a position-based threshold conflates "small motion" with "no
  motion"; velocity near zero is a more direct physical proxy for standstill and is
  already loaded per cycle (`multi_sensor_cycle_extraction.py`), just unused for this
  purpose.
- **Add a minimum-duration / minimum-displacement filter** to `detect_candidate_cycles` so
  trivially short "cycles" (noise crossing the threshold) are rejected — currently
  duration/position range are computed but not enforced (`cycle_detection.py:106-110`).
- **Validate the two "exploratory" thresholds (`movement_threshold`, session gap) against
  the underlying distributions** already available — `time_gap_analysis.py` computes gap
  percentiles; `movement_threshold` could similarly be derived from the Position signal's
  noise floor at rest (e.g., percentile-based, not fixed at 1.0).
- **Reconcile ADR status with code comments**: ADR-006 says "Accepted" for the 1-hour gap
  while the script still calls it "exploratory" — pick one source of truth and document
  the empirical basis (e.g., attach the actual gap histogram/percentile numbers cited).
- **Extend Signal Quality Assessment (Stage 8) into a concrete filter** combining:
  sample-count sufficiency (existing), signal-range sanity (e.g., reject cycles where
  Position never exceeds `movement_threshold` meaningfully — a residual standstill
  artifact), and duration bounds derived from the reported typical cycle duration
  (~3.1s, `implementation_log.md:279-281`) to flag outlier cycles as candidates for
  exclusion from the "useful pool."
