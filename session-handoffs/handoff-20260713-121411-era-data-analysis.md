# Handoff: ERA Watch Data — Best Dataset & Cycle Analysis

## Context
Task: analyze datasets under `/home/ita/ERA` to find which one has the longest,
most "fluent" (gap-free) continuous data stream, and determine cycle start
times and cycle duration.

## Environment notes
- No pyarrow/pandas in system Python; a working venv with pyarrow 24.0.0 and
  pandas 3.0.3 exists at `/home/ita/ERA-NAS/.venv/bin/python` — use that
  interpreter for any further parquet analysis in this session.
- A separate, related project `/home/ita/ERA-NAS` already has stop-analysis
  tooling (`run_stop_analysis.py`, `run_parallel_stop_analysis.sh`,
  `reports/<dataset>/...`) — not yet cross-checked against this task's
  findings; could be a source of an existing/authoritative cycle-detection
  method worth comparing against.
- `/home/ita/ERA` also contains existing docs worth reusing rather than
  re-deriving: `V1_V2_DATA_COMPARISON.md` (V1 vs V2 schema/row/rate
  comparison) and `lazy_load_example.md` (pyarrow.dataset lazy-loading
  patterns, important to avoid full eager loads that crash kernels on large
  exports).

## Dataset layout (parquet, hive-partitioned by `signal_id=<uuid|int>`)
Each recording root typically has: `nodes.parquet` (node hierarchy /
device tree with `parent_node` links), `signal_data_point.parquet` (main
time series, UUID signal ids), `signal_data_point_rel.parquet` (signal_id →
node_id → unit mapping), `signal_data_point_rel_int.parquet` +
`vibration.parquet` (int signal ids, high-rate vibration), and sometimes
`countertable.parquet` (separate small-int signal_id space, cumulative
counters, event-driven sampling, in V3/V4/V5/V6 of `ERAP_EXT_003`).

Units seen in `signal_data_point_rel.parquet` include: `position`,
`counter`, `velocity`, `current`, `pressure`, `temperature`, `voltage`,
`boolean`, `x/y/z_vibration`, gyro axes. The `counter` unit is a
monotonically-incrementing per-cycle counter (increments by exactly 1 per
completed cycle) — this turned out to be the most reliable signal for
gap/fluency and cycle-timing analysis (better than diffing `position`
waveforms).

Node paths for `ERAP_EXT_004` experiments follow pattern
`<Dxx> / Versuch<N> / <ESP32|Wago|Drive>` — `Wago` counters were clean;
`ESP32` channels labeled "counter" were actually noisy oscillating raw
values, NOT cumulative counters (learned this the hard way — don't assume
unit label "counter" always means monotonic increment; verify via
`diff().value_counts()` first).

## Method used
1. Enumerated all recording roots with `signal_data_point.parquet` (see
   script logic below) across: `ERAP_EXT_003` (+V2..V6), `ERAP_EXT_004`
   (6 experiment folders: NAS1/NAS2 × D32/D63/D100), `ERAP_EXT_005`.
2. For each, loaded `signal_data_point_rel.parquet`, found signals with
   `unit == 'position'`, computed time-gap statistics (median dt, gap
   threshold = 5×median, longest gap-free run) — this is a reasonable first
   pass but position signals had many small sampling irregularities.
3. Refined by using `unit == 'counter'` (Wago) signals instead: checked
   `value.diff()` — a truly clean counter has `diff() == 1` for every row
   with **zero** exceptions across the whole recording span. This is a much
   stronger and simpler fluency test than gap-thresholding a continuous
   signal.
4. Compared all `ERAP_EXT_004` Wago counters (see results table below) and
   picked the cleanest + longest.

## Result: best dataset found
**`ERAP_EXT_004/2025_08_27_NAS2_D32/D32_20250827_111906`**
Signal: `D32 / Versuch3 / Wago`, signal_id
`ce3ecefc-2b1f-454f-8baf-a3f3b9809132` (unit `counter`).

- Time range: 2025-08-12 05:52:05 → 2025-08-27 08:14:58 (~15.1 days)
- 256,481 rows, `value.diff()` is exactly `1` for **every single row** — zero
  gaps in the entire recording.
- **Cycle start** = timestamp of each counter increment.
- **Cycle duration** = time delta between consecutive increments:
  median 5.05 s, mean 5.09 s, IQR ≈ 5.05–5.06 s, with occasional longer
  pauses (up to ~50 min / 2993 s) between test batches (likely
  breaks/maintenance) that don't break counter continuity.

Runner-up datasets with the same zero-gap property over the same 15-day
window (2025-08-12 → 2025-08-27): `NAS2_D32/Versuch2`, `NAS2_D63/Versuch2`,
`NAS2_D100/Versuch1-3` (all Wago counters). Older/longer recordings (V3, V4,
V5, V6 of `ERAP_EXT_003`, and `NAS1_*` of `ERAP_EXT_004`) span more days but
have from tens to thousands of gaps — much less fluent.

Full comparison table (gaps count, span, row count) for all 12 scanned
roots was printed to terminal during the session but not saved to disk —
if needed again, rerun the survey script logic described above via
`/home/ita/ERA-NAS/.venv/bin/python`.

## Not yet done / possible next steps
- No CSV/file artifact of cycle start times + durations was written to disk
  yet — user asked "want me to extract the full cycle-start/duration table
  (CSV)?" and had not answered before this handoff.
- Could cross-validate cycle counter findings against the `position`
  ("Drive") signal for the same Versuch to sanity-check that each counter
  increment aligns with a real physical motion cycle (rise/fall of
  position).
- Could compare against `/home/ita/ERA-NAS/stop-analysis` tooling and
  `reports/` outputs to see if this dataset was already analyzed there and
  whether conclusions match.
- `ERAP_001_003_V4` (vibration-only, no `signal_data_point.parquet`) and
  `ERAP_EXT_005` (position signals too small/short) were not usable for this
  cycle analysis and were excluded.

## Suggested skills for next session
- **domain-modeling**: to formally pin down terminology (e.g. what exactly
  a "cycle" means physically — one counter increment vs. one full
  actuator round-trip — and record it as part of a ubiquitous language for
  this ERA dataset domain), especially before building further tooling on
  top of these conclusions.
- **diagnosing-bugs**: if the ESP32 "counter" mislabeling (noisy raw value
  vs. true monotonic counter) needs deeper root-cause investigation into
  the data export pipeline.
- **tdd**: if the next step is to turn the ad-hoc survey script into a
  proper reusable cycle-extraction tool/CLI with tests.
