# Handoff: Actuator Lifetime Dashboard (D32/Versuch1)

Date: 2026-07-15
Workspace: `/home/ita/t1000` (all created files stay under here)
Data source (read-only): `/home/ita/data/ERA/D32_Nr13_14_15`

## Task
Build a single self-contained HTML dashboard to explore/compare cycles of
the D32/Versuch1 endurance test and spot wear/drift/degradation over its
~6-month lifetime. Redesigned UX from scratch (existing
`cycle_overlay_report.html` was only used as a reference for data-loading
patterns, not layout).

## Deliverable
`/home/ita/t1000/cycle_overlay/output/actuator_lifetime_dashboard.html`
(~7.1 MB, single file, opens directly via double-click — no local server
needed, since all data is inlined as JS and only Plotly.js is loaded from
CDN). Verified with Playwright/Chromium (headless): loads with zero
console/page errors, all interactions tested (tab switch, random-N
sample, add-by-ID, opacity slider, channel toggles, legend highlight/
hide, dark mode, reset zoom). Screenshots looked clean in both themes.

## Scope decision (asked user, confirmed)
User chose: **Versuch1 only**, but with extra channels beyond
Drive-only: velocity, position, current, **plus Messrack pressure and
Wago motor/spindle_nut/fixed_bearing_actuator temperature**.
Versuch2/Versuch3 were explicitly out of scope for this session.

## Data facts (Versuch1, discovered this session)
- 8,658,098 total Magnetschalter_Counter cycles over 184 days
  (2025-12-18 → 2026-06-20); 7,690,500 are "active" (dist_to_pause≥10,
  i.e. away from the ~99 pauses), rest excluded from all stats.
- Drive velocity/position/current sampled at 20 Hz (0.05s); Messrack
  pressure & Wago spindle_nut temp at ~16 Hz; Wago motor & fixed_bearing
  temp at ~1 Hz. Median cycle length ≈ 1.8s (~35-37 samples/cycle for the
  fast signals).
- Units taken as-is from `units.parquet` metadata (velocity=m/s,
  position=m, current=A, pressure=Pa, temp=°C) even though raw magnitudes
  look physically odd (velocity ~±70,000, position 0–200) — very likely
  unconverted raw sensor/encoder units upstream, but per project
  convention ("keep axis labels honest to source units") no rescaling
  was invented. Flagged in the dashboard footer.
- No force/torque channel exists. "Hysteresis loop area" in the derived
  metrics table is a **current-vs-position loop area proxy** (shoelace
  formula), clearly not a literal force-position hysteresis loop.

## Why not embed all 8.66M cycles
Embedding every cycle's raw waveform is infeasible in one HTML file.
Instead, built a 3-stage pipeline that stays honest and labeled about
this constraint in the UI itself:
1. **`extract_cycle_stats.py`** — DuckDB ASOF JOIN of the 7 continuous
   signals against the cycle-boundary table (from the already-cached
   `output/counter_v1_annot.parquet`), producing one row per cycle
   (min/max/mean/peak) for ALL 8.66M cycles → `output/cycle_stats_full.parquet`
   (~57s total runtime, fast because DuckDB streams the parquet glob
   without materializing raw 300M-row tables in Python).
