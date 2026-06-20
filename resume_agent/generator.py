"""Generate the tailored resume, cover letter, and skill analysis via any provider.

A single structured-output call (through ``providers.complete_structured``) returns one
validated ``GenerationResult``.
"""

from __future__ import annotations

from typing import Optional

from .models import GenerationResult
from .providers import GenerationError, complete_structured

# Default provider/model. The UI may override these.
DEFAULT_PROVIDER = "Anthropic"
DEFAULT_MODEL = "claude-opus-4-8"

__all__ = [
    "DEFAULT_PROVIDER",
    "DEFAULT_MODEL",
    "GenerationError",
    "SYSTEM_PROMPT",
    "build_user_message",
    "generate",
]

SYSTEM_PROMPT = """You are an expert career coach and professional resume writer.

Given a candidate's details and a target job description, produce:
1. A tailored resume that reorders and rephrases the candidate's real experience and
   skills to match what the job emphasizes.
2. A personalized cover letter body that connects the candidate's background to this
   specific role and company.
3. A skill-gap analysis comparing the candidate against the job description.

Rules:
- Ground every claim in the candidate's actual input. NEVER invent jobs, employers,
  degrees, dates, or skills the candidate did not provide. If a field is unknown,
  leave it empty rather than fabricating.
- Tailor wording to the job description: mirror its key terminology where the
  candidate genuinely has the relevant experience.
- Write achievement-focused resume bullets (action verb + what + measurable impact
  where available).
- In matched_skills, list skills the candidate clearly has that the job wants.
- In missing_skills, list skills the job requires that the candidate does NOT appear
  to have - be honest and specific; do not pad the resume with these.
- In improvement_suggestions, give concrete, actionable advice (skills to learn,
  experience to highlight, certifications, ways to close the gaps).
- The cover_letter_body must be the body only: no address block, no "Dear ..."
  greeting line, and no sign-off - those are added by the application.
"""


def build_user_message(profile_text: str, job_description: str) -> str:
    """Assemble the user turn from the candidate profile and job description."""
    return (
        "=== CANDIDATE DETAILS ===\n"
        f"{profile_text.strip()}\n\n"
        "=== TARGET JOB DESCRIPTION ===\n"
        f"{job_description.strip()}\n\n"
        "Generate the tailored resume, cover letter body, and skill-gap analysis."
    )


def generate(
    profile_text: str,
    job_description: str,
    provider: str = DEFAULT_PROVIDER,
    model: str = DEFAULT_MODEL,
    client: Optional[object] = None,
) -> GenerationResult:
    """Generate a validated ``GenerationResult`` using the chosen provider/model.

    Raises ``GenerationError`` with a clean message on any failure.
    """
    return complete_structured(
        provider,
        model,
        SYSTEM_PROMPT,
        build_user_message(profile_text, job_description),
        GenerationResult,
        client,
    )
