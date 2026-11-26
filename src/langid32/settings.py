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
    validate_acquisition_policy(config)
    return config


def validate_acquisition_policy(config: dict[str, Any]) -> None:
    """Fail closed on unsafe quota aliasing or acquisition runtime settings."""
    acquisition = config["acquisition"]
    execution = config["execution"]
    if not acquisition.get("filter_before_quota") or not acquisition.get("privacy_filter_before_quota"):
        raise ValueError("Acquisition must apply quality and privacy filters before quota accounting")
    target = int(acquisition["first_pass_target_per_source_language"])
    if target != 20000:
        raise ValueError(f"Expected the approved 20,000 post-filter target, got {target}")
    for source, rule in acquisition.get("source_rules", {}).items():
        if "quota_key" in rule:
            raise ValueError(
                f"Source-family quota alias is forbidden: {source}.quota_key; "
                "each original source keeps its own source-language target"
            )
    snapshots = config.get("historical_snapshots", {})
    expected_snapshots = {"v5", "leipzig", "tatoeba", "dgt"}
    if set(snapshots) != expected_snapshots:
        raise ValueError(
            f"Historical snapshot pins must be exactly {sorted(expected_snapshots)}"
        )
    for name, snapshot in snapshots.items():
        required = ("run_id", "artifact_id", "artifact_name", "expires_at", "filename")
        missing = [key for key in required if not snapshot.get(key)]
        if missing:
            raise ValueError(f"historical_snapshots.{name} missing {missing}")
        if int(snapshot["run_id"]) <= 0 or int(snapshot["artifact_id"]) <= 0:
            raise ValueError(f"historical_snapshots.{name} has an invalid run/artifact ID")
        if Path(str(snapshot["filename"])).name != str(snapshot["filename"]):
            raise ValueError(f"historical_snapshots.{name}.filename must be a basename")
    positive = (
        "acquisition_files_per_batch",
        "acquisition_max_parallel_source_tasks",
        "acquisition_job_timeout_minutes",
        "acquisition_global_budget_minutes",
        "acquisition_safety_margin_minutes",
        "acquisition_retry_attempts",
        "acquisition_checkpoint_every_files",
    )
    for key in positive:
        if int(execution[key]) <= 0:
            raise ValueError(f"execution.{key} must be positive")
    budget = int(execution["acquisition_global_budget_minutes"])
    margin = int(execution["acquisition_safety_margin_minutes"])
    timeout = int(execution["acquisition_job_timeout_minutes"])
    if budget + margin > 360:
        raise ValueError("Acquisition budget plus safety margin exceeds the six-hour limit")
    if timeout > budget or timeout + margin > 360:
        raise ValueError("Per-job timeout conflicts with the acquisition budget/six-hour limit")


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
    if not rule and acquisition.get("reject_unregistered_sources", False):
        raise ValueError(f"{source} is not registered in source policy")
    if rule.get("exclude", False):
        raise ValueError(f"{source} is excluded by source policy")
    allowed_languages = rule.get("languages")
    if allowed_languages is not None and language not in allowed_languages:
        raise ValueError(f"{source} is not approved for language {language}")
    overrides = acquisition.get("source_language_overrides", {})
    quota_key = str(rule.get("quota_key", source))
    for key in (f"{source}.{language}", f"{quota_key}.{language}", f"{normalized.split(chr(58), 1)[0]}.{language}"):
        if key in overrides:
            return int(overrides[key])
    return int(rule.get("target", acquisition["first_pass_target_per_source_language"]))


def source_quota_key(config: dict[str, Any], source: str) -> str:
    """Return an explicit source identity for acquisition quota accounting.

    Components share a quota only when their registered source rule declares
    quota_key. Otherwise each original source identifier keeps its own quota.
    """
    source_rules = config["acquisition"].get("source_rules", {})
    normalized = source.replace("-", "_")
    rule = source_rules.get(normalized)
    if rule is None:
        matches = [
            (len(rule_name), candidate)
            for rule_name, candidate in source_rules.items()
            if normalized.startswith(rule_name + ":") or normalized.startswith(rule_name + "_")
        ]
        rule = max(matches, key=lambda item: item[0])[1] if matches else {}
    return str(rule.get("quota_key", source))
