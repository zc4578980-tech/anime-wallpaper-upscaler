from pathlib import Path

import pytest
from PIL import Image

from anime_wallpaper_upscaler.discovery import InputJob
from anime_wallpaper_upscaler.realesrgan import RuntimeFiles
from anime_wallpaper_upscaler.workflow import (
    BatchSummary,
    ProcessingOptions,
    process_batch,
    process_image,
)


def options(tmp_path: Path, **overrides: object) -> ProcessingOptions:
    values: dict[str, object] = {
        "runtime": RuntimeFiles(
            tmp_path / "tool.exe",
            tmp_path / "model.param",
            tmp_path / "model.bin",
        ),
        "model": "realesr-animevideov3",
        "scale": 3,
        "target": (320, 200),
        "mode": "preserve",
        "gpu": None,
        "compare": True,
        "keep_upscaled": True,
        "compare_full_input": False,
        "x_bias": 0.5,
        "y_bias": 0.5,
        "copy_desktop": False,
    }
    values.update(overrides)
    return ProcessingOptions(**values)


def fake_upscale(**kwargs: object) -> None:
    input_path = Path(kwargs["input_path"])
    output_path = Path(kwargs["output_path"])
    with Image.open(input_path) as source:
        source.convert("RGBA").resize((120, 90)).save(output_path)


def test_process_image_names_scale_target_and_mode(tmp_path: Path) -> None:
    source = tmp_path / "art.png"
    Image.new("RGB", (40, 30), "red").save(source)
    output = tmp_path / "out"
    job = InputJob(source, output, output)

    result = process_image(job, options(tmp_path), fake_upscale)

    assert result.source == source
    assert result.output_root == output
    assert result.upscaled.name == "art_realesrgan_3x.png"
    assert result.wallpaper.name == "art_wallpaper_AI_320x200_preserve_3x.jpg"
    assert result.comparison is not None
    assert result.comparison.name == "art_AI_compare_3x.jpg"
    assert result.desktop is None
    assert not (output / "art_wallpaper_AI_2560x1440_full.jpg").exists()


def test_process_image_uses_rgb_cover_and_high_quality_jpeg(
    tmp_path: Path,
) -> None:
    source = tmp_path / "alpha.png"
    Image.new("RGBA", (40, 30), (20, 80, 180, 100)).save(source)
    output = tmp_path / "out"

    result = process_image(
        InputJob(source, output, output),
        options(tmp_path, mode="cover", compare=False),
        fake_upscale,
    )

    assert result.comparison is None
    assert result.wallpaper.name == "alpha_wallpaper_AI_320x200_cover_3x.jpg"
    with Image.open(result.wallpaper) as wallpaper:
        assert wallpaper.mode == "RGB"
        assert wallpaper.size == (320, 200)
        assert wallpaper.info.get("jfif") is not None
        assert wallpaper.layer[0][1:3] == (1, 1)
        assert wallpaper.layer[1][1:3] == (1, 1)
        assert wallpaper.layer[2][1:3] == (1, 1)


def test_process_image_can_remove_intermediate_and_copy_wallpaper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "art.png"
    Image.new("RGB", (40, 30), "red").save(source)
    output = tmp_path / "out"
    fake_home = tmp_path / "home"
    (fake_home / "Desktop").mkdir(parents=True)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))

    result = process_image(
        InputJob(source, output, output),
        options(
            tmp_path,
            compare=False,
            keep_upscaled=False,
            copy_desktop=True,
        ),
        fake_upscale,
    )

    assert not result.upscaled.exists()
    assert result.desktop == fake_home / "Desktop" / result.wallpaper.name
    assert result.desktop.read_bytes() == result.wallpaper.read_bytes()


