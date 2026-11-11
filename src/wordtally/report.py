"""The :func:`analyze` entry point and its :class:`Report` dataclass."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from . import readability
from .ngrams import Phrase, repeated_ngrams
from .sentences import split_sentences
from .tokenize import tokenize, word_frequency


@dataclass(frozen=True)
class Report:
    """Result of :func:`analyze`.

    Counts and readability use every word (including SMOG, Coleman-Liau and
    the automated readability index; SMOG is rough on short texts);
    ``top_words`` and
    ``repeated_phrases`` honour the ``stopwords`` passed to ``analyze``.
    """

    characters: int
    words: int
    unique_words: int
    sentences: int
    syllables: int
    complex_words: int
    avg_words_per_sentence: float
    avg_syllables_per_word: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    gunning_fog: float
    smog_grade: float
    coleman_liau_index: float
    automated_readability_index: float
    top_words: tuple[tuple[str, int], ...]
    repeated_phrases: tuple[Phrase, ...]

    def to_dict(self) -> dict[str, Any]:
        """Plain-data form of the report (floats rounded to 2 places)."""
        return {
            "characters": self.characters,
            "words": self.words,
            "unique_words": self.unique_words,
            "sentences": self.sentences,
            "syllables": self.syllables,
            "complex_words": self.complex_words,
            "avg_words_per_sentence": round(self.avg_words_per_sentence, 2),
            "avg_syllables_per_word": round(self.avg_syllables_per_word, 2),
            "flesch_reading_ease": round(self.flesch_reading_ease, 2),
            "flesch_kincaid_grade": round(self.flesch_kincaid_grade, 2),
            "gunning_fog": round(self.gunning_fog, 2),
            "smog_grade": round(self.smog_grade, 2),
            "coleman_liau_index": round(self.coleman_liau_index, 2),
            "automated_readability_index": round(self.automated_readability_index, 2),
            "top_words": [{"word": w, "count": c} for w, c in self.top_words],
            "repeated_phrases": [
                {"phrase": p.text, "words": p.n, "count": p.count}
                for p in self.repeated_phrases
            ],
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        """The report as a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_text(self) -> str:
        """The report as plain text."""
        d = self.to_dict()
        lines = [
            f"Characters:              {d['characters']}",
            f"Words:                   {d['words']} ({d['unique_words']} unique)",
            f"Sentences:               {d['sentences']}",
            f"Syllables:               {d['syllables']}",
            f"Complex words:           {d['complex_words']}",
            f"Words per sentence:      {d['avg_words_per_sentence']:.2f}",
            f"Syllables per word:      {d['avg_syllables_per_word']:.2f}",
            f"Flesch reading ease:     {d['flesch_reading_ease']:.2f}",
            f"Flesch-Kincaid grade:    {d['flesch_kincaid_grade']:.2f}",
            f"Gunning fog:             {d['gunning_fog']:.2f}",
            f"SMOG grade:              {d['smog_grade']:.2f}",
            f"Coleman-Liau index:      {d['coleman_liau_index']:.2f}",
            f"Automated readability:   {d['automated_readability_index']:.2f}",
        ]
        if self.top_words:
            lines += ["", "Top words:"]
            lines += [f"  {c:>4}  {w}" for w, c in self.top_words]
        if self.repeated_phrases:
            lines += ["", "Repeated phrases:"]
            lines += [f"  {p.count:>4}x  {p.text}" for p in self.repeated_phrases]
        return "\n".join(lines) + "\n"

    def to_markdown(self) -> str:
        """The report as Markdown tables."""
        d = self.to_dict()
        rows = [
            ("Characters", d["characters"]),
            ("Words", d["words"]),
            ("Unique words", d["unique_words"]),
            ("Sentences", d["sentences"]),
            ("Syllables", d["syllables"]),
            ("Complex words", d["complex_words"]),
            ("Words per sentence", f"{d['avg_words_per_sentence']:.2f}"),
            ("Syllables per word", f"{d['avg_syllables_per_word']:.2f}"),
            ("Flesch reading ease", f"{d['flesch_reading_ease']:.2f}"),
            ("Flesch-Kincaid grade", f"{d['flesch_kincaid_grade']:.2f}"),
            ("Gunning fog", f"{d['gunning_fog']:.2f}"),
            ("SMOG grade", f"{d['smog_grade']:.2f}"),
            ("Coleman-Liau index", f"{d['coleman_liau_index']:.2f}"),
            ("Automated readability index", f"{d['automated_readability_index']:.2f}"),
        ]
        out = ["# Text report", "", "| Metric | Value |", "| --- | ---: |"]
        out += [f"| {k} | {v} |" for k, v in rows]
        if self.top_words:
            out += ["", "## Top words", "", "| Word | Count |", "| --- | ---: |"]
            out += [f"| {_md(w)} | {c} |" for w, c in self.top_words]
        if self.repeated_phrases:
            out += ["", "## Repeated phrases", "", "| Phrase | Count |", "| --- | ---: |"]
            out += [f"| {_md(p.text)} | {p.count} |" for p in self.repeated_phrases]
        return "\n".join(out) + "\n"


def _md(cell: str) -> str:
    return cell.replace("|", "\\|")


def analyze(
    text: str,
    *,
    stopwords: Iterable[str] | None = None,
    top: int = 10,
    min_n: int = 2,
    max_n: int = 4,
    min_count: int = 2,
    max_phrases: int = 10,
) -> Report:
    """Analyze ``text`` and return a :class:`Report`.

    Args:
        text: The text to analyze.
        stopwords: Words excluded from ``top_words`` and repeated phrases.
        top: How many frequent words to list.
        min_n, max_n, min_count: Phrase length range and minimum repeats.
        max_phrases: How many repeated phrases to list.
    """
    stop = None if stopwords is None else list(stopwords)
    tokens = tokenize(text)
    words = len(tokens)
    sentences = len(split_sentences(text))
    syllables = readability.syllable_total(tokens)
    complex_words = readability.complex_word_count(tokens)
    letters = readability.letter_count(tokens)
    return Report(
        characters=len(text),
        words=words,
        unique_words=len(set(tokens)),
        sentences=sentences,
        syllables=syllables,
        complex_words=complex_words,
        avg_words_per_sentence=words / sentences if sentences else 0.0,
        avg_syllables_per_word=syllables / words if words else 0.0,
        flesch_reading_ease=readability.flesch_reading_ease(words, sentences, syllables),
        flesch_kincaid_grade=readability.flesch_kincaid_grade(words, sentences, syllables),
        gunning_fog=readability.gunning_fog(words, sentences, complex_words),
        smog_grade=readability.smog_grade(sentences, complex_words),
        coleman_liau_index=readability.coleman_liau_index(words, sentences, letters),
        automated_readability_index=readability.automated_readability_index(
            words, sentences, letters
        ),
        top_words=tuple(word_frequency(text, stopwords=stop, top=top)),
        repeated_phrases=tuple(
            repeated_ngrams(
                text,
                min_n=min_n,
                max_n=max_n,
                min_count=min_count,
                stopwords=stop,
                top=max_phrases,
            )
        ),
    )
