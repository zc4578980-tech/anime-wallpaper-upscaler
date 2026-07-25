import subprocess
import sys
from pathlib import Path

from PIL import Image

from anime_wallpaper_upscaler.imaging import (
    cover_resize,
    make_compare,
    preserve_composition_wallpaper,
)


def test_preserve_mode_keeps_target_size_and_source_center_color() -> None:
    source = Image.new("RGB", (160, 90), (220, 20, 40))
    result = preserve_composition_wallpaper(source, (160, 100))
    assert result.size == (160, 100)
    assert result.getpixel((80, 50))[0] >= 200


def test_cover_mode_fills_exact_target() -> None:
    source = Image.new("RGB", (100, 200), "blue")
    assert cover_resize(source, (160, 100), 0.5, 0.5).size == (160, 100)


def test_compare_preserves_selected_crop_aspect(tmp_path: Path) -> None:
    original = tmp_path / "original.png"
    upscaled = tmp_path / "upscaled.png"
    output = tmp_path / "compare.jpg"
    Image.new("RGB", (200, 100), "red").save(original)
    Image.new("RGB", (800, 400), "red").save(upscaled)
    make_compare(original, upscaled, output)
    with Image.open(output) as result:
        assert result.width > result.height
        assert result.getbbox() is not None


def test_legacy_script_entry_point_can_load_package(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            str(project_root / "scripts" / "upscale_wallpaper.py"),
            "--help",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Upscale anime-style images into wallpapers." in result.stdout
