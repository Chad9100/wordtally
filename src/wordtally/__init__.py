"""wordtally: text analysis library with a small CLI."""

from .diversity import hapax_legomena, mtld, type_token_ratio
from .ngrams import Phrase, repeated_ngrams
from .readability import (
    automated_readability_index,
    coleman_liau_index,
    flesch_kincaid_grade,
    flesch_reading_ease,
    gunning_fog,
    letter_count,
    smog_grade,
)
from .report import Report, analyze
from .sentences import SentenceStats, sentence_stats, split_sentences
from .syllables import count_syllables
from .tokenize import ENGLISH_STOPWORDS, tokenize, word_frequency

__version__ = "0.1.0"

__all__ = [
    "ENGLISH_STOPWORDS",
    "Phrase",
    "Report",
    "SentenceStats",
    "analyze",
    "automated_readability_index",
    "coleman_liau_index",
    "count_syllables",
    "flesch_kincaid_grade",
    "flesch_reading_ease",
    "gunning_fog",
    "hapax_legomena",
    "letter_count",
    "mtld",
    "repeated_ngrams",
    "sentence_stats",
    "smog_grade",
    "split_sentences",
    "tokenize",
    "type_token_ratio",
    "word_frequency",
]
