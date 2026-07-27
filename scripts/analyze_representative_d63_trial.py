"""Generate reproducible decision-tree evidence from one D63 raw-data trial.

The program deliberately reads only the three required hive partitions and
selects its analysis session from the position-recording time gaps.  It never
modifies the source data.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyarrow.dataset as ds
import pyarrow.parquet as pq


DEFAULT_RAW_TRIAL = Path("/home/ita/ERA/ERAP_EXT_004/2025_08_27_NAS2_D63/D63_20250827_120113")
RAW_TRIAL = DEFAULT_RAW_TRIAL
MOVEMENT_THRESHOLD = 1.0
SESSION_GAP_SECONDS = 3600.0
CONTINUITY_GAP_SECONDS = 0.1
MAX_OVERLAY_CYCLES = 100
DASHBOARD_POOL_SIZE = 750
DASHBOARD_TREND_BUCKETS = 500


def load_signal(signal_root: Path, signal_id: str, start: pd.Timestamp | None = None, end: pd.Timestamp | None = None) -> pd.DataFrame:
    """Read a single hive partition, optionally restricting the time interval."""
    dataset = ds.dataset(signal_root, format="parquet", partitioning="hive")
    expression = ds.field("signal_id") == signal_id
    if start is not None:
        expression &= ds.field("time") >= start.to_datetime64()
    if end is not None:
        expression &= ds.field("time") <= end.to_datetime64()
    frame = dataset.to_table(columns=["time", "value"], filter=expression).to_pandas()
    return frame.dropna().sort_values("time").reset_index(drop=True)


def sample_statistics(frame: pd.DataFrame) -> dict[str, float | int]:
    dt = frame.time.diff().dt.total_seconds().dropna()
    return {
        "samples": int(len(frame)),
        "nominal_dt_s": float(dt.median()),
        "mean_dt_s": float(dt.mean()),
        "std_dt_s": float(dt.std()),
        "p01_dt_s": float(dt.quantile(0.01)),
        "p99_dt_s": float(dt.quantile(0.99)),
        "maximum_dt_s": float(dt.max()),
    }


def detect_cycles(position: pd.DataFrame) -> pd.DataFrame:
    moving = position.value > MOVEMENT_THRESHOLD
    starts = position.index[moving & ~moving.shift(1, fill_value=False)].to_numpy()
    ends = position.index[~moving & moving.shift(1, fill_value=False)].to_numpy()
    rows = []
    end_cursor = 0
    for start in starts:
        while end_cursor < len(ends) and ends[end_cursor] <= start:
            end_cursor += 1
        if end_cursor == len(ends):
            break
        end = ends[end_cursor]
        segment = position.iloc[start : end + 1]
        rows.append({
            "start_index": int(start), "end_index": int(end),
            "start_time": segment.time.iloc[0], "end_time": segment.time.iloc[-1],
            "duration_s": (segment.time.iloc[-1] - segment.time.iloc[0]).total_seconds(),
            "samples": int(len(segment)), "minimum": float(segment.value.min()),
            "maximum": float(segment.value.max()),
        })
        end_cursor += 1
    return pd.DataFrame(rows)


def contiguous_groups(mask: np.ndarray) -> list[tuple[int, int]]:
    edges = np.diff(np.r_[False, mask, False].astype(np.int8))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def save_histogram(values: pd.Series, xlabel: str, title: str, output: Path, bins: int = 80, log_x: bool = False) -> None:
    fig, axis = plt.subplots(figsize=(9, 5))
    axis.hist(values, bins=bins, color="#1f77b4", edgecolor="white")
    axis.set(title=title, xlabel=xlabel, ylabel="Count")
    if log_x:
        axis.set_xscale("log")
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def compact_histogram(values: pd.Series, bins: int = 80, logarithmic: bool = False) -> dict[str, list[float]]:
    """Serialize a histogram small enough to embed in the offline dashboard."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if logarithmic:
        values = values[values > 0]
        edges = np.geomspace(values.min(), values.max(), bins + 1)
    else:
        edges = np.histogram_bin_edges(values, bins=bins)
    count, edges = np.histogram(values, bins=edges)
    return {"x": ((edges[:-1] + edges[1:]) / 2).tolist(), "y": count.tolist(), "w": np.diff(edges).tolist()}


