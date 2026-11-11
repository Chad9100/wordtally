import pytest

from wordtally.sentences import sentence_stats, split_sentences


def test_simple_split():
    assert split_sentences("One. Two! Three?") == ["One.", "Two!", "Three?"]


def test_empty_and_blank():
    assert split_sentences("") == []
    assert split_sentences("   \n\n  ") == []


def test_no_terminator_is_one_sentence():
    assert split_sentences("no terminator here") == ["no terminator here"]


def test_trailing_text_without_terminator():
    assert split_sentences("First one. And then a tail") == ["First one.", "And then a tail"]


def test_abbreviations_do_not_split():
    assert split_sentences("Dr. Smith met Mr. Jones. They talked.") == [
        "Dr. Smith met Mr. Jones.",
        "They talked.",
    ]


def test_initials_do_not_split():
    assert split_sentences("J. R. R. Tolkien wrote it. Fine.") == [
        "J. R. R. Tolkien wrote it.",
        "Fine.",
    ]


def test_decimal_numbers_do_not_split():
    assert split_sentences("Pi is 3.14 roughly. Yes.") == ["Pi is 3.14 roughly.", "Yes."]


def test_ellipsis_and_repeated_terminators():
    assert split_sentences("Wait... what?! Really.") == ["Wait...", "what?!", "Really."]


def test_closing_quote_stays_with_sentence():
    assert split_sentences('He said "stop." Then left.') == ['He said "stop."', "Then left."]


def test_paragraph_break_splits_without_terminator():
    assert split_sentences("Title line\n\nBody text.") == ["Title line", "Body text."]


def test_whitespace_collapsed():
    assert split_sentences("A  big\ncat.   Dogs bark.") == ["A big cat.", "Dogs bark."]


def test_unicode_ellipsis_and_text():
    assert split_sentences("Où est-il… Là-bas. Ça va?") == [
        "Où est-il…",
        "Là-bas.",
        "Ça va?",
    ]


def test_stats_basic():
    s = sentence_stats("One two three. Four. Five six seven eight nine ten eleven.")
    assert s is not None
    assert s.count == 3
    assert (s.shortest, s.shortest_words) == ("Four.", 1)
    assert s.longest_words == 7 and s.longest.startswith("Five")
    assert s.mean_words == 3.67
    assert s.histogram == {"1-5": 2, "6-10": 1}
    assert s.long_sentences == ()


def test_stats_long_threshold():
    s = sentence_stats("One two three four. Five six.", long_threshold=3)
    assert s is not None
    assert s.long_sentences == ("One two three four.",)


def test_stats_empty_and_wordless():
    assert sentence_stats("") is None
    assert sentence_stats("... !!! 123.") is None


def test_stats_ties_pick_first():
    s = sentence_stats("Aa bb. Cc dd.")
    assert s is not None
    assert s.shortest == "Aa bb." and s.longest == "Aa bb."


def test_stats_bad_arguments():
    with pytest.raises(ValueError):
        sentence_stats("x.", long_threshold=0)
    with pytest.raises(ValueError):
        sentence_stats("x.", bin_width=0)


def test_stats_to_dict_and_text():
    s = sentence_stats("Hi there. Yes.", bin_width=2)
    assert s is not None
    d = s.to_dict()
    assert d["histogram"] == {"1-2": 2} and d["long_sentences"] == []
    assert "Length histogram" in s.to_text() and "##" in s.to_text()
