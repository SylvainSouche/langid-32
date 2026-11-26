#!/usr/bin/env python3
"""Validate the guarded push-to-run command before any acquisition begins."""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    event_name = os.environ.get("GITHUB_EVENT_NAME", "local")
    result = {"event": event_name, "status": "not_applicable"}
    if event_name == "push":
        if os.environ.get("GITHUB_REF") != "refs/heads/main":
            raise SystemExit("Pipeline push trigger is allowed only on main")
        payload_path = Path(os.environ.get("GITHUB_EVENT_PATH", ""))
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        # GitHub push payloads may omit the commits array (notably for some
        # generated/large pushes). Compare the exact before/after commits via
        # the GitHub API instead of treating an empty payload list as a diff.
        before = payload.get("before")
        after = payload.get("after") or os.environ.get("GITHUB_SHA")
        token = os.environ.get("GH_TOKEN", "")
        if not before or not after or not token:
            raise SystemExit("Push event is missing before/after SHA or GH_TOKEN; refusing guarded run")
        import urllib.error
        import urllib.request
        request = urllib.request.Request(
            f"https://api.github.com/repos/{os.environ.get('GITHUB_REPOSITORY', 'SylvainSouche/langid-32')}/compare/{before}...{after}",
            headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}",
                     "X-GitHub-Api-Version": "2022-11-28"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                comparison = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            raise SystemExit(f"Could not verify guarded push commit diff: {exc}") from exc
        if comparison.get("status") not in {"ahead", "identical"}:
            raise SystemExit(f"Unexpected push comparison status: {comparison.get('status')}")
        changed = {item["filename"] for item in comparison.get("files", [])}
        if changed != {"pipeline-trigger.json"}:
            raise SystemExit(
                "A guarded pipeline push must modify pipeline-trigger.json and no other path; "
                f"changed paths were {sorted(changed)}"
            )
        trigger_path = ROOT / "pipeline-trigger.json"
        trigger = json.loads(trigger_path.read_text(encoding="utf-8"))
        if trigger.get("run_mode") != "clean_full_pipeline":
            raise SystemExit("Pipeline trigger file is not armed for a clean full run")
        nonce = str(trigger.get("nonce", ""))
        if not re.fullmatch(r"[A-Za-z0-9._-]{12,80}", nonce):
            raise SystemExit("Pipeline trigger nonce is missing or malformed")
        hashes = {
            "config_sha256": sha256(ROOT / os.environ.get("LANGID32_CONFIG", "config/langid32.toml")),
            "source_register_sha256": sha256(ROOT / "docs/source-register.md"),
            "pipeline_contract_sha256": sha256(ROOT / "docs/pipeline-contract.md"),
        }
        for key, actual in hashes.items():
            if trigger.get(key) != actual:
                raise SystemExit(f"Pipeline trigger {key} does not match the checked-in source of truth")
        if trigger.get("artifact_reuse") is not False:
            raise SystemExit("Clean pipeline runs must not reuse prior failed/partial acquisition artifacts")
        if trigger.get("final_selection") != "deferred":
            raise SystemExit("Final selection must remain deferred (35,000 release / 350 debug target)")
        if trigger.get("privacy_review_required") is not True:
            raise SystemExit("Manual privacy review must remain a required stop")
        result = {
            "event": event_name,
            "status": "passed",
            "nonce": nonce,
            "trigger_commit_sha": os.environ.get("GITHUB_SHA"),
            **hashes,
            "artifact_reuse": False,
            "final_selection": "deferred",
            "privacy_review_required": True,
        }
    output = ROOT / "out" / "pipeline-trigger-validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
