# wordtally

A small, dependency-free Python library for text analysis (word frequency,
sentence splitting, syllable estimates, readability scores, repeated phrases)
with a command-line tool on top. Python 3.10+, standard library only, fully
typed (`py.typed`).

All outputs below were captured from real runs against the sample file
`sample.txt`:

> The quick brown fox jumps over the lazy dog. The quick brown fox is very quick, and the lazy dog is very lazy. Dr. Smith studied the unbelievable relationship between foxes and dogs. Simple words make simple sentences. Why do we read?

## Install

```console
pip install .
```

## Tokens, frequency, sentences, syllables

Tokens are runs of letters in any script, with internal apostrophes and
hyphens kept. Numbers and punctuation are dropped. Pass `stopwords=` (for
example `ENGLISH_STOPWORDS`) to filter words out.

```python
from wordtally import tokenize, word_frequency, split_sentences, count_syllables, ENGLISH_STOPWORDS

text = open("sample.txt", encoding="utf-8").read()

print(tokenize("Don't panic: it's well-known, café-style!"))
print(word_frequency(text, stopwords=ENGLISH_STOPWORDS, top=5))
print(split_sentences(text))
print([count_syllables(w) for w in ["cat", "table", "unbelievable"]])
```

Output:

```text
["don't", 'panic', "it's", 'well-known', 'café-style']
[('lazy', 3), ('quick', 3), ('brown', 2), ('dog', 2), ('fox', 2)]
['The quick brown fox jumps over the lazy dog.', 'The quick brown fox is very quick, and the lazy dog is very lazy.', 'Dr. Smith studied the unbelievable relationship between foxes and dogs.', 'Simple words make simple sentences.', 'Why do we read?']
[1, 2, 5]
```

Sentence splitting is rule-based: `.`, `!`, `?` and `…` followed by whitespace
end a sentence, blank lines separate paragraphs, and common abbreviations
(`Dr.`, `e.g.`) and single-letter initials do not split. Text with no
terminator is one sentence. Syllable counts are a heuristic estimate for
English and will be wrong for some words.

## Readability

With `W` words, `S` sentences, `Y` syllables and `C` complex words (three or
more estimated syllables):

| Score | Formula |
| --- | --- |
| Flesch reading ease | `206.835 - 1.015 * (W / S) - 84.6 * (Y / W)` |
| Flesch-Kincaid grade | `0.39 * (W / S) + 11.8 * (Y / W) - 15.59` |
| Gunning fog | `0.4 * ((W / S) + 100 * (C / W))` |

Three letter- and complexity-based scores are also included in `analyze()`
and the CLI output (`smog_grade`, `coleman_liau_index`,
`automated_readability_index`), and are available as functions
(`L` is the number of letters, `letter_count(words)` computes it):

| Score | Formula |
| --- | --- |
| SMOG grade | `1.0430 * sqrt(C * (30 / S)) + 3.1291` |
| Coleman-Liau index | `0.0588 * (100 * L / W) - 0.296 * (100 * S / W) - 15.8` |
| Automated readability index | `4.71 * (L / W) + 0.5 * (W / S) - 21.43` |

SMOG is formally defined for samples of 30+ sentences, so treat it as rough on
short texts. Each score returns `0.0` for empty input.

```python
from wordtally import (tokenize, split_sentences, smog_grade,
                       coleman_liau_index, automated_readability_index, letter_count)
from wordtally.readability import complex_word_count

text = open("sample.txt", encoding="utf-8").read()
w = tokenize(text)
s = len(split_sentences(text))
letters = letter_count(w)
print(len(w), s, letters, complex_word_count(w))
print(round(smog_grade(s, complex_word_count(w)), 2))
print(round(coleman_liau_index(len(w), s, letters), 2))
print(round(automated_readability_index(len(w), s, letters), 2))
```

Output:

```text
42 5 186 3
7.55
6.72
3.63
```

```python
from wordtally import flesch_reading_ease, flesch_kincaid_grade, gunning_fog

# arguments: words, sentences, syllables (complex words for fog)
print(round(flesch_reading_ease(10, 1, 15), 2))
print(round(flesch_kincaid_grade(10, 1, 15), 2))
print(round(gunning_fog(10, 2, 1), 2))
```

Output:

```text
69.79
6.01
6.0
```

## Repeated phrases

`repeated_ngrams` finds word sequences that repeat. A shorter phrase is hidden
when a longer one containing it repeats the same number of times.

```python
from wordtally import repeated_ngrams

text = open("sample.txt", encoding="utf-8").read()
for phrase in repeated_ngrams(text, min_n=2, max_n=5):
    print(phrase)
```

Output:

```text
Phrase(text='the quick brown fox', n=4, count=2)
Phrase(text='the lazy dog', n=3, count=2)
Phrase(text='is very', n=2, count=2)
```

## Lexical diversity

- `type_token_ratio(text)`: unique words / total words. It shrinks as texts
  grow, so compare only texts of similar length.
- `mtld(text, threshold=0.72)`: Measure of Textual Lexical Diversity. A running
  type-token ratio is kept; each time it falls to the threshold a factor is
  counted and it resets (a trailing partial factor counts fractionally). MTLD
  is tokens / factors, averaged over a forward and a backward pass. Higher is
  more diverse and it is much less sensitive to length.
- `hapax_legomena(text)`: words that occur exactly once.

All accept `stopwords=`. Empty input gives `0.0` (or `()`).

