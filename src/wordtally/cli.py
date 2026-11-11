"""Command-line interface: ``wordtally FILE|-``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from . import __version__
from .report import analyze
from .tokenize import ENGLISH_STOPWORDS


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wordtally",
        description="Word frequency, readability scores and repeated phrases for a text file.",
    )
    p.add_argument("file", help="path to a UTF-8 text file, or - to read standard input")
    p.add_argument(
        "-f", "--format", choices=["text", "json", "markdown"], default="text",
        help="output format (default: text)",
    )
    p.add_argument("--stopwords", action="store_true", help="ignore common English stopwords")
    p.add_argument("--top", type=int, default=10, help="frequent words to list (default: 10)")
    p.add_argument("--min-n", type=int, default=2, help="shortest repeated phrase (default: 2)")
    p.add_argument("--max-n", type=int, default=4, help="longest repeated phrase (default: 4)")
    p.add_argument("--min-count", type=int, default=2, help="minimum repeats (default: 2)")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


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
    try:
        text = _read(args.file)
    except OSError as exc:
        print(f"wordtally: cannot read {args.file}: {exc.strerror or exc}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(f"wordtally: {args.file} is not valid UTF-8", file=sys.stderr)
        return 1
    report = analyze(
        text,
        stopwords=ENGLISH_STOPWORDS if args.stopwords else None,
        top=args.top,
        min_n=args.min_n,
        max_n=args.max_n,
        min_count=args.min_count,
    )
    if args.format == "json":
        out = report.to_json() + "\n"
    elif args.format == "markdown":
        out = report.to_markdown()
    else:
        out = report.to_text()
    sys.stdout.buffer.write(out.encode("utf-8"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