2. **`build_dashboard_data.py`** — from that per-cycle table, produces:
   - `output/trend.json`: 3,000 chronological buckets (mean/p10/p90 per
     metric) across ALL active cycles → powers the Overview trend chart.
   - `output/pool.json`: 1,500 cycles evenly sampled across the full
     active-cycle range, each with full-resolution waveforms (vel, pos,
     cur, pressure, spindle_temp) plus derived metrics (peak vel, stroke,
     peak current, duration, loop area, deviation-from-reference). This
     pool is the **only** set of cycles selectable in the comparison view
     (labeled explicitly in the UI: "1,500 cycles evenely sampled across
     the full test life ... representative subset, not literally any of
     the 8.66M"). Cycle-ID search snaps to nearest pool cycle.
   - `output/meta.json`: summary counts/timestamps.
   - Waveform extraction batches ~150 non-contiguous cycle windows per
     SQL query (`WHERE (time BETWEEN a AND b) OR (...)  ...`), same
     pattern the original build_report.py used — fast due to row-group
     pruning on sorted `time`.
3. **`build_html.py`** — injects the 3 JSON files as inline `const`
   declarations into `dashboard_template.html` (placeholders
   `__META_JSON__` / `__TREND_JSON__` / `__POOL_JSON__`) to produce the
   final single-file HTML.

Regenerate everything with (from `cycle_overlay/`, using its `.venv`
which has duckdb/pandas/pyarrow):
```
.venv/bin/python extract_cycle_stats.py     # ~1 min
.venv/bin/python build_dashboard_data.py    # ~1 min
.venv/bin/python build_html.py              # instant
```

## Dashboard features implemented
- **Overview tab**: 8 lifetime stat cards (active/total cycles, peak
  velocity, stroke, peak current, mean pressure, motor temp, cycle
  duration, test duration/date range) + a trend chart with per-metric
  toggle chips (11 metrics) and a 10th–90th percentile shaded band. When
  >1 metric is selected, each is **min-max normalized to its own 0–100%
  range** (important fix — raw units differ by orders of magnitude,
  e.g. velocity ~1e4 vs position ~1e2, so without normalization smaller
  series were invisible on a shared axis); tooltip always shows the true
  raw value.
- **Cycle Comparison tab**: left control panel (cycle-ID multi-add,
  random-N sampler, reference-cycle picker, opacity slider, channel
  toggle chips for 5 channels, click-to-highlight/shift-click-to-hide
  legend list) + main area with 5 synchronized subplots (one per active
  channel, x = time-within-cycle in ms) and a derived-metrics table
  (duration, peak velocity, stroke, peak current, loop area, deltas vs
  reference cycle). Colors use the Okabe-Ito colorblind-safe palette
  (`colorFor()` in the template), cycling with lightness shifts beyond 8
  series. Light/dark theme toggle re-renders both Plotly charts with
  matching colors.

## Key gotchas / notes for next session
- DuckDB **ASOF JOIN** (`ON v.time >= b.time`, matches each raw sample to
  the latest boundary ≤ its time) is the efficient way to bin ~300M rows
  into ~8.6M per-cycle aggregates without ever loading the raw tables
  into pandas — much simpler and faster (~10s/signal) than the
  searchsorted approach `build_report.py` used for small windows.
- `output/counter_v1_annot.parquet` (from the prior session) was reused
  as-is for cycle boundaries/pause annotation — do not regenerate unless
  the pause-detection logic changes.
- The multi-metric trend chart normalization was a real bug caught only
  by rendering + visually inspecting a screenshot (Peak velocity's ~1e4
  scale made Max position's ~1e2 scale look flat-lined at zero) — always
  screenshot-check any new multi-series/mixed-unit chart before calling
  it done.
- Validated with Playwright (`npm install playwright && npx playwright
  install chromium --with-deps`, then a headless script) since no
  browser was otherwise available in this environment. This is a good
  general pattern for verifying future generated HTML/JS deliverables in
  this sandbox — install was ~180MB/couple minutes, cleaned up after.

## Next steps (not done, possible future asks)
- Versuch2/Versuch3 extraction (same pipeline, swap signal IDs from
  `nodes.parquet`/`signal_data_point_rel.parquet`, node parents
  `f7efd31b...` / `9ff5e9d1...`) for cross-run comparison.
- Vibration/ESP32 signals (6.25 kHz) intentionally left out — would need
  FFT/PSD-per-cycle or RMS-trend treatment, not raw overlay, as noted in
  the prior handoff.
- Could add an explicit "raw vs normalized" toggle on the trend chart if
  the user wants literal units back for single-metric inspection (single
  metric already renders un-normalized).
