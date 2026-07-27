# Handoff: Full D63 experiment dashboard

Generated a full-length equivalent of `outputs/representative_d63_trial_20260726` for `/home/ita/data/ERA/D63_Nr13_14_15`.

## Output

`outputs/d63_full_experiment_20260727/`

The directory contains the offline dashboard, 100-cycle overlay, four PNG histograms, `results.json`, and `analysis_context.md`.

## Scope

- Dataset: D63_Nr13_14_15, Versuch1, first Drive node
- Signal IDs: position `61443a95-8e2c-4d22-8f76-54d22bd6903f`, velocity `c486972f-a221-456b-b3a6-ca6eac680829`, current `e52319f7-adb0-44e8-aa9d-b31697f26768`
- Timestamp span: 2026-02-12 07:18:46.910 to 2026-06-19 12:42:44.489 (127.225 days)
- Position samples: 202,080,940
- Detected cycles: 1,738,286
- Full-experiment mode splits cycles at gaps over 3,600 seconds and detects cycles independently per recording session.

## Implementation

`scripts/analyze_representative_d63_trial.py` now supports `--full-experiment`. The default representative-block behavior remains unchanged. Full mode uses the whole requested interval, while preserving session boundaries for cycle detection.
