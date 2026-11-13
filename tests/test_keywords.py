import pytest

from wordtally.keywords import Keyword, extract_keywords


def test_long_phrase_beats_single_words():
    text = "Linear diophantine equations are solved. Linear equations are common."
    result = extract_keywords(text)
    assert result[0] == Keyword("linear diophantine equations", 8.0, 1)


def test_scores_and_counts():
    # "red apple" appears twice; "apple" alone never; degree(red)=freq*2
    result = extract_keywords("red apple. a red apple. green pear.")
    by_text = {k.text: k for k in result}
    assert by_text["red apple"].count == 2
    assert by_text["red apple"].score == 4.0
    assert by_text["green pear"].score == 4.0
    assert [k.text for k in result] == ["red apple", "green pear"]


def test_punctuation_splits_phrases():
    texts = [k.text for k in extract_keywords("big cats, small dogs")]
    assert texts == ["big cats", "small dogs"]


def test_digits_split_phrases():
    texts = {k.text for k in extract_keywords("big 12 cats")}
    assert texts == {"big", "cats"}


def test_max_words_drops_long_phrases():
    texts = [k.text for k in extract_keywords("one two three four", max_words=3)]
    assert texts == []
    assert extract_keywords("one two three four", max_words=4)[0].text == "one two three four"


def test_custom_stopwords_and_none():
    assert [k.text for k in extract_keywords("alpha beta", stopwords=["alpha"])] == ["beta"]
    assert [k.text for k in extract_keywords("alpha of beta", stopwords=None)] == [
        "alpha of beta"
    ]


def test_top_and_empty():
    assert extract_keywords("") == []
    assert len(extract_keywords("cats. dogs. birds.", top=2)) == 2
    assert extract_keywords("cats. dogs.", top=0) == []


def test_invalid_max_words():
    with pytest.raises(ValueError):
        extract_keywords("x", max_words=0)
