# Justification strategy for the three provisional thresholds

Type: grilling
Status: resolved
Blocked by: 01

## Question

For each provisional threshold the physical floor rests on — session-gap
`3600 s`, movement threshold `Position > 1.0`, velocity scaling — decide the
**justification strategy** that survives examiner scrutiny (audience #1):

- **Re-derive from data** (data-driven cutoff with a documented method),
- **Physically defend** (argue the value from actuator physics / spec), or
- **Declare openly provisional** (state it as a known limitation for the defense).

The strategy may differ per threshold. The output is a *decision*, not the
re-derived numbers (running the derivation is out of scope). Use the fesibility
findings from ticket 01. Address the `approach_comparison.md` honest caveat
directly: "an unjustified threshold in a physics-based approach is a genuine
weakness." The decision must leave no threshold in an indefensible state.

## Answer

Decision reached with the dev under two baked-in constraints: a **~3-day budget →
one empirical pillar** (one load-bearing result done properly, not three
half-done), and **additive-value = population cleaning** (the pre-stage removes
physically-broken cycles that would otherwise contaminate the population Fatemeh's
Stage 9 statistics learn from). Strategy per threshold:

**Strategy = re-derive the two position thresholds as ONE pillar; declare velocity
provisional.**

1. **Session-gap 3600 s → RE-DERIVE (data-driven).** Justify from the
   timestamp-gap distribution of the position signal: show the natural break
   between intra-recording gaps (~0.05 s median, 20 Hz) and inter-recording
   interruptions (>1 h). Evidence already partly exists
   (`outputs/D63_Nr7_8/…/timestamp_analysis/statistics.csv`: `gaps_gt_1_hour: 5`,
   `maximum_gap_seconds: 531462`); the pillar adds the explicit gap histogram /
   percentile table showing 3600 s sits in the empty band between the two modes.

2. **Movement threshold >1.0 → RE-DERIVE (data-driven), unit deliberately not
   resolved.** Justify from the min-position noise floor over the 4.6 M-cycle
   `cycles.parquet`: show the at-rest floor (~0.06–0.85) sits robustly below 1.0
   and is well separated from motion (~1 % of peak stroke ~85). The cutoff is
   defensible **whatever the position unit means**; the "m"-label vs ~85-value
   mismatch is recorded as an explicit caveat, **not** resolved (resolving it
   would spawn a velocity-style spec dependency and is out of budget).

3. **Velocity scaling → DECLARE PROVISIONAL (openly).** State it as a known,
   named limitation, deferred to ticket **Confirm velocity-signal unit & actuator
   spec** (08). The additive-value claim does **not** depend on velocity: the
   physical floor gates on the position-only cycle index, so it stands without a
   verified velocity unit.

### The one pillar — scope

- **One coherent position-signal / cycle-index study** yields BOTH thresholds
  from the same artifact (two figures, one method): (a) timestamp-gap
  distribution → session-gap break; (b) min-position distribution → movement
  noise floor.
- **Datasets:** full derivation on the existing **D63_Nr7_8** output (primary,
  cheapest — stats + `cycles.parquet` already produced); plus a **cheap
  cross-dataset sanity check** on one second dataset (summary stats only:
  `gaps_gt_1_hour` count and min-position quantiles) to show both cutoffs are
  stable and pre-empt the "overfit to one recording" objection. No full second
  derivation.
- **Tooling:** lazy pyarrow reads via `/home/ita/ERA-NAS/.venv/bin/python`;
  always read `cycles.parquet`, never the 819 MB `cycles.csv`. Executing this
  study is out of scope for the map (post-plan doing); this ticket locks the
  *strategy*, not the numbers.

### Canonical physical-contamination classes (feeds 06/07)

The floor is a **physical gate on the position-only cycle index, before
extraction and before Stage 9 rule generation**. All gates are expressible on the
seam's position-derived per-cycle features (ticket 02: min/max/mean position,
duration, sample count). Canonical list — five classes, all **contamination, not
statistical outliers**:

1. **Non-finite** position (NaN/inf).
2. **Frozen / standstill** (no mechanical movement within the cycle).
3. **Incomplete stroke** (position never reaches the full mechanical range).
4. **Implausible cycle duration** (physically impossible timing).
5. **Implausible sample count** (too few/many samples for a real stroke).

### Anti-circularity argument (banked for ticket 07)

Pre-empt the obvious objection that pre-filtering reintroduces the circularity
Stage 9 is careful to avoid: **it does not.** Removing a *statistical outlier*
before learning a distribution would bias the median/MAD toward a self-fulfilling
cutoff (circular). The physical floor instead removes **contamination** — the
five classes above are physical-invalidity categories defined by absolute physics
and the actuator's mechanics, **independent of the learned distribution**.
Removing non-finite / frozen / incomplete-stroke cycles cleans the population of
data that was never a valid measurement, so Stage 9's statistics are learned on a
genuinely-valid population rather than one polluted by broken cycles — this
*improves* the statistics' input without biasing them toward any threshold.

### Feeds forward

- **06 (evidence plan):** the additive-value demonstration should show physically-
  broken cycles (one of the five classes) that Stage 9's Median/MAD would absorb
  as "normal" (masking) — i.e. contamination the floor removes but statistics
  keep.
- **07 (defense):** use the anti-circularity argument verbatim as the rebuttal to
  the "isn't this redundant with Stage 9 / doesn't it bias the stats" objection.
