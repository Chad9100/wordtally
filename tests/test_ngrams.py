import pytest

from wordtally.ngrams import Phrase, repeated_ngrams


def test_simple_repeat():
    result = repeated_ngrams("a b c a b d", min_n=2, max_n=2)
    assert result == [Phrase("a b", 2, 2)]


def test_no_repeats():
    assert repeated_ngrams("every word here is different") == []


def test_empty_text():
    assert repeated_ngrams("") == []


def test_text_shorter_than_n():
    assert repeated_ngrams("one", min_n=2, max_n=4) == []


def test_subphrases_collapsed_into_longest():
    text = "the quick brown fox. the quick brown fox."
    result = repeated_ngrams(text, min_n=2, max_n=4)
    assert result == [Phrase("the quick brown fox", 4, 2)]


def test_subphrase_kept_when_more_frequent():
    text = "red apple pie. red apple pie. red apple tart. red apple jam."
    result = repeated_ngrams(text, min_n=2, max_n=3)
    phrases = {p.text: p.count for p in result}
    assert phrases["red apple"] == 4
    assert phrases["red apple pie"] == 2


def test_case_insensitive_and_punctuation_ignored():
    assert repeated_ngrams("Hello, World! hello world", min_n=2, max_n=2) == [
        Phrase("hello world", 2, 2)
    ]


def test_overlapping_counts():
    result = repeated_ngrams("a a a a", min_n=2, max_n=2)
    assert result == [Phrase("a a", 2, 3)]


def test_min_count():
    text = "x y x y x y"
    assert repeated_ngrams(text, min_n=2, max_n=2, min_count=3)[0].text == "x y"
    assert repeated_ngrams(text, min_n=2, max_n=2, min_count=4) == []


def test_stopwords_make_words_adjacent():
    text = "fast cars and fast cars"
    assert repeated_ngrams(text, min_n=2, max_n=2, stopwords={"and"}) == [
        Phrase("fast cars", 2, 2)
    ]


def test_top_limits_and_ordering():
    text = "a b a b a b c d c d"
    result = repeated_ngrams(text, min_n=2, max_n=2, top=1)
    assert result == [Phrase("a b", 2, 3)]


def test_unigrams_allowed():
    assert repeated_ngrams("go go stop", min_n=1, max_n=1) == [Phrase("go", 1, 2)]


@pytest.mark.parametrize(
    "kwargs",
    [{"min_n": 0}, {"min_n": 3, "max_n": 2}, {"min_count": 1}],
)
def test_invalid_arguments(kwargs):
    with pytest.raises(ValueError):
        repeated_ngrams("a b", **kwargs)


def test_unicode_phrases():
    text = "très bien, très bien!"
    assert repeated_ngrams(text, min_n=2, max_n=2) == [Phrase("très bien", 2, 2)]
