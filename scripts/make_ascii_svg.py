#!/usr/bin/env python3
"""Convert source-prepped.png into a self-typing monochrome ASCII SVG."""
from __future__ import annotations

import html
from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"
IMAGE = Path("source-prepped.png")
OUTPUT = Path("avi-ascii.svg")

# The target is deliberately wide, because terminal glyphs are taller than
# they are wide. This keeps the portrait from becoming too squat.
COLUMNS = 104
ROWS = 54
FONT_SIZE = 9.4
LINE_HEIGHT = 10.2
LEFT = 12
TOP = 15
FG = "#b9c0c8"
BG = "#0d1117"


def resize_gray() -> np.ndarray:
    if not IMAGE.exists():
        raise FileNotFoundError("source-prepped.png not found. Run prep_photo.py first.")
    img = Image.open(IMAGE).convert("L")
    # Compensate for monospace character aspect ratio before sampling.
    img = img.resize((COLUMNS, ROWS), Image.Resampling.LANCZOS)
    return np.array(img, dtype=np.uint8)


def glyph(value: int) -> str:
    idx = round((255 - int(value)) / 255 * (len(RAMP) - 1))
    return RAMP[max(0, min(len(RAMP) - 1, idx))]


def build() -> str:
    grid = resize_gray()
    width = LEFT * 2 + COLUMNS * (FONT_SIZE * 0.62)
    height = 26 + ROWS * LINE_HEIGHT
    total = ROWS * 0.085 + 0.65

    defs = [
        '<filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">',
        '  <feGaussianBlur stdDeviation="1.2" result="b"/>',
        '  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>',
        '</filter>',
    ]
    body = []

    # Terminal chrome.
    body.append(f'<rect x="0" y="0" width="{width:.1f}" height="{height:.1f}" rx="12" fill="{BG}"/>')
    body.append('<circle cx="18" cy="15" r="4" fill="#ff5f56"/>')
    body.append('<circle cx="32" cy="15" r="4" fill="#ffbd2e"/>')
    body.append('<circle cx="46" cy="15" r="4" fill="#27c93f"/>')
    body.append(f'<text x="62" y="18" fill="#6e7681" font-family="monospace" font-size="8">arman@github:~$ portrait</text>')

    body.append(f'<text x="{LEFT}" y="{TOP + 5}" fill="{FG}" font-family="monospace" font-size="{FONT_SIZE}" filter="url(#softGlow)">')
    # The first line is opened/closed per row below; keeping each row in a
    # single text element helps browser rendering performance.
    body[-1] += "</text>"
    body.pop()  # replace with per-row elements

    for r in range(ROWS):
        line = "".join(glyph(v) for v in grid[r])
        # Strip trailing spaces: they make the SVG larger without changing the look.
        line = line.rstrip()
        y = TOP + 5 + r * LINE_HEIGHT
        delay = 0.55 + r * 0.07
        duration = 0.55
        clip_id = f"row{r}"
        # Width of a monospace line in SVG pixels.
        text_width = max(6.0, max(1, len(line)) * FONT_SIZE * 0.62)
        body.append(f'<clipPath id="{clip_id}"><rect x="{LEFT-2}" y="{y-FONT_SIZE}" width="0" height="{LINE_HEIGHT+2}">'
                    f'<animate attributeName="width" from="0" to="{text_width:.1f}" begin="{delay:.2f}s" dur="{duration:.2f}s" fill="freeze"/></rect></clipPath>')
        body.append(f'<g clip-path="url(#{clip_id})">')
        body.append(f'<text x="{LEFT}" y="{y:.1f}" fill="{FG}" font-family="monospace" font-size="{FONT_SIZE}" xml:space="preserve">{html.escape(line)}</text>')
        # A small cursor block follows the wipe edge, then disappears.
        cursor_x = LEFT - 2
        body.append(
            f'<rect x="{cursor_x}" y="{y-FONT_SIZE+1:.1f}" width="2.5" height="{LINE_HEIGHT:.1f}" fill="#d3dae3">'
            f'<animate attributeName="x" from="{cursor_x}" to="{LEFT + text_width:.1f}" begin="{delay:.2f}s" dur="{duration:.2f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" from="1" to="0" begin="{delay+duration:.2f}s" dur="0.01s" fill="freeze"/>'
            f'</rect>'
        )
        body.append('</g>')

    body.append(f'<text x="{LEFT}" y="{height-8}" fill="#6e7681" font-family="monospace" font-size="8">[{total:.1f}s] transmission complete</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}" height="{height:.1f}" '
            f'viewBox="0 0 {width:.1f} {height:.1f}" role="img" aria-label="Animated ASCII portrait of Arman Kothariya">'
            f'<defs>{"".join(defs)}</defs>{"".join(body)}</svg>')


if __name__ == "__main__":
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"[ok] wrote {OUTPUT}")
