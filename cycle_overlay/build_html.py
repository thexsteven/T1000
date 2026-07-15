"""
Step 3 of the actuator-lifetime dashboard pipeline.

Injects the compact JSON artifacts (output/meta.json, output/trend.json,
output/pool.json produced by build_dashboard_data.py) into
dashboard_template.html, producing a single self-contained HTML file
that can be opened directly in a browser (Plotly.js is loaded from CDN;
all data is inlined, so no local server / file:// fetch restriction
applies).
"""
OUT = "output"

with open("dashboard_template.html") as f:
    template = f.read()

with open(f"{OUT}/meta.json") as f:
    meta = f.read()
with open(f"{OUT}/trend.json") as f:
    trend = f.read()
with open(f"{OUT}/pool.json") as f:
    pool = f.read()

html = (template
        .replace("__META_JSON__", meta)
        .replace("__TREND_JSON__", trend)
        .replace("__POOL_JSON__", pool))

out_path = f"{OUT}/actuator_lifetime_dashboard.html"
with open(out_path, "w") as f:
    f.write(html)

import os
print("wrote", out_path, f"{os.path.getsize(out_path)/1e6:.2f} MB")
