from __future__ import annotations

import shutil
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .discovery import InputJob
from .errors import DependencyError, UserInputError
from .imaging import (
    cover_resize,
    make_compare,
    polish,
    preserve_composition_wallpaper,
)
from .realesrgan import RuntimeFiles, run_upscale

LOG_NAME = "anime-wallpaper-upscaler.log"


@dataclass(frozen=True, slots=True)
class ProcessingOptions:
    runtime: RuntimeFiles
    model: str
    scale: int
    target: tuple[int, int]
    mode: str
    gpu: int | None
    compare: bool
    keep_upscaled: bool
    compare_full_input: bool
    x_bias: float
    y_bias: float
    copy_desktop: bool


@dataclass(frozen=True, slots=True)
class ImageResult:
    source: Path
    output_root: Path
    upscaled: Path
    wallpaper: Path
    comparison: Path | None
    desktop: Path | None


@dataclass(frozen=True, slots=True)
class BatchSummary:
    results: tuple[ImageResult, ...]
    failures: tuple[tuple[Path, str], ...]
    log_paths: tuple[Path, ...]

    @property
    def succeeded(self) -> int:
        return len(self.results)

    @property
    def failed(self) -> int:
        return len(self.failures)

    @property
    def exit_code(self) -> int:
        return 1 if self.failures else 0


def _invalid_image_error(source: Path) -> UserInputError:
    return UserInputError(
        f"Image is damaged or unsupported: {source}. "
        "Use a valid JPG, JPEG, PNG, or WebP image and try again."
    )


def _validate_source_image(source: Path) -> None:
    try:
        with Image.open(source) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise _invalid_image_error(source) from exc


def _decode_upscaled_image(upscaled: Path) -> Image.Image:
    try:
        with Image.open(upscaled) as image:
            return image.convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise DependencyError(
            "Real-ESRGAN did not produce a readable output image at: "
            f"{upscaled}. Run .\\setup.ps1 again and retry; if the problem "
            "continues, check the upstream diagnostics."
        ) from exc


def process_image(
    job: InputJob,
    options: ProcessingOptions,
    upscale_runner: Callable[..., None] = run_upscale,
) -> ImageResult:
    _validate_source_image(job.source)
    job.output_dir.mkdir(parents=True, exist_ok=True)
    stem = job.source.stem
    width, height = options.target
    upscaled = job.output_dir / f"{stem}_realesrgan_{options.scale}x.png"
    wallpaper = job.output_dir / (
        f"{stem}_wallpaper_AI_{width}x{height}_{options.mode}_{options.scale}x.jpg"
    )
    comparison = (
        job.output_dir / f"{stem}_AI_compare_{options.scale}x.jpg"
        if options.compare
        else None
    )

    upscale_runner(
        runtime=options.runtime,
        input_path=job.source,
        output_path=upscaled,
        model=options.model,
        scale=options.scale,
        gpu=options.gpu,
    )
    image = _decode_upscaled_image(upscaled)

    if options.mode == "cover":
        finished = cover_resize(
            image,
            options.target,
            options.x_bias,
            options.y_bias,
        )
    elif options.mode == "preserve":
        finished = preserve_composition_wallpaper(image, options.target)
    else:
        raise UserInputError(
            f"Unsupported wallpaper mode '{options.mode}'. Use preserve or cover."
        )

    polish(finished).save(
        wallpaper,
        format="JPEG",
        quality=97,
        optimize=True,
        subsampling=0,
    )

    if comparison is not None:
        try:
            make_compare(
                job.source,
                upscaled,
                comparison,
                full_input=options.compare_full_input,
            )
        except (UnidentifiedImageError, OSError) as exc:
            raise _invalid_image_error(job.source) from exc

    if not options.keep_upscaled:
        upscaled.unlink()

    desktop_path = None
    if options.copy_desktop:
        desktop_path = Path.home() / "Desktop" / wallpaper.name
        shutil.copy2(wallpaper, desktop_path)

    return ImageResult(
        source=job.source,
        output_root=job.output_root,
        upscaled=upscaled,
        wallpaper=wallpaper,
        comparison=comparison,
        desktop=desktop_path,
    )


def _write_batch_logs(
    jobs: Sequence[InputJob],
    successes: Sequence[tuple[InputJob, ImageResult]],
    failures: Sequence[tuple[InputJob, str, str]],
) -> tuple[Path, ...]:
    roots = tuple(dict.fromkeys(job.output_root for job in jobs))
    log_paths: list[Path] = []
    for root in roots:
        root.mkdir(parents=True, exist_ok=True)
        scoped_successes = [item for item in successes if item[0].output_root == root]
        scoped_failures = [item for item in failures if item[0].output_root == root]
        lines = [
            "Anime Wallpaper Upscaler batch log",
            f"Succeeded: {len(scoped_successes)}",
            f"Failed: {len(scoped_failures)}",
            "",
        ]
        for job, result in scoped_successes:
            destination = (
                f" -> {result.wallpaper}" if isinstance(result, ImageResult) else ""
            )
            lines.append(f"SUCCESS {job.source}{destination}")
        lines.extend(
            f"FAILED {job.source} [{error_type}]: {message}"
            for job, error_type, message in scoped_failures
        )
        log_path = root / LOG_NAME
        log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        log_paths.append(log_path)
    return tuple(log_paths)


def process_batch(
    jobs: Sequence[InputJob],
    options: ProcessingOptions,
    processor: Callable[[InputJob, ProcessingOptions], ImageResult] = process_image,
    progress: Callable[[int, int, InputJob], None] | None = None,
) -> BatchSummary:
    successes: list[tuple[InputJob, ImageResult]] = []
    failures: list[tuple[InputJob, str, str]] = []
    total = len(jobs)

    for current, job in enumerate(jobs, start=1):
        if progress is not None:
            progress(current, total, job)
        try:
            result = processor(job, options)
        except Exception as exc:
            message = str(exc).strip() or type(exc).__name__
            failures.append((job, type(exc).__name__, message))
        else:
            successes.append((job, result))

    log_paths = _write_batch_logs(jobs, successes, failures)
    return BatchSummary(
        results=tuple(result for _, result in successes),
        failures=tuple((job.source, message) for job, _, message in failures),
        log_paths=log_paths,
    )
