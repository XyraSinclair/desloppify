"""Tests for review backend registry contracts."""

from __future__ import annotations

import pytest

from desloppify.app.commands import review_backends as backends_mod
from desloppify.app.commands.review.exceptions import UnsupportedBackendError


def test_batch_runner_registry_defaults():
    assert backends_mod.batch_runner_choices() == ("codex",)
    assert backends_mod.validate_batch_runner("codex") == "codex"


def test_external_runner_registry_defaults():
    assert backends_mod.external_runner_choices() == ("claude",)
    assert backends_mod.validate_external_runner("claude") == "claude"
    assert backends_mod.attested_external_runner_choices() == ("claude",)
    assert backends_mod.blind_provenance_runner_choices() == ("codex", "claude")


def test_validate_batch_runner_rejects_unknown():
    with pytest.raises(UnsupportedBackendError) as exc_info:
        backends_mod.validate_batch_runner("unknown")
    assert "unsupported runner" in str(exc_info.value)
    assert "codex" in str(exc_info.value)


def test_validate_external_runner_rejects_unknown():
    with pytest.raises(UnsupportedBackendError) as exc_info:
        backends_mod.validate_external_runner("unknown")
    assert "unsupported external runner" in str(exc_info.value)
    assert "claude" in str(exc_info.value)
