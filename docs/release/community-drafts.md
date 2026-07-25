# Community Drafts

Use one draft only where it directly answers that community's interests. Adapt the opening to
the venue, disclose affiliation, and participate in follow-up discussion. These drafts do not
assume placement, recommendation traffic, or a particular number of Stars.

## GitHub / Agent-Skill Audience

I built a small Windows workflow skill around the official Real-ESRGAN NCNN/Vulkan release.
It accepts repeated images or folders, detects the physical primary screen, keeps the full
composition with blurred fill by default, and writes comparisons plus batch logs. The setup
creates a local `.venv`, verifies the pinned upstream archive, and registers the repository as
a Codex skill junction.

The inference executable and models are upstream work and are downloaded during setup; they
are not committed here, and this project does not claim an original model or algorithm.

Repository: https://github.com/zc4578980-tech/anime-wallpaper-upscaler

## Windows Utility Audience

For Windows users who have portrait or oddly sized art they want to use as desktop wallpaper:
Anime Wallpaper Upscaler adds a drag-and-drop path around the official local Real-ESRGAN
runtime. Drop files or a folder onto the shortcut, choose 2x/3x/4x, and it detects the main
screen and available Vulkan GPU. The default output keeps the whole image and fills the spare
ratio with a softened copy instead of cutting off the edges.

It needs Windows 10/11, Python 3.10+, and a Vulkan-capable GPU. Images stay local. Setup and
troubleshooting: https://github.com/zc4578980-tech/anime-wallpaper-upscaler

## Real-ESRGAN Audience

This is an independent workflow wrapper, not a competing inference implementation. It invokes
the official `realesrgan-ncnn-vulkan` executable and upstream models, while adding wallpaper
composition, DPI-aware physical-screen detection, repeated/folder inputs, per-image failure
isolation, comparison images, and a verified Windows setup path.

I would especially value feedback on whether the wrapper preserves upstream attribution and
model/scale behavior clearly enough. Source and third-party notices:
https://github.com/zc4578980-tech/anime-wallpaper-upscaler

## Anime-Wallpaper Audience

I wanted a repeatable way to turn vertical anime-style images into desktop wallpapers without
silently cropping the character or redrawing the artwork. This local Windows tool uses the
official Real-ESRGAN runtime for upscaling, then centers the complete image over a blurred copy
that fills the screen. It can process a whole folder and automatically creates a detail
comparison so the result can be checked rather than assumed.

Upscaling cannot reconstruct every lost detail, and `cover` mode still crops when explicitly
selected. Examples, setup, and exact output behavior:
https://github.com/zc4578980-tech/anime-wallpaper-upscaler
