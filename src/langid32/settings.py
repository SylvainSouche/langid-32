"""Load the authoritative langid-32 TOML policy."""
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "config" / "langid32.toml"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else DEFAULT_CONFIG
    if not config_path.is_absolute():
        config_path = (Path.cwd() / config_path).resolve()
    with config_path.open("rb") as stream:
        config = tomllib.load(stream)
    if config.get("schema_version") != 1:
        raise ValueError(f"Unsupported langid-32 config schema in {config_path}")
    return config


def language_target(config: dict[str, Any], language: str) -> int:
    overrides = config.get("candidate", {}).get("language_target_overrides", {})
    return int(overrides.get(language, config["candidate"]["final_sentences_per_language"]))


def acquisition_target(config: dict[str, Any], source: str, language: str) -> int:
    acquisition = config["acquisition"]
    source_rules = acquisition.get("source_rules", {})
    normalized = source.replace("-", "_")
    rule = source_rules.get(normalized)
    if rule is None:
        matches = [
            (len(rule_name), candidate)
            for rule_name, candidate in source_rules.items()
            if normalized.startswith(rule_name + ":") or normalized.startswith(rule_name + "_")
        ]
        rule = max(matches, key=lambda item: item[0])[1] if matches else {}
    if rule.get("exclude", False):
        raise ValueError(f"{source} is excluded by source policy")
    allowed_languages = rule.get("languages")
    if allowed_languages is not None and language not in allowed_languages:
        raise ValueError(f"{source} is not approved for language {language}")
    overrides = acquisition.get("source_language_overrides", {})
    key = f"{source}.{language}"
    if key in overrides:
        return int(overrides[key])
    return int(rule.get("target", acquisition["first_pass_target_per_source_language"]))
