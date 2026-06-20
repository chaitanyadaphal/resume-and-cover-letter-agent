"""AI resume & cover letter generator package.

Modular structure:
- `models`     : Pydantic schemas for the structured Claude response.
- `text_utils` : Pure text helpers (PDF-safe sanitizing, contact line, profile block).
- `generator`  : Anthropic client call returning a validated GenerationResult.
- `pdf_export` : Render the resume / cover letter to PDF bytes.
- `app_logic`  : UI-independent helpers (model registry, input validation).
"""

from .generator import DEFAULT_MODEL, GenerationError, generate
from .models import (
    ContactInfo,
    EducationItem,
    ExperienceItem,
    GenerationResult,
    ResumeData,
    SkillAnalysis,
)
from .pdf_export import cover_letter_pdf, resume_pdf

__all__ = [
    "ContactInfo",
    "EducationItem",
    "ExperienceItem",
    "GenerationResult",
    "ResumeData",
    "SkillAnalysis",
    "DEFAULT_MODEL",
    "GenerationError",
    "generate",
    "cover_letter_pdf",
    "resume_pdf",
]
