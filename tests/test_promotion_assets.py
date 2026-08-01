from __future__ import annotations

import json
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


def test_promotion_evidence_and_notice_are_explicit() -> None:
    evidence_path = ROOT / "docs" / "release" / "evidence" / "k-on-promotion-run.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence == {
        "capturedAt": "2026-07-27T16:32:44+08:00",
        "source": {
            "title": "K-ON!",
            "episode": "not provided by the source contributor",
            "timestamp": "not provided by the source contributor",
            "size": [721, 406],
            "sha256": CASES[0][2],
        },
        "inference": {
            "engine": "official realesrgan-ncnn-vulkan",
            "model": "realesrgan-x4plus-anime",
            "scale": 4,
            "target": [2560, 1600],
            "mode": "preserve",
            "gpu": "NVIDIA GeForce RTX 5070 Ti Laptop GPU",
        },
        "outputs": {
            "rawUpscale": {
                "size": [2884, 1624],
                "sha256": "8d1d214233adccb36371ccfce83a0299b308ed9e84ab46f6dbb48b79e8561dfa",
            },
            "wallpaper": {
                "path": "docs/assets/promotion/k-on-wallpaper-2560x1600.jpg",
                "size": [2560, 1600],
                "sha256": CASES[2][2],
            },
            "detailComparison": {
                "path": "docs/assets/promotion/k-on-detail-comparison-4x.png",
                "size": [1060, 590],
                "sha256": CASES[1][2],
            },
            "desktopComparison": {
                "path": "docs/assets/promotion/k-on-desktop-comparison.png",
                "size": [1280, 1710],
                "sha256": CASES[3][2],
                "layout": "vertical",
                "lowerBorder": "none",
            },
        },
        "verification": {
            "sourceCopyMatches": True,
            "rawUpscaleIsExact4x": True,
            "fullFramePreserved": True,
            "allImagesNonblank": True,
            "succeeded": 1,
            "failed": 0,
            "visualInspection": "passed",
        },
    }

    notice = (PROMOTION / "NOTICE.md").read_text(encoding="utf-8")
    normalized_notice = " ".join(notice.split())
    for required in (
        "K-ON!",
        "not licensed for redistribution",
        "not affiliated",
        "GitHub Issue",
        *[case[0] for case in CASES],
    ):
        assert required in notice
    for required in (
        "does not create permission",
        "establish fair use",
        "prevent a DMCA request",
        "eliminate liability",
        "and every derived social or documentation image",
        "deterministic project-owned demo",
    ):
        assert required in normalized_notice

    parent_notice = (ROOT / "docs" / "assets" / "NOTICE.md").read_text(encoding="utf-8")
    normalized_parent_notice = " ".join(parent_notice.split())
    assert "The four assets listed in the table above are covered" in normalized_parent_notice
    assert (
        "Files under `docs/assets/promotion/` are not project-owned MIT assets"
        in normalized_parent_notice
    )
    assert "The repository MIT License does not relicense those images" in normalized_parent_notice
    assert "These repository-owned assets are covered" not in normalized_parent_notice
