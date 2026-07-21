# Copilot Prompt — ERA Preprocessing Pipeline: Visual Stage Reference (standalone HTML)

> Paste everything below the line into GitHub Copilot inside the `t1000` workspace.

---

## Role & goal
You are working inside the `t1000` workspace on the `flmc-ai` SSH remote. Produce **one single standalone HTML file** that visually explains **every stage of Fatemeh's 11-stage ERA preprocessing pipeline**, so that a test engineer or supervisor can understand at a glance (a) *what* each stage does and (b) *how well-justified* it is.

This file is a **companion / reference to the Confluence page** "Data Preprocessing — Criteria Maturity & Alignment Overview" and must stay consistent with it. It is a read-only explainer, not an interactive pipeline.

## Step 1 — Read the ground truth BEFORE writing any HTML
Cross-check two sources. **Do not invent behaviour.** Where the code and the overview disagree, show **both** and flag the discrepancy visibly on the affected stage card — do not silently pick one.

**Authoritative for wording of justifications & status tags:** the "Reference content" section at the bottom of this prompt (mirrors the Confluence overview).

**Authoritative for what the code actually does:** Fatemeh's pipeline under `/home/ita/MasterThesis` (raw data / artifacts under `/home/ita/ERA` and `/home/ita/ERA-NAS`). At minimum inspect:
- `session_detection.py` — Stage 4, the 3600 s session gap
- `cycle_detection.py` — Stage 5, the `Position > 1.0` movement threshold
- the multi-sensor extraction step — Stage 6
- the cycle quality profiling step — Stage 7 (stroke-range metrics)
- the validation-rule-generation step — Stage 8 (Median + MAD, limit 3.5, quantile fallback 0.01 / 0.99) and `validation_thresholds.json`
- the dataset-validation step — Stage 9
- `docs/architecture_decisions.md` — ADR-006 (session gap), ADR-007 (reference signal)

For each stage, extract from the code: the **concrete parameter/threshold actually used**, the **input consumed and output produced**, and whether the value is **hard-coded, config-driven, or data-derived**. If you must introspect a parquet/JSON artifact, use the venv `/home/ita/ERA-NAS/.venv/bin/python` and **lazy-load only** — never eager-load large parquet exports (they crash the kernel).

**Discrepancy handling:** if a code value differs from the overview — e.g. the log's reported ~3.1 s typical cycle duration vs. the 1.81 s round-trip used in project context — surface it as a small "⚠ discrepancy" note on that stage. Do not resolve it.

## Step 2 — Build the visualization

**Layout:** a single **vertical pipeline flow**, stages 1 → 11 top to bottom, connected by a visible flow line / arrows, each stage a card in order.
- Planned stages (10, 11) rendered visually distinct: dimmed and/or dashed border.
- Do **not** add gap analysis, action items, or the standstill/velocity open-items table — those are intentionally out of scope. Keep the file focused on the 11 stages.

**Each stage card shows exactly these four things:**
1. **Stage number + name**
2. **What it does** — a 1–2 sentence plain-language description, confirmed/derived from the code
3. **Justification** — the "why", in Fatemeh's wording from the overview, refined with what you confirmed in code
4. **Status badge** (color-coded, see below) **+ criterion value(s) and source reference** (file / ADR / log section) where one exists

**Status badge colors** (define as CSS custom properties in `:root`):
- `Justified` → green
- `Provisional` → amber
- `Structural` → blue
- `Statistically derived (not health-validated)` → teal
- `Inconsistent` → orange
- `Unjustified` → red
- `Planned` / `Not implemented` → gray

A stage may carry more than one tag (e.g. Stage 4: mechanism *Justified* but value *Inconsistent*; Stage 9: core logic *Justified*, reference population *Unjustified*, vibration handling *Structural*). Show all applicable tags on the card.

**Header block** at the top: title the file as a companion to the Confluence page, and reproduce the meta line `Last updated: 2026-07-20 · Based on: Fatemeh Heydari, Implementation Log — Preprocessing Pipeline V2.0 (2026-07-19)`. Include a **compact legend** of the status tags.

**Optional nicety:** filter buttons that highlight/dim stages by status tag (pure client-side JS).

