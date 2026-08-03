# Anime Screenshot Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the v0.2.2 installer hotfix, then reposition the repository around turning an anime screenshot into a screen-ready Windows wallpaper using the verified K-ON! example.

**Architecture:** Keep installer repair and promotion as separate review gates. The hotfix ships through protected `main` first; the promotion branch then adds immutable evidence assets, structured provenance, bilingual ordinary-user-first README copy, and a reproducible social preview without changing inference behavior.

**Tech Stack:** PowerShell 5.1, Python 3.10+, Pillow, pytest, Markdown, JSON, GitHub Actions, GitHub CLI.

## Global Constraints

- Primary audience: ordinary Windows anime viewers; Agent users are secondary.
- Chinese headline: `暂停喜欢的一帧，把它留在桌面。`
- English headline: `Pause a frame. Keep it on your desktop.`
- "One click" applies only after setup; first setup still displays upstream terms and requires consent.
- Never claim an original super-resolution model, perfect detail reconstruction, or guaranteed native 4K.
- Attribute Real-ESRGAN, Real-ESRGAN-ncnn-vulkan, ncnn, and Vulkan.
- The selected K-ON! screenshot is not rights-safe; never describe it as licensed or fair use.
- The notice must disclose source uncertainty, non-affiliation, GitHub Issue contact, and an exact removal map.
- Keep the deterministic MIT demo as the immediate replacement if the K-ON! assets must be removed.
- Push, PR readiness, merge, tag, Release, social-preview upload, and external posts are separate approval gates.
- Do not add a GUI, telemetry, uploads, a new model, or runtime dependencies.
- The 30-net-new-Star target is measured at T+30 and is not guaranteed.

---

## File Map

**Release repair**

- Modify `setup.ps1`: setup User-Agent `0.2.1` -> `0.2.2`.
- Modify `tests/powershell/setup.tests.ps1`: package-version assertion.
- Create `docs/release/v0.2.2.md`: factual hotfix notes.
- Modify `PROJECT_NODES.md` only after observed state changes.

**Promotion**

- Create four files under `docs/assets/promotion/`: source, detail comparison, wallpaper, desktop comparison.
- Create `docs/assets/promotion/NOTICE.md` and `docs/release/evidence/k-on-promotion-run.json`.
- Modify `docs/assets/NOTICE.md` to separate MIT assets from the unlicensed example.
- Create `scripts/build_promotion_assets.py` and `tests/test_promotion_assets.py`.
- Create `tests/test_readme_promotion.py`.
- Modify `README.md`, `README.zh-CN.md`, and `docs/assets/social-preview.jpg`.
- Create `docs/release/anime-screenshot-promotion.md` as prepared but unpublished copy.

---

### Task 1: Prepare And Publish v0.2.2

**Files:**
- Modify: `tests/powershell/setup.tests.ps1`
- Modify: `setup.ps1`
- Create: `docs/release/v0.2.2.md`
- Modify after state changes: `PROJECT_NODES.md`

**Interfaces:**
- Consumes: commit `4c36656` on `codex/v0.2.2-skill-conflict`.
- Produces: a protected-main Windows ZIP whose setup preserves a non-matching existing Skill path and exits `0`.

- [ ] **Step 1: Switch to the hotfix branch**

```powershell
git switch codex/v0.2.2-skill-conflict
git status --short --branch
```

Expected: clean `codex/v0.2.2-skill-conflict` at `4c36656`.

- [ ] **Step 2: Add a failing package-version assertion**

Append beside the existing installer-source assertions:

```powershell
$setupSource = Get-Content -LiteralPath (Join-Path $projectRoot "setup.ps1") -Raw
Assert-True ($setupSource -match 'anime-wallpaper-upscaler-setup/0\.2\.2') "setup network requests identify the v0.2.2 package"
```

