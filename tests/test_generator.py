"""Tests for the generation logic, with the Anthropic client mocked."""

from __future__ import annotations

from unittest.mock import MagicMock

import anthropic
import httpx
import pytest

from resume_agent import generator
from resume_agent.generator import (
    GenerationError,
    build_user_message,
    generate,
)


def _mock_client(parse_return=None, parse_side_effect=None):
    client = MagicMock(spec=anthropic.Anthropic)
    if parse_side_effect is not None:
        client.messages.parse.side_effect = parse_side_effect
    else:
        client.messages.parse.return_value = parse_return
    return client


def test_build_user_message_includes_sections():
    msg = build_user_message("  my profile  ", "  the job  ")
    assert "=== CANDIDATE DETAILS ===" in msg
    assert "my profile" in msg
    assert "=== TARGET JOB DESCRIPTION ===" in msg
    assert "the job" in msg


def test_generate_success_with_injected_client(full_result):
    response = MagicMock()
    response.parsed_output = full_result
    client = _mock_client(parse_return=response)

    result = generate("profile", "job", model="claude-sonnet-4-6", client=client)

    assert result is full_result
    # The model id and structured output_format were forwarded.
    kwargs = client.messages.parse.call_args.kwargs
    assert kwargs["model"] == "claude-sonnet-4-6"
    assert kwargs["output_format"].__name__ == "GenerationResult"


def test_generate_creates_default_client_when_none(monkeypatch, full_result):
    response = MagicMock()
    response.parsed_output = full_result
    created = _mock_client(parse_return=response)
    factory = MagicMock(return_value=created)
    monkeypatch.setattr(generator.anthropic, "Anthropic", factory)

    result = generate("profile", "job")  # no client -> constructs default

    factory.assert_called_once_with()
    assert result is full_result


def test_generate_authentication_error():
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    resp = httpx.Response(401, request=req)
    err = anthropic.AuthenticationError("bad key", response=resp, body=None)
    client = _mock_client(parse_side_effect=err)

    with pytest.raises(GenerationError, match="Authentication failed"):
        generate("profile", "job", client=client)


def test_generate_api_error():
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    err = anthropic.APIError("boom", req, body=None)
    client = _mock_client(parse_side_effect=err)

    with pytest.raises(GenerationError, match="The Claude API request failed"):
        generate("profile", "job", client=client)


def test_generate_none_parsed_output():
    response = MagicMock()
    response.parsed_output = None
    client = _mock_client(parse_return=response)

    with pytest.raises(GenerationError, match="did not return a valid structured result"):
        generate("profile", "job", client=client)
