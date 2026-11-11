# Roadmap

Ideas for after v0.1, roughly in priority order.

1. ~~**More readability scores**~~: SMOG, Coleman-Liau and Automated Readability Index are done as functions; Dale-Chall (needs a word list) and exposing the new scores in `Report`/CLI remain open.
2. **Better syllable counting**: an exceptions dictionary for common irregular English words, and optional pluggable counters for other languages.
3. **Custom stopword lists**: load stopwords from a file on the CLI (`--stopwords-file`) and ship lists for a few more languages.
4. ~~**Lexical diversity metrics**~~: done (`type_token_ratio`, `mtld`, `hapax_legomena`); a `--diversity` CLI flag and Report fields remain open.
5. **Keyword extraction**: RAKE-style or TF-IDF keyword ranking across one or many files.
6. **Multi-file and directory input**: analyze several files in one run with a per-file and combined summary, plus `--compare` between two texts.
7. **Sentence statistics**: longest and shortest sentences, sentence length histogram, and a flag for sentences above a configurable length.
8. **CSV output** and a `--output FILE` option for the CLI.
9. **Streaming mode** for very large files so memory stays flat.
