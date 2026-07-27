"""
Build an HTML report overlaying Drive velocity & position cycles for
D32 / Versuch1, at five views:
  1. A single representative cycle
  2. 100 consecutive cycles (short time window) overlaid
  3. 100 cycles spread across the whole ~6 month endurance run, overlaid
  4. 100 consecutive cycles shown in a row (real elapsed time, ~184s)
  5. 100 randomly chosen active cycles shown in a row (filmstrip layout)

Cycle boundaries come from the Magnetschalter_Counter signal (one
increment per stroke). Windows are chosen away from experiment pauses.
"""
import pickle

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUT = "output"
VEL_UNIT = "m/s"   # from units.parquet: common_code='velocity', symbol='m/s'
POS_UNIT = "m"     # common_code='position', symbol='m'


def load(name):
    return pd.read_parquet(f"{OUT}/{name}.parquet")


def assign_cycle(df, boundaries):
    """Attach cycle_index (0-based, chronological) and time_in_cycle (ms) columns."""
    starts = np.array([b[0].value for b in boundaries])
    df = df.copy()
    t = df["time"].values.astype("datetime64[ns]").astype(np.int64)
    idx = np.searchsorted(starts, t, side="right") - 1
    idx = np.clip(idx, 0, len(boundaries) - 1)
    df["cycle_index"] = idx
    cycle_start_ns = starts[idx]
    df["time_in_cycle_ms"] = (t - cycle_start_ns) / 1e6
    df["cycle_start_time"] = pd.to_datetime(cycle_start_ns)
    return df


def build_single_cycle_figure():
    vel = load("vel_single")
    pos = load("pos_single")
    with open(f"{OUT}/single_boundary_v1.pkl", "rb") as f:
        boundary = pickle.load(f)
    vel = assign_cycle(vel, [boundary])
    pos = assign_cycle(pos, [boundary])

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
        subplot_titles=(f"Velocity ({VEL_UNIT})", f"Position ({POS_UNIT})"),
    )
    fig.add_trace(go.Scatter(x=vel["time_in_cycle_ms"], y=vel["value"],
                              mode="lines+markers", name="Velocity",
                              line=dict(color="#1f77b4")), row=1, col=1)
    fig.add_trace(go.Scatter(x=pos["time_in_cycle_ms"], y=pos["value"],
                              mode="lines+markers", name="Position",
                              line=dict(color="#ff7f0e")), row=2, col=1)
    fig.update_xaxes(title_text="Time within cycle (ms)", row=2, col=1)
    fig.update_yaxes(title_text=VEL_UNIT, row=1, col=1)
    fig.update_yaxes(title_text=POS_UNIT, row=2, col=1)
    fig.update_layout(
        title="1. A single representative cycle (Drive, Versuch1)",
        height=550, showlegend=False, template="plotly_white",
    )
    return fig


def build_overlay_figure(vel_name, pos_name, boundary_name, title, color_label,
                          color_values_fn):
    vel = load(vel_name)
    pos = load(pos_name)
    with open(f"{OUT}/{boundary_name}.pkl", "rb") as f:
        boundaries = pickle.load(f)
    vel = assign_cycle(vel, boundaries)
    pos = assign_cycle(pos, boundaries)

    color_vals = color_values_fn(boundaries)
    cmin, cmax = min(color_vals), max(color_vals)

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
        subplot_titles=(f"Velocity ({VEL_UNIT})", f"Position ({POS_UNIT})"),
    )

    for i, (s, e) in enumerate(boundaries):
        cv = vel[vel["cycle_index"] == i]
        cp = pos[pos["cycle_index"] == i]
        color = f"rgba({','.join(str(c) for c in _colorscale(color_vals[i], cmin, cmax))})"
        fig.add_trace(go.Scatter(
            x=cv["time_in_cycle_ms"], y=cv["value"], mode="lines",
            line=dict(color=color, width=1), opacity=0.6,
            showlegend=False,
            hovertemplate=f"cycle {i}<br>t=%{{x:.0f}} ms<br>v=%{{y:.1f}} {VEL_UNIT}<extra></extra>",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=cp["time_in_cycle_ms"], y=cp["value"], mode="lines",
            line=dict(color=color, width=1), opacity=0.6,
            showlegend=False,
            hovertemplate=f"cycle {i}<br>t=%{{x:.0f}} ms<br>p=%{{y:.4f}} {POS_UNIT}<extra></extra>",
        ), row=2, col=1)

    # invisible trace just to render a shared colorbar
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(
            colorscale="Viridis", cmin=cmin, cmax=cmax,
            color=[cmin], colorbar=dict(title=color_label, len=0.9),
            showscale=True,
        ),
        showlegend=False,
    ), row=1, col=1)

    fig.update_xaxes(title_text="Time within cycle (ms)", row=2, col=1)
    fig.update_yaxes(title_text=VEL_UNIT, row=1, col=1)
    fig.update_yaxes(title_text=POS_UNIT, row=2, col=1)
    fig.update_layout(title=title, height=650, template="plotly_white")
    return fig


