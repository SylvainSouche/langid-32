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
    overrides = config.get("source_language_overrides", {})
    key = f"{source}.{language}"
    if key in overrides:
        return int(overrides[key])
    source_rules = config["acquisition"].get("source_rules", {})
    normalized = source.replace("-", "_")
    rule = source_rules.get(normalized, {})
    return int(rule.get("target", config["acquisition"]["first_pass_target_per_source_language"]))
