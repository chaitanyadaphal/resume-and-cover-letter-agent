# AI Resume & Cover Letter Generator

A Streamlit app that turns your details and a target job description into a **tailored
resume** and **personalized cover letter**, then **highlights missing skills** and
**suggests improvements**. Outputs are downloadable as **PDF**.

Powered by Claude (Anthropic) via structured outputs.

## Features

- Clean input forms for personal details, skills, experience, education, and the job description
- One-click generation of a job-tailored resume and cover letter
- Matched-skills / missing-skills gap analysis against the job description
- Actionable improvement suggestions
- Download the resume and cover letter as polished PDFs
- Switch between Claude Opus 4.8 (best) and Sonnet 4.6 (faster/cheaper) in the sidebar

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

3. Add your API key. Copy `.env.example` to `.env` and set your key
   (get one from <https://console.anthropic.com>):

   ```
   ANTHROPIC_API_KEY=your-key-here
   ```

## Run

```bash
streamlit run app.py
```

The app opens at <http://localhost:8501>. Fill in your details and the job
description, click **Generate**, then review the Resume, Cover Letter, and
Skills & Improvements tabs and download the PDFs.

## Project structure

The reusable logic lives in the `resume_agent` package; `app.py` is a thin Streamlit
UI layer on top of it.

```
app.py                     # Streamlit UI (presentation only)
resume_agent/
  __init__.py              # package exports
  models.py                # Pydantic schemas for the structured response
  text_utils.py            # PDF-safe text sanitizing, contact line, profile block
  generator.py             # Anthropic client call -> validated GenerationResult
  pdf_export.py            # resume / cover letter -> PDF bytes (fpdf2)
  app_logic.py             # model registry + input validation
tests/                     # pytest suite (100% line + branch coverage)
requirements.txt           # runtime dependencies
requirements-dev.txt       # + pytest, pytest-cov
pyproject.toml             # pytest + coverage config
```

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
