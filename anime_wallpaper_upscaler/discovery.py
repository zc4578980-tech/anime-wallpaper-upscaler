from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .errors import UserInputError

SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
OUTPUT_DIR_NAME = "Wallpaper Upscaler Output"


@dataclass(frozen=True)
class InputJob:
    source: Path
    output_dir: Path
    output_root: Path


def discover_jobs(
    inputs: Sequence[Path], recursive: bool, explicit_out_dir: Path | None
) -> list[InputJob]:
    jobs: list[InputJob] = []
    seen: set[Path] = set()
    fixed_output = explicit_out_dir.expanduser().resolve() if explicit_out_dir else None

    for raw in inputs:
        path = raw.expanduser().resolve()
        if not path.exists():
            raise UserInputError(f"Input path does not exist: {path}")

        if path.is_file():
            output_root = fixed_output or (path.parent / OUTPUT_DIR_NAME).resolve()
            candidates = [(path, output_root, output_root)]
        elif path.is_dir():
            root_output = fixed_output or (path / OUTPUT_DIR_NAME).resolve()
            iterator = path.rglob("*") if recursive else path.iterdir()
            candidates = []
            for candidate in sorted(iterator, key=lambda item: str(item).casefold()):
                resolved = candidate.resolve()
                if root_output == resolved or root_output in resolved.parents:
                    continue
                if resolved.is_file() and resolved.suffix.casefold() in SUPPORTED_SUFFIXES:
                    relative_parent = (
                        resolved.parent.relative_to(path) if recursive else Path()
                    )
                    candidates.append(
                        (resolved, (root_output / relative_parent).resolve(), root_output)
                    )
        else:
            raise UserInputError(f"Input is not a regular file or folder: {path}")

        for source, output_dir, output_root in candidates:
            if source.suffix.casefold() not in SUPPORTED_SUFFIXES or source in seen:
                continue
            seen.add(source)
            jobs.append(InputJob(source, output_dir, output_root))

    if not jobs:
        raise UserInputError("No supported JPG, JPEG, PNG, or WebP images were found.")
    return jobs
