from wordtally.tokenize import ENGLISH_STOPWORDS, parse_stopwords, tokenize, word_frequency


def test_parse_stopwords():
    got = parse_stopwords("# header\nFoo\n\n bar  # note\r\nÉTÉ\n#\n")
    assert got == frozenset({"foo", "bar", "été"})


def test_parse_stopwords_empty():
    assert parse_stopwords("") == frozenset()


def test_basic_tokens():
    assert tokenize("Hello, world!") == ["hello", "world"]


def test_empty_and_whitespace():
    assert tokenize("") == []
    assert tokenize("  \n\t ") == []


def test_punctuation_only():
    assert tokenize("... --- !!!") == []


def test_keep_case():
    assert tokenize("Hello World", lowercase=False) == ["Hello", "World"]


def test_apostrophes_and_hyphens_kept_inside_words():
    assert tokenize("Don't stop the well-known l'été") == [
        "don't", "stop", "the", "well-known", "l'été",
    ]


def test_curly_apostrophe_normalised():
    assert tokenize("don’t") == ["don't"]


def test_leading_trailing_quotes_dropped():
    assert tokenize("'quoted' -dash-") == ["quoted", "dash"]


def test_numbers_and_underscores_dropped():
    assert tokenize("abc123 4567 snake_case") == ["abc", "snake", "case"]


def test_unicode_letters():
    assert tokenize("Café naïve Ünïcode") == ["café", "naïve", "ünïcode"]


def test_non_latin_scripts():
    assert tokenize("Привет мир") == ["привет", "мир"]
    assert tokenize("γειά σου") == ["γειά", "σου"]


def test_casefold_handles_german_sharp_s():
    assert tokenize("STRASSE Straße") == ["strasse", "strasse"]


def test_stopwords_removed_case_insensitively():
    assert tokenize("The cat and THE hat", stopwords=ENGLISH_STOPWORDS) == ["cat", "hat"]


def test_custom_stopwords():
    assert tokenize("one two three", stopwords=["Two"]) == ["one", "three"]


def test_stopwords_with_keep_case():
    assert tokenize("The Cat", lowercase=False, stopwords={"the"}) == ["Cat"]


def test_frequency_order_and_ties():
    text = "b a b c a b"
    assert word_frequency(text) == [("b", 3), ("a", 2), ("c", 1)]


def test_frequency_tie_alphabetical():
    assert word_frequency("zeta alpha mid") == [("alpha", 1), ("mid", 1), ("zeta", 1)]


def test_frequency_top():
    assert word_frequency("a a a b b c", top=2) == [("a", 3), ("b", 2)]
    assert word_frequency("a b", top=0) == []


def test_frequency_empty():
    assert word_frequency("") == []


def test_frequency_stopwords():
    assert word_frequency("the dog the cat", stopwords=ENGLISH_STOPWORDS) == [
        ("cat", 1),
        ("dog", 1),
    ]


def test_frequency_case_insensitive():
    assert word_frequency("Dog dog DOG") == [("dog", 3)]
