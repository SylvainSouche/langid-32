# Leipzig Corpora Collection REST API audit — 18 November 2026

This is a metadata-only technical and rights-provenance audit of the REST API reference supplied for langid-32. It supersedes the earlier assumption that Leipzig was only an HTML bulk-download route. It does **not** record a text acquisition or a rights clearance.

## API route and reproducible evidence

- Swagger/OpenAPI UI: https://api.wortschatz-leipzig.de/ws/swagger-ui/index.html
- OpenAPI JSON: https://api.wortschatz-leipzig.de/ws/v3/api-docs
- Corpus catalogue: https://api.wortschatz-leipzig.de/ws/corpora/availableCorpora
- Sentence service: `GET /sentences/{corpusName}/sentences/{word}`
- Random-word service: `GET /words/{corpusName}/randomword/`

The API is live and the documented endpoints work. GitHub Actions run [44294190059](https://github.com/SylvainSouche/langid-32/actions/runs/44294190059) produced the first metadata-only probe; run [44294431022](https://github.com/SylvainSouche/langid-32/actions/runs/44294431022) repeated it with region-qualified language prefixes and source-record capture. The second artifact is [14423405978](https://github.com/SylvainSouche/langid-32/actions/runs/44294431022/artifacts/14423405978).

The second probe recorded:

- **104** corpus entries in the official catalogue.
- **20 of the 34** langid-32 target labels have at least one matching corpus.
- **30** corpus-level sentence-service probes across those 20 labels.
- **29/30** probes returned sentence examples. The one failure was the random-word endpoint for `ces_wikipedia_2014_1M` (HTTP 500); the second Czech corpus, `ces_news_2013_1M`, worked.
- **289** example sentences were examined transiently; only their aggregate count/hash and source metadata were retained. No sentence text was written to the artifact.
- **269** source records in those responses included a source URL. This is a probe count, not a count of unique URLs.

### Target-language coverage

Available in the probed catalogue:

`ar bg cs da de el en es et fi fr hu it nl pl pt ro ru sv tr`

No matching corpus was found for:

`ca ga hr is ja ko lt lv mt nb nn sk sl zh`

The catalogue contains multiple corpus types and vintages for some covered languages. For example, Arabic includes regional OSIAN news corpora; German, English, Spanish, French and several other languages have multiple news, newscrawl or Wikipedia corpora. The catalogue reports corpus names, descriptions, sentence/token/type counts and `thanksTo` metadata.

## Per-sentence provenance — useful discovery

The OpenAPI schema defines:

- `SentenceInformation`: `id`, `sentence`, `source`
- `SourceInformation`: `id`, `url`, `date`

The live responses confirm that source objects expose those fields. This is materially better than the previous bulk-archive discovery attempt: it can link a returned excerpt to a source record and, often, an original page URL and date. It does **not** provide title, author or an explicit licence for each underlying article. Those must be recovered from the original page or held if they cannot be established.

The API's random-word endpoint describes its output as randomly selected medium-frequency words. The sentence endpoint returns example sentences for a word, with `offset` and `limit` pagination. This is a query/sample interface, not a documented bulk-corpus export endpoint. A larger sample would require many word and sentence requests and would need to be assessed for frequency bias, duplicate sentences, source concentration and service limits.

## Licence and underlying-text rights

The OpenAPI `info` object declares:

- API licence label: **CC BY 4.0**
- Licence URL: http://creativecommons.org/licenses/by/4.0/
- Terms-of-service URL: https://wortschatz-leipzig.de/usage

Do not interpret the API specification's CC BY 4.0 label as a blanket licence for every sentence or source article. The official Leipzig corpus-statistics portal describes its corpus types as follows:

- News: “Used text material was taken from news websites (typically on a daily basis via RSS feeds).”
- Web: “Used text material was taken from randomly chosen Web sites.”
- Wikipedia: “Used text material was taken from Wikipedia dumps.”

The portal also states that source material is collected from selected publicly available sources and that authors are responsible for the content and opinions. This means a Leipzig sentence can be accompanied by a useful source URL without the underlying publisher having granted redistribution rights. For Wikipedia-derived corpora, the applicable Wikipedia licence and revision attribution need to be established; for news/web-derived corpora, the original publisher's terms and any applicable licence must be checked per source work.

**Current decision: technically viable API lead; rights HOLD; no Leipzig text acquired.** Before any sentence is staged, preserve the returned source ID, URL and date, resolve the original page's title/author/publisher and licence or permission, and apply the project's excerpt-level rights gate. Missing or contradictory source rights mean hold/exclude, not attribution-only release.

## Scholarly citation

The official corpus-statistics portal points users to:

Thomas Eckart and Uwe Quasthoff (2013), “Statistical Corpus and Language Comparison on Comparable Corpora,” in *Building and Using Comparable Corpora*, pp. 151–165, Springer. DOI: https://doi.org/10.1007/978-3-642-20128-8_8.

This is the scholarly citation for the Leipzig corpus collection/statistical comparability work. It is a recommended scholarly citation, not a substitute for legal attribution to source works.

## Earlier bulk-archive attempt

The earlier HTML catalogue scraper remains a separate route. It found 33 pages but zero target archive links and produced 34 errors. That failed archive-discovery run does not invalidate the REST API. Do not describe the Leipzig source as technically unusable on the basis of the HTML scraper failure.

## Next work

1. Review the API's actual usage terms at https://wortschatz-leipzig.de/usage; preserve the exact terms wording and distinguish API terms from underlying corpus-text rights.
2. Build a source-URL inventory from a bounded set of sentence-service responses, without retaining text until the rights route is established.
3. Fetch representative original pages and test whether title, author/publisher, date and licence/terms can be recovered reliably.
4. Only after that assessment, decide whether a bounded, source-attributed Leipzig sample is viable. The REST API currently covers 20 target labels, so it cannot fill the 14 missing labels.
