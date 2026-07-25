# Project Nodes

## Goal

Prepare an honest, ordinary-user-friendly Windows wallpaper workflow built on the official
Real-ESRGAN NCNN/Vulkan runtime.

Acceptance criteria for v0.2.0: verified one-command setup, drag/drop and folder input, automatic
display/GPU detection, 2x/3x/4x controls, actionable repairs, no tracked upstream binaries, and
a real RTX 5070 Ti end-to-end run. Formal release also requires the conservative 30-Star launch
gate to pass from confirmed evidence.

## Current State

- Status: v0.2.0 implementation and technical acceptance complete; rights-safe original demo
  visuals complete; formal release blocked by launch evidence and the missing reusable recording.
- Version: v0.2.0 release candidate on `codex/v0.2.0`; no tag, push, or GitHub Release created.
- Last verified result: Real 2x, 3x, and 4x runs completed on GPU 0, NVIDIA GeForce RTX 5070 Ti
  Laptop GPU, at an automatically detected 2560x1600 target.

## Key Paths

- Source: `D:\CodexWorkspace\projects\anime-wallpaper-upscaler`
- Script: `scripts\upscale_wallpaper.py`
- Installer: `setup.ps1`
- Drag/drop launcher: `scripts\run-wallpaper.cmd`
- External dependency: ignored `tools\realesrgan-ncnn-vulkan-20220424-windows`
- Verification output: `D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.0-verification`
- Verification summary: `D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.0-verification\verification-summary.json`
- Owned demo outputs: `D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.0-demo-owned`
- Owned demo verification: `D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.0-demo-owned\owned-demo-verification.json`
- Launch gate: `scripts\validate_launch_readiness.py docs\release\launch-plan.json`

## Decisions

- Do not bundle Real-ESRGAN binaries or model files: keep the repository small and respect
  external dependency licenses.
- Keep Windows/PowerShell as the first supported platform for this minimal release.
- Use `--tool-dir` or `REALESRGAN_TOOL_DIR` instead of a machine-specific drive path.
- Be explicit that this is an integration wrapper and wallpaper workflow built on
  Real-ESRGAN, `realesrgan-ncnn-vulkan`, and their upstream dependencies. Do not claim the
  underlying super-resolution algorithm or model as original work.
- The project's independent value is composition-preserving wallpaper output, target-screen
  adaptation, comparison generation, batch workflow, and ease of use. The current release
  now packages these into setup, drag/drop, CLI, and Codex skill workflows.
- Scale-aware defaults preserve the existing x4plus-anime model at 4x and use
  realesr-animevideov3 at 2x/3x; incompatible manual fixed-4x combinations fail before inference.
- The checked-in demo source is generated deterministically by `scripts\build_original_demo.py`
  and is an original MIT-licensed technical scene. Comparison, overview, and social-preview
  assets now derive from that source and a real official Real-ESRGAN 4x run.
- A 30-Star first-month target is a release-readiness forecast gate, not an engineering guarantee.

## Commands And Validation

```text
python -m compileall -q anime_wallpaper_upscaler scripts tests
python -m pytest -q
python scripts\upscale_wallpaper.py --help
python scripts\build_original_demo.py --output docs\assets\demo-source-original.png
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests\powershell\setup.tests.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests\powershell\launcher.tests.ps1
python scripts\validate_launch_readiness.py docs\release\launch-plan.json
```

Technical acceptance passed on 2026-07-25: 89 Python tests, 17 setup assertions, 2 launcher
assertions, PowerShell 5.1 parsing, help/compile checks, missing input/runtime/model exit-code 2
paths, and tracked-binary search. The official archive matched 45,474,481 bytes and SHA-256
`abc02804e17982a3be33675e4d471e91ea374e65b70167abc09e31acb412802d`.

Real GPU 0 runs used crop `(0, 50, 479, 770)`, target auto -> 2560x1600, and completed at:
2x `2.417s`, 3x `2.547s`, 4x `3.442s`. Every scale produced a nonblank upscale, preserve
wallpaper, comparison, and batch log. Setup also created the project `.venv`, Codex skill
junction, and desktop shortcut.

A separate real folder smoke used two generated fixtures plus one damaged PNG at 2x/320x200.
The RTX run produced two wallpapers/comparisons, isolated the damaged image, wrote `Succeeded: 2`
and `Failed: 1` to the log, and returned the expected partial-failure exit code `1`.

On 2026-07-25, the new original 480x720 demo fixture completed a real 4x run on GPU 0 at the
automatically detected 2560x1600 target. Its raw upscale, preserve wallpaper, comparison, and
log are under the owned-demo output path. The three checked-in presentation images were rebuilt
from those real outputs and visually inspected for complete colored edge markers.

## Blockers And Risks

- Formal release gate is blocked at 0 confirmed visits, 0 independent channels, and 0 forecast
  Stars. Candidate channels are unconfirmed and deliberately count as zero.
- FFmpeg/FFprobe are not installed in PATH or bundled dependencies, so the real 60-90 second
  reusable demo recording is still missing. A verified Gyan FFmpeg 8.1.2 full-package download
  reached only 18.5 MB before the five-minute stop-loss; an unverified smaller package was not
  used. No synthetic placeholder video was created.
- Real-ESRGAN executable and model files remain external, ignored dependencies.
- The branch and `origin/main` have divergent histories; do not push or rewrite history without
  a separate review and authorization.

## Next Session

1. Read this file, `docs\release\launch-forecast.md`, and the verification summary; inspect Git.
2. Record and verify a real 60-90 second controlled-window workflow demo using
   `docs\assets\demo-source-original.png`; keep real terminal evidence visible.
3. Secure actual, policy-compliant placements and add only attributable evidence to
   `docs\release\launch-plan.json`; rerun the gate.
4. Keep the repository public but do not tag, push, announce, or create v0.2.0 Release until the
   gate passes and the user separately authorizes release actions.
5. Do not add a complex GUI merely to chase Stars; keep further work focused on setup friction,
   proof quality, bilingual discovery, and confirmed channels.

## Update Rule

Update this file at release milestones and before handing the project to a future conversation.
