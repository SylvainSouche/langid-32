# langid-32 operational configuration

The only numeric policy source is [`config/langid32.toml`](../config/langid32.toml).
Scripts load it through `langid32.settings`; workflows must not duplicate
acquisition, corpus-size, source-balance, split, or JQL policy values.

## Override precedence

1. Exact source/language override in `[source_language_overrides]`, e.g.
   `"leipzig_news.hr" = 15000`.
2. Source-specific default in `[acquisition.source_rules]`.
3. Global first-pass acquisition target.

Final target overrides use `[candidate.language_target_overrides]`; otherwise
all languages inherit the exact final target.

## Acquisition

The first pass streams up to **20,000 eligible unique records per individual
source and language**. Leipzig News and Wikipedia are separate sources. DGT,
Common Voice, FineWeb2, Tatoeba CC0, Gaois and each waiting source follow the
same default unless an explicit override is recorded. This is an acquisition
target, not a family-wide cap and not the final candidate quota. Sources with
fewer eligible records retain all available records and report the shortfall.

DGT's per-TMX-document-language sampling ceiling is separately recorded in its
source rule; it does not replace the per-language source target.

## Candidate and final corpus

- Candidate intake floor: **35,000 candidates per language**. Underfilled
  languages trigger additional acquisition; do not lower the final target.
- Final production target: **exactly 25,000 sentences per language**, with
  explicit per-language overrides only in the TOML table.
- Candidate-stage source balancing: preferred maximum **30%** and hard maximum
  **50%** per source, language and split. These are candidate-stage constraints,
  not acquisition quotas.
- Final source proportions preserve the existing baseline core proportions
  independently within each language.
- Split ratios are train **80%**, validation **10%**, test **10%**.
- There is no second source-family cap after acquisition; the acquisition
  limits already apply to individual sources. Do not reintroduce a family cap.

## JQL

The three JQL-Edu heads are Gemma, Mistral and Llama. Normalize each judge's
scores independently over the full assessment corpus using quantile mapping to
a standard normal distribution. Consensus is:

`mean(z_gemma, z_mistral, z_llama) - 0.5 * population_std(z_gemma, z_mistral, z_llama)`.

JQL is **non-filtering QA/diagnostic annotation**. Every sentence is retained
regardless of score. The historical 25th-percentile global quality floor is
recorded as an inactive diagnostic reference (`apply_quality_floor = false`);
it must not be used to select, exclude, rank, down-rank or replace production
sentences.

## Text and privacy checks

The shared global text bounds are 12–500 characters and 1,500 UTF-8 bytes.
Email, URL and IPv4 matches are excluded. Phone-like and long numeric sequences
are retained with flags rather than automatically removed. Source-specific
parsers may have stricter structural/quality rules; such rules must be added to
this TOML before being used in production.

## Change control

A numeric workflow-policy change requires editing this file and its tests.
A code default or workflow argument must not silently override it. Generated
manifests should record the effective configuration and its hash.
