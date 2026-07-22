# Architecture Decision Records (ADR) — T1000

Project:
Data-Quality Preprocessing — Physically Grounded Cycle-Selection Layer for Industrial Electric Actuators

Author:
Steven Braun

Scope:
This thesis (T1000 / practical-semester work). The physically grounded cross-check and transparency layer **on top of** the existing preprocessing pipeline — not the pipeline itself, and not its statistical validation.

Last Update:
2026-07-22

---

# Purpose

This document records the architectural and methodological decisions taken while
developing the physically grounded cycle-selection layer described in the T1000
thesis.

It is the counterpart to the master-thesis ADR file
(`architecture_decisions_master-thesis`, author Fatemeh Heydari), which records the
decisions behind the preprocessing pipeline. That pipeline is **prior work** here.
As of pipeline V2.1 (2026-07-22) it also performs its own data-driven statistical
validation and cycle rejection (Stages 9–10). The decisions below therefore concern
a **physical cross-check and transparency layer** that consumes the pipeline's
validated output and adds an absolute, population-independent floor plus the checks
the pipeline still lacks — not a replacement for the pipeline's statistical
validation.

Where a decision depends on or contrasts with a pipeline decision, the
corresponding master-thesis record is referenced as `master-thesis ADR-0XX`.

Terminology follows the authoritative glossary in `context/terminology.md`. The
five maturity levels used below (inconsistent, provisional, unfounded, structural,
justified) are defined there and in `context/04_kriterien_entscheidungsbaum.md`.

Records are numbered `ADR-T01`, `ADR-T02`, … to keep them distinct from the
master-thesis records. Dates reflect the date of formal recording, not necessarily
the date the decision was first taken; several consolidate decisions made during
the pipeline-analysis phase (see `context/03_pipeline_analyse.md`).

---

# ADR-T01

## Title

Physical Cross-Check On Top of the Existing Pipeline (Not a Reimplementation)

## Date

2026-07-21

## Problem

