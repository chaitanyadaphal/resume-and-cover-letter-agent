# AI Resume & Cover Letter Generator

A Streamlit app that turns your details and a target job description into a **tailored
resume** and **personalized cover letter**, then **highlights missing skills** and
**suggests improvements**. Outputs are downloadable as **PDF**.

Works with **Anthropic (Claude)**, **OpenAI (GPT)**, or **DeepSeek** — pick a provider
and model in the sidebar.

## Features

- Choose your LLM provider/model: Anthropic, OpenAI, or DeepSeek
- **Import an existing resume** (PDF or DOCX): the app extracts your details into the
  form for review/editing before generating
- Clean input forms for personal details, summary, skills, experience, education
- One-click generation of a job-tailored resume and cover letter
- Matched-skills / missing-skills gap analysis against the job description
- Actionable improvement suggestions
- Download the resume and cover letter as polished PDFs

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add an API key for whichever provider(s) you'll use. Copy `.env.example` to `.env`
   and set the relevant key(s) — you only need the one for the provider you select:

   ```
   ANTHROPIC_API_KEY=...   # https://console.anthropic.com
   OPENAI_API_KEY=...      # https://platform.openai.com/api-keys
   DEEPSEEK_API_KEY=...    # https://platform.deepseek.com/api_keys
   ```

## Run

```bash
streamlit run app.py
```

The app opens at <http://localhost:8501>. In the sidebar, pick a **provider** and
**model**. Optionally expand **Import from an existing resume** to upload a PDF/DOCX and
auto-fill the form, then review/edit the fields. Paste the job description, click
**Generate**, and review the Resume, Cover Letter, and Skills & Improvements tabs —
then download the PDFs.

## Project structure

The reusable logic lives in the `resume_agent` package; `app.py` is a thin Streamlit
UI layer on top of it.

```
app.py                     # Streamlit UI (presentation only)
resume_agent/
  __init__.py              # package exports
  models.py                # Pydantic schemas (incl. ExtractedProfile)
  text_utils.py            # PDF-safe text sanitizing, contact line, profile block
  providers.py             # Anthropic/OpenAI/DeepSeek structured-output calls
  generator.py             # tailored resume + cover letter -> GenerationResult
  extract.py               # PDF/DOCX text extraction + profile structuring
  pdf_export.py            # resume / cover letter -> PDF bytes (fpdf2)
  app_logic.py             # provider registry + input/key validation
tests/                     # pytest suite (100% line + branch coverage)
requirements.txt           # runtime dependencies
requirements-dev.txt       # + pytest, pytest-cov
pyproject.toml             # pytest + coverage config
```

All providers go through one abstraction (`providers.complete_structured`), used by
both generation and resume extraction.

## Tests

The `resume_agent` package is covered by a unit-test suite enforcing **100% line and
branch coverage** (the Anthropic client is mocked, so no network or API key is needed
to run the tests). `app.py` is the thin UI entry point and is intentionally outside
the coverage scope.

```bash
pip install -r requirements-dev.txt
pytest
```

Coverage settings live in `pyproject.toml` (`--cov=resume_agent --cov-branch
--cov-fail-under=100`); the run fails if coverage drops below 100%.

## Notes

- The model is instructed to ground all content in your real input and not fabricate
  experience. Always review the output before sending.
- Your key is read from the environment; nothing is hardcoded or stored.
