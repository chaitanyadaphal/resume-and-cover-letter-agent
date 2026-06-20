"""Tests for the multi-provider structured-output abstraction (clients mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock

import anthropic
import httpx
import openai
import pytest

from resume_agent import providers
from resume_agent.models import ExtractedProfile
from resume_agent.providers import GenerationError, complete_structured

SYS = "system"
USER = "user message"


def _call(provider, client):
    return complete_structured(provider, "some-model", SYS, USER, ExtractedProfile, client)


def _auth_error(module):
    req = httpx.Request("POST", "https://api.example.com")
    resp = httpx.Response(401, request=req)
    return module.AuthenticationError("bad key", response=resp, body=None)


def _api_error(module):
    req = httpx.Request("POST", "https://api.example.com")
    return module.APIError("boom", req, body=None)


# --------------------------------------------------------------------------- #
# Dispatch                                                                      #
# --------------------------------------------------------------------------- #
def test_unknown_provider_raises():
    with pytest.raises(GenerationError, match="Unknown provider"):
        _call("Nope", MagicMock())


# --------------------------------------------------------------------------- #
# Anthropic                                                                     #
# --------------------------------------------------------------------------- #
def _anthropic_client(parsed=None, side_effect=None):
    client = MagicMock(spec=anthropic.Anthropic)
    if side_effect is not None:
        client.messages.parse.side_effect = side_effect
    else:
        client.messages.parse.return_value = MagicMock(parsed_output=parsed)
    return client


def test_anthropic_success():
    profile = ExtractedProfile(name="Jane")
    assert _call("Anthropic", _anthropic_client(parsed=profile)) is profile


def test_anthropic_default_client(monkeypatch):
    profile = ExtractedProfile(name="Jane")
    factory = MagicMock(return_value=_anthropic_client(parsed=profile))
    monkeypatch.setattr(providers.anthropic, "Anthropic", factory)
    assert _call("Anthropic", None) is profile
    factory.assert_called_once_with()


def test_anthropic_auth_error():
    with pytest.raises(GenerationError, match="ANTHROPIC_API_KEY"):
        _call("Anthropic", _anthropic_client(side_effect=_auth_error(anthropic)))


def test_anthropic_api_error():
    with pytest.raises(GenerationError, match="Anthropic API request failed"):
        _call("Anthropic", _anthropic_client(side_effect=_api_error(anthropic)))


def test_anthropic_none_result():
    with pytest.raises(GenerationError, match="did not return a valid result"):
        _call("Anthropic", _anthropic_client(parsed=None))


# --------------------------------------------------------------------------- #
# OpenAI                                                                        #
# --------------------------------------------------------------------------- #
def _openai_client(parsed=None, side_effect=None):
    client = MagicMock(spec=openai.OpenAI)
    if side_effect is not None:
        client.chat.completions.parse.side_effect = side_effect
    else:
        message = MagicMock(parsed=parsed)
        client.chat.completions.parse.return_value = MagicMock(choices=[MagicMock(message=message)])
    return client


def test_openai_success():
    profile = ExtractedProfile(name="Jane")
    assert _call("OpenAI", _openai_client(parsed=profile)) is profile


def test_openai_default_client(monkeypatch):
    profile = ExtractedProfile(name="Jane")
    factory = MagicMock(return_value=_openai_client(parsed=profile))
    monkeypatch.setattr(providers.openai, "OpenAI", factory)
    assert _call("OpenAI", None) is profile
    factory.assert_called_once_with()


def test_openai_auth_error():
    with pytest.raises(GenerationError, match="OPENAI_API_KEY"):
        _call("OpenAI", _openai_client(side_effect=_auth_error(openai)))


def test_openai_api_error():
    with pytest.raises(GenerationError, match="OpenAI API request failed"):
        _call("OpenAI", _openai_client(side_effect=_api_error(openai)))


def test_openai_none_result():
    with pytest.raises(GenerationError, match="did not return a valid result"):
        _call("OpenAI", _openai_client(parsed=None))


# --------------------------------------------------------------------------- #
# DeepSeek (OpenAI-compatible, JSON mode)                                       #
# --------------------------------------------------------------------------- #
def _deepseek_client(content=None, side_effect=None):
    client = MagicMock(spec=openai.OpenAI)
    if side_effect is not None:
        client.chat.completions.create.side_effect = side_effect
    else:
        message = MagicMock(content=content)
        client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=message)])
    return client


def test_deepseek_success():
    result = _call("DeepSeek", _deepseek_client(content='{"name": "Jane", "skills": "Python"}'))
    assert result.name == "Jane"
    assert result.skills == "Python"


def test_deepseek_default_client(monkeypatch):
    factory = MagicMock(return_value=_deepseek_client(content='{"name": "Jane"}'))
    monkeypatch.setattr(providers.openai, "OpenAI", factory)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "dummy")
    result = _call("DeepSeek", None)
    assert result.name == "Jane"
    factory.assert_called_once_with(base_url=providers.DEEPSEEK_BASE_URL, api_key="dummy")


def test_deepseek_invalid_json_raises():
    with pytest.raises(GenerationError, match="did not return a valid result"):
        _call("DeepSeek", _deepseek_client(content="this is not json"))


def test_deepseek_none_content_raises():
    # content is None -> coerced to "" -> validation fails cleanly.
    with pytest.raises(GenerationError, match="did not return a valid result"):
        _call("DeepSeek", _deepseek_client(content=None))


def test_deepseek_auth_error():
    with pytest.raises(GenerationError, match="DEEPSEEK_API_KEY"):
        _call("DeepSeek", _deepseek_client(side_effect=_auth_error(openai)))


def test_deepseek_api_error():
    with pytest.raises(GenerationError, match="DeepSeek API request failed"):
        _call("DeepSeek", _deepseek_client(side_effect=_api_error(openai)))
