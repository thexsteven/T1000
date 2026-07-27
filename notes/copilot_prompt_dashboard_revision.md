# Copilot Prompt — D63 Dashboard Revision (v2)

## 0. Environment constraints — read before doing anything

- **Do NOT use patch-based edits.** Patch application fails in this environment
  (`Failed to parse patch: The first line of the patch must be '*** Begin P…'`).
  Rewrite each affected file completely instead. Creating and overwriting whole
  files works reliably.
- Work in `/home/ita/t1000`. Activate `/home/ita/ERA-NAS/.venv/bin/activate`.
- **Do not touch** `src/cycle_overlay/build_report.py` or `build_html.py`.
  Those belong to the unrelated D32 pipeline.
- Plotly is **already vendored** at `src/cycle_overlay/plotly-2.35.2.min.js`
  (4.7 MB, verified). Do not download it again.

## 1. Locate and report the generator — do this first, then stop

The dashboard is `outputs/representative_d63_trial_20260726/d63_interactive_dashboard.html`.
It is produced by `scripts/analyze_representative_d63_trial.py`, which takes a
required `--output` argument.

Before changing anything:

1. Read `scripts/analyze_representative_d63_trial.py` in full.
2. Report: which helper modules it imports, where the Plotly figures are built,
   where the HTML document head is assembled, and where `include_plotlyjs` is set.
3. State the exact command needed to regenerate the dashboard.

Report this and wait for confirmation before continuing.

## 2. Offline safety — blocking issue, complete and verify before anything else

`grep -c "cdn.plot.ly"` on the current dashboard returns `1`. If the presentation
machine has no internet, every chart renders blank.

- Inline `/home/ita/t1000/src/cycle_overlay/plotly-2.35.2.min.js` into a single
  `<script>` tag in the document head. Use an absolute path.
- Set `include_plotlyjs=False` on every `fig.to_html(...)` call so the library is
  present exactly once.
- Regenerate the dashboard.

Verification — report all three results:

```bash
grep -c "cdn.plot.ly" outputs/representative_d63_trial_20260726/d63_interactive_dashboard.html   # must be 0
ls -lh outputs/representative_d63_trial_20260726/d63_interactive_dashboard.html                  # expect ~5 MB
python -c "print(open('outputs/representative_d63_trial_20260726/d63_interactive_dashboard.html').read().count('<script>'))"
```

Then stop and report. Do not start section 3 until this is confirmed working.

---

## 3. Overview tab — two additions

**3a. Gap distribution histogram**, placed directly above the "Detected continuous
recording blocks" table. This histogram is what produces that table, so it belongs
next to it.

- Log-scaled x-axis (Δt in seconds), so the sub-second sampling interval, the
  1.5–20 s band, and the ~21 h session break are all visible in one view.
- Mark the current 3600 s session-gap threshold as a labelled vertical reference line.
- Caption must state explicitly that the data shows **three** regimes, not two:
  normal sampling intervals, an intermediate band of 1.507–20.134 s interruptions,
  and the long session break. Note that the intermediate band is not covered by the
  current binary rule.

**3b. Cycle duration reconciliation**, as a text block in the summary card. State
this in words — do not leave it to be inferred from a chart:

```
Cycle period          ≈ 5.65 s   (60,901 cycles over 344,291 s of the selected block)
  Round-trip motion   = 3.737 s  (movement-threshold cycle duration, median)
  Hold at lower end   = 1.910 s  (median)
  → Single trip       ≈ 1.87 s
```

The previously referenced values of 1.81 s and 3.1 s are not in conflict with
3.737 s — they refer to a single trip and to a different segmentation respectively.
Verify the single-trip figure directly from the position signal rather than only
deriving it by subtraction, and state which method was used.

## 4. New tab: "Criteria & Data Quality"

The core of the meeting. Structure as **one card per criterion**, each containing:
the evidence chart, the current threshold value, a maturity status tag, and the
number and share of cycles that fail it.

