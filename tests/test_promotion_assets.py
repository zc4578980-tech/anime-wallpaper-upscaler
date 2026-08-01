from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest
from PIL import Image, ImageStat

ROOT = Path(__file__).parents[1]
PROMOTION = ROOT / "docs" / "assets" / "promotion"

CASES = [
    ("k-on-source-721x406.jpg", (721, 406), "0cac28576ba219aeaec8bed9378f71dc3e0a7d31b1f4923acc0b72a0230052a3"),
    ("k-on-detail-comparison-4x.png", (1060, 590), "b316c65718f8ac2e6d14da6077406ee71766a75850b7a01e0469e845adbebe94"),
    ("k-on-wallpaper-2560x1600.jpg", (2560, 1600), "22cf61076f816038d3fa855ee18af7d616261c9b31c24bd2054ef14d731321c6"),
    ("k-on-desktop-comparison.png", (1280, 1710), "f6f5e4090d118704ff2054b38c645a8e5f5804648ea22cfdf9bfbf168523713e"),
]


@pytest.mark.parametrize(("name", "size", "digest"), CASES)
def test_checked_in_promotion_asset_matches_verified_source(
    name: str, size: tuple[int, int], digest: str
) -> None:
    path = PROMOTION / name
    assert path.is_file()
    assert sha256(path.read_bytes()).hexdigest() == digest
    with Image.open(path) as image:
        rendered = image.convert("RGB")
        assert rendered.size == size
        assert rendered.getbbox() is not None
        assert sum(ImageStat.Stat(rendered).var) > 100
