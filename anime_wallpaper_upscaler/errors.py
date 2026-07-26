class UpscalerError(RuntimeError):
    """Base class for expected, user-facing upscaler failures."""


class UserInputError(UpscalerError):
    """Raised when an input or option cannot be used."""


class DependencyError(UpscalerError):
    """Raised when a required local dependency is unavailable."""


class VulkanError(UpscalerError):
    """Raised when the Vulkan runtime or a compatible GPU is unavailable."""
