"""Readability formulas.

With ``W`` words, ``S`` sentences, ``Y`` syllables and ``C`` complex words
(three or more estimated syllables):

* Flesch reading ease  = 206.835 - 1.015 * (W / S) - 84.6 * (Y / W)
* Flesch-Kincaid grade = 0.39 * (W / S) + 11.8 * (Y / W) - 15.59
* Gunning fog          = 0.4 * ((W / S) + 100 * (C / W))

With ``L`` letters (alphabetic characters in the words):

* SMOG grade           = 1.0430 * sqrt(C * (30 / S)) + 3.1291
* Coleman-Liau index   = 0.0588 * (100 * L / W) - 0.296 * (100 * S / W) - 15.8
* Automated readability index
                       = 4.71 * (L / W) + 0.5 * (W / S) - 21.43

All of them return ``0.0`` when there are no words or no sentences. Syllable
counts are estimates, so scores are approximate. SMOG is formally defined for
samples of 30 or more sentences; on short texts treat it as a rough figure.
"""

from __future__ import annotations

import math
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


def smog_grade(sentences: int, complex_words: int) -> float:
    """SMOG grade: US grade level from the density of complex words.

    ``complex_words`` is the count of words with three or more syllables.
    Returns ``0.0`` when ``sentences`` is not positive.
    """
    if sentences <= 0:
        return 0.0
    return 1.0430 * math.sqrt(complex_words * (30 / sentences)) + 3.1291


def coleman_liau_index(words: int, sentences: int, letters: int) -> float:
    """Coleman-Liau index: US grade level from letters per word, not syllables."""
    if words <= 0 or sentences <= 0:
        return 0.0
    return 0.0588 * (100 * letters / words) - 0.296 * (100 * sentences / words) - 15.8


def automated_readability_index(words: int, sentences: int, letters: int) -> float:
    """Automated readability index (ARI): US grade level from letters per word."""
    if words <= 0 or sentences <= 0:
        return 0.0
    return 4.71 * (letters / words) + 0.5 * (words / sentences) - 21.43


def letter_count(words: Sequence[str]) -> int:
    """Total alphabetic characters across ``words`` (apostrophes and hyphens excluded)."""
    return sum(1 for w in words for ch in w if ch.isalpha())


def syllable_total(words: Sequence[str]) -> int:
    """Total estimated syllables across ``words``."""
    return sum(count_syllables(w) for w in words)


def complex_word_count(words: Sequence[str]) -> int:
    """Number of words with three or more estimated syllables."""
    return sum(1 for w in words if count_syllables(w) >= 3)
