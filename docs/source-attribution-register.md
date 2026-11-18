# Source attribution and citation register

Status: working release-control register, 18 November 2026. This document separates **legal attribution/notice obligations**, **recommended scholarly citation**, and **record-level source attribution**. A dataset paper citation does not replace a licence-required attribution, and a generic dataset citation does not replace an article/page citation where the source terms require one.

## Attribution model

For every source family, the release manifest must record:
- exact dataset/source name and release;
- upstream publisher/rights holder and stable source URL;
- immutable revision, retrieval date and file/archive SHA-256;
- applicable licence and separate platform/API/contractual terms;
- the exact attribution wording required by the source, if supplied;
- whether attribution is required per record, per document, in a consolidated notice, or in scholarly publications;
- any required source/date/ownership notice and change indication;
- whether the underlying text rights are established, conditional or unresolved.

For any source made from articles, pages, press releases or other individually authored works, retain a private record-level mapping from each selected excerpt to its original document. Where the licence or source terms require attribution to the underlying work, preserve enough metadata to generate that attribution: document title, author/issuing body, publication date, source URL, licence/notice and any stated attribution line. Do not fabricate missing authors or titles. If required attribution cannot be reconstructed, hold or exclude that record.

A consolidated `ATTRIBUTION.md` may satisfy a source's dataset-level notice requirement only where the source terms permit consolidated attribution. It does not automatically satisfy a requirement to identify the individual article or work. The public dataset card should link to the release's attribution file and describe its scope.

## Source-by-source decisions

