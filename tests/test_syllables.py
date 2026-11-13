import pytest

from wordtally.syllables import count_syllables


@pytest.mark.parametrize(
    "word,expected",
    [
        ("cat", 1),
        ("the", 1),
        ("make", 1),
        ("table", 2),
        ("water", 2),
        ("banana", 3),
        ("beautiful", 3),
        ("jumped", 1),
        ("wanted", 2),
        ("needed", 2),
        ("free", 1),
        ("rhythm", 1),
        ("I", 1),
        ("a", 1),
        ("education", 4),
    ],
)
def test_known_words(word, expected):
    assert count_syllables(word) == expected


@pytest.mark.parametrize(
    "word,expected",
    [("idea", 3), ("area", 3), ("business", 2), ("every", 2), ("quiet", 2), ("poem", 2)],
)
def test_exceptions_dictionary(word, expected):
    assert count_syllables(word) == expected


def test_exceptions_case_and_accent_insensitive():
    assert count_syllables("IDEA") == 3
    assert count_syllables("idéa") == 3


def test_exceptions_are_valid():
    from wordtally.syllables import SYLLABLE_EXCEPTIONS

    for word, n in SYLLABLE_EXCEPTIONS.items():
        assert word == word.lower() and word.isascii() and word.isalpha()
        assert n >= 1


def test_no_letters_is_zero():
    assert count_syllables("") == 0
    assert count_syllables("123 !?") == 0


def test_case_insensitive():
    assert count_syllables("BANANA") == count_syllables("banana")


def test_accents_stripped():
    assert count_syllables("café") == count_syllables("cafe")


def test_non_latin_counts_one():
    assert count_syllables("привет") == 1
    assert count_syllables("日本語") == 1


def test_at_least_one_for_any_word():
    assert count_syllables("hmm") == 1
    assert count_syllables("shh") == 1
