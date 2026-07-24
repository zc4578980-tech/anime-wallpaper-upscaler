# Project Nodes

## Goal

Prepare a minimal GitHub-ready release of the local anime wallpaper upscaling skill.

Acceptance criteria: a clean skill folder, documented installation and usage, no personal
machine paths, no bundled model binaries, and a verified end-to-end run.

## Current State

- Status: Public GitHub release published with a full-color comparison image.
- Version: v0.1.0
- Last verified result: Real-ESRGAN produced a 4x PNG, wallpaper, and comparison image on the
  local RTX 5070 Ti using the release copy.

## Key Paths

- Source: `D:\CodexWorkspace\projects\anime-wallpaper-upscaler`
- Script: `scripts\upscale_wallpaper.py`
- Outputs: `outputs\wallpapers` by default
- External dependency: Real-ESRGAN NCNN/Vulkan executable and anime model files
- Verification output: `D:\CodexWorkspace\scratch\anime-upscale-release-test`

## Decisions

- Do not bundle Real-ESRGAN binaries or model files: keep the repository small and respect
  external dependency licenses.
- Keep Windows/PowerShell as the first supported platform for this minimal release.
- Use `--tool-dir` or `REALESRGAN_TOOL_DIR` instead of a machine-specific drive path.

## Commands And Validation

```text
python -m py_compile scripts\upscale_wallpaper.py
python scripts\upscale_wallpaper.py --help
python -m pip install -r requirements.txt
```

End-to-end verification passed on 2026-07-24 with the local Real-ESRGAN tool and a 320x200
test target. Missing input validation also returned the expected non-zero failure.

## Blockers And Risks

- The release currently targets Windows with a Vulkan-capable GPU.
- Real-ESRGAN executable and model files remain external dependencies.

## Next Session

1. Read this file and inspect the working tree.
2. Consider a v0.2.0 with automatic model setup or broader platform support.
3. Replace the demo artwork if broader redistribution is needed.

## Update Rule

Update this file at release milestones and before handing the project to a future conversation.
