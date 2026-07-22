# Comparison of Data-Quality Approaches: Physical Plausibility vs. Statistical Outlier Detection

## Core distinction

The two contributions rest on one methodological axis:

- **Fatemeh's approach** detects *statistical anomalies* (data-driven, Median + MAD).
- **Steven's approach** enforces *physical plausibility* (domain-knowledge-based acceptance criteria).

Almost every advantage and limitation below follows from this single distinction. The two are not competing methods for the same task — they address **different classes of error** and are intended to be complementary.

---

## Side-by-side overview

| Dimension | Physical plausibility (Steven) | Statistical outlier detection (Fatemeh) |
|---|---|---|
| **Question answered** | "Are these data physically usable at all?" | "Is this cycle unusual relative to its neighbours?" |
| **Basis** | Domain knowledge, physics of the actuator | Empirical distribution of the dataset |
| **Reference needed** | None — physics is absolute | Requires a representative, healthy reference population |
| **Interpretability** | High — every rejection has a physical `rejection_reason` | Low — "3 MAD from the median" says little about *what* failed |
| **Robustness to bad batches** | Detects the fault even if a whole batch is faulty | Faulty batch can be absorbed as "normal" (masking) |
| **Sensitivity to subtle drift** | Low — plausible-but-degrading cycles pass | High — good early indicator of degradation |
| **Decision type** | Hard gates (accept / reject) | Relative, distribution-dependent flags |
| **Main risk** | Brittle cutoffs; thresholds must be justified | Statistical outlier ≠ physically invalid |

---

## Steven's approach — physical plausibility checking

**Advantages**

- Every rejection carries a physically meaningful reason (`rejection_reason`), so a test engineer immediately understands *what* is wrong, not only *that* something deviates — a strong fit for a dashboard used daily by engineers.
- Independent of any "healthy" reference population. Even if an entire batch is faulty, physics still catches it, whereas statistics would treat the fault as the norm (masking).
- Flag-based, auditable, and reproducible — the central scientific argument: raw files stay intact, rejected cycles are only flagged, and the pool is an index of passing cycles.
- Defines hard acceptance gates: a clear "may these data be used at all?" decision layer.

**Limitations**

- Every threshold must be explicitly justified and defended. This is exactly where the current open points sit (Movement Threshold > 1.0, velocity scaling, session-gap 3600 s). In a physics-based approach an unjustified threshold is a genuine weakness, not a detail.
- Hard cutoffs are brittle — borderline cycles can be misclassified.
- Subtle but physically *plausible* deviations (e.g. early degradation) pass through, because they violate no physical law even though they depart from the expected pattern.
- Manual definition and maintenance effort per criterion.

---

## Fatemeh's approach — statistical outlier detection (Median + MAD)

**Advantages**

- Adapts to the actual data distribution; MAD is robust against individual outliers.
- Catches exactly the subtle deviations that the physical approach misses — useful as an early-warning signal for degradation.
- One method covers many sensors uniformly, with little criterion-specific justification required.

**Limitations**

- Assumes a representative, healthy reference population — currently unresolved, which is precisely why the tag *"Statistically derived (not health-validated)"* exists for these thresholds.
- Limited physical interpretability: a MAD-based flag does not tell the engineer *what* is broken.
- A statistical outlier is not the same as a physically invalid cycle. The method can reject rare-but-valid cycles and admit physically impossible-but-frequent values.

---

## Why this matters for the thesis

This is not a "better vs. worse" comparison but a division into **two error classes**:

- **Physical plausibility** is the hard floor — *are the data usable at all?*
- **Statistical anomaly detection** is relative — *is this cycle unusual compared to its neighbours?*

A sensible ordering is therefore: **first** apply physical plausibility (Steven's layer), **then** run statistical anomaly detection on the cleaned pool. This complementarity is the strongest argument that Steven's work stands as a **methodologically independent contribution** alongside Fatemeh's, rather than a duplicate.



As long as the Movement Threshold and velocity scaling remain provisional or unjustified, the "physical" advantage is stronger on paper than in the implementation. These should either be closed beforehand or declared openly as *provisional*. In a physics-based approach an unjustified threshold is more exposed to criticism than in a purely statistical one, where the method itself provides the justification.
