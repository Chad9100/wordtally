from wordtally.sentences import split_sentences


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