| Source family | Legal attribution / notice position | Record-level citation and release action |
|---|---|---|
| Common Voice 22.0 / 27.0 | CV22 underlying validated sentence text is identified as CC0; its third-party HF conversion chain and locale-specific distribution terms remain separate checks. CV22 is pinned to immutable revision `ae911de250fe9375d08e2daa2105b671d659d446`. The Romanian Common Voice 27.0 MDC terms acceptance (CC0-1.0; no speaker identification; no re-hosting/re-sharing) applies only to Romanian. Croatian CV27 terms acceptance is not recorded and remains on hold. | For CV22, preserve locale, upstream sentence ID, revision and per-locale TSV SHA-256. For CV27 Croatian, preserve dataset ID and verified archive/TSV hashes; no upstream sentence ID was retained, so group IDs are candidate-record hashes. Cite the exact Common Voice release and third-party conversion in dataset documentation. Never generalize Romanian terms acceptance to other locales. |
| Tatoeba CC0 export | Only `sentences_CC0.csv` is treated as CC0; the general export is CC BY 2.0 FR and is not interchangeable. CC0 does not impose a legal attribution requirement. | Cite Tatoeba and the dated export as scholarly/source acknowledgement. Preserve sentence ID and base/translation relation for leakage control. Current staged text is from the CC0-only export. |
| DGT-TM 2021 | European Commission reuse conditions require attribution, identification of source and date, and retention of Commission ownership. Not CC0. | Preserve translation-unit/document identifiers and source/date metadata. Include the Commission's required notice verbatim in the release attribution file. Do not rely on a paper citation alone. The exact official wording must be copied from the applicable reuse notice before release. |
| JRC-Acquis 3.0 | Official conditions require source attribution and retention of Commission ownership; the corpus includes materials whose rights status differs. It is not a blanket CC0 source. | Keep document-level identifiers and source provenance. Verify component/document rights and official notice wording. Include required Commission ownership and source/date information; hold any component whose terms cannot be determined. |
| Europarl v7 | The project page says its authors are not aware of copyright restrictions; this is not a formal blanket licence grant. | Cite the Europarl v7 corpus and its maintainers in scholarly documentation. Preserve document IDs and source statement. Do not describe it as CC0 or claim that a citation alone clears rights. |
| Målfrid 2026 and Målfrid parallel data | NLOD 2.0 permits reuse with attribution. Database rights are treated separately; the NLOD compatibility section distinguishes ODC-By for database rights. Third-party material and personal data may remain outside the grant. | Preserve document ID, domain, URL, date, title and issuing institution where available. Provide NLOD attribution and database notice as applicable. Keep paragraph-to-document links. Do not assume CC BY 4.0 alone clears the database. |
| Randomized Nynorsk corpus | CC BY 3.0 requires attribution, licence identification/link and indication of changes for adaptations. Corpus is lemmatized/tagged, so it is not a raw-text default. | If used, identify the corpus and its authors/publisher in `ATTRIBUTION.md`; state that text was extracted/segmented/filtered and link CC BY 3.0. Check whether the exact upstream package includes additional citation instructions. |
| IGC2024 Filtered-1 | Source is recorded as CC BY 4.0. The licence requires appropriate credit, licence link and indication of changes; it does not imply all embedded third-party material is cleared. | Preserve original source document metadata and cite the IGC resource/publisher. Generate attribution for underlying source works where supplied or required. Verify the exact IGC terms and bibliographic citation before release. Filtered-2 remains excluded due non-republication terms. |
| GreynirCorpus 21.06 | Source is recorded as CC BY 4.0. Underlying news/government source material may carry separate terms; a corpus-level licence is not proof that every source article was licensed by its publisher. | Preserve article URL, title, publisher/author and date where available. Do not include a news-derived record unless its source-level rights basis is understood; CC BY corpus metadata alone is insufficient. |
| TeMU-BSC Catalan CC0 sentences | CC0-labelled repository/constituents are not assumed to have identical provenance. Constituents may have separate source terms or waivers. | Record constituent dataset name, source/waiver and source document/article identifiers. Use CC0 only for constituents whose own rights status supports it. Do not collapse all TeMU files into one blanket CC0 assertion. |
| BSC Legal Catalan-Spanish corpus | Repository metadata reports CC BY 4.0, but constituent sources differ (e.g. DOGC, APDCAT and legal documents). Some may have government open-data terms or data-sharing agreements. | Preserve per-file and per-document origin. Apply the actual source licence/terms to each constituent. CC BY attribution must identify source, licence and changes; APDCAT material remains conditional on its agreement. |
| Catalan-DPO-V2 | Hugging Face repository metadata reports Apache-2.0, but that does not establish rights in the underlying dialogue/message text or third-party source content. | Do not treat Apache-2.0 metadata as text clearance. Obtain upstream provenance/permission or exclude the affected components. If cleared, cite the dataset card/paper and preserve record-level origins. |
| Korean Wikipedia | CC BY-SA/GFDL obligations apply; share-alike and attribution cannot be replaced by a generic citation. | Preserve page/revision IDs and URLs; generate attribution and licence notices and assess share-alike compatibility before inclusion. Not approved by default. |
| Korean Parallel Bible corpus | Source is recorded as CC BY-SA 3.0. | Preserve translation/version, publisher/translator and source identifiers. Include attribution, licence and change notices; assess share-alike compatibility. Supplementary only. |
| Korea.kr / KOGL government article portal | **Not pursued; no articles were acquired and no records from this route are in the candidate corpus.** | Historical research lead only. No current attribution implementation or release obligation arises from this route. Do not treat Korea.kr/KOGL as an active source. |
| Korean Law Open Data API / Korean legal portal | **Not pursued; no API or portal texts were acquired and no records from this route are in the current candidate corpus.** | Historical exploratory lead only. There is no active attribution obligation or current acquisition work for this route. Do not treat statutory public-domain analysis as source clearance for a corpus that was never acquired. |
| NIKL Written Corpus 2025 | Access is by request; public catalogue does not establish a blanket redistribution licence. | No use until the written approval and actual terms expressly permit text extraction and redistribution. Preserve per-work rights metadata if approved. |
| NSMC | Conflicting licence claims: original repository has no clear licence, HF card says CC BY 2.0, while other metadata/paper says CC0. | Exclude until the rights holder resolves the conflict in writing. A paper citation or HF card cannot cure the conflict. |
| UN Arabic-English Filtered | HF card metadata says CC BY 4.0, but the underlying UN corpus/source terms have not been verified. | Do not infer rights from the HF wrapper. Establish the UN source's reuse terms and required attribution first; preserve UN document/source IDs and dates. |
| Korean Open Historical Corpus | CC BY-NC 4.0. | Exclude from a release intended for unrestricted/commercial reuse. |
| FineWeb / FineWeb2 / HPLT | ODC-By or CC0 packaging terms apply to the compilation/packaging as described by each publisher; they do not automatically license the underlying crawled passages. | Keep on legal hold. A source URL is evidence for investigation, not a rights grant. Do not publish extracted text on the basis of the wrapper licence alone. If any excerpt is independently cleared, preserve original article title/author/publisher/date/licence and the exact passage's provenance. |
| Leipzig Corpora Collection REST API | OpenAPI metadata declares CC BY 4.0 and links https://wortschatz-leipzig.de/usage. This is not treated as a licence for the underlying article/page texts. Leipzig describes corpus content as selected public-source material (news, random web, Wikipedia) and states that authors remain responsible for content. | Sentence responses expose source ID, URL and date, but not title/author/licence. Preserve those fields; retrieve original-page metadata and assess each underlying work's licence/terms before retaining text. Cite Eckart & Quasthoff (2013), “Statistical Corpus and Language Comparison on Comparable Corpora,” pp. 151–165, DOI 10.1007/978-3-642-20128-8_8. Current API probe retained no sentence text; source family remains on rights hold. |\n| OPUS components | OPUS is an aggregator; licences and attribution conditions vary by underlying corpus. | No aggregate-level permission. Assess and cite each component separately, including any paper citation and per-document attribution. |

## What “citation” means in this project

There are three distinct deliverables:

1. **Legal attribution:** the wording and metadata required by the applicable licence or reuse terms. This may include author/issuer, title, source, date, licence link, changes, and ownership statement.
2. **Scholarly citation:** the dataset paper, corpus paper, project page or release that researchers should cite when using the source. This belongs in the dataset card and release bibliography, and is not a substitute for legal attribution.
3. **Record-level provenance:** a mapping from each retained text record to its original document or dataset row. This is required operationally for audit and takedown, and becomes public only to the extent safe and permitted.

Do not reproduce article text merely to satisfy a citation requirement. Quote only where the source's own terms explicitly require a prescribed notice or where a short quotation is independently justified; otherwise provide bibliographic attribution and source links.

## Release gate

Before a source is marked eligible:
- obtain the current official licence/terms and any source-specific citation instructions;
- capture exact required attribution wording rather than paraphrasing it;
- confirm whether attribution is per record, per work, or consolidated;
- retain article/document metadata sufficient to construct the required notice;
- verify that the terms permit redistribution of the selected text and the intended dataset release;
- include all mandatory notices and a complete `ATTRIBUTION.md` in the release;
- test that every released record resolves to a source/attribution entry.

Unknown or contradictory requirements mean **hold**, not “cite the dataset and proceed”.