An existing preprocessing pipeline (prior master's thesis) turns raw test-rig
recordings into structured motion cycles and — as of V2.1 — validates and rejects
them with data-driven statistical thresholds (Stages 9–10). What it does **not**
provide is a *physical*, population-independent judgement of whether a cycle is
usable at all (full stroke, actually moving, plausible), nor an in-cycle standstill
check, nor a transparency rating of how well each threshold is grounded. That
physical cross-check is what this thesis adds.

The work could either extend the pipeline in place or add a separate layer after it.

## Options

### Option 1

Fork or rewrite the pipeline and integrate the quality decision inside it.

Advantages

- Single unified codebase.

Disadvantages

- Duplicates and risks diverging from mature, validated prior work.
- Blurs the contribution boundary between the two theses.
- Large implementation and re-validation effort outside the thesis scope.

### Option 2

Add a downstream layer that consumes the pipeline's existing metrics and validated
cycle classes.

Advantages

- Clear contribution boundary (analyse and extend, do not reimplement).
- Reuses already-computed metrics (cycle duration, position range, per-signal
  sample counts, quality metrics) and the pipeline's validation output.
- Keeps the pipeline authoritative and unchanged.

Disadvantages

- Depends on the stability and correctness of the upstream pipeline output.

## Decision

Option 2 was selected.

The layer sits **after** the pipeline and reuses its computed cycle- and
signal-level metrics and its validated cycle classes. Building, rewriting, or
re-validating the pipeline stages — including its statistical validation
(Stages 9–10) — is explicitly out of scope (see
`context/contribution_split_confluence.md`).

Update (2026-07-22, pipeline V2.1): this ADR originally framed the layer as
supplying the *missing* cycle-admission decision. The pipeline now makes that
decision statistically, so the layer is re-scoped to a physical cross-check on top
of it rather than the primary admission filter.

## Status

Accepted.

---

# ADR-T02

## Title

Physical Plausibility as a Separate Hard Floor, Distinct From Statistical Outlier Detection

## Date

2026-07-21

## Problem

The pipeline now validates and rejects cycles using data-driven statistical
thresholds (master-thesis ADR-012 and Stages 9–10, Median + MAD / quantiles). A
statistical check answers "is this cycle unusual compared to its neighbours?" — a
*relative* question that depends on the reference population, which mixes healthy and
degraded behaviour and can drift as faults grow.

It does not answer whether a cycle is *physically usable at all* — full stroke
reached, actually moving, plausible duration, finite values. These are **absolute**
questions and represent a different class of error, which a population-relative
threshold can miss or mask entirely (e.g. a whole batch degrading together).

## Decision

Physical plausibility and statistical outlier detection are treated as two separate
decisions, not two attempts at the same check.

- Physical plausibility is a **hard floor**: a cycle that fails it is not usable
  data, independent of any population.
- Statistical detection remains relative and is left to the pipeline (and to later
  anomaly-detection / modelling work).

This layer implements only the physical hard floor.

## Reason

Conflating the two would let a physically broken cycle pass because it happens to sit
near the population median, or reject a physically valid but rare cycle because it is
statistically unusual — discarding exactly the degradation signal downstream models
need (see ADR-T08).

## Status

Accepted.

---

# ADR-T03

## Title

Four-Level Ordered Gate as the Decision-Tree Architecture

## Date

2026-07-21

## Problem

The physical quality decision comprises several checks of very different nature
(session validity, complete stroke, multi-sensor presence, per-signal health).
These could be combined into a single flat score or arranged as an ordered sequence
of gates.

## Options

### Option 1

Flat, weighted quality score with a single admission cut-off.

Advantages

- One tunable number.

Disadvantages

- A fatal defect (e.g. missing core signal) can be masked by high scores elsewhere.
- No single, interpretable reason why a cycle was rejected.

### Option 2

Ordered four-level gate; a cycle must pass **all** levels top to bottom.

Levels:

1. Recording session — cycle belongs to a valid, sufficiently long session.
2. True cycle — real, complete stroke; includes standstill / frozen-signal check.
3. Multi-sensor completeness — all required signals present with enough samples.
4. Per-signal quality — coverage, intra-cycle gaps, non-finite values, frozen signal.

Advantages

- Each rejection maps to exactly one level and one documented reason.
- Cheap structural checks run before expensive per-signal checks.
- Gives a single, level-by-level view in which each criterion is tagged by owner
  (pipeline segmentation / pipeline statistical / this work's physical / this work's
  new) and by maturity.

Disadvantages

- Level ordering must be justified.

## Decision

Option 2 was selected. The decision tree is an ordered gate: any failing level
removes the cycle with a documented rejection reason (see
`context/04_kriterien_entscheidungsbaum.md`).

As of pipeline V2.1, most numeric checks in Levels 3–4 and the numeric bounds in
Level 2 are already enforced by the pipeline's statistical validation (Stages 9–10).
The tree therefore does not re-run those as a second filter; it (a) adds the
*physical* absolute cross-checks and the *new* checks the pipeline lacks (in-cycle
standstill 2.5, minimum session size 1.2), and (b) serves as the transparency map
that rates every criterion — the pipeline's included — by owner and maturity.

## Status

Accepted (design). The executable module that applies the added physical / new
checks on top of the pipeline's validated cycle output is still to be implemented
(see `context/06_stand_ergebnisse.md`).

---

# ADR-T04

## Title

Criteria Maturity Framework as an Explicit Meta-Layer

## Date

2026-07-21

## Problem

Prior-work criteria differ widely in how well they are justified: some are confirmed
by domain experts, some are provisional placeholders, some are undocumented "magic
numbers", and at least one is documented inconsistently (session-gap threshold marked
both final and provisional in different places). Presenting all criteria as equally
trustworthy would misrepresent the actual state of the pipeline.

## Decision

Every criterion carries an explicit **maturity level** as a first-class attribute,
using a fixed five-way classification: *inconsistent*, *provisional*, *unfounded*,
*structural*, *justified* (see `context/terminology.md`).

The maturity level is documented alongside each criterion in the decision tree, so
the trustworthiness of each individual quality decision is visible, and it is clear
where supervisor alignment or further data analysis is still required before a
criterion can be promoted to *justified*.

## Benefits

