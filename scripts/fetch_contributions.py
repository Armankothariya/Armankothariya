#!/usr/bin/env python3
"""Fetch a user's public contribution calendar from GitHub's public HTML endpoint.

No GitHub token is required.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

USERNAME = "Armankothariya"
ENDPOINT = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path("data/contributions.json")


def parse_cells(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    cells = []
    for node in soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day"):
        day = node.get("data-date")
        if not day:
            continue
        level_raw = node.get("data-level", "0")
        try:
            level = int(level_raw)
        except ValueError:
            level = 0

        title_text = ""
        title = node.find("title")
        if title:
            title_text = title.get_text(" ", strip=True)
        elif node.find("tool-tip"):
            title_text = node.find("tool-tip").get_text(" ", strip=True)
        elif node.get("aria-label"):
            title_text = node.get("aria-label", "")

        match = re.search(r"(\d[\d,]*) contribution", title_text, flags=re.I)
        count = int(match.group(1).replace(",", "")) if match else None
        cells.append({"date": day, "level": level, "count": count})

    # Fallback: GitHub has historically rendered day cells as <td> only.
    if not cells:
        for node in soup.select("[data-date][data-level]"):
            day = node.get("data-date")
            if not day:
                continue
            try:
                level = int(node.get("data-level", "0"))
            except ValueError:
                level = 0
            aria = node.get("aria-label", "")
            match = re.search(r"(\d[\d,]*) contribution", aria, flags=re.I)
            count = int(match.group(1).replace(",", "")) if match else None
            cells.append({"date": day, "level": level, "count": count})

    if not cells:
        raise RuntimeError("No contribution cells found; GitHub may have changed the HTML structure.")
    return cells


def derive_stats(cells: list[dict[str, Any]]) -> dict[str, Any]:
    parsed = sorted(cells, key=lambda x: x["date"])
    for item in parsed:
        item["count"] = int(item["count"] if item["count"] is not None else 0)

    active = [x for x in parsed if x["count"] > 0]
    best = max(active, key=lambda x: x["count"], default=None)

    longest = 0
    current = 0
    cursor: date | None = None
    run = 0
    for item in parsed:
        d = datetime.strptime(item["date"], "%Y-%m-%d").date()
        if item["count"] > 0:
            if cursor is not None and d == cursor + timedelta(days=1):
                run += 1
            else:
                run = 1
            longest = max(longest, run)
            cursor = d

    today = date.today()
    by_date = {datetime.strptime(x["date"], "%Y-%m-%d").date(): x["count"] for x in parsed}
    probe = today
    current = 0
    while probe in by_date and by_date[probe] > 0:
        current += 1
        probe -= timedelta(days=1)

    monthly = defaultdict(int)
    for item in parsed:
        monthly[item["date"][:7]] += item["count"]

    return {
        "total": sum(x["count"] for x in parsed),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly_totals": dict(sorted(monthly.items())),
        "active_days": len(active),
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "arman-github-profile-art/1.0 (+https://github.com/Armankothariya)"}
    response = requests.get(ENDPOINT, headers=headers, timeout=30)
    response.raise_for_status()
    cells = parse_cells(response.text)
    payload = {
        "username": USERNAME,
        "source": ENDPOINT,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "days": cells,
        "stats": derive_stats(cells),
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[ok] {payload['stats']['total']:,} contributions; wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