## Step 3 — Output rules (standalone HTML — non-negotiable)
- Exactly **one self-contained `.html` file**, opens locally in a browser with no server and no internet.
- **ALL CSS** inside a `<style>` tag in `<head>` — never `<link rel="stylesheet">` for your own styles.
- **ALL JS** inside a `<script>` tag — never an external `.js` file.
- Google Fonts via `<link>` and CDN libraries via `<script src>` are allowed **as enhancement only** — the page must still work offline without them.
- Dark theme, CSS custom properties in `:root`, responsive (mobile-friendly), `JetBrains Mono` / `DM Sans`.
- Save it at the workspace root as **`pipeline_stage_overview.html`** and print the absolute path when done.

---

## Reference content (encode this; verify each item against the code; keep the wording)

**Pipeline: 11 stages (9 implemented, 2 planned). Numbering is the new V2.0 numbering — 3 stages were inserted before the old start, so old "Stage 2/3" are now Stage 4/5.**

| # | Stage | What it does (verify in code) | Justification (overview wording) | Status tag(s) | Value + source |
|---|-------|-------------------------------|----------------------------------|---------------|----------------|
| 1 | Metadata Integration | Attaches recording metadata | Purely technical prerequisite; no methodological justification required | Justified | — |
| 2 | Signal Discovery | Selects the Position reference signal | Enforces exactly one Position reference signal (errors out on 0 or >1 matches); ensures unambiguous reference | Justified | Position ref, ADR-007, `docs/architecture_decisions.md`, Log §8 |
| 3 | Timestamp Analysis | Analyses sampling intervals / gaps | Small sampling variation (~43–58 ms) deliberately not treated as an error; large gaps used to separate sessions | Justified | Log §3 |
| 4 | Recording Session Detection | Splits recordings into sessions on large time gaps | Mechanism prevents joining data across shutdowns/maintenance — but the concrete 3600 s value is not justified, only the approach | Justified (mechanism) + **Inconsistent** (value) | 3600 s; `session_detection.py`, ADR-006, Log §15 "Session-Gap Threshold" |
| 5 | Position-Based Cycle Detection | Detects cycles from the position signal | Actuator is position-controlled (reference-signal choice justified) — but threshold 1.0 is explicitly provisional, no physical derivation | Justified (signal) + **Provisional** (threshold) | `Position > 1.0`; `cycle_detection.py`, Log §8 & §15 "Movement Threshold" |
| 6 | Multi-Sensor Cycle Extraction | Extracts per-cycle multi-sensor windows | No resampling/interpolation because sensors have different native sampling frequencies (avoids artificial artifacts) | Justified | Log §9, §12 |
| 7 | Cycle Quality Profiling | Profiles each cycle; records stroke-range metrics; does NOT reject | Deliberately non-rejecting — prevents arbitrary early filtering, keeps rule generation traceable | Justified | Log §7 (stroke metrics) |
| 8 | Validation Rule Generation | Learns validation thresholds from the cycle population | Median + MAD as robust statistic, quantile fallback for instability — statistically justified, but the reference population is not verified as healthy | **Statistically derived (not health-validated)** | Median+MAD limit 3.5, fallback 0.01/0.99; Log §11, `validation_thresholds.json` |
| 9 | Dataset Validation | Applies rules; handles optional vibration signal | Vibration treated as optional not mandatory (core vs. supplementary signals) — cleanly justified | Justified (core logic) + **Structural** (vibration handling) + **Unjustified** (reference population: `all_profiled_cycles`, no explicit healthy-subset selection) | Log §11, §12, §15 |
| 10 | Feature Engineering | — | Planned, not implemented | Planned | — |
| 11 | Dataset Generation | — | Planned, not implemented | Planned | — |

**Status tag legend (reproduce verbatim in the HTML legend):**
- **Justified** — physically or methodologically grounded (e.g. via ADR)
- **Provisional** — actively used, but not physically/methodologically derived
- **Structural** — enforced by pipeline logic, but not physically validated
- **Statistically derived (not health-validated)** — threshold generated from the observed data distribution (Median + MAD, quantile fallback), but the reference population has not been confirmed to represent healthy behaviour
- **Inconsistent** — conflicting sources disagree on status/value
- **Unjustified** — no documented reasoning exists
- **Planned / Not implemented** — stage does not yet exist in code

**Key summary line to include somewhere prominent:** the *mechanisms* (why a threshold at all, why separate sessions, why a robust statistic) are consistently well justified; the concrete *numeric values* (3600 s, Position > 1.0, MAD limit 3.5) are the open gap the decision tree is meant to close.
