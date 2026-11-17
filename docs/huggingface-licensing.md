# Hugging Face dataset release — licensing and publication gate

## Current decision: do not publish the candidate rows yet

The GitHub repository's root `LICENSE` is MIT and covers the project's software and accompanying documentation. It does **not** license third-party Common Voice text. Do not copy that MIT licence into the Hugging Face dataset repository.

The staged records currently carry `licence_id: CC0-1.0`, but that field is inherited from source metadata/conversion and is not, by itself, sufficient proof that this project may redistribute the combined text.

### Source-by-source status

| Component | Staged rows | Evidence | Publication status |
|---|---:|---|---|
| Common Voice 22.0, third-party HF conversion `fsicoli/common_voice_22_0` | 259,352 | Conversion dataset card labels it CC0; downloaded from a mutable `main` revision. Some locale files have no resolved commit/ETag in the captured manifest. | **Hold** pending conversion provenance, upstream release, per-locale rights and redistribution review. |
| Common Voice Scripted Speech 27.0, Croatian (`hr`) | 1,724 | Existing authorised MDC acquisition; source archive checksum verified; validated TSV hash retained. | **Hold** pending retrieval of the Croatian-specific accepted terms and confirmation that the accepted terms permit redistribution of the curated text. |

The Croatian-specific terms acceptance is not present in the audit record currently available to the release process. Do not infer it from acceptance for another locale or another Common Voice release.

### Required before a public data upload

1. Verify the exact upstream Common Voice release and licence/terms for every locale in the HF conversion.
2. Resolve and pin immutable revisions for every downloaded HF locale, especially Catalan where the previous manifest recorded no resolved commit or ETag.
3. Retrieve and record the exact accepted Mozilla Data Collective terms for Croatian v27. Record any no-rehosting/no-resharing conditions.
4. Decide whether the combined dataset can be redistributed, and under which explicit licence. If source conditions differ, preserve source-specific terms and do not invent a single permissive licence.
5. Review the actual text sample for residual personal data, quotations, copyrighted passages, language-label errors, and quality issues. Automated pattern filters are not legal clearance.
6. Approve a versioned release and record the review decision, date, responsible person, and immutable source manifest.

### Metadata rule

Until the above review is complete, the Hugging Face dataset card must not contain `license: mit` or `license: cc0-1.0`. The MIT licence in the software repository is not the data licence. A future dataset card should state the exact approved licence and attribution/notice obligations.

### Publication exclusions

Never upload:
- audio or speaker/contributor identifiers;
- raw Common Voice TSVs;
- raw download manifests containing signed CDN URLs or temporary credentials;
- internal group IDs or private audit sidecars;
- any source component whose accepted terms prohibit re-hosting or redistribution.

The package builder therefore emits only a candidate Parquet file and a sanitised, non-sensitive source summary. It does not make the candidate legally publishable.
