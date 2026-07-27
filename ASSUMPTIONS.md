# Assumptions and verified facts

## Verified

- `Versuch1` is test specimen `Nr. 7`. This is confirmed by
  `Lifetime_report_endurance_test.xlsx`, sheet `D63_Nr_7_8_9`, row dated
  2026-03-23: `Regreasing Versuch 1 Nr.7`.
- All timestamps are treated as plant-local time in `Europe/Berlin`.
- The baseline includes 2026-03-25 through 2026-03-31; the April analysis
  window is 2026-04-01 through 2026-04-30.
- 2026-03-29 is a 23-hour local calendar day because of the Europe/Berlin DST
  transition. Coverage denominators must use local-day hours, not a fixed 24.
- Boundary chunks overlap by two minutes. Cycles intersecting a chunk boundary
  are marked `is_boundary_cycle` and excluded from aggregates; retained cycles
  use a global key composed of `chunk_id`, `session_id`, and `cycle_id`.
- On 2026-04-03, detected cycle durations were tightly distributed around a
  median of 3.103 s (p05 3.086 s, p95 3.150 s), with no observed second mode.
  Five consecutive cycles each covered a full position excursion from roughly
  0.05-0.09 to 85.008 and back below the movement threshold. Coverage
  expectations therefore use `3600 / 3.103 = 1,160` cycles/hour rather than
  the Excel header value of 5.65 s.
- Vibration was present in 1,310 of 23,642 cycles (5.5%) and was distributed
  nearly uniformly by hour on 2026-04-03. This is consistent with triggered or
  duty-cycled acquisition, not a single outage. It remains excluded from
  regression ranking and is reported as a separately covered trend.

## Not yet verifiable from the current repository

- The raw recording source does not expose a documented, authoritative schema
  for a date-filtered export. The wrapper must measure whether filtering is a
  full-dataset scan and report that timing separately from pipeline execution.
- The current pipeline has no date-window CLI option. `pipeline.py` remains
  unchanged; the wrapper must provide the date-bounded input surface.
- The plant's timestamp export format has not been independently compared with
  a UTC source. Until that is available, timestamps are local Europe/Berlin
  wall-clock values and are not converted to UTC.
- The final chunking strategy remains empirical and will be selected after the
  2026-04-03 measurement using peak RAM, slicing time, output size, and resume
  cost.