- [ ] **Step 3: Verify RED**

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\powershell\setup.tests.ps1
```

Expected: FAIL only at the new v0.2.2 assertion because the source still identifies `0.2.1`.

- [ ] **Step 4: Apply the minimum production change**

In `setup.ps1`:

```powershell
$request.UserAgent = "anime-wallpaper-upscaler-setup/0.2.2"
```

- [ ] **Step 5: Create `docs/release/v0.2.2.md`**

```markdown
# Anime Wallpaper Upscaler v0.2.2

v0.2.2 is a focused Windows setup hotfix. Inference, model selection, output formats, and the
pinned official Real-ESRGAN runtime remain unchanged.

## Fixed

- Keep an existing Codex Skill directory or junction unchanged when it points somewhere else.
- Treat that optional registration conflict as a warning instead of failing core setup.
- Continue shortcut creation and the CLI smoke test after Skill registration is skipped.
- Continue refusing `-ReplaceSkillLink` for an existing non-junction path.

## Install

1. Download and extract `anime-wallpaper-upscaler-v0.2.2-windows.zip`.
2. Double-click `install.cmd`.
3. Review the upstream terms and approve the verified runtime download.

## Verification

- 75 Python tests passed.
- 33 setup assertions passed, including a real temporary Junction conflict.
- 9 launcher assertions passed.
- Compilation, CLI help, and whitespace checks passed.
- A real temporary Junction regression passed; published-ZIP re-download verification remains a
  separate Release gate.

Downloaded upstream software and models remain subject to their upstream terms. See
[Third-Party Notices](../../THIRD_PARTY_NOTICES.md).
```

- [ ] **Step 6: Verify GREEN and full release checks**

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\powershell\setup.tests.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\powershell\launcher.tests.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q anime_wallpaper_upscaler scripts tests
.\.venv\Scripts\python.exe .\scripts\upscale_wallpaper.py --help
git diff --check
```

Expected: every command exits `0`.

- [ ] **Step 7: Commit**

```powershell
git add setup.ps1 tests/powershell/setup.tests.ps1 docs/release/v0.2.2.md
git commit -m "docs: prepare v0.2.2 installer hotfix"
```

- [ ] **Step 8: Stop for push and Draft PR authorization**

After approval only:

```powershell
git push -u origin codex/v0.2.2-skill-conflict
gh pr create --draft --base main --head codex/v0.2.2-skill-conflict --title "Fix optional Codex Skill conflicts during setup" --body-file docs/release/v0.2.2.md
```

- [ ] **Step 9: Stop separately for Ready/merge authorization**

After approval and green CI:

```powershell
$hotfixPr = gh pr view codex/v0.2.2-skill-conflict --json number --jq .number
gh pr ready $hotfixPr
gh pr checks $hotfixPr --watch
gh pr merge $hotfixPr --merge
git fetch origin
git switch main
git pull --ff-only
gh run list --branch main --limit 3
```

Expected: protected `main` contains the PR merge and the newest Windows run passes.

- [ ] **Step 10: Stop for tag and archive authorization**

After tag authorization, create `v0.2.2` and the Windows ZIP from clean protected `main`:

```powershell
$releaseOutput = 'D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.2-windows.zip'
git status --short --branch
git tag -a v0.2.2 -m "Anime Wallpaper Upscaler v0.2.2"
git archive --format=zip --prefix=anime-wallpaper-upscaler-v0.2.2/ --output=$releaseOutput v0.2.2
Get-FileHash -LiteralPath $releaseOutput -Algorithm SHA256
git push origin v0.2.2
```

Expected: the annotated tag points to protected `main`; the archive contains repository files only and has a recorded SHA-256. Do not create a GitHub Release in this step.

- [ ] **Step 11: Stop separately for GitHub Release authorization**

After Release authorization, upload the already reviewed archive, re-download it, and verify the real setup path:

