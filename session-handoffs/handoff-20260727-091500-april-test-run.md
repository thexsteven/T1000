# Handoff: April 2026 test run

## Verified

- `Versuch1 = Nr. 7` is confirmed by `Lifetime_report_endurance_test.xlsx`,
  sheet `D63_Nr_7_8_9`, entry dated 2026-03-23.
- Test date 2026-04-03 completed successfully with the wrapper and
  `stop_after: cycle_quality_profiling`.
- Successful output: `outputs/april_slice_q7s63118/Versuch1/20260727_085413/`.

## Measurements

- Slicing of the 2-minute-overlapped source window: 53.83 s; 83,933,992 source
  rows selected.
- Pipeline runtime: 1,101.53 s (18.36 min).
- Peak RSS: 3,091,048 kB (~2.95 GiB).
- Cycles: 23,642 total; 131 boundary cycles.
- Measurement batches: 48 files, 10,123,611 rows, 63,691,198 bytes (~60.7 MiB).
- Median rates: current/position/velocity 20.3029 Hz; pressure 16.7472 Hz;
  temperature 0.9671 Hz; vibration X/Y/Z 393.871 Hz on 1,310 cycles only.
- `quality_profiling/` is populated; `features/` is empty because the selected
  stop point ends before feature engineering. The stop point is effective.

## Decision pending user Go

- Do not start the full April run yet.
- Recommend five weekly chunks rather than 30 daily chunks or one month run:
  the measured peak is modest, but a full month would increase cycle and long
  measurement state substantially; weekly chunks preserve restartability while
  limiting artificial boundaries and repeated pipeline overhead.
- Keep the required two-minute overlap, mark boundary cycles, exclude them from
  aggregates, and deduplicate using global chunk/session/cycle keys.
