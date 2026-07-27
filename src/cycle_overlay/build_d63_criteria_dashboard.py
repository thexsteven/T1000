"""Create an offline D63 criteria dashboard from compact evidence JSON."""
from __future__ import annotations

import argparse
from pathlib import Path


PLOTLY = Path(__file__).with_name("plotly-2.35.2.min.js")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    template = Path(__file__).with_name("d63_criteria_dashboard_template.html").read_text()
    args.output.write_text(template.replace("__PLOTLY_JS__", PLOTLY.read_text()).replace("__D63_EVIDENCE__", args.evidence.read_text()))


if __name__ == "__main__":
    main()
