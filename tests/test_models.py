"""Tests for the Pydantic schema defaults and structure."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from resume_agent.models import (
    ContactInfo,
    EducationItem,
    ExperienceItem,
    ExtractedProfile,
    GenerationResult,
    ResumeData,
    SkillAnalysis,
)


def test_extracted_profile_defaults():
    p = ExtractedProfile()
    assert (
        p.name == p.email == p.phone == p.location == p.links
        == p.summary == p.skills == p.experience == p.education == ""
    )


def test_contact_defaults():
    c = ContactInfo(name="Jane")
    assert c.email == "" and c.phone == "" and c.location == ""
    assert c.links == []


def test_experience_defaults():
    e = ExperienceItem(role="Dev", company="Acme")
    assert e.dates == ""
    assert e.bullets == []


def test_education_defaults():
    edu = EducationItem(degree="BSc", institution="Uni")
    assert edu.year == ""


def test_resume_defaults():
    r = ResumeData(contact=ContactInfo(name="Jane"), professional_summary="Hi")
    assert r.skills == []
    assert r.experience == []
    assert r.education == []
    assert r.projects == []


def test_skill_analysis_defaults():
    s = SkillAnalysis()
    assert s.matched_skills == []
    assert s.missing_skills == []
    assert s.improvement_suggestions == []


def test_generation_result_roundtrip(full_result):
    dumped = full_result.model_dump()
    rebuilt = GenerationResult(**dumped)
    assert rebuilt == full_result


def test_missing_required_field_raises():
    with pytest.raises(ValidationError):
        ResumeData(contact=ContactInfo(name="Jane"))  # missing professional_summary
