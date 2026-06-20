"""UI-independent helpers: model registry and input validation."""

from __future__ import annotations

from typing import Optional

# Label shown in the UI -> Claude model id.
MODELS = {
    "Claude Opus 4.8 (best quality)": "claude-opus-4-8",
    "Claude Sonnet 4.6 (faster / cheaper)": "claude-sonnet-4-6",
}


def validate_inputs(name: str, experience: str, job_description: str) -> Optional[str]:
    """Return an error message if required inputs are missing, else ``None``."""
    if not name.strip() or not experience.strip() or not job_description.strip():
        return "Please provide at least your name, work experience, and the job description."
    return None
