"""Command-line interface: ``wordtally FILE|-``."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from . import __version__
from .diversity import hapax_legomena, mtld, type_token_ratio
from .report import analyze
from .sentences import sentence_stats
from .tokenize import ENGLISH_STOPWORDS, parse_stopwords, tokenize


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wordtally",
        description="Word frequency, readability scores and repeated phrases for a text file.",
    )
    p.add_argument("file", help="path to a UTF-8 text file, or - to read standard input")
    p.add_argument(
        "-f", "--format", choices=["text", "json", "markdown", "csv"], default="text",
        help="output format (default: text)",
    )
    p.add_argument(
        "-o", "--output", metavar="FILE",
        help="write the report to FILE (UTF-8) instead of standard output",
    )
    p.add_argument("--stopwords", action="store_true", help="ignore common English stopwords")
    p.add_argument(
        "--stopwords-file", metavar="FILE",
        help="also ignore the words in FILE (one per line, # comments); "
        "usable with or without --stopwords",
    )
    p.add_argument("--top", type=int, default=10, help="frequent words to list (default: 10)")
    p.add_argument("--min-n", type=int, default=2, help="shortest repeated phrase (default: 2)")
    p.add_argument("--max-n", type=int, default=4, help="longest repeated phrase (default: 4)")
    p.add_argument("--min-count", type=int, default=2, help="minimum repeats (default: 2)")
    p.add_argument(
        "--sentence-stats", action="store_true",
        help="add shortest/longest sentence, a length histogram and over-long sentences",
    )
    p.add_argument(
        "--long-sentence", type=int, default=30, metavar="N",
        help="with --sentence-stats, flag sentences over N words (default: 30)",
    )
    p.add_argument(
        "--diversity", action="store_true",
        help="add lexical diversity: type-token ratio, MTLD and hapax legomena",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def diversity_summary(text: str) -> dict[str, float | int]:
    """Lexical diversity numbers for ``text`` (all words, floats rounded to 3 places).

    Keys: ``type_token_ratio``, ``mtld``, ``hapax_count`` (words occurring
    exactly once) and ``hapax_share`` (hapax count divided by total words).
    """
    hapax = len(hapax_legomena(text))
    total = len(tokenize(text))
    return {
        "type_token_ratio": round(type_token_ratio(text), 3),
        "mtld": round(mtld(text), 3),
        "hapax_count": hapax,
        "hapax_share": round(hapax / total, 3) if total else 0.0,
    }


def _read(path: str) -> str:
    if path == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(path, "rb") as fh:
            data = fh.read()
    return data.decode("utf-8-sig")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return the process exit code."""
    args = _build_parser().parse_args(argv)
    if args.min_n < 1 or args.max_n < args.min_n or args.min_count < 2:
        print("wordtally: need 1 <= min-n <= max-n and min-count >= 2", file=sys.stderr)
        return 2
    if args.long_sentence < 1:
        print("wordtally: --long-sentence must be >= 1", file=sys.stderr)
        return 2
    try:
        text = _read(args.file)
    except OSError as exc:
        print(f"wordtally: cannot read {args.file}: {exc.strerror or exc}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(f"wordtally: {args.file} is not valid UTF-8", file=sys.stderr)
        return 1
    stop: frozenset[str] | None = ENGLISH_STOPWORDS if args.stopwords else None
    if args.stopwords_file is not None:
        try:
            with open(args.stopwords_file, "rb") as fh:
                custom = parse_stopwords(fh.read().decode("utf-8-sig"))
        except OSError as exc:
            print(
                f"wordtally: cannot read {args.stopwords_file}: {exc.strerror or exc}",
                file=sys.stderr,
            )
            return 1
        except UnicodeDecodeError:
            print(f"wordtally: {args.stopwords_file} is not valid UTF-8", file=sys.stderr)
            return 1
        stop = custom if stop is None else stop | custom
    report = analyze(
        text,
        stopwords=stop,
        top=args.top,
        min_n=args.min_n,
        max_n=args.max_n,
        min_count=args.min_count,
    )
    stats = sentence_stats(text, long_threshold=args.long_sentence) if args.sentence_stats else None
    div = diversity_summary(text) if args.diversity else None
    if args.format == "json":
        data = report.to_dict()
        if div:
            data["diversity"] = div
        if args.sentence_stats:
            data["sentence_stats"] = stats.to_dict() if stats else None
        out = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    elif args.format == "csv":
        extra: list[tuple[str, str, str | int | float]] = []
        if div:
            extra += [("diversity", k, v) for k, v in div.items()]
        if stats:
            extra += [
                ("sentence_stats", "count", stats.count),
                ("sentence_stats", "mean_words", stats.mean_words),
                ("sentence_stats", "shortest_words", stats.shortest_words),
                ("sentence_stats", "longest_words", stats.longest_words),
                ("sentence_stats", "long_sentences", len(stats.long_sentences)),
            ]
            extra += [("histogram", k, v) for k, v in stats.histogram.items()]
        out = report.to_csv(extra)
    elif args.format == "markdown":
        out = report.to_markdown()
        if div:
            out += (
                "\n## Lexical diversity\n\n| Metric | Value |\n| --- | ---: |\n"
                + "".join(f"| {k} | {v} |\n" for k, v in div.items())
            )
        if stats:
            out += "\n## Sentence statistics\n\n```text\n" + stats.to_text() + "```\n"
    else:
        out = report.to_text()
        if div:
            out += (
                "\nLexical diversity:\n"
                f"Type-token ratio:        {div['type_token_ratio']:.3f}\n"
                f"MTLD:                    {div['mtld']:.3f}\n"
                f"Hapax legomena:          {div['hapax_count']} ({div['hapax_share']:.1%} of words)\n"
            )
        if stats:
            out += "\nSentence statistics:\n" + stats.to_text()
    payload = out.encode("utf-8")
    if args.output is not None:
        try:
            with open(args.output, "wb") as fh:
                fh.write(payload)
        except OSError as exc:
            print(
                f"wordtally: cannot write {args.output}: {exc.strerror or exc}",
                file=sys.stderr,
            )
            return 1
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