```powershell
$releaseOutput = 'D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.2-windows.zip'
$releaseVerify = 'D:\CodexWorkspace\scratch\anime-wallpaper-upscaler-v0.2.2-release-verify'
gh release create v0.2.2 $releaseOutput --title "v0.2.2 - Existing Skill conflict hotfix" --notes-file docs/release/v0.2.2.md
New-Item -ItemType Directory -Path $releaseVerify -Force | Out-Null
gh release download v0.2.2 --pattern 'anime-wallpaper-upscaler-v0.2.2-windows.zip' --dir $releaseVerify
Get-FileHash -LiteralPath (Join-Path $releaseVerify 'anime-wallpaper-upscaler-v0.2.2-windows.zip') -Algorithm SHA256
Expand-Archive -LiteralPath (Join-Path $releaseVerify 'anime-wallpaper-upscaler-v0.2.2-windows.zip') -DestinationPath $releaseVerify
Set-Location -LiteralPath (Join-Path $releaseVerify 'anime-wallpaper-upscaler-v0.2.2')
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -AcceptUpstreamLicense
```

Expected: local and re-downloaded ZIP hashes match; the existing Skill path is preserved, a warning is printed, shortcut/smoke-test steps continue, and setup exits `0`. Record the exact SHA-256 in `PROJECT_NODES.md` after verification.

- [ ] **Step 12: Rebase promotion work after release**

```powershell
git switch codex/anime-screenshot-promotion
git rebase main
git status --short --branch
```

---

### Task 2: Import The Verified K-ON! Evidence Set

**Files:**
- Create: `docs/assets/promotion/k-on-source-721x406.jpg`
- Create: `docs/assets/promotion/k-on-detail-comparison-4x.png`
- Create: `docs/assets/promotion/k-on-wallpaper-2560x1600.jpg`
- Create: `docs/assets/promotion/k-on-desktop-comparison.png`
- Create: `tests/test_promotion_assets.py`

**Interfaces:**
- Consumes: verified local assets in `C:\Users\Capricorn\Desktop\umawallpaper\test`.
- Produces: stable repository assets locked by dimensions, hashes, and nonblank checks.

- [ ] **Step 1: Write the failing asset-integrity test**

Create `tests/test_promotion_assets.py`:

```python
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
```

- [ ] **Step 2: Verify RED**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_promotion_assets.py -q
```

Expected: four failures because the asset files are absent.

- [ ] **Step 3: Copy exactly the verified files**

```powershell
New-Item -ItemType Directory -Path .\docs\assets\promotion -Force | Out-Null
Copy-Item -LiteralPath 'C:\Users\Capricorn\Desktop\umawallpaper\test\result\k-on-original-721x406.jpg' -Destination '.\docs\assets\promotion\k-on-source-721x406.jpg'
Copy-Item -LiteralPath 'C:\Users\Capricorn\Desktop\umawallpaper\test\select\k-on-detail-comparison-4x.png' -Destination '.\docs\assets\promotion\k-on-detail-comparison-4x.png'
Copy-Item -LiteralPath 'C:\Users\Capricorn\Desktop\umawallpaper\test\result\k-on-wallpaper-ai-2560x1600.jpg' -Destination '.\docs\assets\promotion\k-on-wallpaper-2560x1600.jpg'
Copy-Item -LiteralPath 'C:\Users\Capricorn\Desktop\umawallpaper\test\select\k-on-desktop-real-world-comparison.png' -Destination '.\docs\assets\promotion\k-on-desktop-comparison.png'
```

- [ ] **Step 4: Verify GREEN and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_promotion_assets.py -q
git add docs/assets/promotion tests/test_promotion_assets.py
git commit -m "docs: add verified anime screenshot evidence"
```

Expected: `4 passed`.

---

### Task 3: Add Structured Evidence And Rights Notices

**Files:**
- Create: `docs/release/evidence/k-on-promotion-run.json`
- Create: `docs/assets/promotion/NOTICE.md`
- Modify: `docs/assets/NOTICE.md`
- Modify: `tests/test_promotion_assets.py`

**Interfaces:**
- Consumes: Task 2 asset hashes.
- Produces: machine-readable run evidence and a public removal map.

