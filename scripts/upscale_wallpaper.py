#!/usr/bin/env python
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anime_wallpaper_upscaler.imaging import (
    cover_resize,
    make_compare,
    polish,
    preserve_composition_wallpaper,
)


DEFAULT_TOOL = Path(
    os.environ.get(
        "REALESRGAN_TOOL_DIR",
        str(Path.home() / ".cache" / "realesrgan" / "realesrgan-ncnn-vulkan-v0.2.0-windows"),
    )
)


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing {label}: {path}")


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
