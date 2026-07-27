# Project Nodes

## Goal

Prepare an honest, ordinary-user-friendly Windows wallpaper workflow built on the official
Real-ESRGAN NCNN/Vulkan runtime.

Acceptance criteria for v0.2.0: verified one-command setup, drag/drop and folder input, automatic
display/GPU detection, 2x/3x/4x controls, actionable repairs, no tracked upstream binaries, and
a real RTX 5070 Ti end-to-end run. The public outcome target is at least 30 net new GitHub Stars
in the first 30 calendar days after a separately authorized v0.2.0 release.

## Current State

- Status: v0.2.0 implementation, one-click installation, Agent-first discovery, technical
  acceptance, rights-safe demo visuals, and the reviewed `origin/main` integration complete.
  PR #1 is merged into protected `main`, its post-merge Windows verification is green, and the
  separately authorized formal release has a recorded Day 0 Star baseline.
- Version: v0.2.0 release source merged to `main` as `445e83a`; a protected release-preparation
  PR records the release notes and measurement baseline before tag publication.
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
- Star-goal tracker: `scripts\validate_launch_readiness.py docs\release\launch-plan.json`
- CI workflow: `.github\workflows\ci.yml`

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
- A 30-Star first-month target is a post-release outcome metric, not a forecast or engineering
  guarantee. Record an auditable public Star baseline immediately before release and assess net
  new Stars at the 30-day checkpoint.
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

On 2026-07-25, the integration branch was pushed and Draft PR #1 was created against `main`:
`https://github.com/zc4578980-tech/anime-wallpaper-upscaler/pull/1`. Its remote head matches
local commit `71af90f` and GitHub reports a clean merge state. The GitHub repository description
and README/install instructions are present, but the repository homepage and Topics are empty,
the custom social-preview endpoint is unconfigured, and no GitHub Release exists. These are
public-positioning follow-ups, not authorization to publish a v0.2.0 Release.

On 2026-07-25, the former release-blocking visit forecast was replaced by the user's actual
requirement: at least 30 net new GitHub Stars in the first 30 calendar days after release. The
tracker validates the target and release-day baseline schema before release, reports progress
before day 30, and assesses the measured public Star count on or after day 30. It does not claim
or guarantee organic Stars, and it no longer requires invented pre-launch traffic.

On 2026-07-25, `.github/workflows/ci.yml` added a Windows GitHub Actions `Verify` workflow for
the release candidate. It installs constrained dependencies and runs the Python suite, compile
check, CLI help, and both PowerShell harnesses without downloading models or requiring a GPU.
After upgrading the Actions integrations to v7, both the push and pull-request runs for commit
`1f0a714` passed without the Node 20 deprecation annotation.

On 2026-07-25, launcher scale handling was hardened in commit `41e2c71`: surrounding whitespace
is trimmed before validating 2x/3x/4x input, while blank input still defaults to 4x and invalid
input retains the existing repair message and exit code. Regression passed: 75 Python tests, 27
setup assertions, 9 launcher assertions, compile, CLI help, and whitespace checks. The cleanroom
clone at `D:\CodexWorkspace\scratch\anime-wallpaper-upscaler-v0.2.0-cleanroom-20260725` then
processed the original demo through the real launcher when `cmd.exe` supplied `2 `, using the RTX
5070 Ti at 2560x1600 and producing the expected wallpaper, comparison, and log. PR #1's Windows
verification run `30165034891` passed; the PR remains Draft and no Release activity occurred.

On 2026-07-26, Draft PR #1 was marked Ready after explicit authorization and merged into
protected `main` as `445e83a`. The post-merge Windows verification run `30188336494` passed, and
local `main` was fast-forwarded to the exact remote merge commit. No branch was deleted and no
tag, Release, or announcement was created during the merge operation.

On 2026-07-27, formal v0.2.0 publication was separately authorized. The public GitHub API
reported 0 Stars at `2026-07-27T15:32:28+08:00`; the immutable Day 0 record is
`docs\release\evidence\release-day.md`. A release-preparation PR updates the launch plan,
measurement row, evidence index, and factual Release Notes before creating the tag and GitHub
Release. Announcement and external channel placement remain outside this authorization.

## Blockers And Risks

- The first-month Star goal starts from the recorded baseline of 0. It remains an outcome target,
  not a guarantee; Day 1/3/7/14/30 observations must use real public counts.
- Real-ESRGAN executable and model files remain external, ignored dependencies.
- GitHub homepage and custom social preview remain optional public-positioning decisions.
  Announcement and external channel placement require separate authorization.

## Next Session

1. Read this file, `docs\release\launch-forecast.md`, and `docs\release\evidence\release-day.md`;
   inspect merged PR #1, protected `main`, and the v0.2.0 Release.
2. Collect the real day 1/3/7/14/30 Star checkpoints in `docs\release\measurement.csv` and keep
   timestamped evidence for every observation.
3. Keep announcements and external channel placement separate from the technical Release unless
   the user explicitly authorizes them.
4. The user will handle any optional recording; do not make it an engineering release blocker.
5. Do not add a complex GUI merely to chase Stars; keep further work focused on setup friction,
   proof quality, bilingual discovery, Agent invocation, and confirmed channels.

## Update Rule

Update this file at release milestones and before handing the project to a future conversation.