def test_damaged_upscale_has_actionable_source_specific_error(tmp_path: Path) -> None:
    source = tmp_path / "damaged.webp"
    Image.new("RGB", (40, 30), "red").save(source)
    output = tmp_path / "out"

    def damaged_upscale(**kwargs: object) -> None:
        Path(kwargs["output_path"]).write_bytes(b"not an image either")

    with pytest.raises(RuntimeError) as caught:
        process_image(
            InputJob(source, output, output),
            options(tmp_path),
            damaged_upscale,
        )

    message = str(caught.value)
    assert str(source) in message
    assert "damaged or unsupported" in message
    assert "JPG, JPEG, PNG, or WebP" in message


def test_damaged_source_is_rejected_before_gpu_upscale(tmp_path: Path) -> None:
    source = tmp_path / "broken.png"
    source.write_bytes(b"not an image")
    output = tmp_path / "out"
    runner_called = False

    def unexpected_upscale(**kwargs: object) -> None:
        nonlocal runner_called
        runner_called = True

    with pytest.raises(RuntimeError, match="damaged or unsupported"):
        process_image(
            InputJob(source, output, output),
            options(tmp_path),
            unexpected_upscale,
        )

    assert runner_called is False


def test_batch_continues_after_one_failure_and_reports_progress(
    tmp_path: Path,
) -> None:
    jobs = [
        InputJob(tmp_path / "bad.png", tmp_path, tmp_path),
        InputJob(tmp_path / "good.png", tmp_path, tmp_path),
    ]
    progress_calls: list[tuple[int, int, InputJob]] = []

    def processor(job: InputJob, opts: ProcessingOptions) -> object:
        if job.source.name == "bad.png":
            raise RuntimeError("decode failed")
        return object()

    summary = process_batch(
        jobs,
        options(tmp_path),
        processor,
        lambda current, total, job: progress_calls.append((current, total, job)),
    )

    assert isinstance(summary, BatchSummary)
    assert summary.succeeded == 1
    assert summary.failed == 1
    assert summary.exit_code == 1
    assert summary.failures == ((jobs[0].source, "decode failed"),)
    assert progress_calls == [(1, 2, jobs[0]), (2, 2, jobs[1])]


def test_batch_writes_one_scoped_log_per_distinct_output_root(
    tmp_path: Path,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    jobs = [
        InputJob(tmp_path / "one.png", first_root / "nested", first_root),
        InputJob(tmp_path / "two.png", first_root, first_root),
        InputJob(tmp_path / "bad.png", second_root, second_root),
    ]

    def processor(job: InputJob, opts: ProcessingOptions) -> object:
        if job.source.name == "bad.png":
            raise ValueError("unsupported pixels")
        return object()

    summary = process_batch(jobs, options(tmp_path), processor)

    assert summary.log_paths == (
        first_root / "anime-wallpaper-upscaler.log",
        second_root / "anime-wallpaper-upscaler.log",
    )
    first_log = summary.log_paths[0].read_text(encoding="utf-8")
    second_log = summary.log_paths[1].read_text(encoding="utf-8")
    assert "Succeeded: 2" in first_log
    assert "Failed: 0" in first_log
    assert str(jobs[0].source) in first_log
    assert str(jobs[1].source) in first_log
    assert str(jobs[2].source) not in first_log
    assert "Succeeded: 0" in second_log
    assert "Failed: 1" in second_log
    assert "unsupported pixels" in second_log


@pytest.mark.parametrize("interrupt", (KeyboardInterrupt, SystemExit))
def test_batch_does_not_swallow_process_interrupts(
    tmp_path: Path,
    interrupt: type[BaseException],
) -> None:
    job = InputJob(tmp_path / "one.png", tmp_path, tmp_path)

    def processor(job: InputJob, opts: ProcessingOptions) -> object:
        raise interrupt("stop")

    with pytest.raises(interrupt):
        process_batch([job], options(tmp_path), processor)


def test_successful_batch_has_zero_exit_code(tmp_path: Path) -> None:
    job = InputJob(tmp_path / "one.png", tmp_path, tmp_path)

    summary = process_batch([job], options(tmp_path), lambda job, opts: object())

    assert summary.succeeded == 1
    assert summary.failed == 0
    assert summary.exit_code == 0
