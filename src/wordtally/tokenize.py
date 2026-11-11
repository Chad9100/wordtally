"""Unicode-aware word tokenizer and word frequency counting."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable

# A word is a run of letters (any script), optionally joined by internal
# apostrophes or hyphens: "don't", "well-known", "l'été". Digits and
# underscores are not word characters here.
_WORD_RE = re.compile(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*")

ENGLISH_STOPWORDS: frozenset[str] = frozenset(
    """
    a about above after again against all am an and any are as at be because
    been before being below between both but by can did do does doing down
    during each few for from further had has have having he her here hers
    herself him himself his how i if in into is it its itself just me more
    most my myself no nor not now of off on once only or other our ours
    ourselves out over own same she should so some such than that the their
    theirs them themselves then there these they this those through to too
    under until up very was we were what when where which while who whom why
    will with you your yours yourself yourselves
    """.split()
)


def tokenize(
    text: str,
    *,
    lowercase: bool = True,
    stopwords: Iterable[str] | None = None,
) -> list[str]:
    """Split ``text`` into word tokens.

    Words are runs of letters from any script, with optional internal
    apostrophes or hyphens. Numbers and punctuation are dropped.

    Args:
        text: The text to tokenize.
        lowercase: Casefold tokens (default). Stopword matching is always
            case-insensitive.
        stopwords: Words to remove, e.g. :data:`ENGLISH_STOPWORDS`.
    """
    tokens = [m.group(0).replace("’", "'") for m in _WORD_RE.finditer(text)]
    if stopwords is not None:
        stop = {s.casefold() for s in stopwords}
        tokens = [t for t in tokens if t.casefold() not in stop]
    if lowercase:
        tokens = [t.casefold() for t in tokens]
    return tokens


def word_frequency(
    text: str,
    *,
    stopwords: Iterable[str] | None = None,
    top: int | None = None,
) -> list[tuple[str, int]]:
    """Count words, most frequent first (ties broken alphabetically).

    Args:
        text: The text to count.
        stopwords: Words to ignore.
        top: Return only the ``top`` most frequent words.
    """
    counts = Counter(tokenize(text, stopwords=stopwords))
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked if top is None else ranked[: max(top, 0)]
