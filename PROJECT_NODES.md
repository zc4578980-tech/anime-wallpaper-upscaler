# Project Nodes

## Goal

Prepare an honest, ordinary-user-friendly Windows wallpaper workflow built on the official
Real-ESRGAN NCNN/Vulkan runtime.

Acceptance criteria for v0.2.0: verified one-command setup, drag/drop and folder input, automatic
display/GPU detection, 2x/3x/4x controls, actionable repairs, no tracked upstream binaries, and
a real RTX 5070 Ti end-to-end run. Formal release also requires the conservative 30-Star launch
gate to pass from confirmed evidence.

## Current State

- Status: v0.2.0 implementation, one-click installation, Agent-first discovery, technical
  acceptance, rights-safe demo visuals, and the reviewed `origin/main` integration complete;
  formal release remains blocked by launch evidence and separate authorization.
- Version: v0.2.0 release candidate on `codex/v0.2.0-integration`; no tag, push, or GitHub
  Release created.
- Last verified result: Real 2x, 3x, and 4x runs completed on GPU 0, NVIDIA GeForce RTX 5070 Ti
  Laptop GPU, at an automatically detected 2560x1600 target.

## Key Paths

- Source: `D:\CodexWorkspace\projects\anime-wallpaper-upscaler`
- Script: `scripts\upscale_wallpaper.py`
- One-click installer: `install.cmd`
- PowerShell installer: `setup.ps1`
- Drag/drop launcher: `scripts\run-wallpaper.cmd`
- External dependency: ignored `tools\realesrgan-ncnn-vulkan-20220424-windows`
- Verification output: `D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.0-verification`
- Verification summary: `D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.0-verification\verification-summary.json`
- Owned demo outputs: `D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.0-demo-owned`
- Owned demo verification: `D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.0-demo-owned\owned-demo-verification.json`
- One-click smoke output: `D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.0-one-click-smoke`
- One-click verification: `D:\CodexWorkspace\outputs\anime-wallpaper-upscaler-v0.2.0-one-click-smoke\one-click-verification.json`
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
- Public positioning leads with "Lightweight Windows and Agent Skill built on official
  Real-ESRGAN." Lightweight describes the repository and orchestration layer only: first setup
  still downloads the verified official runtime and models, which perform inference through
  ncnn and Vulkan.
- Agent requests are mapped to explicit wrapper options. Unspecified screen/GPU values remain
  `auto`; unspecified composition remains `preserve`; an explicit 2x/3x/4x request is retained;
  and `cover` is used only when the user accepts cropping.
- Scale-aware defaults preserve the existing x4plus-anime model at 4x and use
  realesr-animevideov3 at 2x/3x; incompatible manual fixed-4x combinations fail before inference.
- Ordinary users use `install.cmd` and never install upstream models manually. Setup can install
  official Python 3.12 per-user through winget after consent, verifies the official archive, and
  requires the executable plus all pinned 2x/3x/4x model files. The launcher re-enters setup if
  any required local component is missing.
- The checked-in demo source is generated deterministically by `scripts\build_original_demo.py`
  and is an original MIT-licensed technical scene. Comparison, overview, and social-preview
  assets now derive from that source and a real official Real-ESRGAN 4x run.
- A 30-Star first-month target is a release-readiness forecast gate, not an engineering guarantee.
- A recorded demo is optional and user-owned follow-up work, not a v0.2.0 release gate.

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

Technical acceptance passed on 2026-07-25: 89 Python tests, 27 setup assertions, 6 launcher
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

The one-click installer milestone then passed 27 setup assertions, 6 launcher assertions, the
89-test Python suite, PowerShell 5.1 parsing, and a real setup rerun. The launcher confirmed all
10 pinned upstream required files without a manual tool path. A fresh GPU 0 smoke used the
automatic scale-2 model and target detection, resolving 2560x1600 and producing a wallpaper,
comparison, raw upscale, and successful log without `--tool-dir` or `--model`.

The Agent-first discovery milestone updated both READMEs, `SKILL.md`, the Agent-community draft,
and the reproducible social preview. Natural-language examples now cover images, recursive
folders, scale, target, GPU, composition, and output destination while showing the exact wrapper
command and upstream architecture. Validation remained at 89 Python tests, 27 setup assertions,
6 launcher assertions, clean compile/help/PowerShell parsing, a verified missing-runtime exit-2
path, a correct Codex skill junction, no tracked upstream binaries/models, and a visually checked
1280x640 social preview. Inference code was unchanged, so the recorded RTX 5070 Ti acceptance and
one-click smoke remain applicable.

On 2026-07-25, `origin/main` was fetched and its 11 commits were integrated into
`codex/v0.2.0-integration` by merge commit `e3eb1e2`. All five conflicts retained the candidate
content because its tested modular implementation already included the remote full-input and
preserved-aspect comparison behavior, while its demo asset is original MIT content and the
remote replacement is explicitly third-party artwork. The integration tree therefore matches the
candidate tree and retains `origin/main` as a merge parent. Full regression then passed: 89
Python tests, 27 setup assertions, 6 launcher assertions, compile/help, whitespace checks, and
no tracked upstream binaries. The demo fixture test now checks deterministic same-environment
generation plus the checked-in asset's rendered integrity rather than cross-Pillow byte identity.

## Blockers And Risks

- Formal release gate is blocked at 0 confirmed visits, 0 independent channels, and 0 forecast
  Stars. Candidate channels are unconfirmed and deliberately count as zero.
- Real-ESRGAN executable and model files remain external, ignored dependencies.
- `codex/v0.2.0-integration` has no remote branch. Do not push or rewrite history without a
  separate authorization.

## Next Session

1. Read this file, `docs\release\launch-forecast.md`, and the verification summary; inspect the
   integration branch and merge commit `e3eb1e2`.
2. Secure actual, policy-compliant placements and add only attributable evidence to
   `docs\release\launch-plan.json`; rerun the gate.
3. Keep the repository public but do not tag, push, announce, or create v0.2.0 Release until the
   gate passes and the user separately authorizes release actions.
4. The user will handle any optional recording; do not make it an engineering release blocker.
5. Do not add a complex GUI merely to chase Stars; keep further work focused on setup friction,
   proof quality, bilingual discovery, Agent invocation, and confirmed channels.

## Update Rule

Update this file at release milestones and before handing the project to a future conversation.
