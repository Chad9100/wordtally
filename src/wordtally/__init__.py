"""wordtally: text analysis library with a small CLI."""

from .ngrams import Phrase, repeated_ngrams
from .readability import flesch_kincaid_grade, flesch_reading_ease, gunning_fog
from .report import Report, analyze
from .sentences import split_sentences
from .syllables import count_syllables
from .tokenize import ENGLISH_STOPWORDS, tokenize, word_frequency

__version__ = "0.1.0"

__all__ = [
    "ENGLISH_STOPWORDS",
    "Phrase",
    "Report",
    "analyze",
    "count_syllables",
    "flesch_kincaid_grade",
    "flesch_reading_ease",
    "gunning_fog",
    "repeated_ngrams",
    "split_sentences",
    "tokenize",
    "word_frequency",
]