- [ ] **Step 1: Add failing evidence/notice tests**

Append:

```python
import json


def test_promotion_evidence_and_notice_are_explicit() -> None:
    evidence_path = ROOT / "docs" / "release" / "evidence" / "k-on-promotion-run.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["source"]["sha256"] == CASES[0][2]
    assert evidence["inference"] == {
        "engine": "official realesrgan-ncnn-vulkan",
        "model": "realesrgan-x4plus-anime",
        "scale": 4,
        "target": [2560, 1600],
        "mode": "preserve",
        "gpu": "NVIDIA GeForce RTX 5070 Ti Laptop GPU",
    }
    assert evidence["verification"]["succeeded"] == 1
    assert evidence["verification"]["failed"] == 0

    notice = (PROMOTION / "NOTICE.md").read_text(encoding="utf-8")
    for required in (
        "K-ON!",
        "not licensed for redistribution",
        "not affiliated",
        "GitHub Issue",
        *[case[0] for case in CASES],
    ):
        assert required in notice
```

- [ ] **Step 2: Verify RED**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_promotion_assets.py -q
```

Expected: failure because evidence and notice are absent.

- [ ] **Step 3: Create the evidence JSON**

Create `docs/release/evidence/k-on-promotion-run.json` with these exact facts:

```json
{
  "capturedAt": "2026-07-27T16:32:44+08:00",
  "source": {
    "title": "K-ON!",
    "episode": "not provided by the source contributor",
    "timestamp": "not provided by the source contributor",
    "size": [721, 406],
    "sha256": "0cac28576ba219aeaec8bed9378f71dc3e0a7d31b1f4923acc0b72a0230052a3"
  },
  "inference": {
    "engine": "official realesrgan-ncnn-vulkan",
    "model": "realesrgan-x4plus-anime",
    "scale": 4,
    "target": [2560, 1600],
    "mode": "preserve",
    "gpu": "NVIDIA GeForce RTX 5070 Ti Laptop GPU"
  },
  "outputs": {
    "rawUpscale": {"size": [2884, 1624], "sha256": "8d1d214233adccb36371ccfce83a0299b308ed9e84ab46f6dbb48b79e8561dfa"},
    "wallpaper": {"path": "docs/assets/promotion/k-on-wallpaper-2560x1600.jpg", "size": [2560, 1600], "sha256": "22cf61076f816038d3fa855ee18af7d616261c9b31c24bd2054ef14d731321c6"},
    "detailComparison": {"path": "docs/assets/promotion/k-on-detail-comparison-4x.png", "size": [1060, 590], "sha256": "b316c65718f8ac2e6d14da6077406ee71766a75850b7a01e0469e845adbebe94"},
    "desktopComparison": {"path": "docs/assets/promotion/k-on-desktop-comparison.png", "size": [1280, 1710], "sha256": "f6f5e4090d118704ff2054b38c645a8e5f5804648ea22cfdf9bfbf168523713e", "layout": "vertical", "lowerBorder": "none"}
  },
  "verification": {
    "sourceCopyMatches": true,
    "rawUpscaleIsExact4x": true,
    "fullFramePreserved": true,
    "allImagesNonblank": true,
    "succeeded": 1,
    "failed": 0,
    "visualInspection": "passed"
  }
}
```

- [ ] **Step 4: Create `docs/assets/promotion/NOTICE.md`**

```markdown
# K-ON! Promotion Asset Notice

The files in this directory demonstrate the workflow on a user-supplied screenshot identified as
a frame from **K-ON!**. The episode and timestamp were not provided, and this project has not
independently established the exact rightsholder or a redistribution license.

These images are **not licensed for redistribution under this repository's MIT License**. Anime
Wallpaper Upscaler is not affiliated with, sponsored by, or endorsed by the creators, publisher,
animation studio, broadcaster, production committee, or other rightsholders.

