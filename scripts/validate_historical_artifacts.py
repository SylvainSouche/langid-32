#!/usr/bin/env python3
"""Fail-closed preflight for the four explicitly approved historical artifacts."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from langid32.settings import load_config


def github_json(url: str, token: str) -> dict:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "langid-32-historical-preflight",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise SystemExit(f"GitHub historical-artifact preflight failed: {exc}") from exc


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> None:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not repository or not token:
        raise SystemExit("GITHUB_REPOSITORY and GH_TOKEN are required for historical preflight")
    config = load_config(ROOT / "config/langid32.toml")
    now = datetime.now(timezone.utc)
    verified = []
    for name, pin in sorted(config["historical_snapshots"].items()):
        run_id = int(pin["run_id"])
        artifact_id = int(pin["artifact_id"])
        run = github_json(
            f"https://api.github.com/repos/{repository}/actions/runs/{run_id}", token
        )
        if run.get("status") != "completed" or run.get("conclusion") != "success":
            raise SystemExit(
                f"Historical run {run_id} for {name} is not a successful completed run"
            )
        listing = github_json(
            f"https://api.github.com/repos/{repository}/actions/runs/{run_id}/artifacts?per_page=100",
            token,
        )
        matches = [item for item in listing.get("artifacts", []) if int(item.get("id", 0)) == artifact_id]
        if len(matches) != 1:
            raise SystemExit(
                f"Expected exactly artifact ID {artifact_id} in run {run_id}; found {len(matches)}"
            )
        artifact = matches[0]
        if artifact.get("name") != pin["artifact_name"]:
            raise SystemExit(
                f"Artifact name mismatch for {name}: {artifact.get('name')!r}"
            )
        if artifact.get("expired") or int(artifact.get("size_in_bytes", 0)) <= 0:
            raise SystemExit(f"Historical artifact {artifact_id} for {name} is expired or empty")
        expires_at = parse_utc(str(artifact["expires_at"]))
        if expires_at <= now:
            raise SystemExit(f"Historical artifact {artifact_id} for {name} has expired")
        if expires_at.isoformat() != parse_utc(pin["expires_at"]).isoformat():
            raise SystemExit(
                f"Historical artifact expiry changed for {name}: {artifact['expires_at']}"
            )
        verified.append({
            "source": name,
            "run_id": run_id,
            "artifact_id": artifact_id,
            "artifact_name": artifact["name"],
            "size_in_bytes": int(artifact["size_in_bytes"]),
            "expires_at": artifact["expires_at"],
        })
    result = {"historical_artifacts_preflight": "passed", "artifacts": verified}
    output = ROOT / "out" / "historical-artifact-preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
