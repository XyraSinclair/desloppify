"""Invariant tests for the canonical detector registry.

Ensures DISPLAY_ORDER and DETECTORS stay in sync, preventing
silent drift as detectors are added or removed.
"""

from __future__ import annotations

from desloppify.core import registry as registry_mod


def test_display_order_keys_exist_in_detectors():
    """Every key in DISPLAY_ORDER must exist in DETECTORS."""
    missing = [
        name for name in registry_mod.DISPLAY_ORDER
        if name not in registry_mod.DETECTORS
    ]
    assert not missing, f"DISPLAY_ORDER references unknown detectors: {missing}"


def test_detectors_keys_appear_in_display_order():
    """Every key in DETECTORS must appear in DISPLAY_ORDER."""
    order_set = set(registry_mod.DISPLAY_ORDER)
    missing = [
        name for name in registry_mod.DETECTORS
        if name not in order_set
    ]
    assert not missing, f"DETECTORS has entries missing from DISPLAY_ORDER: {missing}"


def test_display_order_has_no_duplicates():
    """DISPLAY_ORDER must not contain duplicate entries."""
    seen: set[str] = set()
    dupes: list[str] = []
    for name in registry_mod.DISPLAY_ORDER:
        if name in seen:
            dupes.append(name)
        seen.add(name)
    assert not dupes, f"DISPLAY_ORDER has duplicates: {dupes}"


def test_judgment_detectors_matches_needs_judgment_flags():
    """JUDGMENT_DETECTORS must equal the set derived from needs_judgment flags."""
    expected = frozenset(
        name for name, meta in registry_mod.DETECTORS.items()
        if meta.needs_judgment
    )
    assert registry_mod.JUDGMENT_DETECTORS == expected, (
        f"JUDGMENT_DETECTORS drift: "
        f"extra={registry_mod.JUDGMENT_DETECTORS - expected}, "
        f"missing={expected - registry_mod.JUDGMENT_DETECTORS}"
    )


def test_every_detector_has_display_and_dimension():
    """Every detector must have a non-empty display and dimension."""
    bad: list[str] = []
    for name, meta in registry_mod.DETECTORS.items():
        if not meta.display or not meta.display.strip():
            bad.append(f"{name}: empty display")
        if not meta.dimension or not meta.dimension.strip():
            bad.append(f"{name}: empty dimension")
    assert not bad, f"Detectors with missing display/dimension: {bad}"