```python
from wordtally import type_token_ratio, mtld, hapax_legomena, ENGLISH_STOPWORDS

text = open("sample.txt", encoding="utf-8").read()
print(round(type_token_ratio(text), 3))
print(round(mtld(text), 2))
print(hapax_legomena(text, stopwords=ENGLISH_STOPWORDS))
print(mtld("a a a a"))
```

Output:

```text
0.643
26.16
('jumps', 'dr', 'smith', 'studied', 'unbelievable', 'relationship', 'foxes', 'dogs', 'words', 'make', 'sentences', 'read')
2.0
```

## analyze()

`analyze(text)` returns a frozen `Report` dataclass with counts, readability
scores, top words and repeated phrases. It also offers `to_dict()`,
`to_json()`, `to_text()` and `to_markdown()`.

```python
from wordtally import analyze, ENGLISH_STOPWORDS

text = open("sample.txt", encoding="utf-8").read()
report = analyze(text, stopwords=ENGLISH_STOPWORDS, top=3)
print(report.words, report.sentences, report.syllables)
print(round(report.flesch_reading_ease, 2))
print(report.top_words)
print(report.repeated_phrases[:2])
```

Output:

```text
42 5 62
73.42
(('lazy', 3), ('quick', 3), ('brown', 2))
(Phrase(text='quick brown fox', n=3, count=2), Phrase(text='lazy dog', n=2, count=2))
```

## Command line

`wordtally FILE|-` reads a UTF-8 file (or standard input with `-`). Options:
`--format text|json|markdown`, `--stopwords`, `--top N`, `--min-n`, `--max-n`,
`--min-count`, `--sentence-stats`, `--long-sentence N`.

## Sentence statistics

`sentence_stats(text, long_threshold=30, bin_width=5)` returns a frozen
`SentenceStats` (or `None` if the text has no sentences with words): the
shortest and longest sentence, mean length, a length histogram in words, and
the sentences longer than `long_threshold` words. On the CLI it is added with
`--sentence-stats` (and `--long-sentence N` to set the threshold), in text,
markdown and JSON (`sentence_stats` key) output.

```python
from wordtally import sentence_stats

s = sentence_stats(open("sample.txt", encoding="utf-8").read(), long_threshold=10)
print(s.count, s.mean_words)
print(s.shortest, s.shortest_words)
print(s.longest_words)
print(s.histogram)
print(s.long_sentences)
```

Output:

```text
5 8.4
Why do we read? 4
14
{'1-5': 2, '6-10': 2, '11-15': 1}
('The quick brown fox is very quick, and the lazy dog is very lazy.',)
```

```console
$ wordtally sample.txt --sentence-stats --long-sentence 10
```

The text report is followed by:

```text
Sentence statistics:
Sentences:               5
Mean length (words):     8.4
Shortest sentence:       Why do we read? (4 words)
Longest sentence:        The quick brown fox is very quick, and the lazy dog is very lazy. (14 words)
Over 10 words:           1
Length histogram (words):
    1-5  ## 2
   6-10  ## 2
  11-15  # 1
```

```console
$ wordtally sample.txt --stopwords --top 5
```

```text
Characters:              235
Words:                   42 (27 unique)
Sentences:               5
Syllables:               62
Complex words:           3
Words per sentence:      8.40
Syllables per word:      1.48
Flesch reading ease:     73.42
Flesch-Kincaid grade:    5.11
Gunning fog:             6.22
SMOG grade:              7.55
Coleman-Liau index:      6.72
Automated readability:   3.63

Top words:
     3  lazy
     3  quick
     2  brown
     2  dog
     2  fox

Repeated phrases:
     2x  quick brown fox
     2x  lazy dog
```

JSON:

```console
$ wordtally sample.txt --format json --top 2 --stopwords
```

```json
{
  "characters": 235,
  "words": 42,
  "unique_words": 27,
  "sentences": 5,
  "syllables": 62,
  "complex_words": 3,
  "avg_words_per_sentence": 8.4,
  "avg_syllables_per_word": 1.48,
  "flesch_reading_ease": 73.42,
  "flesch_kincaid_grade": 5.11,
  "gunning_fog": 6.22,
  "smog_grade": 7.55,
  "coleman_liau_index": 6.72,
  "automated_readability_index": 3.63,
  "top_words": [
    {
      "word": "lazy",
      "count": 3
    },
    {
      "word": "quick",
      "count": 3
    }
  ],
  "repeated_phrases": [
    {
      "phrase": "quick brown fox",
      "words": 3,
      "count": 2
    },
    {
      "phrase": "lazy dog",
      "words": 2,
      "count": 2
    }
  ]
}
```

Markdown:

```console
$ wordtally sample.txt -f markdown --top 3 --stopwords
```

```markdown
# Text report

| Metric | Value |
| --- | ---: |
| Characters | 235 |
| Words | 42 |
| Unique words | 27 |
| Sentences | 5 |
| Syllables | 62 |
| Complex words | 3 |
| Words per sentence | 8.40 |
| Syllables per word | 1.48 |
| Flesch reading ease | 73.42 |
| Flesch-Kincaid grade | 5.11 |
| Gunning fog | 6.22 |
| SMOG grade | 7.55 |
| Coleman-Liau index | 6.72 |
| Automated readability index | 3.63 |

## Top words

| Word | Count |
| --- | ---: |
| lazy | 3 |
| quick | 3 |
| brown | 2 |

## Repeated phrases

| Phrase | Count |
| --- | ---: |
| quick brown fox | 2 |
| lazy dog | 2 |
```

## Development

```console
pip install -e ".[test]"
pytest
```

## License

MIT, see [LICENSE](LICENSE).
