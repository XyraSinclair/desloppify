"""Domain exceptions for review commands."""

from __future__ import annotations


class ReviewCommandError(Exception):
    """Base for review command domain errors."""


class UnsupportedBackendError(ReviewCommandError):
    """Raised when a runner/backend name is not recognized."""


class BatchPrerequisiteError(ReviewCommandError):
    """Raised when batch prerequisites (context, batches) are missing."""
