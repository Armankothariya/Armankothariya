#!/usr/bin/env python3
"""Render data/contributions.json as an animated 53-week SVG heatmap."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG = "#0d1117"
TEXT = "#8b949e"
FG = "#e6edf3"
ACCENT = "#58a6ff"
CELL = 10
GAP = 3
LEFT = 42
TOP = 52
WEEKS = 53
ROWS = 7
WIDTH = LEFT + WEEKS * (CELL + GAP) + 26
HEIGHT = 212


def monday_start_for_latest_year(days: list[dict]) -> datetime:
    dates = sorted(datetime.strptime(d["date"], "%Y-%m-%d") for d in days)
    latest = dates[-1]
    # The 53 columns cover the week containing the earliest day through latest.
    start = latest - timedelta(days=364)
    return start - timedelta(days=(start.weekday() + 1) % 7)


def build() -> str:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    days = payload["days"]
    stats = payload["stats"]
    by_date = {datetime.strptime(d["date"], "%Y-%m-%d").date(): d for d in days}
    latest = max(by_date)
    start = latest - timedelta(days=364)
    start = start - timedelta(days=(start.weekday() + 1) % 7)

    parts = [
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="{BG}"/>',
        '<circle cx="18" cy="18" r="4" fill="#ff5f56"/>',
        '<circle cx="32" cy="18" r="4" fill="#ffbd2e"/>',
        '<circle cx="46" cy="18" r="4" fill="#27c93f"/>',
        '<text x="62" y="22" fill="#6e7681" font-family="monospace" font-size="10">arman@github:~$ contributions.sh</text>',
        f'<text x="18" y="40" fill="{FG}" font-family="monospace" font-size="13" font-weight="700">{stats["total"]:,} contributions in the last year</text>',
        '<text x="18" y="58" fill="#6e7681" font-family="monospace" font-size="9">LESS</text>',
        '<text x="8" y="77" fill="#6e7681" font-family="monospace" font-size="9">SUN</text>',
        '<text x="8" y="104" fill="#6e7681" font-family="monospace" font-size="9">WED</text>',
        '<text x="8" y="131" fill="#6e7681" font-family="monospace" font-size="9">SAT</text>',
        '<text x="18" y="186" fill="#6e7681" font-family="monospace" font-size="9">activity → consistency → compounding</text>',
        f'<text x="{WIDTH-216}" y="186" fill="{TEXT}" font-family="monospace" font-size="9">{stats["active_days"]} active days</text>',
    ]

    # Month labels based on where the first day of each month lands.
    seen_months = set()
    for col in range(WEEKS):
        col_date = start + timedelta(days=col * 7)
        label = col_date.strftime("%b")
        key = col_date.strftime("%Y-%m")
        if key not in seen_months and col > 0:
            x = LEFT + col * (CELL + GAP)
            parts.append(f'<text x="{x}" y="69" fill="{TEXT}" font-family="monospace" font-size="9">{label}</text>')
            seen_months.add(key)

    # Bottom-up diagonal reveal. Earlier columns begin first and each later
    # column drops in a little after the previous one.
    for col in range(WEEKS):
        for row in range(ROWS):
            d = start + timedelta(days=col * 7 + row)
            item = by_date.get(d, {"level": 0, "count": 0})
            level = max(0, min(5, int(item.get("level", 0))))
            x = LEFT + col * (CELL + GAP)
            y = TOP + row * (CELL + GAP)
            delay = 0.35 + col * 0.016 + row * 0.009
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{PALETTE[level]}" opacity="0" data-date="{d.isoformat()}" data-count="{item.get("count", 0)}">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.24s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="0 -5" to="0 0" begin="{delay:.3f}s" dur="0.24s" fill="freeze"/>'
                '</rect>'
            )

    # Legend
    legend_y = 156
    for i, color in enumerate(PALETTE):
        x = 52 + i * 18
        parts.append(f'<rect x="{x}" y="{legend_y}" width="11" height="11" rx="2" fill="{color}"/>')
    parts.append(f'<text x="{52 + len(PALETTE)*18 + 8}" y="165" fill="{TEXT}" font-family="monospace" font-size="9">MORE</text>')

    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="GitHub contribution heatmap for Armankothariya"><title>{stats["total"]:,} contributions in the last year</title>{"".join(parts)}</svg>'


if __name__ == "__main__":
    if not DATA.exists():
        raise SystemExit("data/contributions.json not found. Run fetch_contributions.py first.")
    OUT.write_text(build(), encoding="utf-8")
    print(f"[ok] wrote {OUT}")
