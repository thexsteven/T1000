# Integration seam and data contract into Fatemeh's pipeline

Type: grilling
Status: open
Blocked by: 02, 04

## Question

Specify the **seam**: at which point does t1000's physical-plausibility floor
hand off to Fatemeh's pipeline, and in **what form**?

Decide, using the interface facts from ticket 02 and the coordination stance
from ticket 04:

- **Attach point** — which stage's input the floor sits in front of.
- **Hand-off form** — filtered pool index, an annotated cycle table with
  `rejection_reason` flags, or a modified per-cycle validity column that
  Fatemeh's Stage 10 consumes. Raw files must stay intact (flag, don't delete).
- **Contract shape** — exact columns/keys, per-cycle vs per-sample, how the
  floor's rejections coexist with Fatemeh's `valid_core_cycle` / `invalid_cycle`.
- **Ordering guarantee** — physical floor runs first, statistics on the cleaned
  pool second (per `approach_comparison.md`).

Output is the interface *specification* (the seam contract), not the code that
implements it (out of scope).
