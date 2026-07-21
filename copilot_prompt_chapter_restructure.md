# Copilot Prompt — Restructure Thesis Chapters 3–6

You are editing the **LaTeX source** of my Bachelor's thesis. Chapters 3–6 still carry heading placeholders from an unrelated template ("Comparison of the Life-Cycle Tests"), which contradicts what Section 1.6 ("Structure of the Thesis") actually promises. Your job is to **replace the chapter and section headings of Chapters 3–6** with the target structure below and add a short comment under each section describing what it will contain. **Do not write any body prose.**

## Hard rules — read first

1. **Only touch Chapters 3, 4, 5, 6.** Leave Chapters 1 and 2, the preamble, and all front/back matter completely unchanged.
2. **Locate the source first.** Determine whether chapters live in `main.tex` or in separate files (e.g. `chapters/03_methodology.tex`). Report what you find before editing.
3. **No content.** Each section gets only its `\section{...}`, a `\label{...}`, and a LaTeX comment (`%`) with the description I give below. No paragraphs, no filler text.
4. **Keep it compilable.** Valid LaTeX, balanced braces. Do not remove `\chapter`/`\section` commands elsewhere. If any `\ref`/`\autoref` elsewhere points to a label you change, update it.
5. **Preserve my citation convention.** At the end of each of Chapters 3–6, keep or add a commented block `% Required references: ...` listing the `\cite{TODO-...}` topics that chapter will need. Never insert real citations.
6. The table of contents regenerates automatically on the next compile — do not edit it by hand.
7. This is a git repo: note the current state (or suggest I commit) before you start.

## Target structure

### Chapter 3 — `\chapter{Methodology}`
- `\section{Procedure Model}`
  `% Overall research approach; how the work proceeds along the three objectives (decision tree, data pool, HTML overlay) as a case study on the Emerson test-series data.`
- `\section{Analysis of the Existing Pipeline and Identified Gaps}`
  `% Stage-by-stage catalogue of the 11-stage pipeline and the criteria it applies; the gaps from Section 1.2 (no standstill detection, provisional thresholds, velocity unused, no physical plausibility check, no maturity accounting).`
- `\section{Criteria Maturity Framework}`
  `% The maturity-level system for every criterion (Begruendet, Provisorisch, Strukturell, Inkonsistent, Nicht begruendet, "Statistically derived (not health-validated)"); purpose and how a criterion moves between levels.`
- `\section{Physical Plausibility Criteria}`
  `% Domain-knowledge-based checks: full-stroke/minimum-motion, plausible cycle duration, non-finite/constant (frozen) value check, sample-count and coverage ranges; derivation basis and maturity of each; definition of the reference population for statistically derived thresholds; contrast with the statistical (Median+MAD) validation.`
- `\section{Standstill Detection and Movement-Threshold Derivation}`
  `% Velocity-window-based standstill/frozen-signal detection; empirical derivation of the movement threshold from the rest-position distribution; dependency on velocity-signal scaling.`
- `\section{The Four-Level Decision Tree}`
  `% How the criteria are assembled into the multi-level keep/reject logic; note this is a manual, criteria-based filter, not an ML classifier.`
- `\section{Data Pool Derivation and Rejection Logging}`
  `% Turning the decision tree into a filter step; flag-based approach (raw data never deleted, rejection_reason in a quality log, pool as an index e.g. pool_cycles.parquet); reproducibility and auditability.`
- `\section{HTML Cycle Overlay}`
  `% Method for the self-contained, server-less HTML visualization that overlays cycles from the vetted pool; built on the pool, not on raw data.`

### Chapter 4 — `\chapter{Application and Results}`  (was "Comparison of the Life-Cycle Tests")
- `\section{Test Series and Data Basis}`
  `% The selected test series used as the case study; scope of the data (sessions, number of cycles, available signals).`
- `\section{Application of the Decision Tree}`
  `% Running the four-level decision tree over the recorded cycles; how the thresholds were instantiated from the observed data.`
- `\section{Data Pool and Rejection Statistics}`
  `% The resulting vetted pool and rejection log; rejection statistics per category (the empirical core result); what a spike in a category indicates about sensor/recording problems.`
- `\section{HTML Cycle Overlay}`
  `% The produced visualization; example trend and comparison views across the service life of a device under test.`
- `\section{Interim Conclusion}`
  `% Brief summary of what the application produced, bridging into the discussion.`

### Chapter 5 — `\chapter{Discussion}`
- `\section{Interpretation of the Results}`
  `% What the rejection statistics and the pool tell us; does the physical layer change decisions vs. the purely statistical filter?`
- `\section{Recommendations for Daily Data-Quality Evaluation}`
  `% Recommendations for the planned engineer dashboard: what to surface, early-warning value of rejection spikes. (NEW section per Section 1.6.)`
- `\section{Comparison with the State of Research}`
  `% Relate the approach to the literature from Chapter 2 (data quality, robust thresholds, standstill detection).`
- `\section{Critical Appraisal of the Results}`
  `% Honest strengths and weaknesses; trade-offs of the physical-plausibility approach (needs expert input, limited transfer, more manual).`
- `\section{Limitations of the Thesis}`
  `% Scope limits: single test series, case-study character, out-of-scope items.`

### Chapter 6 — `\chapter{Conclusion \& Outlook}`  (keep sections, add comments)
- `\section{Summary of Findings}`
  `% Concise recap of what was built and found.`
- `\section{Answering the Research Question}`
  `% Return to the research question from Section 1.3 and answer the preprocessing side of it.`
- `\section{Practical and Theoretical Implications}`
  `% Value for Emerson (dashboard, auditable rejection log) and methodological contribution.`
- `\section{Outlook on Further Work}`
  `% Velocity-based standstill definition, extension to further test series and signals, integration into the dashboard, downstream model building.`

## After editing

Report a short before/after list of the chapter and section headings you changed, confirm Chapters 1–2 and the preamble are untouched, and confirm the source still compiles (or note any label references you had to update).
