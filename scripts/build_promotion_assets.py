#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

SIZE = (1280, 640)
BACKGROUND = "#101417"
TEXT = "#f7f8f8"
MUTED = "#c4cbd0"
ACCENT = "#55c2a4"


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
        "segoeui.ttf",
        "DejaVuSans.ttf",
        "LiberationSans-Regular.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _open(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).convert("RGB")


def _paste_contained(
    canvas: Image.Image,
    image: Image.Image,
    box: tuple[int, int, int, int],
) -> None:
    left, top, right, bottom = box
    available = (right - left, bottom - top)
    contained = ImageOps.contain(image, available, Image.Resampling.LANCZOS)
    x = left + (available[0] - contained.width) // 2
    y = top + (available[1] - contained.height) // 2
    canvas.paste(contained, (x, y))


def build_social_preview(detail: Path, wallpaper: Path, output: Path) -> None:
    canvas = Image.new("RGB", SIZE, BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 12, SIZE[1]), fill=ACCENT)
    draw.text((42, 26), "Anime Wallpaper Upscaler", fill=TEXT, font=_font(36))
    draw.text((42, 78), "Pause a frame. Keep it on your desktop.", fill=TEXT, font=_font(28))
    draw.text(
        (42, 119),
        "Local 4x detail + composition-preserving Windows wallpaper",
        fill=MUTED,
        font=_font(18),
    )
    _paste_contained(canvas, _open(detail), (42, 174, 802, 604))
    _paste_contained(canvas, _open(wallpaper), (828, 174, 1238, 604))
    draw.rectangle((42, 174, 802, 604), outline="#69747c", width=2)
    draw.rectangle((828, 174, 1238, 604), outline="#69747c", width=2)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, format="JPEG", quality=94, optimize=True, subsampling=0)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the anime screenshot campaign preview.")
    parser.add_argument("--detail", required=True, type=Path)
    parser.add_argument("--wallpaper", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build_social_preview(args.detail, args.wallpaper, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
