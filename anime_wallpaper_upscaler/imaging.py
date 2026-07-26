from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


def cover_resize(
    img: Image.Image,
    target: tuple[int, int],
    x_bias: float,
    y_bias: float,
) -> Image.Image:
    tw, th = target
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = round((nw - tw) * x_bias)
    top = round((nh - th) * y_bias)
    return resized.crop((left, top, left + tw, top + th))


def preserve_composition_wallpaper(
    img: Image.Image,
    target: tuple[int, int],
) -> Image.Image:
    tw, th = target
    sw, sh = img.size

    bg = cover_resize(img, target, 0.5, 0.5)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=max(tw, th) * 0.012))
    bg = ImageEnhance.Brightness(bg).enhance(0.82)
    bg = ImageEnhance.Contrast(bg).enhance(0.92)

    scale = min(tw / sw, th / sh)
    fw, fh = round(sw * scale), round(sh * scale)
    fg = img.resize((fw, fh), Image.Resampling.LANCZOS)
    left = (tw - fw) // 2
    top = (th - fh) // 2
    bg.paste(fg, (left, top))
    return bg


def polish(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Color(img).enhance(1.02)
    img = ImageEnhance.Contrast(img).enhance(1.02)
    return img.filter(ImageFilter.UnsharpMask(radius=0.7, percent=35, threshold=3))


def make_compare(
    original_path: Path,
    upscaled_path: Path,
    out_path: Path,
    full_input: bool = False,
) -> None:
    with Image.open(original_path) as original_image, Image.open(
        upscaled_path
    ) as upscaled_image:
        orig = original_image.convert("RGB")
        up = upscaled_image.convert("RGB")

    ow, oh = orig.size
    box = (
        (0, 0, ow, oh)
        if full_input
        else (
            round(ow * 0.36),
            round(oh * 0.13),
            round(ow * 0.54),
            round(oh * 0.46),
        )
    )
    crop = orig.crop(box)
    scale = min(520 / crop.width, 720 / crop.height)
    panel_size = (
        max(1, round(crop.width * scale)),
        max(1, round(crop.height * scale)),
    )
    normal = crop.resize(panel_size, Image.Resampling.LANCZOS)
    sx = up.width / ow
    sy = up.height / oh
    up_box = (
        round(box[0] * sx),
        round(box[1] * sy),
        round(box[2] * sx),
        round(box[3] * sy),
    )
    ai_crop = up.crop(up_box).resize(panel_size, Image.Resampling.LANCZOS)
    canvas = Image.new(
        "RGB",
        (panel_size[0] * 2 + 20, panel_size[1] + 50),
        "white",
    )
    canvas.paste(normal, (0, 50))
    canvas.paste(ai_crop, (panel_size[0] + 20, 50))
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 15), "Normal upscale", fill=(0, 0, 0))
    draw.text(
        (panel_size[0] + 30, 15),
        "Real-ESRGAN AI upscale",
        fill=(0, 0, 0),
    )
    divider_x = panel_size[0] + 10
    draw.line(
        (divider_x, 0, divider_x, canvas.height),
        fill=(180, 180, 180),
        width=2,
    )
    canvas.save(out_path, quality=95)
