"""
Step 2 of the actuator-lifetime dashboard pipeline.

Reads output/cycle_stats_full.parquet (one row per cycle, ~8.66M rows,
produced by extract_cycle_stats.py) and produces two compact artifacts
that get embedded into the final dashboard HTML:

1. output/trend.json
   Lifetime trend: active cycles are grouped into ~N_BUCKETS buckets
   (chronological order); each bucket stores mean/p10/p90 for every
   metric plus the bucket's representative cycle_index and timestamp.
   This is what powers the "Overview" trend chart across the whole test
   life without shipping 8.66M raw rows to the browser.

2. output/pool.json
   A representative pool of POOL_SIZE active cycles, evenly spread across
   the whole test life. For each pool cycle we ship:
     - full-resolution waveforms (time_in_cycle_ms, value) for velocity,
       position, current, pressure, spindle temperature
     - single snapshot values for motor/bearing temperature (slow signals)
     - precomputed derived metrics (peak vel, stroke, peak current,
       duration, current-vs-position loop area) for the stat cards/table
   This pool is the full set of cycles selectable/overlay-able in the
   comparison view (an honest, labeled subset -- not literally any of the
   8.66M cycles, which would be infeasible to embed in one HTML file).

Cycle boundaries/windows for the pool come from output/counter_v1_annot.parquet
(same source as extract_cycle_stats.py), so pool windows exactly match the
aggregate stats.
"""
import json
import time

import duckdb
import numpy as np
import pandas as pd

BASE = "/home/ita/data/ERA/D32_Nr13_14_15"
SDP = f"{BASE}/signal_data_point.parquet"
OUT = "output"

N_BUCKETS = 3000
POOL_SIZE = 1500
BATCH = 150  # windows per SQL query when extracting pool waveforms

WAVE_SIGNALS = {
    "vel": "30fc7262-528d-4e79-94f0-e7124f489f48",
    "pos": "8663194d-7e7c-4caf-b1a2-7ce991f7a46d",
    "cur": "597b058c-47a6-4543-94f4-c033fc59308f",
    "prs": "f3096da4-27a1-4490-8dac-9546b34f8244",
    "stemp": "dec67657-8faf-48db-9e0f-9fb7e621571b",
}

METRICS = ["vel_vpeak", "vel_vavg", "pos_vmax", "pos_vmin", "cur_vpeak", "cur_vavg",
           "prs_vavg", "mtemp_vavg", "stemp_vavg", "btemp_vavg", "duration_s"]


