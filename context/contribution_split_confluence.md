# Data-Quality Preprocessing — Who Does What, and Why It Matters for Emerson

## In one sentence

The master's thesis (Fatemeh) builds the **pipeline that turns raw recordings into structured motion cycles and validates them with data-driven, statistical thresholds** (Stages 9–10: automatic rule generation + cycle rejection). This bachelor's thesis (Steven) adds a **physically grounded cross-check on top of that validation, one check the pipeline does not yet have (in-cycle standstill), and a transparent maturity rating of every criterion**. The two are complementary: statistical validity vs. physical plausibility.

---

## The core distinction

| | **Fatemeh (master's thesis) — prior work** | **Steven (this thesis) — contribution** |
|---|---|---|
| **Role in the chain** | Produces the structured cycles **and** validates / rejects them with data-driven thresholds (Stages 9–10) | Adds a physical cross-check and one missing check *on top of* that validation |
| **Question answered** | "Is this cycle statistically unusual relative to the population?" | "Is this cycle physically usable at all — full stroke, actually moving, plausible?" |
| **Method** | Data-driven statistical thresholds (Median + MAD, quantiles) | Domain-knowledge-based physical plausibility (absolute bounds) |
| **Reference needed** | A population of cycles (mixes healthy + degraded) | None — physics is absolute, so it does not drift with the population |
| **Output** | Validated cycle classes + rejection reason codes | An additional physical rejection reason, a per-criterion maturity rating, and an HTML overlay of the validated pool |

The important point: these are **two different classes of error**, not two attempts at the same check. Statistical detection is relative ("is this cycle unusual compared to its neighbours?"); physical plausibility is an absolute floor ("are the data usable at all?") that does not move even when a growing share of the population is degraded.

---

## What Steven contributes

**Genuinely new — not in the pipeline today:**
- **In-cycle standstill / frozen-segment detection** — the pipeline's `constant_signal` flag only catches a signal that is flat across the *whole* cycle. A sliding-window check (ideally on velocity) catches a short frozen segment *inside* an otherwise moving cycle. This is the clearest new check.
- **Minimum session size** — reject cycles from very short, non-representative recording sessions (e.g. commissioning or aborted runs).

**Physical cross-check — an absolute floor alongside the pipeline's statistical rules (Stages 9–10):**
- **Full mechanical stroke, physically plausible duration, expected sample count, per-signal sanity** — checked against *absolute* physical values, not the learned population range. This matters because the pipeline's thresholds are learned from a population that mixes healthy and degraded cycles: as a fault grows, the statistical "normal" can drift with it, while an absolute physical bound does not.

**Transparency & re-derivation:**
- **Criteria Maturity Framework** — tags every criterion (the pipeline's included) by how well it is justified, so the trustworthiness of each threshold is visible at a glance.
- **Re-derivation of the two provisional segmentation thresholds** — the session gap (`3600 s`) and the cycle-detection cut-off (`position > 1.0`). Both sit upstream of the pipeline's rule generation and are still provisional; they are re-derived from the data and handed back for the pipeline to apply at the source.

**Visualization:**
- **HTML cycle overlay** — a server-free visualization that overlays cycles from the validated pool for engineer inspection.

## What Steven does *not* do (explicitly out of scope)

- **Building or rewriting the pipeline itself** — cycle detection, multi-sensor extraction, quality profiling and the segmentation thresholds are Fatemeh's prior work; they are analysed and extended, not reimplemented.
- **Data-driven statistical validation and cycle rejection** — automatic threshold generation (Median / MAD) and the pass/fail cycle classification are now implemented in the pipeline (Stages 9–10). Steven complements this, he does not rebuild it.
- **Model building (machine learning)** — feature engineering, RUL / condition-monitoring models, and any modelling on top of the finished data pool belong to the master's thesis and to follow-up work.

---

## The benefit for Emerson

- **A second, population-independent safety net for the planned engineer dashboard.** The pipeline already decides which cycles are statistically valid; the physical cross-check adds an absolute floor that does not drift as actuators wear, so a slowly developing fault is less likely to be quietly accepted as "normal".
- **Physically interpretable rejection reasons.** On top of the pipeline's statistical reason codes, a physical reason (e.g. *frozen segment*, *incomplete stroke*) tells a test engineer *what* is wrong in physical terms, not just that a cycle was statistically unusual.
- **Early warning for rig and sensor problems.** A spike in any rejection category — statistical or physical — is an immediate indicator of a sensor fault or recording issue during a running test.
- **Transparent trust in every threshold.** The maturity rating makes explicit how well each criterion (the pipeline's included) is grounded, which matters for a dataset that will later train condition-monitoring / RUL models.
- **Protects the degradation signal.** The physical checks remove bad *data* while deliberately keeping cycles that are merely unusual-but-real — exactly the signal future data-driven models depend on.

---

## The decision tree (compact overview)

The quality criteria are organized as **four levels**. Many are now enforced by the pipeline's own validation (Stages 9–10); this work adds the physical cross-checks, the two checks the pipeline lacks, and a maturity rating for how well each criterion is grounded.

```
Level 1 → Level 2 → Level 3 → Level 4 → (ALL PASS) → VALIDATED POOL OF USEFUL CYCLES
```

**Status legend (updated for pipeline V2.1, 2026-07-22)**
- **Pipeline · segmentation** — a threshold that *creates* sessions / cycles; lives upstream in the pipeline. This work only re-derives the value.
- **Pipeline · statistical** — now validated by the pipeline's data-driven rules (Stages 9–10), relative to the population.
- **This work · physical** — an absolute physical cross-check added *on top of* the statistical rule.
- **This work · new** — a check the pipeline does not have at all.

### Level 1 — Recording Session
*Does the cycle belong to a valid, continuous recording?*

| # | Criterion | Rule | Status |
|---|---|---|---|
| 1.1 | Session boundary — gap split | `gap > 3600 s → new session` | Pipeline · segmentation (value re-derived) |
| 1.2 | Minimum session size | `cycles / session ≥ N (≈100, TBD)` | This work · new |

### Level 2 — True Cycle (Standstill & Outlier Exclusion)
*Is this a real, complete actuator stroke — not noise, standstill or a fragment?*

| # | Criterion | Rule | Status |
|---|---|---|---|
| 2.1 | Cycle boundary detection | `position crosses 1.0` | Pipeline · segmentation (value re-derived) |
| 2.2 | Plausible cycle duration | `3.00 s ≤ duration ≤ 3.20 s` | Pipeline · statistical + This work · physical |
| 2.3 | Full stroke reached | `max_pos ≥ 84.0 ∧ min_pos ≤ 1.0` | Pipeline · statistical + This work · physical |
| 2.4 | Expected sample count | `60 ≤ samples ≤ 66` | Pipeline · statistical + This work · physical |
| 2.5 | Standstill / frozen-signal check | `Δpos > δ per window T, or \|v\| > ε` | This work · new |

### Level 3 — Multi-Sensor Completeness
*Are all required sensor signals present with enough samples?*

| # | Criterion | Rule | Status |
|---|---|---|---|
| 3.1 | All required signals present | `8 / 8 signals present` | Pipeline · statistical (`valid_core_cycle`) |
| 3.2 | Minimum samples per signal | `per-signal sample_count ≥ min` | Pipeline · statistical |

### Level 4 — Per-Signal Quality
*Is each signal internally healthy within the cycle?*

| # | Criterion | Rule | Status |
|---|---|---|---|
| 4.1 | Signal coverage of the cycle | `pos/vel/cur ≥ 0.95, press ≥ 0.90; vib/temp exempt` | Pipeline · statistical |
| 4.2 | No large intra-cycle gaps | `pos/vel/cur/press ≤ 0.15 s; temp ≤ 1.5 s; vib ≤ 0.10 s` | Pipeline · statistical |
| 4.3 | No invalid values | `non_finite_count = 0` | Pipeline · statistical (hard rule) |
| 4.4 | Signal not frozen / constant | `std > 0 (dynamic signals); temp exempt` | Pipeline · statistical (whole-cycle) · in-cycle segment → 2.5 |

**How this maps to the split above:** most of Levels 3–4 and the numeric bounds in Level 2 are now covered by the pipeline's statistical validation (Stages 9–10). This thesis's genuine additions are the *new* checks (in-cycle standstill 2.5, minimum session size 1.2), the *physical* absolute cross-checks in Level 2, the re-derivation of the two *segmentation* thresholds (1.1, 2.1), and the maturity rating across all criteria. So the tree is not a new validation pipeline — it is a physical cross-check and transparency layer on top of the existing one.

---

*This page summarises the delineation of the two theses and the decision-tree logic. Full per-criterion detail (rule, empirical evidence, exact source file + line) lives in the interactive `preprocessing_decision_tree.html`.*
