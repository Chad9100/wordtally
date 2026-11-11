import pytest

from wordtally.readability import (
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