This notice does not create permission, establish fair use, prevent a DMCA request, or eliminate
liability. For a removal request, open a GitHub Issue:
https://github.com/zc4578980-tech/anime-wallpaper-upscaler/issues

Remove `k-on-source-721x406.jpg`, `k-on-detail-comparison-4x.png`,
`k-on-wallpaper-2560x1600.jpg`, `k-on-desktop-comparison.png`, and every derived social or
documentation image. Replace them with the deterministic project-owned demo documented in
`../NOTICE.md`.
```

- [ ] **Step 5: Correct the repository-wide asset notice**

In `docs/assets/NOTICE.md`, change:

```text
These repository-owned assets are covered by the repository MIT License.
```

to:

```text
The four assets listed in the table above are covered by the repository MIT License.
```

Append:

```markdown
## Unlicensed Promotional Example

Files under `docs/assets/promotion/` are not project-owned MIT assets. Their separate notice
records source uncertainty, non-affiliation, the contact route, and the removal map. The repository
MIT License does not relicense those images.
```

- [ ] **Step 6: Verify GREEN and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_promotion_assets.py -q
git diff --check
git add docs/assets/NOTICE.md docs/assets/promotion/NOTICE.md docs/release/evidence/k-on-promotion-run.json tests/test_promotion_assets.py
git commit -m "docs: record promotion evidence and rights boundary"
```

---

### Task 4: Build A Reproducible Social Preview

**Files:**
- Create: `scripts/build_promotion_assets.py`
- Modify: `tests/test_promotion_assets.py`
- Generate: `docs/assets/social-preview.jpg`

**Interfaces:**
- Produces: `build_social_preview(detail: Path, wallpaper: Path, output: Path) -> None` and a 1280x640 JPEG.

- [ ] **Step 1: Write the failing builder test**

Append:

```python
def test_promotion_social_preview_has_exact_dimensions(tmp_path: Path) -> None:
    from scripts.build_promotion_assets import build_social_preview

    detail = tmp_path / "detail.png"
    wallpaper = tmp_path / "wallpaper.png"
    output = tmp_path / "social.jpg"
    Image.new("RGB", (1060, 590), "#e84855").save(detail)
    Image.new("RGB", (2560, 1600), "#2a9d8f").save(wallpaper)

    build_social_preview(detail, wallpaper, output)

    with Image.open(output) as image:
        rendered = image.convert("RGB")
        assert rendered.size == (1280, 640)
        assert sum(ImageStat.Stat(rendered).var) > 100
```

- [ ] **Step 2: Verify RED**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_promotion_assets.py::test_promotion_social_preview_has_exact_dimensions -q
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `scripts/build_promotion_assets.py`**

```python
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
    canvas.paste(ImageOps.fit(_open(detail), (760, 430), Image.Resampling.LANCZOS), (42, 174))
    canvas.paste(ImageOps.fit(_open(wallpaper), (410, 430), Image.Resampling.LANCZOS), (828, 174))
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
```

- [ ] **Step 4: Verify GREEN and generate**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_promotion_assets.py -q
.\.venv\Scripts\python.exe .\scripts\build_promotion_assets.py --detail .\docs\assets\promotion\k-on-detail-comparison-4x.png --wallpaper .\docs\assets\promotion\k-on-wallpaper-2560x1600.jpg --output .\docs\assets\social-preview.jpg
```

Inspect at original resolution: exact 1280x640, readable text, both images visible, no clipping or blank panels.

- [ ] **Step 5: Commit**

```powershell
git add scripts/build_promotion_assets.py tests/test_promotion_assets.py docs/assets/social-preview.jpg
git commit -m "docs: build anime screenshot social preview"
```

---

### Task 5: Reorder Both README Files

**Files:**
- Create: `tests/test_readme_promotion.py`
- Modify: `README.md`
- Modify: `README.zh-CN.md`

**Interfaces:**
- Consumes: Tasks 2-4 assets/evidence.
- Produces: equivalent ordinary-user-first English and Chinese pages.

- [ ] **Step 1: Write failing copy/order/link tests**

```python
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
    assert text.index("## How This Differs from Official Real-ESRGAN") < text.index("## Agent Skill (Advanced)")


