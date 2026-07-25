from __future__ import annotations

import ctypes
import re
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import UserInputError, VulkanError

FALLBACK_TARGET = (2560, 1600)
MINIMUM_DISPLAY_SIZE = (320, 200)

_TARGET_PATTERN = re.compile(r"^(\d+)[xX](\d+)$")
_GPU_PATTERN = re.compile(r"^\[(\d+)\s+(.+?)\]\s+queueC=", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class GpuDevice:
    id: int
    name: str


def parse_target(value: str) -> tuple[int, int] | None:
    normalized = value.strip()
    if normalized.lower() == "auto":
        return None

    match = _TARGET_PATTERN.fullmatch(normalized)
    if match is None:
        raise UserInputError(
            "Target must be 'auto' or WIDTHxHEIGHT, for example 2560x1600."
        )

    width, height = (int(part) for part in match.groups())
    if width < MINIMUM_DISPLAY_SIZE[0] or height < MINIMUM_DISPLAY_SIZE[1]:
        raise UserInputError(
            "Target must use WIDTHxHEIGHT with dimensions of at least 320x200."
        )
    return width, height


def _enable_dpi_awareness(user32: Any) -> None:
    modern_api = getattr(user32, "SetProcessDpiAwarenessContext", None)
    if modern_api is not None:
        try:
            if modern_api(ctypes.c_void_p(-4)):
                return
        except (OSError, TypeError, ValueError):
            pass

    legacy_api = getattr(user32, "SetProcessDPIAware", None)
    if legacy_api is None:
        raise OSError("Windows DPI-awareness APIs are unavailable")
    legacy_api()


def get_primary_display_resolution(*, user32: Any | None = None) -> tuple[int, int]:
    try:
        active_user32 = user32 if user32 is not None else ctypes.windll.user32
        _enable_dpi_awareness(active_user32)
        width = int(active_user32.GetSystemMetrics(0))
        height = int(active_user32.GetSystemMetrics(1))
    except Exception as exc:
        if isinstance(exc, OSError):
            raise
        raise OSError(f"Windows display detection failed: {exc}") from exc

    minimum_width, minimum_height = MINIMUM_DISPLAY_SIZE
    if width < minimum_width or height < minimum_height:
        raise OSError(
            "Windows returned an invalid primary display size "
            f"({width}x{height}); expected at least 320x200"
        )
    return width, height


def resolve_target(
    value: str,
    detector: Callable[[], tuple[int, int]] = get_primary_display_resolution,
) -> tuple[tuple[int, int], str | None]:
    parsed = parse_target(value)
    if parsed is not None:
        return parsed, None

    try:
        return detector(), None
    except OSError as exc:
        width, height = FALLBACK_TARGET
        warning = (
            f"Could not detect the primary display ({exc}). "
            f"Using {width}x{height}; pass --target WIDTHxHEIGHT to override it."
        )
        return FALLBACK_TARGET, warning


def parse_gpu_devices(output: str) -> list[GpuDevice]:
    devices: list[GpuDevice] = []
    seen_ids: set[int] = set()
    for match in _GPU_PATTERN.finditer(output):
        device_id = int(match.group(1))
        if device_id in seen_ids:
            continue
        seen_ids.add(device_id)
        devices.append(GpuDevice(device_id, match.group(2).strip()))
    return devices


def _output_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def probe_gpus(
    executable: Path,
    cwd: Path,
    runner: Callable[..., subprocess.CompletedProcess[object]] = subprocess.run,
) -> list[GpuDevice]:
    command = [
        str(executable),
        "-i",
        str(cwd / "__aups_probe_missing__.png"),
        "-o",
        str(cwd / "__aups_probe_output__.png"),
        "-v",
    ]
    result = runner(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = "\n".join(
        part
        for part in (_output_text(result.stdout), _output_text(result.stderr))
        if part
    )
    devices = parse_gpu_devices(output)
    if devices:
        return devices

    raise VulkanError(
        "No Vulkan GPU was reported by realesrgan-ncnn-vulkan. Update the GPU "
        "driver and try again:\n"
        "NVIDIA: https://www.nvidia.com/Download/index.aspx\n"
        "AMD: https://www.amd.com/en/support/download/drivers.html\n"
        "Intel: https://www.intel.com/content/www/us/en/download-center/home.html"
    )


def resolve_gpu(value: str, devices: Sequence[GpuDevice]) -> int | None:
    normalized = value.strip()
    if normalized.lower() == "auto":
        return None

    available = ", ".join(f"{device.id} ({device.name})" for device in devices)
    available_message = available or "none detected"
    if not normalized.isdecimal():
        raise UserInputError(
            "GPU must be auto or a numeric GPU ID. "
            f"Available GPU IDs: {available_message}."
        )

    selected = int(normalized)
    if not any(device.id == selected for device in devices):
        raise UserInputError(
            f"GPU ID {selected} was not detected. "
            f"Available GPU IDs: {available_message}."
        )
    return selected
