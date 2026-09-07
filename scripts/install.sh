#!/usr/bin/env bash
# One-time bootstrap for a new collaborator. Safe to re-run (idempotent).
#
# What it does:
#   1. Backs up ~/.claude/settings.json, then merges in a SessionStart hook
#      that calls scripts/sync.sh on every future session (replaces any
#      previous ai-workflow hook entry instead of duplicating it).
#   2. Adds one `@<this-repo>/CLAUDE.md` import line to ~/.claude/CLAUDE.md
#      if it isn't already there. Never touches any other line in that file.
#   3. Runs scripts/sync.sh once immediately, so skills/agents/plugins are
#      in place without waiting for the next session.
set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SETTINGS="$CLAUDE_DIR/settings.json"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"

mkdir -p "$CLAUDE_DIR"

echo "Installing ai-workflow sync for this machine..."

# --- 1. Merge the SessionStart hook into settings.json ---
if [ -f "$SETTINGS" ]; then
  cp "$SETTINGS" "$SETTINGS.ai-workflow-backup"
  echo "Backed up existing settings.json to settings.json.ai-workflow-backup"
fi

python3 - "$SETTINGS" "$REPO_DIR" <<'PYEOF'
import json
import os
import sys

settings_path, repo_dir = sys.argv[1], sys.argv[2]

try:
    with open(settings_path) as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}
except json.JSONDecodeError as e:
    print(f"ERROR: {settings_path} is not valid JSON ({e}); not touching it.", file=sys.stderr)
    sys.exit(1)

command = f"bash {repo_dir}/scripts/sync.sh"

hooks = settings.setdefault("hooks", {})
session_start = hooks.setdefault("SessionStart", [])

replaced = False
for group in session_start:
    for hook in group.get("hooks", []):
        if hook.get("type") == "command" and "ai-workflow" in hook.get("command", ""):
            hook["command"] = command
            hook["timeout"] = 20
            hook["statusMessage"] = "同步 ai-workflow..."
            replaced = True

if not replaced:
    session_start.append({
        "hooks": [{
            "type": "command",
            "command": command,
            "timeout": 20,
            "statusMessage": "同步 ai-workflow...",
        }]
    })

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

print("settings.json SessionStart hook set to call scripts/sync.sh")
PYEOF
STATUS=$?
if [ "$STATUS" -ne 0 ]; then
  echo "Aborted: could not update settings.json safely. Your file was not modified beyond the backup above."
  exit 1
fi

# --- 2. Add the CLAUDE.md import line (idempotent, one line only) ---
IMPORT_LINE="@$REPO_DIR/CLAUDE.md"
if [ -f "$CLAUDE_MD" ] && grep -qxF "$IMPORT_LINE" "$CLAUDE_MD"; then
  echo "CLAUDE.md already imports this repo's conventions, leaving it as-is"
else
  {
    echo ""
    echo "$IMPORT_LINE"
  } >> "$CLAUDE_MD"
  echo "Added '$IMPORT_LINE' to $CLAUDE_MD"
fi

# --- 3. Run the sync once now ---
echo "Running initial sync..."
bash "$REPO_DIR/scripts/sync.sh"
echo "Done. New skills/agents added to this repo will sync automatically on every future session."
