"""Repeated n-gram (phrase) finder."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from .tokenize import tokenize


@dataclass(frozen=True)
class Phrase:
    """A repeated phrase and how often it occurs."""

    text: str
    n: int
    count: int


def repeated_ngrams(
    text: str,
    *,
    min_n: int = 2,
    max_n: int = 4,
    min_count: int = 2,
    stopwords: Iterable[str] | None = None,
    top: int | None = None,
) -> list[Phrase]:
    """Find word sequences that occur at least ``min_count`` times.

    N-grams from ``min_n`` to ``max_n`` words are counted over the
    lowercased token stream (stopwords, if given, are removed first, which
    makes the remaining words adjacent). A phrase is dropped when a longer
    phrase that contains it occurs the same number of times, so
    "the quick brown fox" repeated twice is reported once, not as every
    sub-phrase. Results are sorted by count, then length, then text.
    """
    if min_n < 1 or max_n < min_n:
        raise ValueError("need 1 <= min_n <= max_n")
    if min_count < 2:
        raise ValueError("min_count must be at least 2")
    tokens = tokenize(text, stopwords=stopwords)
    found: dict[tuple[str, ...], int] = {}
    for n in range(min_n, max_n + 1):
        counts = Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))
        found.update({g: c for g, c in counts.items() if c >= min_count})

    def covered(gram: tuple[str, ...], count: int) -> bool:
        n = len(gram)
        for other, c in found.items():
            if len(other) > n and c == count:
                if any(other[i : i + n] == gram for i in range(len(other) - n + 1)):
                    return True
        return False

    phrases = [
        Phrase(" ".join(g), len(g), c) for g, c in found.items() if not covered(g, c)
    ]
    phrases.sort(key=lambda p: (-p.count, -p.n, p.text))
    return phrases if top is None else phrases[: max(top, 0)]
