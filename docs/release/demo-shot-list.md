# Demo Shot List

Target runtime: 60-90 seconds (the matching script is approximately 78 seconds). Record a
real local run on Windows; do not replace terminal evidence with simulated overlays.

| Time | Capture | Required evidence | Edit note |
| --- | --- | --- | --- |
| 0-8s | A portrait source stretched, then cropped to a desktop ratio | Visible distortion followed by missing edge content | Use only distributable source artwork |
| 8-17s | Official raw Real-ESRGAN output | Show the `_realesrgan_4x.png` filename and a detail zoom, then the unchanged aspect ratio | Do not label it as this project's model |
| 17-27s | One-time `setup.ps1` flow | Upstream notice, official URL, verification, local `.venv`, shortcut completion | Cut download waiting time; retain source/license screen |
| 27-38s | Drag a folder onto the desktop shortcut | Folder cursor/drop action and one scale prompt | Use 3-5 supported images |
| 38-49s | Select scale `3` and show the terminal | Real `Target: 2560x1600`, detected Vulkan GPU line(s), and `[n/total]` progress | Capture the actual RTX validation run; do not pre-type fake output |
| 49-64s | Open the finished preserve wallpaper | All four source edges remain visible; blurred fill occupies the spare screen ratio | Briefly contrast with `cover`, clearly label the crop |
| 64-71s | Open the output directory | Wallpaper, comparison, raw upscale, and `anime-wallpaper-upscaler.log` | Keep filenames readable |
| 71-78s | Repository README and final URL | Upstream attribution, difference table, direct repository URL | Hold the URL for at least three seconds |

## Capture Checklist

- Record at 2560x1600 or retain the actual detected target if hardware differs; narration must
  match the captured value.
- Keep the real detected GPU name visible long enough to read.
- Capture scale 2/3/4 as available choices without implying all inputs benefit equally.
- Show that `preserve` is the default and that `cover` deliberately crops.
- Confirm all visible source art, filenames, desktop notifications, and account names are safe
  to publish.
- End with the upstream credits and
  `https://github.com/zc4578980-tech/anime-wallpaper-upscaler`.