Maturity tags — use verbatim, do not invent new ones:
`Begründet` · `Provisorisch` · `Strukturell` · `Inkonsistent` · `Nicht begründet` ·
`Statistically derived (not health-validated)`

| Criterion | Evidence chart | Current threshold | Tag |
|---|---|---|---|
| Movement threshold | Standstill noise histogram (position σ within standstill windows, plus quantisation steps if resolvable) | Position > 1.0 | `Nicht begründet` |
| Session / continuity | Gap histogram (link back to Overview) | 3600 s | `Inkonsistent` |
| Cycle duration plausibility | Cycle duration histogram with acceptance band marked | derive from p1/p99 of observed distribution | `Statistically derived (not health-validated)` |
| Stroke / end-stop plausibility | Position end-stop histogram | derive from observed spread | `Provisorisch` |
| Peak current plausibility | Peak current distribution per cycle | derive from observed spread | `Provisorisch` |

Reference PNGs for these charts exist in `outputs/representative_d63_trial_20260726/`
(`cycle_duration_histogram.png`, `gap_distribution_histogram.png`,
`position_endstops_histogram.png`, `standstill_noise_histogram.png`). Reproduce them
as interactive Plotly charts computed from the same underlying data — do not embed
the PNGs as images.

For the standstill-noise chart: allow zoom into a narrow value range, since the noise
band is expected to be small relative to the 190-unit stroke. State the measured σ
and, if discrete levels are visible, the apparent encoder quantisation step. This
chart is the evidence base for replacing the arbitrary `Position > 1.0` movement
threshold — make that connection explicit in the card caption.

**Rejection summary at the top of the tab.** A table and a stacked bar over time
showing, per criterion, how many of the 60,901 cycles would be rejected, plus the
count passing all criteria (the resulting data pool size).

Two statements must appear as visible on-page text:

- **All thresholds shown are provisional and pending review.** Prominent banner at
  the top of the tab, not a footnote.
- **No data is deleted.** Rejected cycles are flagged with a `rejection_reason`,
  raw files remain untouched, and the pool is only an index of passing cycles.
  This is the auditability argument and reviewers will ask about it.

Add a note that a spike in any single rejection category over time is an early
indicator of a sensor or recording fault — the stacked-bar-over-time chart is what
makes that visible.

## 5. Corrections and labelling

- `meta.end` is `2025-08-18T13:37:52.144` while `sessions[36].end` is
  `2025-08-18T13:37:55.470` (3.3 s apart). Determine which is correct, fix the
  generator, note the cause.
- `velocity_peak_abs` values around 62,978 are raw counts. Label every velocity axis
  explicitly as raw counts with unresolved scaling, and list velocity scaling as an
  open question in the Criteria tab rather than presenting it as a validated
  engineering unit.
- Add sampling-rate evidence: a small Δt-per-channel summary (nominal rate, jitter)
  in the Overview summary card. 20 Hz is currently asserted but not demonstrated.
- Verify the trial path: `meta.trial` points at a folder named `2025_08_27_NAS2_D63`
  while the data spans 2025-08-14 to 2025-08-18. Confirm whether this is a naming
  convention (e.g. export date) or a mismatch, and record the answer.

## 6. Output constraints

- Do not modify or delete raw data.
- Do not delete the existing dashboard — write the revised version alongside it or
  rely on git history.
- The output must remain a single standalone HTML file that opens with no running
  Python server and no network access.
- Log which script version and parameters produced the output.

## 7. Deliverables

1. Regenerated `d63_interactive_dashboard.html` (standalone, offline-verified)
2. Updated `scripts/analyze_representative_d63_trial.py` (and any helper modules it
   actually uses — report which)
3. A short markdown changelog listing: what changed, the numeric results newly
   surfaced (σ of standstill noise, quantisation step, derived acceptance bands,
   rejection counts per criterion, resulting pool size), and which of the four
   correction items in section 5 are resolved versus still open