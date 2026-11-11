"""Rule-based sentence splitting."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .tokenize import tokenize

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


@dataclass(frozen=True)
class SentenceStats:
    """Sentence length statistics; lengths are measured in words."""

    count: int
    mean_words: float
    shortest: str
    shortest_words: int
    longest: str
    longest_words: int
    long_threshold: int
    long_sentences: tuple[str, ...]
    histogram: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        """A JSON-serialisable dict of the statistics."""
        return {
            "count": self.count,
            "mean_words": self.mean_words,
            "shortest": self.shortest,
            "shortest_words": self.shortest_words,
            "longest": self.longest,
            "longest_words": self.longest_words,
            "long_threshold": self.long_threshold,
            "long_sentences": list(self.long_sentences),
            "histogram": dict(self.histogram),
        }

    def to_text(self) -> str:
        """The statistics as a plain-text block."""
        lines = [
            f"Sentences:               {self.count}",
            f"Mean length (words):     {self.mean_words}",
            f"Shortest sentence:       {self.shortest} ({self.shortest_words} words)",
            f"Longest sentence:        {self.longest} ({self.longest_words} words)",
            f"Over {self.long_threshold} words:".ljust(25) + str(len(self.long_sentences)),
            "Length histogram (words):",
        ]
        width = max((len(k) for k in self.histogram), default=0)
        lines += [f"  {k.rjust(width)}  {'#' * v} {v}" for k, v in self.histogram.items()]
        return "\n".join(lines) + "\n"


def sentence_stats(
    text: str, *, long_threshold: int = 30, bin_width: int = 5
) -> SentenceStats | None:
    """Longest/shortest sentence, a length histogram and over-long sentences.

    Length is the number of :func:`~wordtally.tokenize.tokenize` words.
    Sentences with no words (for example ``"..."``) are ignored. Sentences
    with more than ``long_threshold`` words are listed in ``long_sentences``.
    The histogram groups lengths into bins of ``bin_width`` words
    (``"1-5"``, ``"6-10"``, ...), omitting empty bins. Ties for shortest or
    longest go to the first sentence. Returns ``None`` if there are no
    sentences with words. Raises ``ValueError`` for non-positive arguments.
    """
    if long_threshold < 1 or bin_width < 1:
        raise ValueError("long_threshold and bin_width must be >= 1")
    measured = [(s, len(tokenize(s))) for s in split_sentences(text)]
    measured = [(s, n) for s, n in measured if n > 0]
    if not measured:
        return None
    shortest = min(measured, key=lambda p: p[1])
    longest = max(measured, key=lambda p: p[1])
    bins: dict[int, int] = {}
    for _, n in measured:
        b = (n - 1) // bin_width
        bins[b] = bins.get(b, 0) + 1
    histogram = {
        f"{b * bin_width + 1}-{(b + 1) * bin_width}": bins[b] for b in sorted(bins)
    }
    return SentenceStats(
        count=len(measured),
        mean_words=round(sum(n for _, n in measured) / len(measured), 2),
        shortest=shortest[0],
        shortest_words=shortest[1],
        longest=longest[0],
        longest_words=longest[1],
        long_threshold=long_threshold,
        long_sentences=tuple(s for s, n in measured if n > long_threshold),
        histogram=histogram,
    )
