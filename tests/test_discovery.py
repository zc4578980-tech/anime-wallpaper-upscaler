from pathlib import Path

import pytest

from anime_wallpaper_upscaler.discovery import OUTPUT_DIR_NAME, discover_jobs
from anime_wallpaper_upscaler.errors import UserInputError


def test_discovers_supported_files_once(tmp_path: Path) -> None:
    image = tmp_path / "one.PNG"
    image.write_bytes(b"not-decoded-yet")
    jobs = discover_jobs([image, image], recursive=False, explicit_out_dir=None)
    assert [job.source for job in jobs] == [image.resolve()]
    assert jobs[0].output_dir == (tmp_path / OUTPUT_DIR_NAME).resolve()
    assert jobs[0].output_root == (tmp_path / OUTPUT_DIR_NAME).resolve()


def test_folder_is_non_recursive_by_default(tmp_path: Path) -> None:
    (tmp_path / "top.jpg").write_bytes(b"x")
    child = tmp_path / "child"
    child.mkdir()
    (child / "nested.webp").write_bytes(b"x")
    assert [job.source.name for job in discover_jobs([tmp_path], False, None)] == [
        "top.jpg"
    ]


def test_recursive_folder_preserves_relative_output_and_excludes_outputs(
    tmp_path: Path,
) -> None:
    child = tmp_path / "child"
    child.mkdir()
    (child / "nested.png").write_bytes(b"x")
    generated = tmp_path / OUTPUT_DIR_NAME
    generated.mkdir()
    (generated / "old.png").write_bytes(b"x")
    jobs = discover_jobs([tmp_path], True, None)
    assert [job.source.name for job in jobs] == ["nested.png"]
    assert jobs[0].output_dir == (generated / "child").resolve()
    assert jobs[0].output_root == generated.resolve()


def test_missing_input_is_actionable(tmp_path: Path) -> None:
    with pytest.raises(UserInputError, match="Input path does not exist"):
        discover_jobs([tmp_path / "missing.png"], False, None)
