"""Streamlit UI for the AI-powered resume & cover letter generator.

This file is the thin presentation layer only — all reusable logic lives in the
``resume_agent`` package (which is what the test suite covers).
"""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from resume_agent.app_logic import MODELS, validate_inputs
from resume_agent.generator import GenerationError, generate
from resume_agent.models import GenerationResult
from resume_agent.pdf_export import cover_letter_pdf, resume_pdf
from resume_agent.text_utils import build_profile_text

load_dotenv()

st.set_page_config(page_title="AI Resume & Cover Letter Generator", page_icon="📄", layout="wide")


def _render_resume(result: GenerationResult) -> None:
    r = result.resume
    st.subheader(r.contact.name or "Tailored Resume")
    contact_bits = [r.contact.email, r.contact.phone, r.contact.location, *r.contact.links]
    line = "  •  ".join(b for b in contact_bits if b)
    if line:
        st.caption(line)

    if r.professional_summary:
        st.markdown("**Summary**")
        st.write(r.professional_summary)

    if r.skills:
        st.markdown("**Skills**")
        st.write(", ".join(r.skills))

    if r.experience:
        st.markdown("**Experience**")
        for item in r.experience:
            header = item.role + (f" — {item.company}" if item.company else "")
            st.markdown(f"**{header}**")
            if item.dates:
                st.caption(item.dates)
            for b in item.bullets:
                st.markdown(f"- {b}")

    if r.education:
        st.markdown("**Education**")
        for edu in r.education:
            edu_line = edu.degree + (f" — {edu.institution}" if edu.institution else "")
            edu_line += f" ({edu.year})" if edu.year else ""
            st.markdown(f"- {edu_line}")

    if r.projects:
        st.markdown("**Projects**")
        for proj in r.projects:
            st.markdown(f"- {proj}")


def _render_results(result: GenerationResult) -> None:
    resume_bytes = resume_pdf(result.resume)
    cover_bytes = cover_letter_pdf(result.resume.contact, result.cover_letter_body)
    safe_name = (result.resume.contact.name or "candidate").replace(" ", "_")

    tab_resume, tab_cover, tab_skills = st.tabs(
        ["📄 Resume", "✉️ Cover Letter", "🎯 Skills & Improvements"]
    )

    with tab_resume:
        st.download_button(
            "⬇️ Download Resume PDF",
            data=resume_bytes,
            file_name=f"{safe_name}_resume.pdf",
            mime="application/pdf",
            type="primary",
        )
        st.divider()
        _render_resume(result)

    with tab_cover:
        st.download_button(
            "⬇️ Download Cover Letter PDF",
            data=cover_bytes,
            file_name=f"{safe_name}_cover_letter.pdf",
            mime="application/pdf",
            type="primary",
        )
        st.divider()
        st.write("Dear Hiring Manager,")
        for para in [p for p in result.cover_letter_body.split("\n") if p.strip()]:
            st.write(para.strip())
        st.write("Sincerely,")
        st.write(result.resume.contact.name or "")

    with tab_skills:
        analysis = result.skill_analysis
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ✅ Matched skills")
            if analysis.matched_skills:
                for s in analysis.matched_skills:
                    st.success(s)
            else:
                st.caption("No clearly matched skills found.")
        with col2:
            st.markdown("#### ⚠️ Missing skills")
            if analysis.missing_skills:
                for s in analysis.missing_skills:
                    st.warning(s)
            else:
                st.caption("No obvious gaps — nice!")

        st.markdown("#### 💡 Suggested improvements")
        if analysis.improvement_suggestions:
            for s in analysis.improvement_suggestions:
                st.markdown(f"- {s}")
        else:
            st.caption("No suggestions provided.")


def main() -> None:
    st.title("📄 AI Resume & Cover Letter Generator")
    st.write(
        "Enter your details and a target job description. The app tailors a resume and "
        "cover letter for that specific role, highlights skill gaps, and suggests "
        "improvements."
    )

    with st.sidebar:
        st.header("Settings")
        model_label = st.selectbox("Model", list(MODELS.keys()), index=0)
        model = MODELS[model_label]
        st.caption("Set ANTHROPIC_API_KEY in your environment or a .env file.")

    key_present = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if not key_present:
        st.error(
            "**ANTHROPIC_API_KEY is not set.** Create a `.env` file with "
            "`ANTHROPIC_API_KEY=your-key-here` (get a key from "
            "https://console.anthropic.com) and restart the app."
        )

    with st.form("inputs"):
        st.subheader("1. Your details")
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Full name")
        email = c2.text_input("Email")
        phone = c3.text_input("Phone")
        c4, c5 = st.columns(2)
        location = c4.text_input("Location")
        links = c5.text_input("Links (LinkedIn, GitHub, portfolio)")

        skills = st.text_area("Skills", placeholder="Python, SQL, project management, ...", height=80)
        experience = st.text_area(
            "Work experience",
            placeholder="Role, company, dates, and what you did. One job per block.",
            height=160,
        )
        education = st.text_area("Education", placeholder="Degree, institution, year", height=80)

        st.subheader("2. Target job")
        job_description = st.text_area(
            "Paste the job description", placeholder="The role you're applying for...", height=200
        )

        submitted = st.form_submit_button("✨ Generate", type="primary", disabled=not key_present)

    if submitted:
        error = validate_inputs(name, experience, job_description)
        if error:
            st.error(error)
        else:
            profile = build_profile_text(
                name, email, phone, location, links, skills, experience, education
            )
            with st.spinner("Tailoring your resume and cover letter..."):
                try:
                    st.session_state["result"] = generate(profile, job_description, model=model)
                except GenerationError as exc:
                    st.session_state.pop("result", None)
                    st.error(str(exc))

    if "result" in st.session_state:
        st.divider()
        _render_results(st.session_state["result"])


if __name__ == "__main__":
    main()
