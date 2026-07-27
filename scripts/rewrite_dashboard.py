from pathlib import Path
p=Path('/home/ita/t1000/scripts/analyze_representative_d63_trial.py')
s=p.read_text()
start=s.index('def build_dashboard(')
end=s.index('\ndef main() -> None:', start)
new=r"""def build_dashboard(output: Path, cycles: pd.DataFrame, session_summary: pd.DataFrame,
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
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.tabs button,.view').forEach(x=>x.classList.remove('active'));b.classList.add('active');$(b.dataset.v).classList.add('active');}});init();</script></body></html>"""
p.write_text(s[:start]+new+s[end:])
