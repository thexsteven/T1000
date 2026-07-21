"""
Step 1 of the actuator-lifetime dashboard pipeline.

Computes per-cycle aggregate statistics (min/max/mean/peak) for every one
of the ~8.66M Magnetschalter_Counter cycles in D32/Versuch1, for all 7
continuous signals (velocity, position, current, pressure, motor/spindle/
bearing temperature). Cycle boundaries come from the already-cached
`output/counter_v1_annot.parquet` (Magnetschalter_Counter with dt and
dist_to_pause columns), consistent with the prior cycle_overlay work.

Uses DuckDB ASOF JOIN (each raw sample matched to the latest cycle
boundary <= its timestamp) so we never materialize the raw 300M-row
signal tables in Python -- only the final ~8.66M-row aggregate.

Output: output/cycle_stats_full.parquet (one row per cycle).
"""
import time

import duckdb
import numpy as np
import pandas as pd

BASE = "/home/ita/data/ERA/D32_Nr13_14_15"
SDP = f"{BASE}/signal_data_point.parquet"
OUT = "output"

SIGNALS = {
    "vel": "30fc7262-528d-4e79-94f0-e7124f489f48",       # velocity, m/s (per metadata)
    "pos": "8663194d-7e7c-4caf-b1a2-7ce991f7a46d",       # position, m
    "cur": "597b058c-47a6-4543-94f4-c033fc59308f",       # current, A
    "prs": "f3096da4-27a1-4490-8dac-9546b34f8244",       # pressure, Pa
    "mtemp": "1ff90183-3f43-4b82-b27f-0c5829462233",     # motor temperature, C
    "stemp": "dec67657-8faf-48db-9e0f-9fb7e621571b",     # spindle_nut temperature, C
    "btemp": "947c0031-296f-4c97-a7c1-b6961b7f65a1",     # fixed_bearing_actuator temp, C
}


def main():
    con = duckdb.connect()

    counter = pd.read_parquet(f"{OUT}/counter_v1_annot.parquet")
    boundaries = counter[["time", "dist_to_pause"]].reset_index(drop=True)
    boundaries["cycle_index"] = np.arange(len(boundaries))
    n_cycles = len(boundaries)
    print(f"{n_cycles} cycle boundaries loaded")
    con.register("boundaries", boundaries)

    result = boundaries[["cycle_index", "time", "dist_to_pause"]].copy()
    result["duration_s"] = result["time"].diff().shift(-1).dt.total_seconds()
    result["is_active"] = result["dist_to_pause"] >= 10

    for name, sid in SIGNALS.items():
        path = f"{SDP}/signal_id={sid}"
        t0 = time.time()
        agg = con.execute(f"""
            SELECT b.cycle_index,
                   count(*)               AS n,
                   min(v.value)           AS vmin,
                   max(v.value)           AS vmax,
                   avg(v.value)           AS vavg,
                   max(abs(v.value))      AS vpeak
            FROM read_parquet('{path}/*.parquet') v
            ASOF JOIN boundaries b ON v.time >= b.time
            GROUP BY b.cycle_index
        """).df()
        agg = agg.set_index("cycle_index")
        for col in ("n", "vmin", "vmax", "vavg", "vpeak"):
            result[f"{name}_{col}"] = result["cycle_index"].map(agg[col]).astype("float32")
        print(f"{name}: {time.time()-t0:.1f}s, {len(agg)} cycles with data")

    # cast for compactness
    result["cycle_index"] = result["cycle_index"].astype("int32")
    result["dist_to_pause"] = result["dist_to_pause"].astype("int32")
    result["duration_s"] = result["duration_s"].astype("float32")

    out_path = f"{OUT}/cycle_stats_full.parquet"
    result.to_parquet(out_path, index=False)
    print("wrote", out_path, result.shape)


if __name__ == "__main__":
    main()
