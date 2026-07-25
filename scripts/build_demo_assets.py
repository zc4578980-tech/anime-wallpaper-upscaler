#!/usr/bin/env python
"""Build reproducible repository overview images from local demo outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

TRIPTYCH_SIZE = (1440, 810)
SOCIAL_PREVIEW_SIZE = (1280, 640)
PANEL_SIZE = (440, 700)
BACKGROUND = "#111417"
PANEL_BACKGROUND = "#20252a"
TEXT = "#f5f7f8"
MUTED_TEXT = "#b7c0c7"
ACCENT = "#5ec2a5"


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "segoeui.ttf",
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
        "DejaVuSans.ttf",
        "LiberationSans-Regular.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _open_rgb(path: Path) -> Image.Image:
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


def _save(canvas: Image.Image, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.casefold() in {".jpg", ".jpeg"}:
        canvas.save(output, format="JPEG", quality=95, optimize=True, subsampling=0)
    else:
        canvas.save(output, format="PNG", optimize=True)


def build_triptych(
    source: Path,
    upscaled: Path,
    wallpaper: Path,
    output: Path,
) -> None:
    """Build a labeled three-panel overview without cropping any input."""

    canvas = Image.new("RGB", TRIPTYCH_SIZE, BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    labels = ("Original", "Real-ESRGAN upscale", "Finished wallpaper")
    images = (_open_rgb(source), _open_rgb(upscaled), _open_rgb(wallpaper))
    label_font = _font(24)
    panel_top = 80

    for x, label, image in zip((40, 500, 960), labels, images, strict=True):
        panel_box = (x, panel_top, x + PANEL_SIZE[0], panel_top + PANEL_SIZE[1])
        draw.text((x, 34), label, fill=TEXT, font=label_font)
        draw.rectangle(panel_box, fill=PANEL_BACKGROUND, outline="#46515a", width=2)
        _paste_contained(canvas, image, panel_box)

    _save(canvas, output)


def build_social_preview(overview: Path, output: Path) -> None:
    """Build a GitHub/social preview that contains the complete overview."""

    canvas = Image.new("RGB", SOCIAL_PREVIEW_SIZE, BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 12, SOCIAL_PREVIEW_SIZE[1]), fill=ACCENT)
    draw.text(
        (46, 28),
        "Anime Wallpaper Upscaler",
        fill=TEXT,
        font=_font(38),
    )
    draw.text(
        (48, 82),
        "Full composition. Screen ready. Built on Real-ESRGAN.",
        fill=MUTED_TEXT,
        font=_font(22),
    )
    _paste_contained(canvas, _open_rgb(overview), (40, 130, 1240, 616))
    _save(canvas, output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the repository overview and social-preview images."
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--upscaled", required=True, type=Path)
    parser.add_argument("--wallpaper", required=True, type=Path)
    parser.add_argument("--overview", required=True, type=Path)
    parser.add_argument("--social-preview", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build_triptych(args.source, args.upscaled, args.wallpaper, args.overview)
    build_social_preview(args.overview, args.social_preview)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
