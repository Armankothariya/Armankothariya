#!/usr/bin/env python3
"""Prepare a portrait for ASCII rendering.

Usage:
    python scripts/prep_photo.py source-photo.jpg

Writes:
    source-prepped.png

Notes:
- rembg is used when available to remove the background.
- OpenCV CLAHE boosts local contrast so facial features survive downsampling.
- The final image is composited on white because white becomes the sparse end
  of the ASCII density ramp.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def remove_background_rgba(image_path: Path) -> Image.Image:
    try:
        from rembg import remove  # type: ignore
    except Exception as exc:
        print(f"[warn] rembg unavailable ({exc}); continuing without background removal.")
        return Image.open(image_path).convert("RGBA")

    data = image_path.read_bytes()
    try:
        output = remove(data)
        return Image.open(__import__("io").BytesIO(output)).convert("RGBA")
    except Exception as exc:
        print(f"[warn] rembg failed ({exc}); continuing without background removal.")
        return Image.open(image_path).convert("RGBA")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py source-photo.jpg")
        return 2

    source = Path(sys.argv[1])
    if not source.exists():
        print(f"[error] File not found: {source}")
        return 1

    rgba = remove_background_rgba(source)
    rgba.thumbnail((1400, 1400), Image.Resampling.LANCZOS)

    bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    bg.alpha_composite(rgba)

    rgb = np.array(bg.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Slight local-contrast boost while preserving a soft photographic look.
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # Keep the white background white. This prevents faint background texture
    # from turning into visible ASCII noise.
    white_mask = np.all(rgb > 247, axis=2)
    enhanced[white_mask] = 255

    out = Image.fromarray(enhanced, mode="L")
    out.save("source-prepped.png", optimize=True)
    print("[ok] wrote source-prepped.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