- Makes justification status auditable rather than implicit.
- Separates "what is checked" from "how well the check is grounded".
- Turns threshold re-derivation (ADR-T06) into a visible maturity promotion.
- Applies to the pipeline's now-implemented statistical rules too — including its own
  `provisional` flag (Stage 9) — giving one consistent trust rating across both
  theses' criteria.

## Status

Accepted.

---

# ADR-T05

## Title

Standstill / Frozen-Signal Detection via a Sliding Window (Velocity Preferred)

## Date

2026-07-21

## Problem

The pipeline detects a signal that is constant across a *whole* cycle
(`constant_signal`, Stage 8), but it does not check whether motion is real *within*
a cycle: a frozen sensor or communication dropout that affects only part of an
otherwise-moving cycle passes as an active cycle. No in-cycle standstill detection
exists (identified gap, `context/03_pipeline_analyse.md`).

## Options

### Option 1

Position-threshold check only.

Disadvantages

- A position threshold cannot reliably separate "small movement" from "no movement".

### Option 2

Sliding-window standstill check with velocity as the primary indicator.

Within each window of fixed length, either the position must change by more than a
small minimum, or — preferred, as the more direct physical indicator — the velocity
magnitude must exceed a small threshold. A window satisfying neither marks a
standstill / frozen segment and rejects the cycle.

Advantages

- Velocity near zero is a direct physical indicator of standstill.
- Catches frozen segments inside otherwise "active" cycles.

Disadvantages

- Requires a verified physical scaling/calibration of the velocity signal, which the
  pipeline has not conclusively checked.

## Decision

Option 2 is the target architecture, with velocity as the preferred indicator.
Because velocity calibration is unverified, the **position-based variant is used as
an interim** while the velocity-based variant is documented and prepared as the
methodologically superior target.

## Status

Accepted (in principle). Velocity variant blocked on velocity-signal calibration;
position-based interim in use (see open points, `context/06_stand_ergebnisse.md`).

---

# ADR-T06

## Title

Data-Driven Re-Derivation of Provisional Thresholds

## Date

2026-07-21

## Problem

Central pipeline thresholds — the motion threshold for cycle detection
(`position > 1.0`) and the recording-session gap (`3600 s`) — are provisional
placeholders, in places duplicated in code and not derived from the observed data.
Their safety margin to the physical rest state is narrow and undocumented.

## Decision

The two **provisional segmentation thresholds** — the motion threshold for cycle
detection (`position > 1.0`) and the recording-session gap (`3600 s`) — are
re-derived from the observed data distributions rather than inherited as
placeholders: analysis of the distribution near known physical states (e.g. position
noise in the rest position), comparison against alternative thresholds, and a safety
margin — then documented and promoted from *provisional* to *justified* (ADR-T04).

These two live **upstream** of the pipeline's own rule generation (Stage 9), which is
why Stage 9 does not settle them: they shape how sessions and cycles are cut in the
first place. The re-derived values are therefore handed back to be applied at the
source in the pipeline (see `context/04_kriterien_entscheidungsbaum.md`, segmentation
vs. gate). The per-signal numeric thresholds in Levels 3–4 are **not** re-derived
here — those are generated data-driven by the pipeline's Stage 9; this thesis instead
adds the *absolute physical* bounds where they complement that statistic (ADR-T02).

## Reason

Data-derived thresholds with a documented margin are defensible and reproducible;
provisional placeholders are neither, and the resulting pool would inherit
unjustified boundaries.

## Status

Accepted (method). Final numeric values pending distribution analysis and supervisor
alignment (motion threshold, session-gap inconsistency, minimum session size); see
`context/06_stand_ergebnisse.md`.

---

# ADR-T07

## Title

Non-Destructive Data Pool — Flag and Log, Never Delete

## Date

2026-07-21

## Problem

Applying the decision tree partitions cycles into usable and rejected. The rejected
cycles could be physically discarded or merely marked.

## Decision

Raw files are never deleted. The pipeline already applies this principle for its own
statistical validation (Stage 10 writes `invalid_cycles.parquet` and a
`validation_reason_summary.csv` rather than deleting anything). This thesis follows
and extends it, producing:

