#!/usr/bin/env python3
"""Create an animated neofetch-style SVG info card."""
from __future__ import annotations

import os
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path("info-card.svg")
STATIC = os.getenv("STATIC", "0") == "1"

ROWS = [
    ("NOW", "B.Tech IT · CHARUSAT · Class of 2027"),
    ("FOCUS", "AI/ML · BCI · Multimodal AI · Geospatial AI"),
    ("BUILDING", "VenueIQ · Case404 · BCI Robotic Arm"),
    ("RESEARCH", "Emotion-aware EEG → ML → real-time control"),
    ("STACK", "Python · C++ · TypeScript · Next.js · Streamlit"),
    ("INTERNSHIP", "AI Research · Planto.ai / Coding Jr."),
    ("STATUS", "Open to research & AI engineering opportunities"),
]

W, H = 490, 550
BG = "#0d1117"
FG = "#e6edf3"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
PURPLE = "#bc8cff"


def animate(tag: str, begin: float, attrs: str = "") -> str:
    if STATIC:
        return ""
    return f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'


def build() -> str:
    parts = [
        f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>',
        '<circle cx="18" cy="18" r="4" fill="#ff5f56"/>',
        '<circle cx="32" cy="18" r="4" fill="#ffbd2e"/>',
        '<circle cx="46" cy="18" r="4" fill="#27c93f"/>',
        '<text x="62" y="22" fill="#6e7681" font-family="monospace" font-size="11">arman@github:~$ neofetch</text>',
        f'<line x1="18" y1="38" x2="472" y2="38" stroke="#30363d"/>',
        '<text x="20" y="76" fill="#58a6ff" font-family="monospace" font-size="22" font-weight="700">ARMAN KOTHARIYA</text>',
        '<text x="20" y="99" fill="#8b949e" font-family="monospace" font-size="11">AI / ML · RESEARCH · BUILDER</text>',
    ]

    y = 138
    for i, (key, value) in enumerate(ROWS):
        delay = 0.42 + i * 0.22
        parts.append(f'<g opacity="{"1" if STATIC else "0"}">')
        parts.append(f'<text x="20" y="{y}" fill="{ACCENT}" font-family="monospace" font-size="12" font-weight="700">{escape(key)}:</text>')
        parts.append(f'<text x="124" y="{y}" fill="{FG}" font-family="monospace" font-size="11">{escape(value)}</text>')
        parts.append(animate("opacity", delay))
        parts.append('</g>')
        y += 49

    y += 4
    parts.extend([
        f'<line x1="20" y1="{y}" x2="470" y2="{y}" stroke="#30363d"/>',
        f'<text x="20" y="{y+31}" fill="{MUTED}" font-family="monospace" font-size="11">MISSION</text>',
        f'<text x="20" y="{y+56}" fill="{GREEN}" font-family="monospace" font-size="11">→ Turn research prototypes into real systems.</text>',
        f'<text x="20" y="{y+80}" fill="{PURPLE}" font-family="monospace" font-size="11">→ Build at the edge of AI × human interaction.</text>',
        f'<text x="20" y="{y+118}" fill="#6e7681" font-family="monospace" font-size="10">OS        : GitHub / India</text>',
        f'<text x="20" y="{y+137}" fill="#6e7681" font-family="monospace" font-size="10">TERM      : ARMAN.EXE</text>',
        f'<text x="20" y="{y+156}" fill="#6e7681" font-family="monospace" font-size="10">UPTIME    : learning · shipping · iterating</text>',
    ])
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Arman Kothariya profile information card"><title>Arman Kothariya — AI/ML Researcher and Builder</title>{"".join(parts)}</svg>'


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"[ok] wrote {OUT}")