def _colorscale(v, vmin, vmax):
    """Map v in [vmin, vmax] to an RGBA viridis-like color."""
    import plotly.colors as pc
    frac = 0 if vmax == vmin else (v - vmin) / (vmax - vmin)
    rgb = pc.sample_colorscale("Viridis", [frac])[0]
    # rgb like 'rgb(r, g, b)' -> extract numbers, add alpha
    nums = rgb[rgb.find("(") + 1:rgb.find(")")].split(",")
    return [n.strip() for n in nums] + ["0.7"]


def _break_on_cycle(df, x_col):
    """Insert a NaN row after each cycle so lines don't connect across gaps."""
    out = []
    for _, g in df.groupby("cycle_index", sort=True):
        out.append(g)
        gap = g.iloc[[-1]].copy()
        gap[x_col] = np.nan
        gap["value"] = np.nan
        out.append(gap)
    return pd.concat(out, ignore_index=True)


def build_row_figure(vel_name, pos_name, boundaries_name, title, mode,
                      tick_every=10, subtitle=""):
    """
    A 'filmstrip' view: full cycles placed one after another along the x-axis.

    mode='contiguous' -> x is real elapsed time (cycles are back-to-back
      in reality, e.g. 100 consecutive cycles).
    mode='filmstrip'  -> cycles are NOT adjacent in real time (e.g. randomly
      sampled cycles); each cycle gets its own fixed-width slot with a
      small gap, and x-axis ticks show the real date of each slot.
    """
    vel = load(vel_name)
    pos = load(pos_name)
    with open(f"{OUT}/{boundaries_name}.pkl", "rb") as f:
        boundaries = pickle.load(f)
    vel = assign_cycle(vel, boundaries)
    pos = assign_cycle(pos, boundaries)

    if mode == "contiguous":
        t0 = boundaries[0][0]
        vel["x"] = (vel["time"] - t0).dt.total_seconds()
        pos["x"] = (pos["time"] - t0).dt.total_seconds()
        slot_positions = [(b[0] - t0).total_seconds() for b in boundaries]
        slot_width = np.median(np.diff(slot_positions)) if len(slot_positions) > 1 else 2.0
    else:
        slot_width = 2.0  # seconds per slot, fixed spacing regardless of real time gap
        vel["x"] = vel["cycle_index"] * slot_width + vel["time_in_cycle_ms"] / 1000.0
        pos["x"] = pos["cycle_index"] * slot_width + pos["time_in_cycle_ms"] / 1000.0
        slot_positions = [i * slot_width for i in range(len(boundaries))]

    vel["cycle_start_time"] = vel["cycle_start_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    pos["cycle_start_time"] = pos["cycle_start_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    vel_b = _break_on_cycle(vel, "x")
    pos_b = _break_on_cycle(pos, "x")

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
        subplot_titles=(f"Velocity ({VEL_UNIT})", f"Position ({POS_UNIT})"),
    )

    # light alternating background bands, one per cycle, for a clean filmstrip feel
    for i in range(0, len(boundaries), 2):
        x0 = slot_positions[i]
        x1 = slot_positions[i + 1] if i + 1 < len(slot_positions) else x0 + slot_width
        fig.add_vrect(x0=x0, x1=x1, fillcolor="lightgray", opacity=0.15,
                       line_width=0, row="all", col=1)

    fig.add_trace(go.Scatter(x=vel_b["x"], y=vel_b["value"], mode="lines",
                              line=dict(color="#1f77b4", width=1),
                              showlegend=False,
                              hovertemplate="cycle %{customdata[0]}<br>%{customdata[1]}<br>"
                                            f"v=%{{y:.1f}} {VEL_UNIT}<extra></extra>",
                              customdata=vel_b[["cycle_index", "cycle_start_time"]].values,
                              ), row=1, col=1)
    fig.add_trace(go.Scatter(x=pos_b["x"], y=pos_b["value"], mode="lines",
                              line=dict(color="#ff7f0e", width=1),
                              showlegend=False,
                              hovertemplate="cycle %{customdata[0]}<br>%{customdata[1]}<br>"
                                            f"p=%{{y:.4f}} {POS_UNIT}<extra></extra>",
                              customdata=pos_b[["cycle_index", "cycle_start_time"]].values,
                              ), row=2, col=1)

    # sparse tick labels showing the real date/time of every Nth cycle
    tick_idx = list(range(0, len(boundaries), tick_every))
    tickvals = [slot_positions[i] for i in tick_idx]
    if mode == "contiguous":
        ticktext = [f"{slot_positions[i]:.0f}s" for i in tick_idx]
        x_title = "Elapsed time (s), 100 consecutive cycles back-to-back"
    else:
        ticktext = [boundaries[i][0].strftime("%b %d\n%H:%M") for i in tick_idx]
        x_title = "Cycle slot (fixed width per cycle) \u2014 label = real date/time of that cycle"

    fig.update_xaxes(tickvals=tickvals, ticktext=ticktext, row=2, col=1, title_text=x_title)
    fig.update_xaxes(tickvals=tickvals, ticktext=ticktext, row=1, col=1)
    fig.update_yaxes(title_text=VEL_UNIT, row=1, col=1)
    fig.update_yaxes(title_text=POS_UNIT, row=2, col=1)
    fig.update_layout(
        title=title + (f"<br><sup>{subtitle}</sup>" if subtitle else ""),
        height=650, template="plotly_white",
    )
    return fig