def test_chinese_readme_leads_with_equivalent_outcome() -> None:
    text = _read("README.zh-CN.md")
    assert "暂停喜欢的一帧，把它留在桌面。" in text[:2500]
    assert "番剧截图一键超分" in text[:2500]
    assert text.index("## 从番剧截图到桌面壁纸") < text.index("## Agent Skill（进阶）")
    assert text.index("## 本项目与官方 Real-ESRGAN 的区别") < text.index("## Agent Skill（进阶）")


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
```

- [ ] **Step 2: Verify RED**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_readme_promotion.py -q
```

Expected: first two tests fail because headline/order are absent.

- [ ] **Step 3: Replace the English first viewport**

Use this exact block before the existing upstream-difference section:

```markdown
# Anime Wallpaper Upscaler

## Pause a frame. Keep it on your desktop.

**Turn anime screenshots into screen-ready Windows wallpapers while preserving the complete
composition.** After setup, drag a screenshot onto the desktop shortcut, choose 2x/3x/4x, and the
local workflow detects your physical screen and Vulkan GPU automatically.

- Windows 10/11
- Local processing; screenshots are not uploaded
- Official Real-ESRGAN NCNN/Vulkan inference
- Full-composition wallpaper output by default

[简体中文](README.zh-CN.md)

## From Screenshot to Wallpaper

### See the 4x detail difference

![Original K-ON screenshot enlarged normally compared with the verified Real-ESRGAN 4x result](docs/assets/promotion/k-on-detail-comparison-4x.png)

### See the result on a real 2560x1600 Windows desktop

![Original screenshot wallpaper above and the Real-ESRGAN 4x composition-preserving wallpaper below](docs/assets/promotion/k-on-desktop-comparison.png)

The example uses one recorded local run: a 721x406 screenshot, official
`realesrgan-x4plus-anime` at 4x, `preserve` mode, and a 2560x1600 target on an NVIDIA GeForce RTX
5070 Ti Laptop GPU. [Run evidence](docs/release/evidence/k-on-promotion-run.json) ·
[Promotion asset notice](docs/assets/promotion/NOTICE.md)

## Three Steps

1. Download and extract the latest Windows ZIP from [Releases](https://github.com/zc4578980-tech/anime-wallpaper-upscaler/releases/latest).
2. Double-click `install.cmd`, review the upstream terms, and approve the verified runtime download.
3. Drag a screenshot or folder onto the desktop shortcut and choose 2x, 3x, or 4x.

No manual model installation is required. Real-ESRGAN and ncnn perform inference; this repository
provides the Windows wallpaper workflow, not an original model. Upscaling cannot guarantee recovery
of every detail absent from the source.
```

Move the complete existing `## Agent Skill` block to immediately after `## How This Differs from Official Real-ESRGAN` and rename it `## Agent Skill (Advanced)`. Retain every command and pipeline line unchanged.

- [ ] **Step 4: Replace the Chinese first viewport**

