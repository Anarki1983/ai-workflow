#!/usr/bin/env python3
"""Reconcile installed third-party Claude Code plugins against scripts/third-party-plugins.json.

Fail-soft by design: any unexpected error becomes a warning line on stdout,
never a non-zero exit that could block the SessionStart hook. Prints one
plain-text warning per line for scripts/sync.sh to collect; prints nothing
when everything already matches.

Version tracking is advisory and semver-only. `claude plugin install` has no
flag to request a specific version, so a missing plugin is always installed at
whatever the marketplace currently serves; the manifest records what the team
agreed on, and drift from it is reported, never forced. A plugin whose entry
omits "version" is deliberately untracked: some marketplace plugins are
versioned by the marketplace repo's own commit sha, which changes on every
upstream commit, so comparing it would warn forever and teach everyone to
ignore the warnings.
"""
import json
import re
import subprocess
import sys

# Matches a semver-shaped version string; anything else (a commit sha, a date,
# a branch name) is not a version this script knows how to compare.
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def warn(msg: str) -> None:
    print(msg)


def main() -> int:
    if len(sys.argv) != 2:
        warn("sync_plugins.py: missing manifest path argument")
        return 0

    manifest_path = sys.argv[1]
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except Exception as e:
        warn(f"third-party plugin manifest unreadable ({manifest_path}): {e}")
        return 0

    # Ensure each declared marketplace is registered. Idempotent: adding an
    # already-known marketplace is expected to no-op or error harmlessly.
    for mp in manifest.get("marketplaces", []):
        source = mp.get("source", {})
        repo = source.get("repo")
        if not repo:
            continue
        try:
            subprocess.run(
                ["claude", "plugin", "marketplace", "add", repo],
                capture_output=True, text=True, timeout=15,
            )
        except Exception as e:
            warn(f"could not add marketplace {repo}: {e}")

    try:
        result = subprocess.run(
            ["claude", "plugin", "list", "--json"],
            capture_output=True, text=True, timeout=15,
        )
        installed_raw = result.stdout.strip()
        installed = json.loads(installed_raw) if installed_raw else []
    except Exception as e:
        warn(f"could not read installed plugin list: {e}")
        installed = []

    if isinstance(installed, dict):
        installed = installed.get("plugins", [])

    # `claude plugin list --json` reports each plugin as {"id": "<name>@<marketplace>", "version": ...}
    installed_by_key = {}
    for entry in installed if isinstance(installed, list) else []:
        key = entry.get("id")
        version = entry.get("version")
        if key:
            installed_by_key[key] = version

    for p in manifest.get("plugins", []):
        name = p.get("name")
        marketplace = p.get("marketplace")
        pinned_version = p.get("version")
        if not name or not marketplace:
            continue
        key = f"{name}@{marketplace}"
        have = installed_by_key.get(key)

        if have is None:
            try:
                install = subprocess.run(
                    ["claude", "plugin", "install", key, "-y"],
                    capture_output=True, text=True, timeout=60,
                )
                if install.returncode != 0:
                    warn(f"failed to auto-install {key}: {install.stderr.strip()[:200]}")
            except Exception as e:
                warn(f"failed to auto-install {key}: {e}")
            continue

        if pinned_version is None:
            continue  # deliberately untracked: follows whatever the marketplace serves

        if not SEMVER_RE.match(str(pinned_version)):
            warn(
                f"third-party plugin pin for {key} is not a comparable version "
                f"({pinned_version!r}); drop the \"version\" field to track it as "
                f"marketplace-versioned, or set a semver value"
            )
            continue

        if have != pinned_version:
            warn(
                f"third-party plugin version mismatch for {key}: "
                f"local={have} pinned={pinned_version} "
                f"(run `claude plugin update {name}` to move to latest, "
                f"or ask the team to bump the pin in scripts/third-party-plugins.json)"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
