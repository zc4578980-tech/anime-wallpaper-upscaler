---
name: anime-wallpaper-upscale
description: Use when the user wants an anime, illustration, game, or wallpaper image to become clearer, sharper, higher resolution, AI-upscaled, Real-ESRGAN-enhanced, or adapted to a screen while preserving the original composition unless cropping is explicitly requested.
---

# Anime Wallpaper Upscale

Use this skill to turn low-resolution anime-style images into sharper wallpapers.

Prefer faithful local Real-ESRGAN upscaling over ordinary resizing when the source is small,
blurred, compressed, or intended for a high-DPI screen.

Do not use Stable Diffusion, img2img, or other generative redraw workflows unless the user
explicitly asks for a redraw or accepts altering the original art style and details.

## Workflow

1. Inspect the source image size and screen ratio.
2. Run `scripts/upscale_wallpaper.py` for deterministic Real-ESRGAN processing.
3. Generate a 4x PNG upscale, a target-size wallpaper, and a comparison crop.
4. Preserve the full original composition by default. Use crop mode only when requested.
5. Save final wallpapers under `outputs/wallpapers` unless the user names another destination.
6. Copy the recommended wallpaper to the desktop only when the user asks for easy access.

If a redraw attempt looks less faithful than the Real-ESRGAN result, prefer the non-redraw
version and say so.

## Script

```powershell
python .\scripts\upscale_wallpaper.py `
  --input "C:\path\to\image.jpg" `
  --tool-dir "C:\path\to\realesrgan-ncnn-vulkan-v0.2.0-windows" `
  --target 2560x1600 `
  --copy-desktop
```

The tool directory can also be provided through the `REALESRGAN_TOOL_DIR` environment
variable. The executable and selected model files must already be present. Do not silently
fall back to ordinary resizing when the AI tool is unavailable.

Important options:

- `--target 2560x1600`: suitable for a 16:10 laptop screen.
- `--target 2560x1440`: suitable for a 16:9 monitor.
- `--mode preserve`: keeps the full composition and fills extra space with a blurred backdrop.
- `--mode cover`: crops to fill the target exactly; use only when cropping is accepted.
- `--compare-full-input`: use the whole input image for the comparison without a second crop.
- `--x-bias` and `--y-bias`: adjust the crop position in cover mode.
- `--model realesrgan-x4plus-anime`: preferred for anime and illustration images.

## Tool Expectations

The script expects a local Real-ESRGAN NCNN/Vulkan tool directory. Pass it with `--tool-dir`
or set `REALESRGAN_TOOL_DIR`.

Required files:

- `realesrgan-ncnn-vulkan.exe`
- `models\realesrgan-x4plus-anime.param`
- `models\realesrgan-x4plus-anime.bin`

If these files are missing, download or restore the portable executable and model files before
running the script. Do not commit binaries or model files to the repository.

## Quality Notes

- Tell the user when the original is too low-resolution for perfect recovery.
- Upscale first, then downscale to the target wallpaper size for cleaner line art.
- Avoid heavy final sharpening because it creates halos around anime line art and text.
- Use a blurred backdrop or letterbox-style composition instead of cropping unless the user asks.
