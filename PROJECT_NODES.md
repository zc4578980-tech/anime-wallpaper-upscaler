# Project Nodes

## Goal

Prepare a minimal GitHub-ready release of the local anime wallpaper upscaling skill.

Acceptance criteria: a clean skill folder, documented installation and usage, no personal
machine paths, no bundled model binaries, and a verified end-to-end run.

## Current State

- Status: Minimal release preparation complete; repository is ready for remote setup.
- Version: pre-release v0.1.0
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

- No remote GitHub URL or owner has been configured yet.
- The release currently targets Windows with a Vulkan-capable GPU.
- README still contains the placeholder `YOUR-USERNAME` until a repository owner is chosen.

## Next Session

1. Read this file and inspect the working tree.
2. Replace the README repository placeholder and add comparison screenshots if available.
3. Create a GitHub repository, add its remote, commit, and push after reviewing the license.

## Update Rule

Update this file at release milestones and before handing the project to a future conversation.
