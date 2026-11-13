"""RAKE-style keyword extraction (Rapid Automatic Keyword Extraction)."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from .tokenize import ENGLISH_STOPWORDS, tokenize

# Characters that end a candidate phrase: anything that is not a letter,
# whitespace, apostrophe or hyphen, digit runs, blank lines and spaced dashes.
_BOUNDARY_RE = re.compile(r"[^\s\w'’-]+|[\d_]+|\n\s*\n|\s-+\s")


@dataclass(frozen=True)
class Keyword:
    """A candidate keyword phrase with its RAKE score and occurrence count."""

    text: str
    score: float
    count: int


def extract_keywords(
    text: str,
    *,
    stopwords: Iterable[str] | None = ENGLISH_STOPWORDS,
    max_words: int = 3,
    top: int | None = None,
) -> list[Keyword]:
    """Rank keyword phrases with RAKE.

    The text is cut into candidate phrases at punctuation, digits and
    stopwords. Each word scores ``degree / frequency``, where frequency is
    how often it appears in candidates and degree is the total length of the
    candidates it appears in (so words that sit in long phrases score high).
    A phrase scores the sum of its word scores. Results are sorted by score,
    then count, then text.

    Args:
        text: The text to analyze.
        stopwords: Words that split phrases (default: English stopwords).
        max_words: Drop candidate phrases longer than this many words.
        top: Return only the ``top`` best keywords.
    """
    if max_words < 1:
        raise ValueError("max_words must be at least 1")
    stop = {s.casefold() for s in (stopwords or ())}
    candidates: list[tuple[str, ...]] = []
    for segment in _BOUNDARY_RE.split(text):
        run: list[str] = []
        for word in [*tokenize(segment), None]:
            if word is not None and word not in stop:
                run.append(word)
            elif run:
                candidates.append(tuple(run))
                run = []
    freq: Counter[str] = Counter()
    degree: Counter[str] = Counter()
    for cand in candidates:
        for word in cand:
            freq[word] += 1
            degree[word] += len(cand)
    counts = Counter(c for c in candidates if len(c) <= max_words)
    result = [
        Keyword(" ".join(c), round(sum(degree[w] / freq[w] for w in c), 2), n)
        for c, n in counts.items()
    ]
    result.sort(key=lambda k: (-k.score, -k.count, k.text))
    return result if top is None else result[: max(top, 0)]
