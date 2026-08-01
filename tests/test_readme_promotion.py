from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]


def _read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_english_readme_leads_with_screenshot_outcome() -> None:
    text = _read("README.md")
    assert "Pause a frame. Keep it on your desktop." in text[:2500]
    assert "Turn anime screenshots into screen-ready Windows wallpapers" in text[:2500]
    assert text.index("## From Screenshot to Wallpaper") < text.index("## Agent Skill (Advanced)")
    assert text.index("## How This Differs from Official Real-ESRGAN") < text.index(
        "## Agent Skill (Advanced)"
    )


def test_chinese_readme_leads_with_equivalent_outcome() -> None:
    text = _read("README.zh-CN.md")
    assert "暂停喜欢的一帧，把它留在桌面。" in text[:2500]
    assert "番剧截图一键超分" in text[:2500]
    assert text.index("## 从番剧截图到桌面壁纸") < text.index("## Agent Skill（进阶）")
    assert text.index("## 本项目与官方 Real-ESRGAN 的区别") < text.index(
        "## Agent Skill（进阶）"
    )


def test_all_relative_readme_images_exist() -> None:
    for name in ("README.md", "README.zh-CN.md"):
        for target in re.findall(r"!\[[^]]*\]\(([^)]+)\)", _read(name)):
            if "://" not in target:
                assert (ROOT / target).is_file(), f"missing {name} image: {target}"


def test_readmes_keep_attribution_and_rights_boundaries() -> None:
    for name in ("README.md", "README.zh-CN.md"):
        text = _read(name)
        assert "Real-ESRGAN" in text
        assert "docs/assets/promotion/NOTICE.md" in text
        assert "guaranteed 4K" not in text
        assert "original super-resolution model" not in text


def test_readmes_use_selected_examples_and_reproducible_preview_command() -> None:
    for name in ("README.md", "README.zh-CN.md"):
        text = _read(name)
        assert "docs/assets/promotion/k-on-detail-comparison-4x.png" in text
        assert "docs/assets/promotion/k-on-desktop-comparison.png" in text
        assert "scripts\\build_promotion_assets.py" in text
        assert "--desktop-comparison" in text
        assert '--social-preview ".\\docs\\assets\\social-preview.jpg"' not in text
