"""Lexical diversity metrics: type-token ratio, hapax legomena and MTLD."""

from __future__ import annotations

from collections import Counter
from collections.abc import Collection

from .tokenize import tokenize


def type_token_ratio(text: str, *, stopwords: Collection[str] | None = None) -> float:
    """Unique words divided by total words (``0.0`` for empty input).

    The ratio falls as texts get longer, so only compare texts of similar
    length; use :func:`mtld` for a length-robust measure.
    """
    tokens = tokenize(text, stopwords=stopwords)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def hapax_legomena(text: str, *, stopwords: Collection[str] | None = None) -> tuple[str, ...]:
    """Words that occur exactly once, in order of first appearance."""
    tokens = tokenize(text, stopwords=stopwords)
    counts = Counter(tokens)
    return tuple(w for w in dict.fromkeys(tokens) if counts[w] == 1)


def _mtld_pass(tokens: list[str], threshold: float) -> float:
    """Mean factor length for one reading direction."""
    factors = 0.0
    seen: set[str] = set()
    length = 0
    for tok in tokens:
        seen.add(tok)
        length += 1
        if len(seen) / length <= threshold:
            factors += 1
            seen = set()
            length = 0
    if length:
        ttr = len(seen) / length
        factors += (1 - ttr) / (1 - threshold)
    if factors == 0:
        # TTR never dropped to the threshold: the text is at least this diverse.
        return float(len(tokens))
    return len(tokens) / factors


def mtld(
    text: str,
    *,
    threshold: float = 0.72,
    stopwords: Collection[str] | None = None,
) -> float:
    """Measure of Textual Lexical Diversity (McCarthy and Jarvis, 2010).

    Words are read in order while a running type-token ratio is kept; each
    time it falls to ``threshold`` one "factor" is counted and the ratio
    resets. A trailing partial factor counts fractionally. MTLD is the
    token count divided by the factor count, averaged over a forward and a
    backward pass. Higher means more diverse. Returns ``0.0`` for empty
    input; if the ratio never reaches the threshold in a pass, that pass
    contributes the token count.

    Raises:
        ValueError: if ``threshold`` is not strictly between 0 and 1.
    """
    if not 0 < threshold < 1:
        raise ValueError("threshold must be between 0 and 1 (exclusive)")
    tokens = tokenize(text, stopwords=stopwords)
    if not tokens:
        return 0.0
    forward = _mtld_pass(tokens, threshold)
    backward = _mtld_pass(tokens[::-1], threshold)
    return (forward + backward) / 2
