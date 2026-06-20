"""Tests for PDF rendering. Exercises both populated and empty branches."""

from __future__ import annotations

from resume_agent.models import ContactInfo, ResumeData
from resume_agent.pdf_export import cover_letter_pdf, resume_pdf


def _is_pdf(data: bytes) -> bool:
    return isinstance(data, bytes) and data.startswith(b"%PDF-") and len(data) > 0


def test_resume_pdf_full(full_result):
    data = resume_pdf(full_result.resume)
    assert _is_pdf(data)


def test_resume_pdf_minimal(minimal_result):
    # No contact line, no summary/skills/education-extras/projects -> false branches.
    data = resume_pdf(minimal_result.resume)
    assert _is_pdf(data)


def test_resume_pdf_no_experience_or_education():
    # Empty experience AND education lists -> the outer false branches.
    resume = ResumeData(
        contact=ContactInfo(name="Jane"),
        professional_summary="",
        skills=[],
        experience=[],
        education=[],
        projects=[],
    )
    assert _is_pdf(resume_pdf(resume))


def test_cover_letter_pdf_full(full_result):
    data = cover_letter_pdf(full_result.resume.contact, full_result.cover_letter_body)
    assert _is_pdf(data)


def test_cover_letter_pdf_minimal():
    # Empty name and empty body -> header false branch + no paragraphs.
    data = cover_letter_pdf(ContactInfo(name=""), "")
    assert _is_pdf(data)
