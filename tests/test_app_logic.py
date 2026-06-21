"""Tests for the UI-independent helpers."""

from __future__ import annotations

import pytest

from resume_agent.app_logic import (
    PROVIDER_ENV,
    PROVIDER_MODELS,
    missing_key_message,
    validate_inputs,
)


def test_provider_registries_aligned():
    assert set(PROVIDER_MODELS) == {"Anthropic", "OpenAI", "DeepSeek"}
    assert set(PROVIDER_ENV) == set(PROVIDER_MODELS)
    # Each provider has at least one model and a default (first) entry.
    for models in PROVIDER_MODELS.values():
        assert len(models) >= 1
    assert PROVIDER_MODELS["Anthropic"][0] == "claude-opus-4-8"


def test_validate_inputs_all_present_returns_none():
    assert validate_inputs("Jane", "Dev at Acme", "Some job") is None


@pytest.mark.parametrize(
    "name,experience,job",
    [
        ("", "exp", "job"),
        ("  ", "exp", "job"),
        ("Jane", "", "job"),
        ("Jane", "exp", ""),
        ("Jane", "exp", "   "),
    ],
)
def test_validate_inputs_missing_returns_message(name, experience, job):
    msg = validate_inputs(name, experience, job)
    assert msg is not None and "Please provide" in msg


def test_missing_key_message_when_absent(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    msg = missing_key_message("OpenAI")
    assert msg is not None and "OPENAI_API_KEY" in msg


def test_missing_key_message_when_present(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert missing_key_message("Anthropic") is None
