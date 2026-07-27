# Copilot Prompt — Data Analysis Run for Decision Tree Grounding

## Context
I need a new analysis run on a single representative test trial (D32/D63 endurance test data) to derive concrete, physically grounded thresholds for my Decision Tree / Data Pool criteria. This feeds directly into tomorrow's meeting (27.07.) — I need numbers, not just plots.

Use the existing environment:
- Fatemeh's pipeline: `/home/ita/MasterThesis`
- venv: `/home/ita/ERA-NAS/.venv/bin/python`
- Raw/external data: `/home/ita/ERA` and `/home/ita/ERA-NAS`
- Relevant existing script: `validation_cycle_selection.py`
- Existing outputs to reuse if available: `pool_cycles.parquet`, `preprocessing_decision_tree.html`

Select **one representative trial** with a complete session (no major gaps) as the basis for this run. State which trial/file you used.

## Tasks

For each task: compute the metric, produce the relevant plot/histogram, and report the concrete numeric result (not just "looks fine"). Flag anything that contradicts existing assumptions (e.g. 3600s Session-Gap threshold, Position > 1.0 Movement Threshold, 1.81s vs 3.1s cycle duration).

1. **Sampling rate per signal**
   - Compute the Δt distribution per channel (position, current, velocity if present)
   - Check whether all channels share the same sampling rate or differ
   - Report: nominal Δt per channel, variance/jitter

2. **Position end-stops, offset, control deviation**
   - Build a histogram of position values at cycle end-stops across many cycles
   - Derive: typical offset, spread (std/percentiles), suggested hard position limits

3. **Noise band at standstill + encoder resolution**
   - Identify standstill windows (velocity ≈ 0 or position flat)
   - Compute σ of position signal within standstill windows
   - Check for quantization steps (discrete peaks) indicating encoder resolution
   - Report: noise band width, quantization step size

4. **Gap distribution**
   - Compute Δt histogram between consecutive samples/sessions across the full trial
   - Check for bimodal separation between micro-gaps (normal recording gaps) and session gaps (real interruptions)
   - Report: where the natural separation point falls, and whether 3600s is justified or should change

5. **Cycle structure, hold time, cycle duration**
   - Segment cycles and build a cycle-duration histogram
   - Report: mean/median cycle duration, hold-time duration
   - Explicitly resolve: is the true cycle duration ~1.81s or ~3.1s? Explain the discrepancy (e.g. hold time included/excluded, single trip vs round trip)

6. **Current magnitude per phase**
   - Segment each cycle into start-up / travel / standstill phases
   - Report peak and RMS current per phase

7. **100-cycle overlay visualization**
   - Build an HTML visualization overlaying 100 cycles: position and motor current on a shared time axis with two Y-axes
   - Purpose: support the decision on where to cut a cycle (start/end point)
   - Save as a standalone HTML file

## Output format
- One markdown context file summarizing all numeric results (for me to hand to Claude for thesis/decision-tree drafting)
- Any plots as separate image files, referenced by filename in the markdown
- The 100-cycle HTML visualization as a separate file
- Explicitly list: which results confirm current assumptions, which contradict them, and which remain unclear/need more data

## Constraints
- Do not modify or delete any raw data files
- Do not change `validation_cycle_selection.py` unless needed to extract intermediate signals — if you do, note the diff separately
- Keep the run reproducible: log which trial/file, which script version, which parameters were used