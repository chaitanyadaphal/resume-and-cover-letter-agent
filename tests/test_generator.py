"""Tests for the generation entry point (delegates to the provider abstraction)."""

from __future__ import annotations

from resume_agent import generator
from resume_agent.generator import build_user_message, generate


def test_build_user_message_includes_sections():
    msg = build_user_message("  my profile  ", "  the job  ")
    assert "=== CANDIDATE DETAILS ===" in msg
    assert "my profile" in msg
    assert "=== TARGET JOB DESCRIPTION ===" in msg
    assert "the job" in msg


def test_generate_delegates_to_provider(monkeypatch, full_result):
    captured = {}

    def fake_complete(provider, model, system, user_message, schema, client):
        captured.update(
            provider=provider,
            model=model,
            system=system,
            user_message=user_message,
            schema=schema,
            client=client,
        )
        return full_result

    monkeypatch.setattr(generator, "complete_structured", fake_complete)

    sentinel_client = object()
    result = generate(
        "profile", "job", provider="OpenAI", model="gpt-4o", client=sentinel_client
    )

    assert result is full_result
    assert captured["provider"] == "OpenAI"
    assert captured["model"] == "gpt-4o"
    assert captured["schema"].__name__ == "GenerationResult"
    assert captured["client"] is sentinel_client
    assert "profile" in captured["user_message"]
    assert "job" in captured["user_message"]


def test_generate_defaults_to_anthropic(monkeypatch, full_result):
    captured = {}
    monkeypatch.setattr(
        generator,
        "complete_structured",
        lambda provider, *a, **k: captured.setdefault("provider", provider) or full_result,
    )
    generate("profile", "job")
    assert captured["provider"] == "Anthropic"
