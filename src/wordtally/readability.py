"""Readability formulas.

With ``W`` words, ``S`` sentences, ``Y`` syllables and ``C`` complex words
(three or more estimated syllables):

* Flesch reading ease  = 206.835 - 1.015 * (W / S) - 84.6 * (Y / W)
* Flesch-Kincaid grade = 0.39 * (W / S) + 11.8 * (Y / W) - 15.59
* Gunning fog          = 0.4 * ((W / S) + 100 * (C / W))

All three return ``0.0`` when there are no words or no sentences. Syllable
counts are estimates, so scores are approximate.
"""

from __future__ import annotations

from collections.abc import Sequence

from .syllables import count_syllables


def flesch_reading_ease(words: int, sentences: int, syllables: int) -> float:
    """Flesch reading ease: higher is easier (60-70 is plain English)."""
    if words <= 0 or sentences <= 0:
        return 0.0
    return 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)


def flesch_kincaid_grade(words: int, sentences: int, syllables: int) -> float:
    """Flesch-Kincaid grade: approximate US school grade level."""
    if words <= 0 or sentences <= 0:
        return 0.0
    return 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59


def gunning_fog(words: int, sentences: int, complex_words: int) -> float:
    """Gunning fog index: years of formal education needed to read the text."""
    if words <= 0 or sentences <= 0:
        return 0.0
    return 0.4 * ((words / sentences) + 100 * (complex_words / words))


def syllable_total(words: Sequence[str]) -> int:
    """Total estimated syllables across ``words``."""
    return sum(count_syllables(w) for w in words)


def complex_word_count(words: Sequence[str]) -> int:
    """Number of words with three or more estimated syllables."""
    return sum(1 for w in words if count_syllables(w) >= 3)
