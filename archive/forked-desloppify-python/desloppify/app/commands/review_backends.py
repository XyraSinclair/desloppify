"""Review runner backend contracts and canonical registry helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Protocol, TypeVar

from desloppify.app.commands.review.exceptions import UnsupportedBackendError


class BatchRunFn(Protocol):
    """Callable contract for local review batch runners."""

    def __call__(
        self,
        prompt: str,
        repo_root: Path,
        output_file: Path,
        log_file: Path,
    ) -> int: ...


@dataclass(frozen=True)
class BatchRunnerSpec:
    """Static metadata for a local review batch runner backend."""

    name: str
    description: str


@dataclass(frozen=True)
class BatchRunnerBackend:
    """Executable local review batch backend contract."""

    name: str
    run_batch: BatchRunFn


@dataclass(frozen=True)
class ExternalReviewBackendSpec:
    """Static metadata for an external review backend."""

    name: str
    launch_prompt_filename: str
    launch_prompt_label: str
    supports_durable_submit: bool = True
    supports_attested_assessment_import: bool = True


# ---------------------------------------------------------------------------
# Generic backend registry
# ---------------------------------------------------------------------------

T = TypeVar("T")


@dataclass(frozen=True)
class BackendRegistry(Generic[T]):
    """Lookup registry for named backend specs."""

    specs: dict[str, T]
    default_name: str
    label: str  # "runner" or "external runner" — used in error messages

    def choices(self) -> tuple[str, ...]:
        return tuple(self.specs.keys())

    def validate(self, name: str | None) -> str:
        normalized = _normalized_name(name, default=self.default_name)
        if normalized in self.specs:
            return normalized
        raise UnsupportedBackendError(
            f"unsupported {self.label} "
            f"'{normalized}' (supported: {self.supported_text()})"
        )

    def spec(self, name: str | None) -> T | None:
        normalized = _normalized_name(name, default=self.default_name)
        return self.specs.get(normalized)

    def supported_text(self) -> str:
        return ", ".join(self.choices()) or "<none>"


# ---------------------------------------------------------------------------
# Registry instances
# ---------------------------------------------------------------------------

BATCH_RUNNERS: BackendRegistry[BatchRunnerSpec] = BackendRegistry(
    specs={
        "codex": BatchRunnerSpec(
            name="codex",
            description="Local Codex CLI batch execution backend",
        ),
    },
    default_name="codex",
    label="runner",
)

EXTERNAL_BACKENDS: BackendRegistry[ExternalReviewBackendSpec] = BackendRegistry(
    specs={
        "claude": ExternalReviewBackendSpec(
            name="claude",
            launch_prompt_filename="claude_launch_prompt.md",
            launch_prompt_label="Claude launch prompt",
            supports_durable_submit=True,
        ),
    },
    default_name="claude",
    label="external runner",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalized_name(raw_name: str | None, *, default: str) -> str:
    if not isinstance(raw_name, str):
        return default
    cleaned = raw_name.strip().lower()
    return cleaned or default


# ---------------------------------------------------------------------------
# Public wrappers — preserve backward compat and __all__ surface
# ---------------------------------------------------------------------------

def batch_runner_choices() -> tuple[str, ...]:
    """Return supported local batch runner backend names."""
    return BATCH_RUNNERS.choices()


def external_runner_choices() -> tuple[str, ...]:
    """Return supported external review backend names."""
    return EXTERNAL_BACKENDS.choices()


def supported_batch_runners_text() -> str:
    return BATCH_RUNNERS.supported_text()


def supported_external_runners_text() -> str:
    return EXTERNAL_BACKENDS.supported_text()


def blind_provenance_runner_choices() -> tuple[str, ...]:
    """Return runner names accepted in blind provenance payloads."""
    runners: list[str] = list(batch_runner_choices())
    for name in external_runner_choices():
        if name not in runners:
            runners.append(name)
    return tuple(runners)


def attested_external_runner_choices() -> tuple[str, ...]:
    """Return external runners allowed for attested external score imports."""
    allowed = [
        name
        for name, spec in EXTERNAL_BACKENDS.specs.items()
        if spec.supports_durable_submit and spec.supports_attested_assessment_import
    ]
    return tuple(allowed)


def supported_attested_external_runners_text() -> str:
    return ", ".join(attested_external_runner_choices()) or "<none>"


def batch_runner_spec(name: str | None) -> BatchRunnerSpec | None:
    """Resolve batch runner spec by name."""
    return BATCH_RUNNERS.spec(name)


def external_review_backend_spec(name: str | None) -> ExternalReviewBackendSpec | None:
    """Resolve external review backend spec by name."""
    return EXTERNAL_BACKENDS.spec(name)


def validate_batch_runner(name: str | None) -> str:
    """Return normalized batch runner name or raise UnsupportedBackendError."""
    return BATCH_RUNNERS.validate(name)


def validate_external_runner(name: str | None) -> str:
    """Return normalized external backend name or raise UnsupportedBackendError."""
    return EXTERNAL_BACKENDS.validate(name)


__all__ = [
    "BackendRegistry",
    "BatchRunFn",
    "BatchRunnerBackend",
    "BatchRunnerSpec",
    "ExternalReviewBackendSpec",
    "attested_external_runner_choices",
    "batch_runner_choices",
    "batch_runner_spec",
    "blind_provenance_runner_choices",
    "external_review_backend_spec",
    "external_runner_choices",
    "supported_attested_external_runners_text",
    "supported_batch_runners_text",
    "supported_external_runners_text",
    "validate_batch_runner",
    "validate_external_runner",
    "UnsupportedBackendError",
]
