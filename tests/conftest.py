"""Shared fixtures for the test suite."""

from __future__ import annotations

import pytest

from resume_agent.models import (
    ContactInfo,
    EducationItem,
    ExperienceItem,
    GenerationResult,
    ResumeData,
    SkillAnalysis,
)


@pytest.fixture
def full_contact() -> ContactInfo:
    return ContactInfo(
        name="Jane Doe",
        email="jane@example.com",
        phone="555-1234",
        location="Berlin",
        links=["github.com/jane"],
    )


@pytest.fixture
def full_result(full_contact) -> GenerationResult:
    """A fully-populated result exercising every optional field."""
    return GenerationResult(
        resume=ResumeData(
            contact=full_contact,
            professional_summary="Engineer with “smart quotes”, an em—dash and a bullet • too.",
            skills=["Python", "SQL"],
            experience=[
                ExperienceItem(
                    role="Senior Dev",
                    company="Acme",
                    dates="2021 - Present",
                    bullets=["Built things", "Shipped more things"],
                )
            ],
            education=[EducationItem(degree="BSc CS", institution="Uni", year="2020")],
            projects=["A cool project"],
        ),
        cover_letter_body="First paragraph.\n\nSecond paragraph with résumé accent.",
        skill_analysis=SkillAnalysis(
            matched_skills=["Python"],
            missing_skills=["Kubernetes"],
            improvement_suggestions=["Learn Kubernetes"],
        ),
    )


@pytest.fixture
def minimal_result() -> GenerationResult:
    """A bare result where every optional field is empty (exercises the false branches)."""
    return GenerationResult(
        resume=ResumeData(
            contact=ContactInfo(name=""),  # no name, no contact details
            professional_summary="",
            skills=[],
            experience=[
                # an experience item with no company and no dates and no bullets
                ExperienceItem(role="Dev", company="", dates="", bullets=[]),
            ],
            education=[EducationItem(degree="Diploma", institution="", year="")],
            projects=[],
        ),
        cover_letter_body="",
        skill_analysis=SkillAnalysis(),
    )
