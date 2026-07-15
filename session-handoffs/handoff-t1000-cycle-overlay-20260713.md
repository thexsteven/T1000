# Handoff: D32 cycle-overlay visualization (ERA endurance-test data)

Date: 2026-07-13
Workspace: `/home/ita/t1000` (all created files must stay under here)
Data source (read-only, do not modify): `/home/ita/data/ERA/D32_Nr13_14_15`

## Task
Build an HTML report that visualizes how individual motion "cycles" of a
linear-actuator endurance test (dataset D32, Versuch1/2/3) look, overlaid
and side-by-side, to help spot short-term repeatability and long-term
drift/wear across a ~6-month run.

## Dataset summary
- Parquet-based dataset with 3 test runs: `D32 > Versuch{1,2,3}`.
- Key tables: `nodes.parquet` (hierarchy), `units.parquet`,
  `signal_data_point_rel(.parquet/_int)` (signal_id -> node -> unit),
  `signal_data_point.parquet` (main float signals, partitioned by
  `signal_id`, weekly sub-files, ~317M rows for Drive velocity alone),
  `vibration.parquet` (6.25 kHz vibration signals, partitioned by small
  int `signal_id`, ~525M rows per sensor).
- Per Versuch signals: Drive velocity (m/s) & position (m) & current (A),
  Wago motor/spindle_nut/fixed_bearing_actuator temperature (°C),
  Messrack pressure (Pa), ESP32 X/Y/Z vibration, Sensor_1-4 vibration,
  Analog_1 current, and **Wago `Magnetschalter_Counter`** — a magnetic
  switch counter that increments once per stroke/cycle (median cycle
  length ≈ 1.84s). This counter is the cycle-boundary source of truth.
- The experiment was paused ~99 times over its life (gaps from ~12s up to
  ~19h); cycle windows for plotting must be chosen away from these pauses
  (buffer of 10 cycles used) to avoid transient/restart artifacts.
- Signal IDs used so far (Versuch1): Drive velocity =
  `30fc7262-528d-4e79-94f0-e7124f489f48`, Drive position =
  `8663194d-7e7c-4caf-b1a2-7ce991f7a46d`, Magnetschalter_Counter =
  `9676f2db-0831-476d-bcf9-681c70a3fb37`.

## What exists now
Project dir: `/home/ita/t1000/cycle_overlay/`
- `.venv/` — isolated Python venv (duckdb, pandas, pyarrow, plotly installed).
- `build_report.py` — the report generator (only script needed to
  regenerate the HTML from the cached parquet files in `output/`).
- `output/cycle_overlay_report.html` — the deliverable, ~1.2MB standalone
  HTML (Plotly via CDN). Currently covers **Versuch1, Drive velocity &
  position only**, with 5 views:
  1. Single representative cycle.
  2. 100 consecutive cycles overlaid (aligned to cycle start, colored by
     cycle order).
  3. ~100 cycles evenly spread across the whole run, overlaid (colored by
     real date via colorbar).
  4. 100 consecutive cycles shown in a row on real elapsed time
     (~184s, continuous, no normalization).
  5. 100 randomly-sampled *active* cycles (pause-avoided) shown as a
     "filmstrip": each cycle in its own fixed-width slot, light banding,
     x-axis/hover shows real date per cycle (random seed=42, reproducible).
- `output/*.parquet` — cached intermediate data (counter series with
  pause/safety annotations, and extracted velocity/position windows for
  each of the 5 views) so the report can be rebuilt quickly without
  rescanning the raw dataset.
- `output/*.pkl` — cached cycle-boundary timestamp lists per view.

## How to view it
The HTML is too large to comfortably open in the VS Code editor. Serve it
instead:
```
cd /home/ita/t1000/cycle_overlay/output && python3 -m http.server 8000 --bind 127.0.0.1
```
A server was left running in the background on port 8000 during this
session (PID may no longer be alive in a fresh session — restart it if
needed). In VS Code, use the **Ports** tab to forward port 8000 and open
it in the browser, then click `cycle_overlay_report.html`.

## Key implementation notes / gotchas
- Data extraction uses **DuckDB** directly on the parquet globs with
  `WHERE time BETWEEN ... OR (time BETWEEN ...) ...` clauses — this
  enables row-group pruning on the sorted `time` column so only the
  relevant weekly files/row-groups are scanned (sub-2s per 100-window
  extraction instead of reading 317M rows).
- Cycle boundaries always come from the `Magnetschalter_Counter` signal,
  never inferred from velocity zero-crossings.
- "Safe" cycles = `dist_to_pause >= 10` (rows), computed in
  `output/counter_v1_annot.parquet`.
- For filmstrip-style plots (non-contiguous cycles placed in a row), a
  NaN separator row is inserted between each cycle's data so Plotly
  doesn't draw a connecting line across the artificial gap
  (`_break_on_cycle` helper in `build_report.py`).
- Units are read from `units.parquet` (`VEL_UNIT = "m/s"`,
  `POS_UNIT = "m"` constants at top of the script) — keep axis labels
  honest to source units if new signals are added.

## Next steps (not yet done)
- Only Versuch1 / Drive velocity+position has been built. Versuch2/3 and
  other signals (current, temperature, pressure, vibration) were
  discussed but not implemented.
- Vibration analysis would need a different approach (6.25kHz, too dense
  to overlay raw — user was told FFT/PSD-per-cycle or RMS trend would be
  more appropriate; not implemented yet).
- No interactive cycle-picker/slider built yet (mentioned as a possible
  future enhancement, not requested).
- User cares strongly about **clean, transparent-unit, easy-to-read
  layout** — validate any new chart against that bar before considering
  it done.

## Suggested skills for the next session
- No specialized skill from the current toolkit is a strong fit for this
  data-visualization/ETL task. If the next work involves designing a
  more elaborate/reusable extraction module (e.g., generalizing signal
  selection across Versuche), consider `codebase-design` to keep the
  `build_report.py` interface deep and simple rather than growing many
  ad-hoc parameters.
- If asked to add automated checks (e.g., regression-testing that cycle
  boundaries or extracted windows stay correct as the script evolves),
  consider `tdd`.
