import json
from dataclasses import FrozenInstanceError

import pytest

import wordtally
from wordtally import ENGLISH_STOPWORDS, Report, analyze

SAMPLE = "The cat sat on the mat. The cat sat on the hat. A dog barked!"


def test_counts():
    r = analyze(SAMPLE)
    assert r.words == 15
    assert r.sentences == 3
    assert r.unique_words == 9
    assert r.characters == len(SAMPLE)
    assert r.avg_words_per_sentence == pytest.approx(5.0)


def test_empty_text():
    r = analyze("")
    assert r.words == 0 and r.sentences == 0 and r.syllables == 0
    assert r.flesch_reading_ease == 0.0
    assert r.flesch_kincaid_grade == 0.0
    assert r.gunning_fog == 0.0
    assert r.smog_grade == 0.0
    assert r.coleman_liau_index == 0.0
    assert r.automated_readability_index == 0.0
    assert r.top_words == () and r.repeated_phrases == ()
    assert r.avg_syllables_per_word == 0.0


def test_whitespace_only():
    r = analyze(" \n\t ")
    assert r.words == 0 and r.sentences == 0


def test_punctuation_only_has_no_words():
    r = analyze("?!?! ...")
    assert r.words == 0
    assert r.flesch_reading_ease == 0.0


def test_no_sentence_terminators():
    r = analyze("just some words without an ending")
    assert r.sentences == 1
    assert r.words == 6


def test_unicode_text():
    r = analyze("Café crème. Naïve façade!")
    assert r.words == 4
    assert r.sentences == 2


def test_top_words_and_stopwords():
    r = analyze(SAMPLE, stopwords=ENGLISH_STOPWORDS, top=2)
    assert r.top_words == (("cat", 2), ("sat", 2))
    r_all = analyze(SAMPLE, top=1)
    assert r_all.top_words == (("the", 4),)


def test_repeated_phrases_in_report():
    r = analyze("one two three. one two three. four.")
    assert [(p.text, p.count) for p in r.repeated_phrases] == [("one two three", 2)]


def test_readability_matches_formula():
    r = analyze(SAMPLE)
    w, s, y = r.words, r.sentences, r.syllables
    assert r.flesch_reading_ease == pytest.approx(
        206.835 - 1.015 * (w / s) - 84.6 * (y / w)
    )
    assert r.flesch_kincaid_grade == pytest.approx(0.39 * (w / s) + 11.8 * (y / w) - 15.59)
    assert r.gunning_fog == pytest.approx(0.4 * (w / s + 100 * r.complex_words / w))


def test_extra_scores_match_functions():
    from wordtally import tokenize
    from wordtally.readability import (
        automated_readability_index,
        coleman_liau_index,
        complex_word_count,
        letter_count,
        smog_grade,
    )

    r = analyze(SAMPLE)
    toks = tokenize(SAMPLE)
    letters = letter_count(toks)
    assert r.smog_grade == pytest.approx(smog_grade(3, complex_word_count(toks)))
    assert r.coleman_liau_index == pytest.approx(coleman_liau_index(15, 3, letters))
    assert r.automated_readability_index == pytest.approx(
        automated_readability_index(15, 3, letters)
    )


def test_extra_scores_in_every_output_format():
    r = analyze(SAMPLE)
    d = json.loads(r.to_json())
    for key in ("smog_grade", "coleman_liau_index", "automated_readability_index"):
        assert d[key] == round(getattr(r, key), 2)
    assert "SMOG grade:" in r.to_text()
    assert "Coleman-Liau index:" in r.to_text()
    assert "Automated readability:" in r.to_text()
    md = r.to_markdown()
    assert "| SMOG grade |" in md and "| Automated readability index |" in md


def test_report_is_frozen():
    with pytest.raises(FrozenInstanceError):
        analyze("hi").words = 5  # type: ignore[misc]


def test_to_dict_and_json_roundtrip():
    r = analyze(SAMPLE, top=3)
    d = json.loads(r.to_json())
    assert d == r.to_dict()
    assert d["words"] == 15
    assert d["top_words"][0] == {"word": "the", "count": 4}


def test_json_keeps_unicode():
    r = analyze("très très très")
    assert "très" in r.to_json()


def test_text_output_sections():
    out = analyze(SAMPLE).to_text()
    assert "Flesch reading ease:" in out
    assert "Top words:" in out
    assert out.endswith("\n")


def test_text_output_empty_has_no_sections():
    out = analyze("").to_text()
    assert "Top words" not in out and "Repeated phrases" not in out


def test_markdown_output():
    out = analyze(SAMPLE).to_markdown()
    assert out.startswith("# Text report")
    assert "| Words | 15 |" in out
    assert "## Top words" in out
    assert "| the | 4 |" in out


def test_markdown_escapes_pipes():
    r = Report(**{**analyze("x").__dict__, "top_words": (("a|b", 1),)})
    assert "a\\|b" in r.to_markdown()


def test_csv_output():
    out = analyze(SAMPLE, top=2).to_csv()
    lines = out.splitlines()
    assert lines[0] == "section,name,value"
    assert "metric,words,15" in lines
    assert "top_word,the,4" in lines
    assert "phrase,cat sat on the,2" in lines
    assert "\r" not in out and out.endswith("\n")


def test_csv_quotes_and_extra_rows():
    r = Report(**{**analyze("x").__dict__, "top_words": (('a,"b"', 1),)})
    out = r.to_csv([("extra", "k", 1.5)])
    assert 'top_word,"a,""b""",1' in out
    assert out.endswith("extra,k,1.5\n")


def test_csv_empty_has_only_metrics():
    out = analyze("").to_csv()
    assert "top_word" not in out and "phrase" not in out
    assert "metric,words,0" in out


def test_public_api_exports():
    for name in wordtally.__all__:
        assert hasattr(wordtally, name)
    assert wordtally.__version__ == "0.1.0"
