"""Claude-backed generation of the tailored resume, cover letter, and skill analysis.

A single structured-output call returns one validated ``GenerationResult``.
"""

from __future__ import annotations

from typing import Optional

import anthropic

from .models import GenerationResult

# Default model. The UI may override this (e.g. claude-sonnet-4-6 for speed/cost).
DEFAULT_MODEL = "claude-opus-4-8"

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


class GenerationError(Exception):
    """Raised with a user-friendly message when generation fails."""


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
    model: str = DEFAULT_MODEL,
    client: Optional["anthropic.Anthropic"] = None,
) -> GenerationResult:
    """Call Claude and return a validated ``GenerationResult``.

    The API key is read from ``ANTHROPIC_API_KEY`` by the default Anthropic client.
    A client may be injected (used in tests). Raises ``GenerationError`` with a clean
    message on any failure.
    """
    if client is None:
        client = anthropic.Anthropic()

    try:
        response = client.messages.parse(
            model=model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": build_user_message(profile_text, job_description),
                }
            ],
            output_format=GenerationResult,
        )
    except anthropic.AuthenticationError as exc:
        raise GenerationError(
            "Authentication failed. Check that ANTHROPIC_API_KEY is set to a valid key."
        ) from exc
    except anthropic.APIError as exc:
        raise GenerationError(f"The Claude API request failed: {exc}") from exc

    result = response.parsed_output
    if result is None:
        raise GenerationError(
            "The model did not return a valid structured result. Please try again."
        )
    return result