def main():
    fig1 = build_single_cycle_figure()
    fig2 = build_overlay_figure(
        "vel_consec", "pos_consec", "consec_boundaries_v1",
        "2. 100 consecutive cycles overlaid (Drive, Versuch1, ~3 min window)",
        "Cycle order (0-99)",
        lambda boundaries: list(range(len(boundaries))),
    )
    fig3 = build_overlay_figure(
        "vel_spread", "pos_spread", "spread_boundaries_v1",
        "3. ~100 cycles spread across the full run overlaid (Drive, Versuch1, Dec 2025\u2013Jun 2026)",
        "Cycle date",
        lambda boundaries: [b[0].value for b in boundaries],
    )
    fig4 = build_row_figure(
        "vel_consec", "pos_consec", "consec_boundaries_v1",
        "4. 100 consecutive cycles in a row (Drive, Versuch1)",
        mode="contiguous",
        subtitle="Real, unmodified time series \u2014 ~184s of continuous operation, back-to-back.",
    )
    fig5 = build_row_figure(
        "vel_random", "pos_random", "random_boundaries_v1",
        "5. 100 randomly chosen active cycles, shown in a row (Drive, Versuch1)",
        mode="filmstrip",
        subtitle="Each cycle sits in its own fixed-width slot; slots are ordered chronologically "
                 "but not adjacent in real time \u2014 hover for the exact date/time of each cycle.",
    )

plotly_js = Path(__file__).with_name("plotly-2.35.2.min.js").read_text()
    html_parts = [
        "<html><head><meta charset='utf-8'>"
        "<title>D32 Versuch1 - Drive cycle overlay</title>"
        f"<script>{plotly_js}</script>"
        "<style>body{font-family:Arial,Helvetica,sans-serif;max-width:1100px;margin:20px auto;}"

    html_parts = [
        "<html><head><meta charset='utf-8'>"
        "<title>D32 Versuch1 - Drive cycle overlay</title>"
        "<style>body{font-family:Arial,Helvetica,sans-serif;max-width:1100px;margin:20px auto;}"
        "h1{font-size:22px;} h2{font-size:17px;margin-top:40px;border-top:1px solid #ddd;padding-top:20px;}"
        "p.note{color:#555;font-size:14px;}</style>"
        "</head><body>"
        "<h1>D32 / Versuch1 - Drive velocity & position, cycle overlay</h1>"
        "<p class='note'>Cycles are defined by the Magnetschalter_Counter signal "
        "(one increment per stroke, median cycle length ~1.84s). "
        "Windows were chosen away from experiment pauses "
        "(gaps &gt; a few cycle-lengths were excluded).</p>"
    ]
    for fig in (fig1, fig2, fig3, fig4, fig5):
        html_parts.append(fig.to_html(full_html=False, include_plotlyjs=False))
    html_parts.append("</body></html>")

    with open(f"{OUT}/cycle_overlay_report.html", "w") as f:
        f.write("\n".join(html_parts))
    print("wrote", f"{OUT}/cycle_overlay_report.html")


if __name__ == "__main__":
    main()
