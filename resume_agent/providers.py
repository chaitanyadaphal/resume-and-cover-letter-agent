"""Provider abstraction for structured LLM calls.

A single ``complete_structured`` entry point serves both resume/cover-letter
generation and resume extraction across Anthropic, OpenAI, and DeepSeek. Each provider
returns a validated Pydantic model instance.
"""

from __future__ import annotations

import json
import os
from typing import Optional, Type, TypeVar

import anthropic
import openai
from pydantic import BaseModel, ValidationError

# Label shown in the UI -> available model ids (first entry is the default).
PROVIDER_MODELS = {
    "Anthropic": ["claude-opus-4-8", "claude-sonnet-4-6"],
    "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4.1"],
    "DeepSeek": ["deepseek-chat", "deepseek-reasoner"],
}

# Provider -> environment variable holding its API key.
PROVIDER_ENV = {
    "Anthropic": "ANTHROPIC_API_KEY",
    "OpenAI": "OPENAI_API_KEY",
    "DeepSeek": "DEEPSEEK_API_KEY",
}

DEEPSEEK_BASE_URL = "https://api.deepseek.com"

MAX_TOKENS = 16000

T = TypeVar("T", bound=BaseModel)


class GenerationError(Exception):
    """Raised with a user-friendly message when an LLM call fails."""


def _auth_hint(provider: str) -> str:
    return (
        f"Authentication failed. Check that {PROVIDER_ENV[provider]} is set to a valid "
        f"{provider} key."
    )


def _anthropic(model, system, user_message, schema: Type[T], client) -> T:
    if client is None:
        client = anthropic.Anthropic()
    try:
        response = client.messages.parse(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user_message}],
            output_format=schema,
        )
    except anthropic.AuthenticationError as exc:
        raise GenerationError(_auth_hint("Anthropic")) from exc
    except anthropic.APIError as exc:
        raise GenerationError(f"The Anthropic API request failed: {exc}") from exc

    result = response.parsed_output
    if result is None:
        raise GenerationError("The model did not return a valid result. Please try again.")
    return result


def _openai(model, system, user_message, schema: Type[T], client) -> T:
    if client is None:
        client = openai.OpenAI()
    try:
        response = client.chat.completions.parse(
            model=model,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
            response_format=schema,
        )
    except openai.AuthenticationError as exc:
        raise GenerationError(_auth_hint("OpenAI")) from exc
    except openai.APIError as exc:
        raise GenerationError(f"The OpenAI API request failed: {exc}") from exc

    result = response.choices[0].message.parsed
    if result is None:
        raise GenerationError("The model did not return a valid result. Please try again.")
    return result


def _deepseek(model, system, user_message, schema: Type[T], client) -> T:
    if client is None:
        client = openai.OpenAI(
            base_url=DEEPSEEK_BASE_URL, api_key=os.environ.get("DEEPSEEK_API_KEY")
        )
    # DeepSeek has JSON mode but no strict json_schema: describe the schema in the
    # prompt (the word "json" is required) and validate the response ourselves.
    augmented_system = (
        f"{system}\n\nRespond with ONLY a valid JSON object matching this JSON schema:\n"
        f"{json.dumps(schema.model_json_schema())}"
    )
    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": augmented_system},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
        )
    except openai.AuthenticationError as exc:
        raise GenerationError(_auth_hint("DeepSeek")) from exc
    except openai.APIError as exc:
        raise GenerationError(f"The DeepSeek API request failed: {exc}") from exc

    content = response.choices[0].message.content or ""
    try:
        return schema.model_validate_json(content)
    except ValidationError as exc:
        raise GenerationError(
            "The model did not return a valid result. Please try again."
        ) from exc


_ADAPTERS = {
    "Anthropic": _anthropic,
    "OpenAI": _openai,
    "DeepSeek": _deepseek,
}


def complete_structured(
    provider: str,
    model: str,
    system: str,
    user_message: str,
    schema: Type[T],
    client: Optional[object] = None,
) -> T:
    """Run a structured LLM call for ``provider`` and return a validated ``schema``.

    A client may be injected (used in tests); otherwise the default client for the
    provider is constructed (reading the provider's API key from the environment).
    Raises ``GenerationError`` with a clean message on any failure.
    """
    adapter = _ADAPTERS.get(provider)
    if adapter is None:
        raise GenerationError(f"Unknown provider: {provider}")
    return adapter(model, system, user_message, schema, client)
