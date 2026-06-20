"""Tests for the UI-independent helpers."""

from __future__ import annotations

import pytest

from resume_agent.app_logic import MODELS, validate_inputs


def test_models_registry_maps_to_known_ids():
    assert set(MODELS.values()) == {"claude-opus-4-8", "claude-sonnet-4-6"}
    # Default (first) entry is Opus.
    assert next(iter(MODELS.values())) == "claude-opus-4-8"


def test_validate_inputs_all_present_returns_none():
    assert validate_inputs("Jane", "Dev at Acme", "Some job") is None


@pytest.mark.parametrize(
    "name,experience,job",
    [
        ("", "exp", "job"),       # missing name
        ("  ", "exp", "job"),     # whitespace name
        ("Jane", "", "job"),      # missing experience
        ("Jane", "exp", ""),      # missing job
        ("Jane", "exp", "   "),   # whitespace job
    ],
)
def test_validate_inputs_missing_returns_message(name, experience, job):
    msg = validate_inputs(name, experience, job)
    assert msg is not None and "Please provide" in msg
