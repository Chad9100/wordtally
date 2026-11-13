# Roadmap

Ideas for after v0.1, roughly in priority order.

1. ~~**More readability scores**~~: SMOG, Coleman-Liau and Automated Readability Index are done as functions and shown in `Report` and the CLI output; Dale-Chall (needs a word list) remains open.
2. **Better syllable counting**: ~~an exceptions dictionary for common irregular English words~~ is done (`SYLLABLE_EXCEPTIONS`); optional pluggable counters for other languages remain open.
3. **Custom stopword lists**: ~~load stopwords from a file on the CLI (`--stopwords-file`)~~ is done (`parse_stopwords`, `--stopwords-file`); shipping lists for a few more languages remains open.
4. ~~**Lexical diversity metrics**~~: done (`type_token_ratio`, `mtld`, `hapax_legomena`); the `--diversity` CLI flag is done too (text, JSON, CSV, Markdown); adding the numbers to `Report` remains open.
5. **Keyword extraction**: ~~RAKE-style keyword ranking~~ is done (`extract_keywords`, `--keywords N`); TF-IDF ranking across many files remains open.
6. **Multi-file and directory input**: analyze several files in one run with a per-file and combined summary, plus `--compare` between two texts.
7. ~~**Sentence statistics**~~: done (`sentence_stats`, `--sentence-stats`, `--long-sentence`).
8. ~~**CSV output** and a `--output FILE` option for the CLI~~: done (`-f csv`, `Report.to_csv`, `-o/--output`).
9. **Streaming mode** for very large files so memory stays flat.
