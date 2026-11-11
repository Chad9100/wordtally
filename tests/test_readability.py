import pytest

from wordtally.readability import (
    automated_readability_index,
    coleman_liau_index,
    letter_count,
    smog_grade,
    complex_word_count,
    flesch_kincaid_grade,
    flesch_reading_ease,
    gunning_fog,
    syllable_total,
)


def test_flesch_reading_ease_hand_computed():
    # 206.835 - 1.015*10 - 84.6*1.5
    assert flesch_reading_ease(10, 1, 15) == pytest.approx(69.785)


def test_flesch_kincaid_hand_computed():
    # 0.39*10 + 11.8*1.5 - 15.59
    assert flesch_kincaid_grade(10, 1, 15) == pytest.approx(6.01)


def test_gunning_fog_hand_computed():
    # 0.4 * (10/2 + 100*1/10)
    assert gunning_fog(10, 2, 1) == pytest.approx(6.0)


@pytest.mark.parametrize("fn", [flesch_reading_ease, flesch_kincaid_grade, gunning_fog])
def test_zero_inputs_give_zero(fn):
    assert fn(0, 0, 0) == 0.0
    assert fn(5, 0, 5) == 0.0
    assert fn(0, 3, 0) == 0.0


def test_smog_hand_computed():
    # 1.043 * sqrt(30 * 30 / 30) + 3.1291 with 30 sentences, 30 complex words
    assert smog_grade(30, 30) == pytest.approx(1.0430 * 30**0.5 + 3.1291)
    # no complex words: just the constant
    assert smog_grade(5, 0) == pytest.approx(3.1291)


def test_coleman_liau_hand_computed():
    # 100 words, 5 sentences, 450 letters: 0.0588*450 - 0.296*5 - 15.8
    assert coleman_liau_index(100, 5, 450) == pytest.approx(9.18)


def test_ari_hand_computed():
    # 4.71*4.5 + 0.5*20 - 21.43
    assert automated_readability_index(100, 5, 450) == pytest.approx(9.765)


def test_new_scores_zero_inputs():
    assert smog_grade(0, 4) == 0.0
    assert coleman_liau_index(0, 1, 5) == 0.0
    assert coleman_liau_index(5, 0, 5) == 0.0
    assert automated_readability_index(0, 1, 5) == 0.0
    assert automated_readability_index(5, 0, 5) == 0.0


def test_letter_count_ignores_apostrophes_and_hyphens():
    assert letter_count(["don't", "well-known", "café"]) == 4 + 9 + 4
    assert letter_count([]) == 0


def test_simpler_text_scores_easier():
    easy = flesch_reading_ease(20, 4, 22)
    hard = flesch_reading_ease(20, 1, 50)
    assert easy > hard


def test_syllable_total_and_complex():
    words = ["cat", "banana", "education", "table"]
    assert syllable_total(words) == 1 + 3 + 4 + 2
    assert complex_word_count(words) == 2


def test_helpers_on_empty():
    assert syllable_total([]) == 0
    assert complex_word_count([]) == 0
