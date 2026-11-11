import io
import json
import sys

import pytest

from wordtally.cli import main

TEXT = "The cat sat. The cat sat again. Dogs bark loudly.\n"


class _FakeStdin:
    def __init__(self, data: bytes) -> None:
        self.buffer = io.BytesIO(data)


@pytest.fixture
def textfile(tmp_path):
    p = tmp_path / "in.txt"
    p.write_text(TEXT, encoding="utf-8")
    return str(p)


def test_text_output(textfile, capsysbinary):
    assert main([textfile]) == 0
    out = capsysbinary.readouterr().out.decode("utf-8")
    assert "Words:" in out and "Top words:" in out


def test_json_output(textfile, capsysbinary):
    assert main([textfile, "--format", "json"]) == 0
    data = json.loads(capsysbinary.readouterr().out)
    assert data["words"] == 10
    assert data["sentences"] == 3


def test_markdown_output(textfile, capsysbinary):
    assert main([textfile, "-f", "markdown"]) == 0
    assert capsysbinary.readouterr().out.decode().startswith("# Text report")


def test_stdin(monkeypatch, capsysbinary):
    monkeypatch.setattr(sys, "stdin", _FakeStdin(TEXT.encode()))
    assert main(["-", "-f", "json"]) == 0
    assert json.loads(capsysbinary.readouterr().out)["words"] == 10


def test_stopwords_flag(textfile, capsysbinary):
    assert main([textfile, "-f", "json", "--stopwords"]) == 0
    words = [w["word"] for w in json.loads(capsysbinary.readouterr().out)["top_words"]]
    assert "the" not in words and "cat" in words


def _top_words(capsysbinary):
    return [w["word"] for w in json.loads(capsysbinary.readouterr().out)["top_words"]]


def test_stopwords_file(textfile, tmp_path, capsysbinary):
    sw = tmp_path / "sw.txt"
    sw.write_text("# mine\nCat\n\n  sat  # trailing\n", encoding="utf-8")
    assert main([textfile, "-f", "json", "--stopwords-file", str(sw)]) == 0
    words = _top_words(capsysbinary)
    assert "cat" not in words and "sat" not in words and "the" in words


def test_stopwords_file_combined(textfile, tmp_path, capsysbinary):
    sw = tmp_path / "sw.txt"
    sw.write_bytes(b"\xef\xbb\xbfcat\n")
    assert main([textfile, "-f", "json", "--stopwords", "--stopwords-file", str(sw)]) == 0
    words = _top_words(capsysbinary)
    assert "the" not in words and "cat" not in words and "sat" in words


def test_stopwords_file_missing(textfile, tmp_path, capsys):
    assert main([textfile, "--stopwords-file", str(tmp_path / "nope.txt")]) == 1
    assert "cannot read" in capsys.readouterr().err


def test_stopwords_file_invalid_utf8(textfile, tmp_path, capsys):
    sw = tmp_path / "bad.txt"
    sw.write_bytes(b"\xff\xfe\x00")
    assert main([textfile, "--stopwords-file", str(sw)]) == 1
    assert "UTF-8" in capsys.readouterr().err


def test_top_option(textfile, capsysbinary):
    assert main([textfile, "-f", "json", "--top", "1"]) == 0
    assert len(json.loads(capsysbinary.readouterr().out)["top_words"]) == 1


def test_phrase_options(textfile, capsysbinary):
    assert main([textfile, "-f", "json", "--min-n", "3", "--max-n", "3"]) == 0
    phrases = json.loads(capsysbinary.readouterr().out)["repeated_phrases"]
    assert phrases[0]["phrase"] == "the cat sat"


def test_missing_file(tmp_path, capsys):
    assert main([str(tmp_path / "nope.txt")]) == 1
    assert "cannot read" in capsys.readouterr().err


def test_invalid_utf8(tmp_path, capsys):
    p = tmp_path / "bad.txt"
    p.write_bytes(b"\xff\xfe\x00bad")
    assert main([str(p)]) == 1
    assert "UTF-8" in capsys.readouterr().err


def test_bom_is_stripped(tmp_path, capsysbinary):
    p = tmp_path / "bom.txt"
    p.write_bytes(b"\xef\xbb\xbfhello world.")
    assert main([str(p), "-f", "json"]) == 0
    assert json.loads(capsysbinary.readouterr().out)["characters"] == len("hello world.")


def test_empty_file(tmp_path, capsysbinary):
    p = tmp_path / "empty.txt"
    p.write_text("")
    assert main([str(p), "-f", "json"]) == 0
    assert json.loads(capsysbinary.readouterr().out)["words"] == 0


def test_invalid_options(textfile, capsys):
    assert main([textfile, "--min-count", "1"]) == 2
    assert "min-count" in capsys.readouterr().err


def test_bad_format_exits(textfile):
    with pytest.raises(SystemExit) as exc:
        main([textfile, "-f", "xml"])
    assert exc.value.code == 2


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "wordtally 0.1.0" in capsys.readouterr().out


def test_sentence_stats_text(textfile, capsysbinary):
    assert main([textfile, "--sentence-stats", "--long-sentence", "3"]) == 0
    out = capsysbinary.readouterr().out.decode()
    assert "Sentence statistics:" in out and "Over 3 words:            1" in out


def test_sentence_stats_json(textfile, capsysbinary):
    assert main([textfile, "-f", "json", "--sentence-stats"]) == 0
    stats = json.loads(capsysbinary.readouterr().out)["sentence_stats"]
    assert stats["count"] == 3 and stats["longest"] == "The cat sat again."


def test_sentence_stats_json_empty(tmp_path, capsysbinary):
    p = tmp_path / "e.txt"
    p.write_text("")
    assert main([str(p), "-f", "json", "--sentence-stats"]) == 0
    assert json.loads(capsysbinary.readouterr().out)["sentence_stats"] is None


def test_sentence_stats_markdown(textfile, capsysbinary):
    assert main([textfile, "-f", "markdown", "--sentence-stats"]) == 0
    assert "## Sentence statistics" in capsysbinary.readouterr().out.decode()


def test_no_stats_by_default(textfile, capsysbinary):
    assert main([textfile, "-f", "json"]) == 0
    assert "sentence_stats" not in json.loads(capsysbinary.readouterr().out)


def test_bad_long_sentence(textfile, capsys):
    assert main([textfile, "--long-sentence", "0"]) == 2
    assert "long-sentence" in capsys.readouterr().err


def test_unicode_output(tmp_path, capsysbinary):
    p = tmp_path / "u.txt"
    p.write_text("très très bien", encoding="utf-8")
    assert main([str(p), "-f", "json"]) == 0
    assert "très".encode() in capsysbinary.readouterr().out
