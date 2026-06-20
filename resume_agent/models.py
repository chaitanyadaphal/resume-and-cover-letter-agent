"""Pydantic schemas for the structured Claude response.

A single `GenerationResult` carries the tailored resume, the cover letter body, and
the skill-gap analysis so the UI and PDF exporter render typed data deterministically.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: str = Field(default="", description="Email address, or empty if not given")
    phone: str = Field(default="", description="Phone number, or empty if not given")
    location: str = Field(default="", description="City/region, or empty if not given")
    links: List[str] = Field(
        default_factory=list,
        description="Relevant URLs (LinkedIn, GitHub, portfolio). Empty if none.",
    )


class ExperienceItem(BaseModel):
    role: str = Field(description="Job title")
    company: str = Field(description="Company/organization name")
    dates: str = Field(default="", description="Date range, e.g. 'Jan 2021 - Present'")
    bullets: List[str] = Field(
        default_factory=list,
        description="Achievement-focused bullet points tailored to the target job.",
    )


class EducationItem(BaseModel):
    degree: str = Field(description="Degree or qualification")
    institution: str = Field(description="School/university name")
    year: str = Field(default="", description="Graduation year or range")


class ResumeData(BaseModel):
    contact: ContactInfo
    professional_summary: str = Field(
        description="2-4 sentence summary tailored to the target job."
    )
    skills: List[str] = Field(
        default_factory=list,
        description="Skills relevant to the target job, ordered by relevance.",
    )
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[str] = Field(
        default_factory=list,
        description="Short one-line descriptions of relevant projects. Empty if none.",
    )


class SkillAnalysis(BaseModel):
    matched_skills: List[str] = Field(
        default_factory=list,
        description="Skills the candidate already has that the job asks for.",
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Skills the job asks for that the candidate appears to lack.",
    )
    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="Concrete, actionable suggestions to strengthen the application.",
    )


class GenerationResult(BaseModel):
    resume: ResumeData
    cover_letter_body: str = Field(
        description=(
            "The body of the cover letter only (no contact header, date, or signature "
            "block). Several short paragraphs, personalized to the job."
        )
    )
    skill_analysis: SkillAnalysis
