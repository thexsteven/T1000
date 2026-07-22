# Confirm velocity-signal unit and actuator spec

Type: task
Status: open
Blocked by: —

## Question

Manual work that unblocks the velocity part of the threshold-justification
decision (ticket 03). Nothing to decide here — obtain the fact, then record it.

The velocity signal is declared with unit `m/s` in `selected_signals.csv`, but
per-cycle `std_value` reaches a minimum of ~156.1 — physically impossible for a
rod-style actuator if the unit were truly `m/s` (ticket 01 finding;
`implementation_log.md` §15: "physical scaling and unit interpretation of the
Velocity signal still require verification"). No physically meaningful standstill
epsilon or velocity threshold can be set until this is resolved.

**Do:** obtain the actuator datasheet / velocity-signal scaling from the
supervisor or Fatemeh (this is an open item on `weekly_plan.md:36`). Confirm the
true physical unit and any raw→physical scaling factor.

**Record in the Answer:** the confirmed unit and scaling factor (or, if it cannot
be obtained in time, an explicit statement that velocity scaling stays unverified,
which forces ticket 03 to declare the velocity variant provisional). This is a
HITL task — the human obtains the fact; the agent cannot invent it.
