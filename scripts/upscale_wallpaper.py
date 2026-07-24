#!/usr/bin/env python
import argparse
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


DEFAULT_TOOL = Path(
    os.environ.get(
        "REALESRGAN_TOOL_DIR",
        str(Path.home() / ".cache" / "realesrgan" / "realesrgan-ncnn-vulkan-v0.2.0-windows"),
    )
)


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing {label}: {path}")


def cover_resize(img: Image.Image, target: tuple[int, int], x_bias: float, y_bias: float) -> Image.Image:
    tw, th = target
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = round((nw - tw) * x_bias)
    top = round((nh - th) * y_bias)
    return resized.crop((left, top, left + tw, top + th))


def preserve_composition_wallpaper(img: Image.Image, target: tuple[int, int]) -> Image.Image:
    tw, th = target
    sw, sh = img.size

    bg = cover_resize(img, target, 0.5, 0.5)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=max(tw, th) * 0.012))
    bg = ImageEnhance.Brightness(bg).enhance(0.82)
    bg = ImageEnhance.Contrast(bg).enhance(0.92)

    scale = min(tw / sw, th / sh)
    fw, fh = round(sw * scale), round(sh * scale)
    fg = img.resize((fw, fh), Image.Resampling.LANCZOS)
    left = (tw - fw) // 2
    top = (th - fh) // 2
    bg.paste(fg, (left, top))
    return bg


def polish(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Color(img).enhance(1.02)
    img = ImageEnhance.Contrast(img).enhance(1.02)
    return img.filter(ImageFilter.UnsharpMask(radius=0.7, percent=35, threshold=3))


def make_compare(
    original_path: Path,
    upscaled_path: Path,
    out_path: Path,
    full_input: bool = False,
) -> None:
    orig = Image.open(original_path).convert("RGB")
    up = Image.open(upscaled_path).convert("RGB")
    ow, oh = orig.size
    box = (0, 0, ow, oh) if full_input else (
        round(ow * 0.36),
        round(oh * 0.13),
        round(ow * 0.54),
        round(oh * 0.46),
    )
    crop = orig.crop(box)
    scale = min(520 / crop.width, 720 / crop.height)
    panel_size = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
    normal = crop.resize(panel_size, Image.Resampling.LANCZOS)
    sx = up.width / ow
    sy = up.height / oh
    up_box = (
        round(box[0] * sx),
        round(box[1] * sy),
        round(box[2] * sx),
        round(box[3] * sy),
    )
    ai_crop = up.crop(up_box).resize(panel_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (panel_size[0] * 2 + 20, panel_size[1] + 50), "white")
    canvas.paste(normal, (0, 50))
    canvas.paste(ai_crop, (panel_size[0] + 20, 50))
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 15), "Normal upscale", fill=(0, 0, 0))
    draw.text((panel_size[0] + 30, 15), "Real-ESRGAN AI upscale", fill=(0, 0, 0))
    divider_x = panel_size[0] + 10
    draw.line((divider_x, 0, divider_x, canvas.height), fill=(180, 180, 180), width=2)
    canvas.save(out_path, quality=95)


def main() -> None:
    parser = argparse.ArgumentParser(description="Upscale anime-style images into wallpapers.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", default=Path("outputs") / "wallpapers", type=Path)
    parser.add_argument("--tool-dir", default=DEFAULT_TOOL, type=Path)
    parser.add_argument("--model", default="realesrgan-x4plus-anime")
    parser.add_argument("--target", default="2560x1600")
    parser.add_argument("--mode", choices=["preserve", "cover"], default="preserve")
    parser.add_argument("--copy-desktop", action="store_true")
    parser.add_argument(
        "--compare-full-input",
        action="store_true",
        help="Use the whole input image for the comparison without a second crop.",
    )
    parser.add_argument("--x-bias", default=0.5, type=float)
    parser.add_argument("--y-bias", default=0.5, type=float)
    args = parser.parse_args()

    source = args.input
    require_file(source, "input image")

    exe = args.tool_dir / "realesrgan-ncnn-vulkan.exe"
    model_param = args.tool_dir / "models" / f"{args.model}.param"
    model_bin = args.tool_dir / "models" / f"{args.model}.bin"
    require_file(exe, "Real-ESRGAN executable")
    require_file(model_param, "Real-ESRGAN model param")
    require_file(model_bin, "Real-ESRGAN model bin")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    upscaled = args.out_dir / f"{stem}_realesrgan_4x.png"

    cmd = [
        str(exe),
        "-i",
        str(source),
        "-o",
        str(upscaled),
        "-n",
        args.model,
        "-s",
        "4",
        "-f",
        "png",
    ]
    subprocess.run(cmd, cwd=args.tool_dir, check=True)

    tw, th = (int(part) for part in args.target.lower().split("x", 1))
    ai = Image.open(upscaled).convert("RGB")
    if args.mode == "cover":
        wallpaper = cover_resize(ai, (tw, th), args.x_bias, args.y_bias)
        suffix = f"wallpaper_AI_{tw}x{th}_cover"
    else:
        wallpaper = preserve_composition_wallpaper(ai, (tw, th))
        suffix = f"wallpaper_AI_{tw}x{th}_preserve"
    wallpaper = polish(wallpaper)
    wallpaper_path = args.out_dir / f"{stem}_{suffix}.jpg"
    wallpaper.save(wallpaper_path, quality=97, optimize=True, subsampling=0)

    if (tw, th) != (2560, 1440):
        full_16_9 = polish(ai.resize((2560, 1440), Image.Resampling.LANCZOS))
        full_16_9.save(args.out_dir / f"{stem}_wallpaper_AI_2560x1440_full.jpg", quality=97, optimize=True, subsampling=0)

    compare_path = args.out_dir / f"{stem}_AI_compare.jpg"
    make_compare(source, upscaled, compare_path, full_input=args.compare_full_input)

    desktop_path = None
    if args.copy_desktop:
        desktop = Path.home() / "Desktop"
        desktop_path = desktop / wallpaper_path.name
        shutil.copy2(wallpaper_path, desktop_path)

    print(f"upscaled={upscaled}")
    print(f"wallpaper={wallpaper_path}")
    print(f"compare={compare_path}")
    if desktop_path:
        print(f"desktop={desktop_path}")


if __name__ == "__main__":
    main()
