"""
Step 3 of the actuator-lifetime dashboard pipeline.

Injects the compact JSON artifacts (output/meta.json, output/trend.json,
output/pool.json produced by build_dashboard_data.py) into
report_template.html, producing a single self-contained HTML file
that can be opened directly in a browser (Plotly.js is loaded from CDN;
all data is inlined, so no local server / file:// fetch restriction
applies).
"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = Path("/home/ita/ERA-NAS/reports/t1000")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE_PATH = REPORTS_DIR / "dashboard_template_source.html"
if not TEMPLATE_PATH.exists():
    TEMPLATE_PATH = REPORTS_DIR / "dashboard_template.html"

OUT_DIR = SCRIPT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_OUT_DIR = REPORTS_DIR / "output"
REPORT_OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(TEMPLATE_PATH) as f:
    template = f.read()

with open(OUT_DIR / "meta.json") as f:
    meta = f.read()
with open(OUT_DIR / "trend.json") as f:
    trend = f.read()
with open(OUT_DIR / "pool.json") as f:
    pool = f.read()

html = (template
        .replace("__META_JSON__", meta)
        .replace("__TREND_JSON__", trend)
        .replace("__POOL_JSON__", pool))

out_path = REPORT_OUT_DIR / "actuator_lifetime_dashboard.html"
with open(out_path, "w") as f:
    f.write(html)

# Also write the finished dashboard to the browser-facing report path.
report_path = REPORTS_DIR / "dashboard_template.html"
with open(report_path, "w") as f:
    f.write(html)

import os
print("wrote", out_path, f"{os.path.getsize(out_path)/1e6:.2f} MB")
