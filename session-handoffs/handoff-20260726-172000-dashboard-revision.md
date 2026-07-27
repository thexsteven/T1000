# Handoff: Dashboard revision attempt

The requested dashboard revision was investigated. `scripts/analyze_representative_d63_trial.py` is the generator; it imports matplotlib, numpy, pandas, plotly, pyarrow and builds dashboard HTML in `build_dashboard`; Plotly overlay uses `include_plotlyjs=True` at line 274. Existing output remains generated at `outputs/representative_d63_trial_20260726`.

A rewrite was attempted but the generated output did not update despite the script compiling; do not assume sections 3–7 are complete. The working tree contains pre-existing unrelated modifications (`src/cycle_overlay/build_report.py`, notes, vendored Plotly). Do not modify protected files. Next session should inspect `git diff -- scripts/analyze_representative_d63_trial.py`, run the generator with visible timestamps, and verify the output markers.