def build_trend(df):
    active = df[df["is_active"]].reset_index(drop=True)
    n = len(active)
    bucket_id = (np.arange(n) * N_BUCKETS // n)
    active = active.assign(_bucket=bucket_id)

    rows = []
    for b, g in active.groupby("_bucket", sort=True):
        rec = {
            "cycle_index": int(g["cycle_index"].iloc[len(g) // 2]),
            "t": g["time"].iloc[len(g) // 2].isoformat(),
            "n_cycles": int(len(g)),
        }
        for m in METRICS:
            vals = g[m].dropna().values
            if len(vals) == 0:
                rec[m] = None
                continue
            rec[m] = {
                "mean": round(float(np.mean(vals)), 4),
                "p10": round(float(np.percentile(vals, 10)), 4),
                "p90": round(float(np.percentile(vals, 90)), 4),
            }
        rows.append(rec)
    return rows


def loop_area(pos, cur):
    """Shoelace-formula area of the closed current-vs-position loop (proxy
    for a hysteresis loop, since no direct force/torque channel exists)."""
    if len(pos) < 3:
        return 0.0
    x = np.asarray(pos)
    y = np.asarray(cur)
    return float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def build_pool(con, boundaries, stats):
    active = stats[stats["is_active"]].reset_index(drop=True)
    idx = np.linspace(0, len(active) - 1, POOL_SIZE).astype(int)
    idx = np.unique(idx)
    pool_stats = active.iloc[idx].reset_index(drop=True)

    b = boundaries.set_index("cycle_index")
    windows = []
    for ci in pool_stats["cycle_index"]:
        start = b.loc[ci, "time"]
        nxt = ci + 1
        end = b.loc[nxt, "time"] if nxt in b.index else start + pd.Timedelta(seconds=3)
        windows.append((int(ci), start, end))

    waves = {name: {} for name in WAVE_SIGNALS}
    for name, sid in WAVE_SIGNALS.items():
        path = f"{SDP}/signal_id={sid}"
        t0 = time.time()
        for i in range(0, len(windows), BATCH):
            chunk = windows[i:i + BATCH]
            clauses = " OR ".join(
                f"(time >= '{s}' AND time < '{e}')" for _, s, e in chunk
            )
            df = con.execute(f"""
                SELECT time, value FROM read_parquet('{path}/*.parquet')
                WHERE {clauses}
                ORDER BY time
            """).df()
            if df.empty:
                continue
            starts = np.array([s.value for _, s, _ in chunk])
            ends = np.array([e.value for _, _, e in chunk])
            t = df["time"].values.astype("datetime64[ns]").astype(np.int64)
            pos_idx = np.searchsorted(starts, t, side="right") - 1
            pos_idx = np.clip(pos_idx, 0, len(chunk) - 1)
            valid = t < ends[pos_idx]
            df = df[valid]
            pos_idx = pos_idx[valid]
            t = t[valid]
            for j, (ci, s, e) in enumerate(chunk):
                m = pos_idx == j
                if not m.any():
                    continue
                tt = (t[m] - s.value) / 1e6  # ms since cycle start
                vv = df["value"].values[m]
                waves[name][ci] = (np.round(tt, 1).tolist(), np.round(vv, 4).tolist())
        print(f"{name}: {time.time()-t0:.1f}s, {len(waves[name])} cycles with waveform")

    pool = []
    ref = None
    for _, row in pool_stats.iterrows():
        ci = int(row["cycle_index"])
        rec = {
            "cycle_index": ci,
            "t": row["time"].isoformat(),
            "duration_s": round(float(row["duration_s"]), 3) if pd.notna(row["duration_s"]) else None,
            "vel_peak": round(float(row["vel_vpeak"]), 2),
            "vel_avg": round(float(row["vel_vavg"]), 2),
            "stroke": round(float(row["pos_vmax"] - row["pos_vmin"]), 4),
            "pos_min": round(float(row["pos_vmin"]), 4),
            "pos_max": round(float(row["pos_vmax"]), 4),
            "cur_peak": round(float(row["cur_vpeak"]), 3),
            "cur_avg": round(float(row["cur_vavg"]), 3),
            "pressure_avg": round(float(row["prs_vavg"]), 1) if pd.notna(row["prs_vavg"]) else None,
            "motor_temp": round(float(row["mtemp_vavg"]), 2) if pd.notna(row["mtemp_vavg"]) else None,
            "spindle_temp": round(float(row["stemp_vavg"]), 2) if pd.notna(row["stemp_vavg"]) else None,
            "bearing_temp": round(float(row["btemp_vavg"]), 2) if pd.notna(row["btemp_vavg"]) else None,
        }
        wv = {}
        for name in WAVE_SIGNALS:
            if ci in waves[name]:
                tt, vv = waves[name][ci]
                wv[name] = {"t": tt, "v": vv}
        rec["wave"] = wv
        if "pos" in wv and "cur" in wv and len(wv["pos"]["v"]) == len(wv["cur"]["v"]):
            rec["loop_area"] = round(loop_area(wv["pos"]["v"], wv["cur"]["v"]), 5)
        else:
            rec["loop_area"] = None
        if ref is None:
            ref = rec
        rec["dev_from_ref"] = {
            "stroke": round(rec["stroke"] - ref["stroke"], 4),
            "vel_peak": round(rec["vel_peak"] - ref["vel_peak"], 2),
            "cur_peak": round(rec["cur_peak"] - ref["cur_peak"], 3),
            "duration_s": round((rec["duration_s"] or 0) - (ref["duration_s"] or 0), 3),
        }
        pool.append(rec)
    return pool


def main():
    stats = pd.read_parquet(f"{OUT}/cycle_stats_full.parquet")
    counter = pd.read_parquet(f"{OUT}/counter_v1_annot.parquet")
    boundaries = counter[["time"]].reset_index(drop=True)
    boundaries["cycle_index"] = np.arange(len(boundaries))

    print("building trend...")
    trend = build_trend(stats)
    with open(f"{OUT}/trend.json", "w") as f:
        json.dump(trend, f)
    print(f"wrote trend.json: {len(trend)} buckets")

    print("building pool (waveform extraction)...")
    con = duckdb.connect()
    pool = build_pool(con, boundaries, stats)
    with open(f"{OUT}/pool.json", "w") as f:
        json.dump(pool, f)
    print(f"wrote pool.json: {len(pool)} cycles")

    meta = {
        "total_cycles": int(len(stats)),
        "active_cycles": int(stats["is_active"].sum()),
        "start_time": stats["time"].min().isoformat(),
        "end_time": stats["time"].max().isoformat(),
        "pool_size": len(pool),
        "n_buckets": len(trend),
    }
    with open(f"{OUT}/meta.json", "w") as f:
        json.dump(meta, f)
    print("meta:", meta)


if __name__ == "__main__":
    main()
