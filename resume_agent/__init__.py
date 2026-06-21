"""AI resume & cover letter generator package.

Modular structure:
- `models`     : Pydantic schemas for structured LLM responses.
- `text_utils` : Pure text helpers (PDF-safe sanitizing, contact line, profile block).
- `providers`  : Multi-provider (Anthropic/OpenAI/DeepSeek) structured-output calls.
- `generator`  : Tailored resume + cover letter generation.
- `extract`    : Resume upload text extraction + profile structuring.
- `pdf_export` : Render the resume / cover letter to PDF bytes.
- `app_logic`  : UI-independent helpers (provider registry, validation).
"""

from .extract import ExtractionError, extract_profile, extract_text
from .generator import DEFAULT_MODEL, DEFAULT_PROVIDER, generate
from .models import (
    ContactInfo,
    EducationItem,
    ExperienceItem,
    ExtractedProfile,
    GenerationResult,
    ResumeData,
    SkillAnalysis,
)
from .pdf_export import cover_letter_pdf, resume_pdf
from .providers import (
    PROVIDER_ENV,
    PROVIDER_MODELS,
    GenerationError,
    complete_structured,
)

__all__ = [
    "ContactInfo",
    "EducationItem",
    "ExperienceItem",
    "ExtractedProfile",
    "GenerationResult",
    "ResumeData",
    "SkillAnalysis",
    "DEFAULT_MODEL",
    "DEFAULT_PROVIDER",
    "GenerationError",
    "ExtractionError",
    "PROVIDER_ENV",
    "PROVIDER_MODELS",
    "complete_structured",
    "generate",
    "extract_text",
    "extract_profile",
    "cover_letter_pdf",
    "resume_pdf",
]
