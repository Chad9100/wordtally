"""Rule-based sentence splitting."""

from __future__ import annotations

import re

_ABBREVIATIONS = frozenset(
    "mr mrs ms dr prof sr jr st vs etc e.g i.e eg ie fig no inc ltd co".split()
)

# Terminator run, optional closing quotes/brackets, then whitespace.
_BOUNDARY_RE = re.compile(r"([.!?…]+[\"'”’)\]]*)(\s+)")
_PARAGRAPH_RE = re.compile(r"\n\s*\n")


def _is_abbreviation(chunk: str) -> bool:
    """True if ``chunk`` (text up to and including a '.') ends in an abbreviation."""
    if not chunk.endswith("."):
        return False
    last = chunk.rstrip(".").split()[-1].lower() if chunk.rstrip(".").split() else ""
    last = last.lstrip("(\"'“")
    if last in _ABBREVIATIONS:
        return True
    # Single-letter initials such as "J. R. R. Tolkien".
    return len(last) == 1 and last.isalpha()


def _split_paragraph(par: str) -> list[str]:
    sentences: list[str] = []
    start = 0
    for m in _BOUNDARY_RE.finditer(par):
        chunk = par[start : m.start(2)]
        if m.group(1) == "." and _is_abbreviation(chunk):
            continue
        sentences.append(chunk)
        start = m.end(2)
    sentences.append(par[start:])
    return sentences


def split_sentences(text: str) -> list[str]:
    """Split ``text`` into sentences.

    Boundaries are ``.``, ``!``, ``?`` or ``…`` followed by whitespace, plus
    blank lines between paragraphs. Common abbreviations (``Dr.``, ``e.g.``)
    and single-letter initials do not end a sentence. Text with no
    terminator is returned as a single sentence; empty text gives ``[]``.
    Whitespace inside sentences is collapsed.
    """
    result: list[str] = []
    for par in _PARAGRAPH_RE.split(text):
        for s in _split_paragraph(par):
            s = " ".join(s.split())
            if s:
                result.append(s)
    return result
