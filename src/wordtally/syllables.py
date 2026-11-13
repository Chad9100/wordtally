"""Heuristic English syllable estimation."""

from __future__ import annotations

import re
import unicodedata

_VOWEL_GROUPS = re.compile(r"[aeiouy]+")

#: Syllable counts for common irregular English words that the vowel-group
#: heuristic gets wrong. Keys are lower-case ASCII, letters only.
SYLLABLE_EXCEPTIONS: dict[str, int] = {
    "area": 3,
    "business": 2,
    "create": 2,
    "idea": 3,
    "every": 2,
    "poem": 2,
    "quiet": 2,
    "science": 2,
    "video": 3,
    "really": 2,
    "different": 3,
    "evening": 2,
    "family": 3,
    "chocolate": 3,
    "comfortable": 3,
    "vegetable": 3,
    "literature": 4,
    "violence": 3,
    "variety": 4,
    "being": 2,
    "doing": 2,
    "going": 2,
    "seeing": 2,
    "lion": 2,
    "diet": 2,
    "poet": 2,
    "fuel": 2,
    "duel": 2,
}


def count_syllables(word: str) -> int:
    """Estimate the number of syllables in ``word``.

    Counts groups of consecutive vowels (``y`` included), then adjusts for a
    silent trailing ``e`` (``make``; ``table`` keeps its ``-le`` syllable) and
    a silent ``-ed`` (``jumped``; ``wanted`` keeps it). Accents are stripped
    first, so ``café`` counts like ``cafe``. Any word with letters has at
    least one syllable; a word with no letters has zero. Words in scripts
    other than Latin are counted as one syllable. Common irregular words are
    looked up in ``SYLLABLE_EXCEPTIONS`` first. This is still an estimate and
    is wrong for many other irregular English words.
    """
    letters = "".join(ch for ch in word.casefold() if ch.isalpha())
    if not letters:
        return 0
    w = "".join(
        ch for ch in unicodedata.normalize("NFKD", letters) if not unicodedata.combining(ch)
    )
    if not w.isascii():
        return 1
    if w in SYLLABLE_EXCEPTIONS:
        return SYLLABLE_EXCEPTIONS[w]
    count = len(_VOWEL_GROUPS.findall(w))
    if len(w) > 2 and w.endswith("e") and not w.endswith(("le", "ee", "ye")):
        count -= 1
    elif len(w) > 3 and w.endswith("le") and w[-3] in "aeiouy":
        count -= 1  # "whale": silent e after a vowel
    if len(w) > 3 and w.endswith("ed") and w[-3] not in "tdaeiouy":
        count -= 1
    return max(count, 1)
