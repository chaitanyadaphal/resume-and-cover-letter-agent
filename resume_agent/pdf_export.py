"""Render generated content into clean, print-ready PDFs using fpdf2 (pure Python)."""

from __future__ import annotations

from datetime import date

from fpdf import FPDF

from .models import ContactInfo, ResumeData
from .text_utils import clean, contact_line


class _PDF(FPDF):
    def section_title(self, title: str) -> None:
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(20, 40, 90)
        self.cell(0, 8, clean(title.upper()), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(20, 40, 90)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def body_text(self, text: str, size: int = 10, style: str = "") -> None:
        self.set_font("Helvetica", style, size)
        self.multi_cell(0, 5, clean(text), new_x="LMARGIN", new_y="NEXT")

    def bullet(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        x = self.get_x()
        self.cell(5, 5, "-")
        self.multi_cell(0, 5, clean(text), new_x="LMARGIN", new_y="NEXT")
        self.set_x(x)


def _header(pdf: _PDF, contact: ContactInfo, name_size: int) -> None:
    pdf.set_font("Helvetica", "B", name_size)
    pdf.cell(0, 10, clean(contact.name or ""), new_x="LMARGIN", new_y="NEXT")
    line = contact_line(contact)
    if line:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 5, clean(line), new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)


def _new_pdf() -> _PDF:
    pdf = _PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    return pdf


def resume_pdf(resume: ResumeData) -> bytes:
    pdf = _new_pdf()
    _header(pdf, resume.contact, name_size=20)
    pdf.ln(3)

    if resume.professional_summary:
        pdf.section_title("Summary")
        pdf.body_text(resume.professional_summary)
        pdf.ln(2)

    if resume.skills:
        pdf.section_title("Skills")
        pdf.body_text(", ".join(resume.skills))
        pdf.ln(2)

    if resume.experience:
        pdf.section_title("Experience")
        for item in resume.experience:
            header = item.role + (f" - {item.company}" if item.company else "")
            pdf.body_text(header, size=11, style="B")
            if item.dates:
                pdf.set_text_color(110, 110, 110)
                pdf.body_text(item.dates, size=9, style="I")
                pdf.set_text_color(0, 0, 0)
            for b in item.bullets:
                pdf.bullet(b)
            pdf.ln(2)

    if resume.education:
        pdf.section_title("Education")
        for edu in resume.education:
            line = edu.degree + (f" - {edu.institution}" if edu.institution else "")
            line += f" ({edu.year})" if edu.year else ""
            pdf.body_text(line)
        pdf.ln(2)

    if resume.projects:
        pdf.section_title("Projects")
        for proj in resume.projects:
            pdf.bullet(proj)

    return bytes(pdf.output())


def cover_letter_pdf(contact: ContactInfo, body: str) -> bytes:
    pdf = _new_pdf()
    _header(pdf, contact, name_size=14)
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, clean(date.today().strftime("%B %d, %Y")), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.body_text("Dear Hiring Manager,")
    pdf.ln(2)

    for para in [p for p in body.split("\n") if p.strip()]:
        pdf.body_text(para.strip())
        pdf.ln(2)

    pdf.ln(2)
    pdf.body_text("Sincerely,")
    pdf.body_text(contact.name or "")

    return bytes(pdf.output())