1. A **data pool** — the index of cycles that pass both the pipeline's statistical
   validation and this thesis's physical floor.
2. A **physical rejection log** — for every cycle excluded by the physical floor or
   the standstill check, the concrete physical reason (e.g. incomplete stroke,
   standstill / frozen segment), recorded alongside the pipeline's statistical reason
   codes.

Rejected cycles are flagged, not removed.

## Benefits

- Every quality decision is traceable, reproducible, and defensible — important for a
  dataset that will later train condition-monitoring / RUL models.
- The rejection log is itself a key empirical result: it quantifies how many cycles
  fail at which level and why, and a spike in any rejection category is an immediate
  indicator of a sensor or rig fault during a running test.

## Status

Accepted (design). Pool-filter module and full-population rejection statistics
pending implementation (see ADR-T03, `context/06_stand_ergebnisse.md`).

---

# ADR-T08

## Title

Reject Bad Data, Retain Unusual-but-Real Cycles

## Date

2026-07-21

## Problem

A cycle can be physically unusual (atypical current profile, position range, or
vibration) yet technically valid. Such behaviour may represent actuator degradation —
exactly the signal downstream anomaly-detection / RUL models must see. A quality
filter that removes everything "abnormal" would destroy that signal.

## Decision

The physical floor rejects only technical / physical **data** problems (missing core
signals, non-finite or frozen values, invalid timestamps, insufficient coverage,
impossible or fragmentary cycles). Physically unusual but technically valid cycles
are deliberately **retained** in the pool.

This mirrors the pipeline's separation of quality from health (master-thesis ADR-013)
and constrains what the physical hard floor of ADR-T02 must *not* do.

## Status

Accepted.

---

# ADR-T09

## Title

Visualization Built on the Vetted Pool, Not on Raw Data

## Date

2026-07-21

## Problem

The cycle-overlay visualization could render raw cycles directly or only pool cycles
that passed validation (the pipeline's statistical rules plus this thesis's physical
floor).

## Options

### Option 1

Overlay raw, unvetted cycles.

Disadvantages

- Raw recordings span millions of cycles and hundreds of millions of samples — far
  too much for an interactive browser report.
- Artifacts (standstills, incomplete strokes, sensor dropouts) would appear visually
  on equal footing with valid cycles; an engineer could mistake a broken-sensor
  outlier for real actuator wear.

### Option 2

Overlay only vetted pool cycles.

Advantages

- Shows real operating-behaviour trends, not data-quality noise.
- Consistent with the pool that downstream modelling would also use.

## Decision

Option 2 was selected. The visualization consumes the vetted data pool, so it is a
direct visual tool for inspecting the same dataset later analyses rely on
(see `context/05_datenpool_visualisierung.md`).

## Status

Accepted.

---

# ADR-T10

## Title

Server-Free, Self-Contained HTML via Offline Three-Stage Aggregation

## Date

2026-07-21

## Problem

Even the vetted pool is too large to embed at full resolution in a single browser
file, yet the target users (test engineers) need a report that runs daily without
additional IT infrastructure.

## Decision

Principle: **aggregate once offline, ship only the compact result, run all
interactivity in the browser on that small result set.** A three-stage offline
compaction (raw → cycle metrics → compact trend / sample datasets → embedded HTML)
produces two complementary views embedded in a single self-contained HTML file:

- A **trend view** over *all* active pool cycles: the full operating period is split
  into a fixed number of chronological buckets; per bucket and metric it stores mean
  plus a lower/upper percentile — statistically exact over the full pool.
- A **comparison view** embedding a limited, evenly time-distributed representative
  sample of individual cycles at full signal resolution, explicitly labelled as a
  representative subset to avoid misreading it as the complete set.

The file needs no server or database at runtime and opens by double-click.

## Reason

A self-contained file matches the daily-use requirement without infrastructure; the
trend view keeps lifetime trends honest over the full pool while the comparison view
enables detailed per-cycle inspection.

## Status

Accepted. First working version demonstrated for one test series; extension to
further test series and to vibration signals is planned and non-blocking
(see `context/06_stand_ergebnisse.md`).
