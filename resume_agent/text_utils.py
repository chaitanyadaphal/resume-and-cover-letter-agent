"""Pure text helpers shared by the UI and the PDF exporter.

Kept free of Streamlit / fpdf imports so they are trivially unit-testable.
"""

from __future__ import annotations

from .models import ContactInfo

# fpdf2's core fonts are Latin-1 only. Map common Unicode the model might emit
# (smart quotes, dashes, bullets) to safe ASCII equivalents.
_REPLACEMENTS = {
    "‘": "'", "’": "'",   # ' '
    "“": '"', "”": '"',   # " "
    "–": "-", "—": "-",   # – —
    "•": "-", "…": "...",  # • …
    " ": " ", "−": "-",   # nbsp −
}


def clean(text: str) -> str:
    """Return a Latin-1-safe version of ``text`` for PDF rendering."""
    if not text:
        return ""
    for bad, good in _REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text.encode("latin-1", "replace").decode("latin-1")


def contact_line(contact: ContactInfo, sep: str = "  |  ") -> str:
    """Join the non-empty contact fields into a single line."""
    parts = [contact.email, contact.phone, contact.location, *contact.links]
    return sep.join(p for p in parts if p)


def build_profile_text(
    name: str,
    email: str,
    phone: str,
    location: str,
    links: str,
    skills: str,
    experience: str,
    education: str,
) -> str:
    """Combine the structured form inputs into one block for the model prompt."""
    return (
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n"
        f"Location: {location}\n"
        f"Links: {links}\n\n"
        f"Skills:\n{skills}\n\n"
        f"Experience:\n{experience}\n\n"
        f"Education:\n{education}"
    )
