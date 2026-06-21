"""Extract text from an uploaded resume (PDF/DOCX) and structure it into a profile."""

from __future__ import annotations

from io import BytesIO
from typing import Optional

import docx
from pypdf import PdfReader

from .models import ExtractedProfile
from .providers import complete_structured

EXTRACTION_SYSTEM_PROMPT = """You extract a candidate's details from the raw text of \
their resume.

Rules:
- Only use information present in the resume text. NEVER invent details. If a field is
  not present, return an empty string for it.
- Put skills as a comma-separated list.
- Put links (LinkedIn, GitHub, portfolio) as a comma-separated list.
- For experience, produce readable text covering each role: title, company, dates, and
  key responsibilities/achievements.
- For education, list each qualification with institution and year.
"""


class ExtractionError(Exception):
    """Raised with a user-friendly message when text extraction fails."""


def _pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _docx_text(file_bytes: bytes) -> str:
    document = docx.Document(BytesIO(file_bytes))
    return "\n".join(para.text for para in document.paragraphs)


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Return the plain text of a PDF or DOCX upload.

    Raises ``ExtractionError`` for unsupported file types or empty documents.
    """
    name = filename.lower()
    if name.endswith(".pdf"):
        text = _pdf_text(file_bytes)
    elif name.endswith(".docx"):
        text = _docx_text(file_bytes)
    else:
        raise ExtractionError("Unsupported file type. Please upload a PDF or DOCX file.")

    text = text.strip()
    if not text:
        raise ExtractionError(
            "Could not read any text from the file. It may be empty or a scanned image."
        )
    return text


def extract_profile(
    resume_text: str,
    provider: str,
    model: str,
    client: Optional[object] = None,
) -> ExtractedProfile:
    """Structure raw resume text into an ``ExtractedProfile`` via the chosen provider."""
    user_message = "Extract the candidate's details from this resume:\n\n" + resume_text
    return complete_structured(
        provider, model, EXTRACTION_SYSTEM_PROMPT, user_message, ExtractedProfile, client
    )
