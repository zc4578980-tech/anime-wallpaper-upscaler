#!/usr/bin/env python
"""Build a deterministic, redistributable portrait fixture for demos."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

CANVAS_SIZE = (480, 720)
CORNER_COLORS = {
    "top_left": "#f4c95d",
    "top_right": "#63c7b2",
    "bottom_left": "#ef798a",
    "bottom_right": "#72b7e2",
}


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    windows_name = "segoeuib.ttf" if bold else "segoeui.ttf"
    candidates = (
        Path("C:/Windows/Fonts") / windows_name,
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf",
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


def _blend(start: tuple[int, int, int], end: tuple[int, int, int], ratio: float) -> tuple[int, int, int]:
    return tuple(round(a + (b - a) * ratio) for a, b in zip(start, end, strict=True))


def _draw_corner_markers(draw: ImageDraw.ImageDraw) -> None:
    marker = 58
    inset = 14
    width = 6
    right = CANVAS_SIZE[0] - inset - 1
    bottom = CANVAS_SIZE[1] - inset - 1

    draw.line((inset, inset, inset + marker, inset), fill=CORNER_COLORS["top_left"], width=width)
    draw.line((inset, inset, inset, inset + marker), fill=CORNER_COLORS["top_left"], width=width)
    draw.line((right - marker, inset, right, inset), fill=CORNER_COLORS["top_right"], width=width)
    draw.line((right, inset, right, inset + marker), fill=CORNER_COLORS["top_right"], width=width)
    draw.line((inset, bottom - marker, inset, bottom), fill=CORNER_COLORS["bottom_left"], width=width)
    draw.line((inset, bottom, inset + marker, bottom), fill=CORNER_COLORS["bottom_left"], width=width)
    draw.line((right, bottom - marker, right, bottom), fill=CORNER_COLORS["bottom_right"], width=width)
    draw.line((right - marker, bottom, right, bottom), fill=CORNER_COLORS["bottom_right"], width=width)


def build_original_demo(output: Path) -> None:
    """Render a small original scene whose four colored corners expose cropping."""

    image = Image.new("RGB", CANVAS_SIZE)
    draw = ImageDraw.Draw(image)

    for y in range(500):
        ratio = y / 499
        draw.line((0, y, CANVAS_SIZE[0], y), fill=_blend((17, 25, 52), (121, 82, 113), ratio))
    for y in range(500, CANVAS_SIZE[1]):
        ratio = (y - 500) / 219
        draw.line((0, y, CANVAS_SIZE[0], y), fill=_blend((38, 82, 105), (9, 31, 50), ratio))

    stars = ((48, 95), (104, 162), (151, 83), (223, 132), (299, 74), (380, 146), (430, 92))
    for x, y in stars:
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="#f8f1d4")

    draw.ellipse((314, 76, 400, 162), fill="#f7dfa0")
    draw.ellipse((337, 60, 417, 145), fill=(25, 35, 66))
    draw.polygon(((0, 430), (78, 338), (148, 414), (231, 306), (321, 428)), fill="#293f57")
    draw.polygon(((158, 430), (280, 350), (360, 421), (430, 330), (480, 388), (480, 500), (0, 500), (0, 452)), fill="#1b3449")

    for y, span, color in ((526, 130, "#80c8ca"), (556, 86, "#d1e5d8"), (590, 145, "#5ea6b5"), (628, 110, "#376f89")):
        draw.arc((CANVAS_SIZE[0] // 2 - span, y - 14, CANVAS_SIZE[0] // 2 + span, y + 14), 5, 175, fill=color, width=3)

    draw.rectangle((345, 330, 374, 494), fill="#e8e1d2", outline="#202d3f", width=4)
    draw.polygon(((336, 330), (383, 330), (374, 304), (346, 304)), fill="#d95d5d", outline="#202d3f")
    draw.rectangle((349, 344, 370, 361), fill="#f4c95d", outline="#202d3f", width=3)
    draw.polygon(((339, 302), (380, 302), (359, 284)), fill="#263b50")
    draw.line((359, 284, 359, 258), fill="#263b50", width=4)
    draw.polygon(((359, 258), (422, 274), (359, 287)), fill=(244, 201, 93, 110))

    draw.polygon(((0, 616), (70, 576), (146, 594), (210, 720), (0, 720)), fill="#102638")
    draw.ellipse((104, 512, 154, 562), fill="#172333", outline="#0b1722", width=3)
    draw.polygon(((105, 532), (83, 568), (122, 558), (158, 532), (146, 507)), fill="#202c3d")
    draw.polygon(((89, 694), (109, 566), (145, 557), (181, 694)), fill="#22364c")
    draw.polygon(((142, 570), (224, 596), (149, 610)), fill="#ef798a")
    draw.line((154, 610, 194, 694), fill="#101b28", width=12)
    draw.line((114, 612, 84, 694), fill="#101b28", width=12)

    draw.line((0, 680, CANVAS_SIZE[0], 680), fill="#d8e3e8", width=4)
    for x in range(20, CANVAS_SIZE[0], 54):
        draw.line((x, 640, x, 720), fill="#a9bbc6", width=4)

    draw.rounded_rectangle((92, 28, 388, 100), radius=8, fill=(12, 19, 37), outline="#d8e3e8", width=2)
    draw.text((114, 40), "ORIGINAL FULL FRAME", fill="#f4f1ea", font=_font(25, bold=True))
    draw.text((153, 72), "SEA LIGHT - 01", fill="#a9bbc6", font=_font(15))
    _draw_corner_markers(draw)

    output.parent.mkdir(parents=True, exist_ok=True)
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", "Original full-frame demo fixture")
    metadata.add_text("Author", "Anime Wallpaper Upscaler contributors")
    metadata.add_text("License", "MIT")
    image.save(output, format="PNG", optimize=True, pnginfo=metadata)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the original redistributable demo fixture.")
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    build_original_demo(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