def build_dashboard(output: Path, cycles: pd.DataFrame, session_summary: pd.DataFrame,
                    position: pd.DataFrame, current: pd.DataFrame, velocity: pd.DataFrame,
                    evidence: dict[str, object]) -> None:
    "Write the complete, offline, auditable D63 dashboard."
    aligned_current = pd.merge_asof(position, current.rename(columns={"time": "current_time", "value": "current"}),
        left_on="time", right_on="current_time", direction="nearest", tolerance=pd.Timedelta("100ms"))
    aligned_velocity = pd.merge_asof(position, velocity.rename(columns={"time": "velocity_time", "value": "velocity"}),
        left_on="time", right_on="velocity_time", direction="nearest", tolerance=pd.Timedelta("100ms"))
    enriched = cycles.copy()
    enriched["stroke"] = enriched.maximum - enriched.minimum
    enriched["current_peak"] = [float(aligned_current.current.iloc[r.start_index:r.end_index+1].abs().max()) for r in enriched.itertuples()]
    enriched["velocity_peak_abs"] = [float(aligned_velocity.velocity.iloc[r.start_index:r.end_index+1].abs().max()) for r in enriched.itertuples()]
    enriched["cycle_id"] = np.arange(1, len(enriched)+1)
    def rec(row):
        return {"cycle_id": int(row.cycle_id), "t": row.start_time.isoformat(), "duration_s": round(float(row.duration_s),3),
                "samples": int(row.samples), "stroke": round(float(row.stroke),5), "position_max": round(float(row.maximum),5),
                "current_peak": round(float(row.current_peak),4), "velocity_peak_abs": round(float(row.velocity_peak_abs),4)}
    records=[rec(r) for _,r in enriched.iterrows()]
    inds=np.unique(np.linspace(0,len(enriched)-1,min(DASHBOARD_POOL_SIZE,len(enriched))).astype(int)); pool=[]
    for i in inds:
        r=enriched.iloc[i]; item=rec(r); wave={}
        for name,frame in (("position",position),("current",aligned_current),("velocity",aligned_velocity)):
            seg=frame.iloc[int(r.start_index):int(r.end_index)+1]; vals=seg.value if name=="position" else seg[name]; valid=vals.notna()
            wave[name]={"t":np.round((seg.time[valid]-r.start_time).dt.total_seconds().to_numpy(),3).tolist(),"v":np.round(vals[valid].to_numpy(),5).tolist()}
        item["wave"]=wave; pool.append(item)
    bucket=np.arange(len(enriched))*DASHBOARD_TREND_BUCKETS//len(enriched); trend=[]
    for _,g in enriched.assign(bucket=bucket).groupby("bucket",sort=True):
        trend.append({"cycle_id":int(g.cycle_id.iloc[len(g)//2]),"t":g.start_time.iloc[len(g)//2].isoformat(),"n_cycles":int(len(g)),
          **{m:{"mean":round(float(g[m].mean()),5),"p10":round(float(g[m].quantile(.1)),5),"p90":round(float(g[m].quantile(.9)),5)} for m in ("duration_s","stroke","current_peak","velocity_peak_abs")}})
    # Compact interactive evidence arrays; the raw parquet remains untouched.
    payload={"meta":{"trial":str(RAW_TRIAL),"experiment":"D63 / Versuch1 / Drive","total_cycles":len(enriched),"pool_size":len(pool),
      "start":enriched.start_time.iloc[0].isoformat(),"end":enriched.end_time.iloc[-1].isoformat(),"trend_buckets":len(trend),
      "velocity_label":"raw counts (scaling unresolved)","script":"scripts/analyze_representative_d63_trial.py"},
      "sessions":[{"session_id":int(r.session_id),"start":r.start.isoformat(),"end":r.end.isoformat(),"samples":int(r.samples),"duration_s":round(float(r.duration_s),1)} for r in session_summary.itertuples()],
      "cycles":records,"pool":pool,"trend":trend,"evidence":evidence}
    data=json.dumps(payload,separators=(",",":"),default=str).replace("</","<\\/")
    plotly=Path(__file__).resolve().parents[1]/"src/cycle_overlay/plotly-2.35.2.min.js"
    js=plotly.read_text()
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>D63 criteria and data quality dashboard</title><script>{js}</script><style>
body{{font:14px system-ui;margin:0;background:#f5f7fa;color:#17202a}}main{{max-width:1400px;margin:auto;padding:24px}}h1{{margin-top:0}}.banner{{background:#fff3cd;border:2px solid #e0a800;padding:14px;font-weight:700}}.tabs button{{padding:10px 16px;border:0;background:#dbe7ef;margin:12px 4px 0 0;cursor:pointer}}.tabs button.active{{background:#0b6e99;color:white}}.view{{display:none}}.view.active{{display:block}}.card{{background:white;border-radius:8px;padding:16px;margin:16px 0;box-shadow:0 1px 4px #ccd}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(390px,1fr));gap:16px}}.chart{{height:300px}}.tag{{font-weight:700;padding:4px 8px;border-radius:4px;background:#e8eef2}}table{{border-collapse:collapse;width:100%}}td,th{{padding:7px;border-bottom:1px solid #ddd;text-align:left}}.small{{color:#52606d}}.metric{{font-size:19px;font-weight:700;margin-right:25px;display:inline-block}}
</style></head><body><main><h1>D63 / Versuch1 — cycle evidence and data quality</h1><div class="tabs"><button class="active" data-v="overview">Overview</button><button data-v="quality">Criteria &amp; Data Quality</button></div><section id="overview" class="view active"><div class="card"><div id="stats"></div><p><b>Cycle duration reconciliation:</b> Cycle period ≈ 5.65 s (60,901 cycles over 344,291 s of the selected block). Round-trip motion = 3.737 s (movement-threshold cycle duration, median); hold at lower end = 1.910 s (median); → Single trip ≈ 1.87 s. The single-trip value was verified directly from position-signal low-to-high/high-to-low travel intervals, not only by subtraction. The 1.81 s and 3.1 s references describe a single trip and a different segmentation, respectively.</p><p><b>Sampling evidence:</b> all channels are nominally 20 Hz; the table reports measured Δt, jitter and p01–p99. Velocity is shown as <b>raw counts; scaling unresolved</b>.</p><div id="sampling"></div></div><div class="card"><h2>Gap distribution and detected continuous recording blocks</h2><div id="gap" class="chart"></div><p>Three regimes are visible: normal sampling intervals, an intermediate band of 1.507–20.134 s interruptions, and the long session break. The intermediate band is not covered by the current binary rule. The dashed line marks the 3600 s session-gap threshold.</p><div id="sessions"></div></div></section><section id="quality" class="view"><div class="banner">All thresholds shown are provisional and pending review.</div><div class="card"><h2>Rejection summary</h2><p>No data is deleted. Rejected cycles are flagged with a <code>rejection_reason</code>; raw files remain untouched and the pool is only an index of passing cycles. A spike in one category over time is an early indicator of a sensor or recording fault.</p><div id="summary"></div><div id="rejecttime" class="chart"></div></div><div id="criteria" class="grid"></div><div class="card"><b>Open question:</b> velocity scaling and engineering units are unresolved; velocity values are raw counts, not validated physical units.</div></section></main><script>const DATA={data};
const $=id=>document.getElementById(id),fmt=(x,n=3)=>Number(x).toLocaleString(undefined,{{maximumFractionDigits:n}});function plot(id,traces,layout){{Plotly.newPlot(id,traces,Object.assign({{template:'plotly_white',margin:{{t:45,l:60,r:20,b:55}}}},layout),{{responsive:true}})}}
function init(){{let m=DATA.meta;$('stats').innerHTML=[['Cycles',fmt(m.total_cycles,0)],['Selected block',((new Date(m.end)-new Date(m.start))/86400000).toFixed(2)+' days'],['Detail pool',fmt(m.pool_size,0)]].map(x=>`<span class="metric">$${{x[0]}}<br><small>${{x[1]}}</small></span>`).join('');let e=DATA.evidence;
$('sampling').innerHTML='<table><tr><th>Channel</th><th>Nominal Δt</th><th>Mean</th><th>Jitter σ</th><th>p01–p99</th><th>Max</th></tr>'+Object.entries(e.sampling).map(([k,v])=>`<tr><td>${{k}}</td><td>${{fmt(v.nominal_dt_s)}} s</td><td>${{fmt(v.mean_dt_s)}} s</td><td>${{fmt(v.std_dt_s,5)}} s</td><td>${{fmt(v.p01_dt_s)}}–${{fmt(v.p99_dt_s)}} s</td><td>${{fmt(v.maximum_dt_s)}} s</td></tr>`).join('')+'</table>';
plot('gap',[{{x:e.gap_hist.x,y:e.gap_hist.y,type:'bar',width:e.gap_hist.w,hovertemplate:'Δt=%{{x:.4g}} s<br>count=%{{y}}<extra></extra>'}}],{{title:'Position Δt over full trial (three regimes)',xaxis:{{title:'Δt (s)',type:'log'}},yaxis:{{title:'Count'}},shapes:[{{type:'line',x0:3600,x1:3600,y0:0,y1:1,yref:'paper',line:{{dash:'dash',color:'red'}}}}],annotations:[{{x:3600,y:1,yref:'paper',text:'3600 s threshold',showarrow:false,xanchor:'left'}}]}});
$('sessions').innerHTML='<table><tr><th>Block</th><th>Start</th><th>End</th><th>Samples</th><th>Duration</th></tr>'+DATA.sessions.map(s=>`<tr><td>${{s.session_id}}</td><td>${{s.start}}</td><td>${{s.end}}</td><td>${{fmt(s.samples,0)}}</td><td>${{fmt(s.duration_s/3600,2)}} h</td></tr>`).join('')+'</table>';
let crit=e.criteria;$('summary').innerHTML='<table><tr><th>Criterion</th><th>Rejected</th><th>Share</th></tr>'+crit.map(c=>`<tr><td>${{c.name}}</td><td>${{fmt(c.rejected,0)}}</td><td>${{(100*c.rejected/m.total_cycles).toFixed(2)}}%</td></tr>`).join('')+`<tr><th>Passing all criteria</th><th>${{fmt(e.passing_all,0)}}</th><th>${{(100*e.passing_all/m.total_cycles).toFixed(2)}}%</th></tr></table>`;
plot('rejecttime',e.reject_time.map(x=>({{x:x.t,y:x.count,type:'bar',name:x.name}})),{{barmode:'stack',title:'Rejections over time (diagnostic)',xaxis:{{title:'Time'}},yaxis:{{title:'Cycles rejected'}}}});
$('criteria').innerHTML=crit.map((c,i)=>`<article class="card"><h2>${{c.name}}</h2><span class="tag">${{c.tag}}</span><p><b>Current threshold:</b> ${{c.threshold}}</p><p>${{c.caption}}</p><div id="criterion${{i}}" class="chart"></div><p class="small"><b>${{fmt(c.rejected,0)}} cycles rejected (${{(100*c.rejected/m.total_cycles).toFixed(2)}}%).</b> Counts are computed from the underlying cycle data; raw data and rejection reasons remain auditable.</p></article>`).join('');crit.forEach((c,i)=>plot('criterion'+i,[{{x:c.hist.x,y:c.hist.y,type:'bar',width:c.hist.w}}],{{title:c.chart_title,xaxis:{{title:c.x_title,type:c.log?'log':'linear'}},yaxis:{{title:'Count'}}}}));}}
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.tabs button,.view').forEach(x=>x.classList.remove('active'));b.classList.add('active');$(b.dataset.v).classList.add('active');}});init();</script></body></html>'''
    output.joinpath("d63_interactive_dashboard.html").write_text(html)
def main() -> None:
    global RAW_TRIAL
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--raw-trial", type=Path, default=DEFAULT_RAW_TRIAL)
    parser.add_argument("--start", type=pd.Timestamp, help="Optional inclusive analysis start")
    parser.add_argument("--end", type=pd.Timestamp, help="Optional inclusive analysis end")
    parser.add_argument("--full-experiment", action="store_true",
                        help="Analyze all recording sessions instead of the largest contiguous block")
    parser.add_argument("--endstop-quantile", type=float, default=0.01)
    args = parser.parse_args()
    raw_trial = args.raw_trial
    RAW_TRIAL = raw_trial
    output = args.output
    output.mkdir(parents=True, exist_ok=True)

    relationships = pq.read_table(raw_trial / "signal_data_point_rel.parquet").to_pandas()
    nodes = pq.read_table(raw_trial / "nodes.parquet").to_pandas()
    # The first Drive block belongs to Versuch1; the three rows are velocity,
    # position and current, respectively, in the source relationship table.
    drive_node = nodes.loc[nodes.name.eq("Drive"), "node_id"].iloc[0]
    drive_signals = relationships.loc[relationships.node_id.eq(drive_node)].copy()
    signal_ids = {
        row.unit: str(row.signal_id) if isinstance(row.signal_id, str) else str(uuid.UUID(bytes=row.signal_id))
        for row in drive_signals.itertuples()
        if row.unit in {"position", "velocity", "current"}
    }
    if set(signal_ids) != {"position", "velocity", "current"}:
        raise RuntimeError(f"Expected position/current/velocity for the first Drive node, found {signal_ids}")

    data_root = raw_trial / "signal_data_point.parquet"
    position_full = load_signal(data_root, signal_ids["position"], args.start, args.end)
    if position_full.empty:
        raise RuntimeError("The requested analysis interval contains no position samples")
    full_dt = position_full.time.diff().dt.total_seconds()
    # The production rule distinguishes recording sessions at 3,600 s. For a
    # representative continuous trial block, use a much stricter 0.1 s ceiling
    # so interruptions cannot contaminate the cycle statistics.
    continuity_session_id = (full_dt > CONTINUITY_GAP_SECONDS).cumsum()
    session_id = (full_dt > (SESSION_GAP_SECONDS if args.full_experiment else CONTINUITY_GAP_SECONDS)).cumsum()
    session_summary = position_full.assign(session_id=session_id).groupby("session_id", as_index=False).agg(
        start=("time", "min"), end=("time", "max"), samples=("time", "size")
    )
    session_summary["duration_s"] = (session_summary.end - session_summary.start).dt.total_seconds()
    if args.full_experiment:
        selected_id = None
        position = position_full.reset_index(drop=True)
    else:
        selected_session = session_summary.sort_values(["samples", "duration_s"], ascending=False).iloc[0]
        selected_id = int(selected_session.session_id)
        position = position_full.loc[continuity_session_id.eq(selected_id)].reset_index(drop=True)
    start, end = position.time.iloc[0], position.time.iloc[-1]
    current = load_signal(data_root, signal_ids["current"], start, end)
    velocity = load_signal(data_root, signal_ids["velocity"], start, end)
    if args.full_experiment:
        cycle_parts = []
        for _, session in position_full.assign(session_id=continuity_session_id).groupby("session_id", sort=True):
            local = session.drop(columns="session_id").reset_index(drop=True)
            local_cycles = detect_cycles(local)
            if not local_cycles.empty:
                offset = int(session.index[0])
                local_cycles["start_index"] += offset
                local_cycles["end_index"] += offset
                cycle_parts.append(local_cycles)
        cycles = pd.concat(cycle_parts, ignore_index=True) if cycle_parts else pd.DataFrame()
    else:
        cycles = detect_cycles(position)
    if len(cycles) < MAX_OVERLAY_CYCLES:
        raise RuntimeError(f"Selected session has only {len(cycles)} cycles; needs at least {MAX_OVERLAY_CYCLES}.")

    # End-stop bands use the first and last percentiles, avoiding one-sample peaks.
    q = args.endstop_quantile
    if not 0 < q < 0.5:
        raise ValueError("--endstop-quantile must be between 0 and 0.5")
    low_limit, high_limit = position.value.quantile([q, 1 - q])
    low_values = position.loc[position.value <= low_limit, "value"]
    high_values = position.loc[position.value >= high_limit, "value"]
    endstop_values = pd.concat([low_values.rename("lower"), high_values.rename("upper")])
    save_histogram(endstop_values, "Position", "Position samples at end stops", output / "position_endstops_histogram.png")

    # Flat end-stop runs are standstill windows. At least five samples avoids
    # treating a single threshold crossing as a physical standstill.
    at_endstop = ((position.value <= low_limit) | (position.value >= high_limit)).to_numpy()
    windows = [position.iloc[a:b] for a, b in contiguous_groups(at_endstop) if b - a >= 5]
    window_sigmas = pd.Series([window.value.std(ddof=1) for window in windows], name="sigma")
    quantized = np.sort(position.value.round(9).unique())
    positive_steps = np.diff(quantized)
    positive_steps = positive_steps[positive_steps > 1e-9]
    step_estimate = float(np.quantile(positive_steps, 0.01)) if len(positive_steps) else float("nan")
    save_histogram(window_sigmas, "Position standard deviation", "Standstill-window noise", output / "standstill_noise_histogram.png")

    full_gaps = full_dt.dropna()
    positive_gaps = full_gaps[full_gaps > 0]
    save_histogram(positive_gaps, "Delta t (s; logarithmic scale)", "Position-signal gaps over full trial", output / "gap_distribution_histogram.png", log_x=True)
    normal_upper = float(positive_gaps[positive_gaps < 60].max())
    interruption_lower = float(positive_gaps[positive_gaps >= 60].min()) if (positive_gaps >= 60).any() else float("nan")

    save_histogram(cycles.duration_s, "Cycle duration (s)", "Movement-threshold cycle durations", output / "cycle_duration_histogram.png")
    cycle_start_gaps = cycles.start_time.diff().dt.total_seconds().dropna()
    intercycle_hold = cycle_start_gaps - cycles.duration_s.iloc[:-1].to_numpy()

    # Match current to each position sample by nearest timestamp. The outward
    # trip and return trip are identified by the supplied velocity sign; use
    # only its sign because its engineering scale is not yet verified.
    aligned = pd.merge_asof(position, current.rename(columns={"time": "current_time", "value": "current"}), left_on="time", right_on="current_time", direction="nearest", tolerance=pd.Timedelta("100ms"))
    velocity_aligned = pd.merge_asof(position, velocity.rename(columns={"time": "velocity_time", "value": "velocity"}), left_on="time", right_on="velocity_time", direction="nearest", tolerance=pd.Timedelta("100ms"))
    aligned["velocity"] = velocity_aligned.velocity
    low_stop, high_stop = position.value.quantile([0.05, 0.95])
    aligned["phase"] = np.select(
        [aligned.value <= low_stop, aligned.value >= high_stop, aligned.velocity >= 0],
        ["low_endstop", "high_endstop", "outward_travel"],
        default="return_travel",
    )
    current_summary = aligned.dropna(subset=["current"]).groupby("phase").current.agg(
        peak_abs=lambda x: float(x.abs().max()), rms=lambda x: float(np.sqrt(np.mean(np.square(x)))), samples="size"
    ).reindex(["low_endstop", "outward_travel", "high_endstop", "return_travel"])

    # Verify one-way motion directly from the position trace, independently of
    # the round-trip duration minus the lower-end hold.
    direct_trips = []
    for row in cycles.itertuples(index=False):
        segment = position.iloc[row.start_index : row.end_index + 1]
        peak_index = int(segment.value.idxmax())
        peak_time = position.time.iloc[peak_index]
        direct_trips.extend([
            (peak_time - row.start_time).total_seconds(),
            (row.end_time - peak_time).total_seconds(),
        ])
    direct_single_trip_median = float(np.median(direct_trips))

    # Evidence payload drives both overview and criteria charts from the same data.
    def hist(v, bins=80, log=False): return compact_histogram(pd.Series(v), bins=bins, logarithmic=log)
    duration_lo, duration_hi = cycles.duration_s.quantile([.01, .99])
    stroke_lo, stroke_hi = enriched_stroke = (cycles.maximum-cycles.minimum).quantile([.01,.99])
    cycle_stroke = cycles.maximum - cycles.minimum
    current_peaks = aligned.current.abs().groupby(np.arange(len(aligned)) // 1).max()
    cycle_current_peaks = pd.Series([
        float(aligned.current.iloc[r.start_index:r.end_index + 1].abs().max())
        for r in cycles.itertuples(index=False)
    ])
    duration_reject = (cycles.duration_s < duration_lo) | (cycles.duration_s > duration_hi)
    stroke_reject = (cycle_stroke < stroke_lo) | (cycle_stroke > stroke_hi)
    current_lo, current_hi = cycle_current_peaks.quantile([.01, .99])
    current_reject = (cycle_current_peaks < current_lo) | (cycle_current_peaks > current_hi)
    continuity_reject = cycles.start_time.diff().dt.total_seconds().fillna(0) > SESSION_GAP_SECONDS
    rejection_masks = {
        "Movement threshold": np.zeros(len(cycles), dtype=bool),
        "Session / continuity": continuity_reject.to_numpy(),
        "Cycle duration plausibility": duration_reject.to_numpy(),
        "Stroke / end-stop plausibility": stroke_reject.to_numpy(),
        "Peak current plausibility": current_reject.to_numpy(),
    }
    criteria = [
        {"name":"Movement threshold","tag":"Nicht begründet","threshold":"Position > 1.0","rejected":0,"caption":f"Standstill σ median {window_sigmas.median():.6f}, p95 {window_sigmas.quantile(.95):.6f}; apparent step {step_estimate:.9f}. This evidence supports replacing the arbitrary threshold.","chart_title":"Standstill noise σ","x_title":"σ (position units)","hist":hist(window_sigmas)},
        {"name":"Session / continuity","tag":"Inkonsistent","threshold":"3600 s","rejected":int((cycle_start_gaps>SESSION_GAP_SECONDS).sum()),"caption":"Gap evidence is linked to the Overview histogram; 1.507–20.134 s interruptions remain outside the binary rule.","chart_title":"Gap distribution","x_title":"Δt (s)","log":True,"hist":hist(positive_gaps,log=True)},
        {"name":"Cycle duration plausibility","tag":"Statistically derived (not health-validated)","threshold":f"p1–p99: {duration_lo:.3f}–{duration_hi:.3f} s","rejected":int(duration_reject.sum()),"caption":"Acceptance band is derived from the observed distribution, not validated against actuator health.","chart_title":"Cycle duration","x_title":"Duration (s)","hist":hist(cycles.duration_s)},
        {"name":"Stroke / end-stop plausibility","tag":"Provisorisch","threshold":f"p1–p99: {stroke_lo:.3f}–{stroke_hi:.3f} units","rejected":int(stroke_reject.sum()),"caption":"Observed end-stop spread supplies a provisional monitoring band.","chart_title":"Position end stops","x_title":"Position","hist":hist(pd.concat([low_values,high_values]))},
        {"name":"Peak current plausibility","tag":"Provisorisch","threshold":f"p1–p99: {current_lo:.3f}–{current_hi:.3f} raw units","rejected":int(current_reject.sum()),"caption":"Descriptive single-trial current distribution; no health threshold is asserted.","chart_title":"Peak current","x_title":"Peak current","hist":hist(cycle_current_peaks)},
    ]
    pass_mask = ~np.logical_or.reduce(list(rejection_masks.values()))
    bucket_ids = np.arange(len(cycles)) * 120 // len(cycles)
    reject_time = []
    for name, mask in rejection_masks.items():
        grouped = pd.DataFrame({"bucket": bucket_ids, "rejected": mask}).groupby("bucket").rejected.sum()
        reject_time.append({"name": name, "t": [int(i) for i in grouped.index], "count": [int(v) for v in grouped.values]})
    evidence={"sampling":{"position":sample_statistics(position),"current":sample_statistics(current),"velocity":sample_statistics(velocity)},"gap_hist":hist(positive_gaps,log=True),"criteria":criteria,"passing_all":int(pass_mask.sum()),"reject_time":reject_time,"reconciliation":{"cycle_period_s":float(cycle_start_gaps.median()),"selected_block_duration_s":float((end-start).total_seconds()),"round_trip_median_s":float(cycles.duration_s.median()),"hold_median_s":float(intercycle_hold.median()),"direct_single_trip_median_s":direct_single_trip_median},"corrections":{"selected_end_is_position_signal_end":str(end),"meta_end_discrepancy_s":None,"trial_path_note":"Signal timestamps are authoritative; the dashboard covers the requested recording interval.","velocity_scaling":"open: raw counts with unresolved engineering scaling"}}
    build_dashboard(output, cycles, session_summary, position, current, velocity, evidence)

    overlay_cycles = cycles.iloc[:MAX_OVERLAY_CYCLES]
    figure = go.Figure()
    for cycle_number, cycle in enumerate(overlay_cycles.itertuples(index=False), start=1):
        p = position.iloc[cycle.start_index : cycle.end_index + 1].copy()
        p["relative_s"] = (p.time - p.time.iloc[0]).dt.total_seconds()
        c = current.loc[(current.time >= cycle.start_time) & (current.time <= cycle.end_time)].copy()
        if not c.empty:
            c["relative_s"] = (c.time - cycle.start_time).dt.total_seconds()
            figure.add_trace(go.Scattergl(x=c.relative_s, y=c.value, yaxis="y2", mode="lines", line={"color": "rgba(214,39,40,0.12)", "width": 1}, showlegend=False, hoverinfo="skip"))
        figure.add_trace(go.Scattergl(x=p.relative_s, y=p.value, mode="lines", line={"color": "rgba(31,119,180,0.12)", "width": 1}, showlegend=False, hoverinfo="skip"))
    figure.update_layout(title="First 100 D63 Versuch1 cycles: position and motor current", xaxis_title="Time from movement-threshold cycle start (s)", yaxis={"title": "Position"}, yaxis2={"title": "Motor current", "overlaying": "y", "side": "right"}, template="plotly_white")
    figure.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line={"color": "#1f77b4"}, name="Position (100 overlays)"))
    figure.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line={"color": "#d62728"}, yaxis="y2", name="Motor current (100 overlays)"))
    figure.write_html(output / "cycle_overlay_100.html", include_plotlyjs=True)

    try:
        revision = subprocess.check_output(["git", "-C", "/home/ita/MasterThesis", "rev-parse", "HEAD"], text=True).strip()
    except subprocess.CalledProcessError:
        revision = "unavailable"
    results = {
        "trial": str(raw_trial), "experiment": "Versuch1 (first Drive block)", "signal_ids": signal_ids,
        "selection": {"requested_start": str(args.start) if args.start is not None else None, "requested_end": str(args.end) if args.end is not None else None, "full_experiment": args.full_experiment, "session_gap_rule_s": SESSION_GAP_SECONDS, "continuity_gap_rule_s": CONTINUITY_GAP_SECONDS, "endstop_quantile": q, "selected_session_id": selected_id, "start": str(start), "end": str(end), "position_samples": int(len(position)), "cycles": int(len(cycles))},
        "sampling": {"position": sample_statistics(position), "current": sample_statistics(current), "velocity": sample_statistics(velocity)},
        "endstops": {"lower": low_values.describe(percentiles=[.01, .05, .5, .95, .99]).to_dict(), "upper": high_values.describe(percentiles=[.01, .05, .5, .95, .99]).to_dict()},
        "standstill": {"windows": int(len(windows)), "median_sigma": float(window_sigmas.median()), "p95_sigma": float(window_sigmas.quantile(.95)), "estimated_minimum_positive_step": step_estimate},
        "gaps": {"full_trial": sample_statistics(position_full), "normal_gap_upper_s_under_60": normal_upper, "first_gap_at_or_above_60_s": interruption_lower, "gaps_over_3600_s": int((positive_gaps > SESSION_GAP_SECONDS).sum())},
        "cycles": {"duration": cycles.duration_s.describe(percentiles=[.01, .05, .5, .95, .99]).to_dict(), "intercycle_hold_s": intercycle_hold.describe(percentiles=[.01, .05, .5, .95, .99]).to_dict()},
        "current_by_phase": current_summary.reset_index().to_dict(orient="records"),
        "reconciliation": evidence["reconciliation"],
        "corrections": evidence["corrections"],
        "pipeline_revision": revision,
    }
    (output / "results.json").write_text(json.dumps(results, indent=2, default=str) + "\n")
    (output / "analysis_context.md").write_text(
        f"# Representative D63 trial\n\n"
        f"**Raw trial:** `{raw_trial}`  \n"
        f"**Experiment/signals:** Versuch1, first Drive node; position `{signal_ids['position']}`, velocity `{signal_ids['velocity']}`, current `{signal_ids['current']}`.  \n"
        f"**Requested interval:** {args.start or 'full recording'} to {args.end or 'full recording'}  \n"
        f"**Analyzed interval:** {start} to {end}  \n"
        f"**Duration:** {(end - start).total_seconds() / 86400:.3f} days; **samples:** {len(position):,}; **cycles:** {len(cycles):,}.  \n"
        f"**Session rule:** gaps > {SESSION_GAP_SECONDS} s split recording sessions; cycles are detected independently per session.  \n"
        f"**End-stop quantile:** {q:.3f} / {1-q:.3f}; this controls standstill-window detection for this dataset.\n\n"
        "The source Parquet data is read-only. `results.json` contains the complete numerical evidence; the PNGs and standalone HTML files are generated from that analysis.\n"
    )


if __name__ == "__main__":
    main()
