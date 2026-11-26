# Source exclusion registry

`data/source-exclusions.jsonl` is the versioned, machine-readable input to the corpus exclusion filter. It currently contains three active source-dataset exclusions: the two mislabelled Catalan DPO components and the legacy generic Greynir source identity. The Greynir rule matches only the exact original source `greynir`; it does not match the separately approved `greynir_copper` or `greynir_silver` identities. Add one JSON object per line when a documented notice, provider restriction, privacy request or legal review requires exclusion.

Fields:
- `scope`: `document`, `url`, `domain`, `archive-batch`, or `source-dataset`.
- `reason_code`: a stable, non-identifying reason code. Current active values include `mixed_language_mislabelled` and `quality_hold_nonrepresentative_gold_dev_sample`; other examples include `rights_notice`, `privacy_notice`, `provider_restriction`, `legal_review`, `source_unknown` and `archive_takedown`.
- `effective_at`: ISO-8601 timestamp/date.
- `status`: `active` (default) or `superseded`.
- `case_id`: internal case reference; never claimant identity.
- Scope-specific key: `source_key`, `url_sha256` or `source_url`, `domain`, `archive_batch`, or `source` and optional `source_release`.

Example (inactive placeholder; do not activate without a documented case):
```json
{"scope":"url","source_url":"https://example.org/page","reason_code":"rights_notice","case_id":"CASE-0001","effective_at":"2026-11-18T00:00:00Z","status":"superseded"}
```

The build cascades a match to all records sharing the matched document group or split group. URL and domain matching read `source_url`, `url`, or `canonical_url` from either the staged row's `provenance` object or its top level. URL rules match the exact recorded URL or its SHA-256 digest; they do not perform URL canonicalization. Domain rules include subdomains. Missing provenance cannot be treated as a successful match and must be handled as a separate release-quality failure.
