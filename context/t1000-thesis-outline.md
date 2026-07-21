# T1000 Thesis Outline — Draft

**Constraint:** 25–35 pages (excluding table of contents, list of figures/tables, bibliography, appendix)
**Target:** ~30 pages, distributed as below
**Language:** English

---

## 1. Introduction *(~2 pages)*
- 1.1 Motivation — endurance testing at Emerson, why data quality matters for the planned test-engineer dashboard
- 1.2 Research Question & Scope
  - Core question: *How does one arrive at high-quality datasets?*
  - **Explicit scope statement (important):** this thesis covers the criteria/decision layer on top of the existing preprocessing pipeline (Heydari, 2026) — not the pipeline implementation itself
- 1.3 Thesis Structure

---

## 2. Background *(~4 pages)*
Keep this lean — it's context, not the contribution. Two sections only.
- 2.1 Actuator Endurance Testing & the Existing Pipeline
  - D32/D63 test setup, carriage cycle definition
  - Brief, clearly-attributed summary of Heydari's 11-stage pipeline (cite as prior/parallel work)
- 2.2 Data Quality Foundations
  - Condensed literature grounding (ISO 25012, steady-state/cycle-segmentation methods, PHM dataset-curation criteria) — draw from your existing reference list, don't re-research from scratch

---

## 3. Methodology *(~6 pages)*
This is where you establish *how* you worked, before showing *what* you built.
- 3.1 Criteria Maturity Framework — your status-tag system, presented as a general method for auditing preprocessing criteria
- 3.2 Decision Tree Development Process — how criteria were elicited, discussed with Heydari, structured
- 3.3 Approach to Physical Grounding — general procedure (distribution analysis near known physical states, comparison against alternative thresholds, validation against domain expectations)

---

## 4. Implementation *(~10 pages — largest chapter, this is your core contribution)*
- 4.1 Standstill / Frozen-State Detection *(largest subsection)*
- 4.2 Movement Threshold Derivation
- 4.3 Decision Tree & Data Pool Derivation
- 4.4 HTML Cycle Visualization *(kept brief — describe design decisions, not a full UI walkthrough)*

---

## 5. Evaluation *(~5 pages)*
- 5.1 Statistically-Derived vs. Physically-Grounded Thresholds — direct comparison, this is your evidence chapter
- 5.2 Data Pool Quality Assessment — before/after your criteria were applied

---

## 6. Discussion & Conclusion *(~3 pages — merged to save space)*
- 6.1 Limitations
- 6.2 Integration with the Overall Pipeline & Dashboard
- 6.3 Conclusion & Future Work

---

## Notes on Scope Given the Page Limit

At 30 pages total, you likely cannot give deep, well-evidenced treatment to all six contribution candidates from the earlier discussion. Recommendation: treat **Standstill Detection**, **Movement Threshold Derivation**, and **Decision Tree / Data Pool** as your three deep, fully-evidenced contributions (Chapter 4's backbone). Fold the **Criteria Maturity Framework** and **Reference Population Definition** into Chapter 3 as methodology rather than standalone implementation chapters — they support the other work rather than standing alone. Keep the **Visualization** as a brief, concrete deliverable (4.4) without over-investing page budget in UI description.

## Open Questions for You
- Does DHBW require a separate "Related Work" chapter distinct from "Background," or can they stay merged as above?
- Should the pipeline description (2.1) include a diagram, and does that diagram count against the page limit or go in an appendix?
