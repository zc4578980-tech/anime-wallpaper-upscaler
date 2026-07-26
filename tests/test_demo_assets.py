from pathlib import Path

from PIL import Image, ImageColor, ImageStat


def _save_fixture(path: Path, size: tuple[int, int], color: str) -> None:
    Image.new("RGB", size, color).save(path)


def _assert_rendered_image(path: Path, expected_size: tuple[int, int]) -> None:
    with Image.open(path) as image:
        rendered = image.convert("RGB")
        assert rendered.size == expected_size
        assert rendered.getbbox() is not None
        assert sum(ImageStat.Stat(rendered).var) > 0


def test_build_demo_assets_have_exact_dimensions_and_visible_content(
    tmp_path: Path,
) -> None:
    from scripts.build_demo_assets import build_social_preview, build_triptych

    source = tmp_path / "source.png"
    upscaled = tmp_path / "upscaled.png"
    wallpaper = tmp_path / "wallpaper.png"
    overview = tmp_path / "overview.png"
    social_preview = tmp_path / "social-preview.png"
    _save_fixture(source, (300, 500), "#e84a5f")
    _save_fixture(upscaled, (600, 1000), "#38a3a5")
    _save_fixture(wallpaper, (800, 450), "#f9c74f")

    build_triptych(source, upscaled, wallpaper, overview)
    build_social_preview(overview, social_preview)

    _assert_rendered_image(overview, (1440, 810))
    _assert_rendered_image(social_preview, (1280, 640))


def test_original_demo_fixture_is_deterministic_and_marks_all_four_corners(
    tmp_path: Path,
) -> None:
    from scripts.build_original_demo import CANVAS_SIZE, CORNER_COLORS, build_original_demo

    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    build_original_demo(first)
    build_original_demo(second)

    assert first.read_bytes() == second.read_bytes()
    checked_in = Path(__file__).parents[1] / "docs" / "assets" / "demo-source-original.png"
    with Image.open(first) as image:
        assert image.info["License"] == "MIT"
        rendered = image.convert("RGB")
        assert rendered.size == CANVAS_SIZE
        assert sum(ImageStat.Stat(rendered).var) > 1_000
        assert rendered.getpixel((20, 14)) == ImageColor.getrgb(CORNER_COLORS["top_left"])
        assert rendered.getpixel((460, 14)) == ImageColor.getrgb(CORNER_COLORS["top_right"])
        assert rendered.getpixel((20, 705)) == ImageColor.getrgb(CORNER_COLORS["bottom_left"])
        assert rendered.getpixel((460, 705)) == ImageColor.getrgb(CORNER_COLORS["bottom_right"])
    with Image.open(checked_in) as image:
        assert image.info["License"] == "MIT"
        rendered = image.convert("RGB")
        assert rendered.size == CANVAS_SIZE
        assert sum(ImageStat.Stat(rendered).var) > 1_000
        assert rendered.getpixel((20, 14)) == ImageColor.getrgb(CORNER_COLORS["top_left"])
        assert rendered.getpixel((460, 14)) == ImageColor.getrgb(CORNER_COLORS["top_right"])
        assert rendered.getpixel((20, 705)) == ImageColor.getrgb(CORNER_COLORS["bottom_left"])
        assert rendered.getpixel((460, 705)) == ImageColor.getrgb(CORNER_COLORS["bottom_right"])
