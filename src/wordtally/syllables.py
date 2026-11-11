"""Heuristic English syllable estimation."""

from __future__ import annotations

import re
import unicodedata

_VOWEL_GROUPS = re.compile(r"[aeiouy]+")


def count_syllables(word: str) -> int:
    """Estimate the number of syllables in ``word``.

    Counts groups of consecutive vowels (``y`` included), then adjusts for a
    silent trailing ``e`` (``make``; ``table`` keeps its ``-le`` syllable) and
    a silent ``-ed`` (``jumped``; ``wanted`` keeps it). Accents are stripped
    first, so ``café`` counts like ``cafe``. Any word with letters has at
    least one syllable; a word with no letters has zero. Words in scripts
    other than Latin are counted as one syllable. This is an estimate and is
    wrong for many irregular English words.
    """
    letters = "".join(ch for ch in word.casefold() if ch.isalpha())
    if not letters:
        return 0
    w = "".join(
        ch for ch in unicodedata.normalize("NFKD", letters) if not unicodedata.combining(ch)
    )
    if not w.isascii():
        return 1
    count = len(_VOWEL_GROUPS.findall(w))
    if len(w) > 2 and w.endswith("e") and not w.endswith(("le", "ee", "ye")):
        count -= 1
    elif len(w) > 3 and w.endswith("le") and w[-3] in "aeiouy":
        count -= 1  # "whale": silent e after a vowel
    if len(w) > 3 and w.endswith("ed") and w[-3] not in "tdaeiouy":
        count -= 1
    return max(count, 1)
