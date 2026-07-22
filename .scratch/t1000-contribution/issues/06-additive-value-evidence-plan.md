# Evidence plan that the physical floor is additive, not redundant

Type: grilling
Status: open
Blocked by: 03

## Question

Decide the **empirical demonstration** that closes the "value on paper vs. in
implementation" gap: a concrete, reproducible case where t1000's physical floor
catches errors Fatemeh's statistics miss — e.g. a whole-batch fault the Median/
MAD absorbs as normal (masking), or a physically-impossible-but-frequent value
the distribution admits.

Decide (not build — this is the *plan* for the evidence):

- **Which phenomenon** to demonstrate (masking / batch fault / impossible-but-
  frequent / in-cycle standstill the stats ignore).
- **Which data** exhibits it (which ERA root/dataset, informed by ticket 01).
- **What the artifact is** — the minimal figure/table/case that a defense can
  point at, and where it lives in `t1000/`.
- **Success criterion** — what result would count as proof of additive value,
  and what result would instead reveal t1000 is redundant (honest null result).

Producing the actual figure/analysis is execution (out of scope); this ticket
locks *what evidence* and *how it would be judged*.
