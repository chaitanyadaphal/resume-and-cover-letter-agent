"""UI-independent helpers: provider/model registry and input validation."""

from __future__ import annotations

import os
from typing import Optional

from .providers import PROVIDER_ENV, PROVIDER_MODELS

__all__ = ["PROVIDER_MODELS", "PROVIDER_ENV", "validate_inputs", "missing_key_message"]


def validate_inputs(name: str, experience: str, job_description: str) -> Optional[str]:
    """Return an error message if required inputs are missing, else ``None``."""
    if not name.strip() or not experience.strip() or not job_description.strip():
        return "Please provide at least your name, work experience, and the job description."
    return None


def missing_key_message(provider: str) -> Optional[str]:
    """Return a setup message if the provider's API key is missing, else ``None``."""
    env_var = PROVIDER_ENV[provider]
    if not os.environ.get(env_var):
        return (
            f"**{env_var} is not set.** Add it to your environment or `.env` file to "
            f"use {provider} models."
        )
    return None
