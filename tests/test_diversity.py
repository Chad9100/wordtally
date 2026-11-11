import pytest

from wordtally import ENGLISH_STOPWORDS, hapax_legomena, mtld, type_token_ratio


def test_ttr_basic():
    assert type_token_ratio("a b a b") == 0.5
    assert type_token_ratio("a b c d") == 1.0


def test_ttr_empty_and_case():
    assert type_token_ratio("") == 0.0
    assert type_token_ratio("... 123") == 0.0
    assert type_token_ratio("Cat cat CAT") == pytest.approx(1 / 3)


def test_ttr_stopwords():
    assert type_token_ratio("the cat the dog", stopwords=ENGLISH_STOPWORDS) == 1.0


def test_hapax_order_and_content():
    assert hapax_legomena("b a b c a d") == ("c", "d")
    assert hapax_legomena("") == ()
    assert hapax_legomena("x x x") == ()


def test_mtld_empty():
    assert mtld("") == 0.0


def test_mtld_repeated_word_is_low():
    # "a a a a": ratio hits 0.5 after 2 tokens, so each pass has 2 factors.
    assert mtld("a a a a") == pytest.approx(2.0)


def test_mtld_all_unique_falls_back_to_length():
    assert mtld("one two three four five") == 5.0


def test_mtld_diverse_beats_repetitive():
    rep = "the cat sat on the mat the cat sat on the mat " * 4
    div = "quick brown foxes jump over lazy dogs while tired cats nap near warm stoves " * 1
    assert mtld(div) > mtld(rep)


def test_mtld_partial_factor():
    # a b a: TTR 1, 1, 2/3 <= 0.72 on third token -> one full factor, 3 tokens.
    assert mtld("a b a") == pytest.approx(3.0)
    # a b: no factor completes; partial = 0, so fallback to token count.
    assert mtld("a b") == 2.0


def test_mtld_bad_threshold():
    for bad in (0, 1, -0.5, 1.5):
        with pytest.raises(ValueError):
            mtld("a b c", threshold=bad)


def test_mtld_threshold_changes_result():
    text = "a b c a b d a e f a"
    assert mtld(text, threshold=0.5) != mtld(text, threshold=0.9)