```markdown
# Anime Wallpaper Upscaler

## 暂停喜欢的一帧，把它留在桌面。

**番剧截图一键超分，自动生成适配当前屏幕、保留完整构图的高清 Windows 壁纸。** 完成首次
安装后，把截图拖到桌面快捷方式，选择 2x/3x/4x；工作流会在本机自动检测物理屏幕和 Vulkan GPU。

- 支持 Windows 10/11
- 全程本地处理，不上传截图
- 使用官方 Real-ESRGAN NCNN/Vulkan 推理
- 默认保留完整构图，不悄悄裁掉边缘内容

[English](README.md)

## 从番剧截图到桌面壁纸

### 查看 4x 局部细节差异

![普通放大的 K-ON 截图与经验证的 Real-ESRGAN 4x 结果对比](docs/assets/promotion/k-on-detail-comparison-4x.png)

### 查看 2560x1600 Windows 桌面实测

![上方为原截图直接设为壁纸，下方为 Real-ESRGAN 4x 保留构图壁纸](docs/assets/promotion/k-on-desktop-comparison.png)

示例来自同一次本地记录：721x406 截图、官方 `realesrgan-x4plus-anime`、4x、`preserve`
模式、2560x1600 目标，以及 NVIDIA GeForce RTX 5070 Ti Laptop GPU。
[运行证据](docs/release/evidence/k-on-promotion-run.json) ·
[宣传素材声明](docs/assets/promotion/NOTICE.md)

## 三步开始

1. 从 [Releases](https://github.com/zc4578980-tech/anime-wallpaper-upscaler/releases/latest) 下载并解压最新版 Windows ZIP。
2. 双击 `install.cmd`，阅读上游条款并确认下载经过校验的官方运行时。
3. 把截图或文件夹拖到生成的桌面快捷方式，选择 2x、3x 或 4x。

不需要手动安装模型。真正执行推理的是 Real-ESRGAN 和 ncnn；本仓库提供 Windows 壁纸工作
流，不宣称原创模型。超分不能保证恢复源截图中不存在的全部细节。
```

Move the equivalent Chinese Agent block after `## 本项目与官方 Real-ESRGAN 的区别` and rename it `## Agent Skill（进阶）`.

- [ ] **Step 5: Verify GREEN and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_readme_promotion.py -q
git add README.md README.zh-CN.md tests/test_readme_promotion.py
git commit -m "docs: lead with anime screenshot workflow"
```

---

### Task 6: Prepare Public Copy Without Publishing

**Files:**
- Create: `docs/release/anime-screenshot-promotion.md`
- Modify: `tests/test_readme_promotion.py`

- [ ] **Step 1: Add a failing prepared-copy test**

```python
def test_prepared_campaign_copy_is_specific_and_honest() -> None:
    text = _read("docs/release/anime-screenshot-promotion.md")
    assert "暂停喜欢的一帧，把它留在桌面。" in text
    assert "Pause a frame. Keep it on your desktop." in text
    assert "docs/assets/promotion/NOTICE.md" in text
    assert "30 Stars guaranteed" not in text
    assert "licensed K-ON" not in text
```

- [ ] **Step 2: Verify RED**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_readme_promotion.py::test_prepared_campaign_copy_is_specific_and_honest -q
```

- [ ] **Step 3: Create `docs/release/anime-screenshot-promotion.md`**

```markdown
# Anime Screenshot Promotion Copy

Prepared copy only. Release edits, social-preview upload, and external placement require separate
authorization.

## Chinese

**暂停喜欢的一帧，把它留在桌面。**

Anime Wallpaper Upscaler 可以把番剧截图在本机进行 2x/3x/4x 超分，并生成适配当前 Windows
屏幕、默认保留完整构图的壁纸。安装后拖入截图即可，不需要手动配置 Real-ESRGAN 模型。

- 本地处理，不上传截图
- 自动检测屏幕和 Vulkan GPU
- 提供局部细节对比和真实桌面效果
- 基于官方 Real-ESRGAN NCNN/Vulkan；本项目不宣称原创模型

Repository: https://github.com/zc4578980-tech/anime-wallpaper-upscaler

## English

**Pause a frame. Keep it on your desktop.**

Anime Wallpaper Upscaler turns anime screenshots into screen-ready Windows wallpapers using a
local 2x/3x/4x workflow. After setup, drag in a screenshot; the tool detects the screen and Vulkan
GPU, preserves complete composition by default, and produces a detail comparison.

Repository: https://github.com/zc4578980-tech/anime-wallpaper-upscaler

## Asset Boundary

The K-ON! example is user-supplied and is not represented as licensed for redistribution. See
`docs/assets/promotion/NOTICE.md` for non-affiliation, contact, and removal details.
```

