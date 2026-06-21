"""Tests for the pure text helpers."""

from __future__ import annotations

from resume_agent.models import ContactInfo
from resume_agent.text_utils import build_profile_text, clean, contact_line


def test_clean_empty_returns_empty():
    assert clean("") == ""


def test_clean_replaces_known_unicode():
    out = clean("“quote” — bullet • ’s…")
    assert out == '"quote" - bullet - \'s...'
    # round-trips cleanly through latin-1
    out.encode("latin-1")


def test_clean_replaces_unknown_unicode_with_placeholder():
    # An emoji has no mapping and is not latin-1 -> replaced, never raises.
    out = clean("hi 🚀 there")
    assert "hi " in out and " there" in out
    out.encode("latin-1")


def test_contact_line_full():
    c = ContactInfo(
        name="Jane", email="a@b.com", phone="555", location="Berlin", links=["gh/jane"]
    )
    assert contact_line(c) == "a@b.com  |  555  |  Berlin  |  gh/jane"


def test_contact_line_partial_skips_empty():
    c = ContactInfo(name="Jane", email="a@b.com", phone="", location="", links=["gh/jane"])
    assert contact_line(c) == "a@b.com  |  gh/jane"


def test_contact_line_empty():
    assert contact_line(ContactInfo(name="Jane")) == ""


def test_contact_line_custom_separator():
    c = ContactInfo(name="Jane", email="a@b.com", location="Berlin")
    assert contact_line(c, sep=" / ") == "a@b.com / Berlin"


def test_build_profile_text_contains_all_sections():
    text = build_profile_text(
        "Jane", "a@b.com", "555", "Berlin", "gh/jane", "Python", "Dev at Acme", "BSc",
        "Seasoned engineer",
    )
    for token in (
        "Name: Jane",
        "Email: a@b.com",
        "Professional summary:",
        "Seasoned engineer",
        "Skills:",
        "Python",
        "Experience:",
        "Education:",
    ):
        assert token in text


def test_build_profile_text_summary_defaults_empty():
    text = build_profile_text("Jane", "", "", "", "", "", "Dev", "BSc")
    assert "Professional summary:\n\n" in text