- [ ] **Step 4: Verify GREEN and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_readme_promotion.py -q
git add docs/release/anime-screenshot-promotion.md tests/test_readme_promotion.py
git commit -m "docs: prepare anime screenshot campaign copy"
```

---

### Task 7: Full Verification And PR Gate

**Files:**
- Modify after observed results: `PROJECT_NODES.md`
- Append milestone log: `D:\CodexWorkspace\obsidian\Codex Logs\2026-07-29.md`

- [ ] **Step 1: Run full automated verification**

```powershell
.\.venv\Scripts\python.exe -m pytest -q
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\powershell\setup.tests.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\powershell\launcher.tests.ps1
.\.venv\Scripts\python.exe -m compileall -q anime_wallpaper_upscaler scripts tests
.\.venv\Scripts\python.exe .\scripts\upscale_wallpaper.py --help
$currentStars = [int](gh api repos/zc4578980-tech/anime-wallpaper-upscaler --jq '.stargazers_count')
$asOf = Get-Date -Format 'yyyy-MM-dd'
.\.venv\Scripts\python.exe .\scripts\validate_launch_readiness.py .\docs\release\launch-plan.json --as-of $asOf --current-stars $currentStars
git diff --check
```

Expected: all commands exit `0`; launch validation reports the T+2 goal in progress.

- [ ] **Step 2: Verify tracked-binary boundaries**

```powershell
git ls-files | Select-String -Pattern '(realesrgan-ncnn-vulkan\.exe|\.param$|\.bin$|vulkan-1\.dll$)'
git status --short --branch
```

Expected: no upstream executables/models/DLLs; only intended promotion files.

- [ ] **Step 3: Review every image at original resolution**

Inspect source, detail comparison, wallpaper, desktop comparison, and social preview. Confirm same K-ON! evidence chain, readable labels, correct 4x claim, full composition, vertical desktop layout, no lower green border, no overlaps, and exact 1280x640 social preview.

- [ ] **Step 4: Review README rendering and rights language**

Confirm both first viewports show the screenshot outcome before Agent material, every relative image resolves, and the notice says the asset is unlicensed/uncertain rather than claiming that attribution creates permission.

- [ ] **Step 5: Record only observed evidence**

Update `PROJECT_NODES.md` with the expected 86 Python tests, 33 setup assertions, 9 launcher assertions, checked hashes, branch/commit, copyright risk, and next gate, but replace any count that differs with the observed output. Append the same concise milestone to Obsidian with:

```powershell
& 'C:\Users\Capricorn\.codex\skills\obsidian-evolution\scripts\write-evolution-log.ps1' `
  -Title 'Anime Wallpaper Upscaler screenshot promotion candidate' `
  -Summary 'Prepared an ordinary-user-first K-ON screenshot-to-wallpaper README campaign with verified local evidence and explicit unlicensed-asset boundaries.' `
  -Evidence 'Promotion branch; Python, setup, and launcher verification counts from the current run; checked promotion asset hashes; social preview 1280x640.' `
  -Next 'Obtain explicit approval before push, PR, merge, social-preview upload, Release edit, or external placement.'
```

Do not record a push, PR, Release edit, placement, view, download, or Star that has not occurred.

- [ ] **Step 6: Commit milestone records**

```powershell
git add PROJECT_NODES.md
git commit -m "docs: record promotion verification"
```

- [ ] **Step 7: Stop for push and Draft PR authorization**

After approval only:

```powershell
git push -u origin codex/anime-screenshot-promotion
gh pr create --draft --base main --head codex/anime-screenshot-promotion --title "Lead with the anime screenshot wallpaper workflow" --body "Repositions the README around a verified screenshot-to-wallpaper example. Includes explicit unlicensed-asset and takedown disclosure. No inference behavior changes."
```

- [ ] **Step 8: Keep publication actions separate**

Require separate authorization for Ready, merge, GitHub social-preview upload, Release edit/new Release, each external post, and each write to `docs/release/measurement.csv`.
