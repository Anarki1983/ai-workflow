#!/usr/bin/env bash
# Invoked by the global SessionStart hook on every Claude Code session.
# Fail-soft by design: no step here may block session start. Idempotent:
# safe to run every session, safe to run manually any time.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
WARNINGS=()

# --- 0. Keep this repo (and this script) fresh before using it ---
# --ff-only is required, not a preference: this runs unattended on every
# collaborator's machine. A plain `git pull` on a checkout that has any local
# commit silently creates a merge commit in a repo whose scripts execute with
# that collaborator's permissions. Refusing to fast-forward and warning is the
# only safe failure here.
if ! git -C "$REPO_DIR" pull --ff-only --quiet >/dev/null 2>&1; then
  WARNINGS+=("ai-workflow git pull could not fast-forward, using local checkout as-is (diverged, dirty, or offline)")
fi

# --- 1. Symlink this repo's own skills/ and agents/ into the global dirs ---
sync_dir() {
  local kind="$1" # "skills" or "agents"
  local src_root="$REPO_DIR/$kind"
  local dst_root="$CLAUDE_DIR/$kind"
  [ -d "$src_root" ] || return 0
  mkdir -p "$dst_root"
  for src in "$src_root"/*/; do
    [ -d "$src" ] || continue
    local name src_abs dst
    name="$(basename "$src")"
    dst="$dst_root/$name"
    src_abs="$(cd "$src" && pwd)"

    if [ -L "$dst" ] && [ "$(readlink -f "$dst" 2>/dev/null)" = "$src_abs" ]; then
      continue # already correct
    fi
    if [ -e "$dst" ] || [ -L "$dst" ]; then
      WARNINGS+=("skipped $kind/$name: $dst already exists and is not ai-workflow's symlink")
      continue
    fi
    ln -s "$src_abs" "$dst" 2>/dev/null || WARNINGS+=("failed to link $kind/$name into $dst_root")
  done
}
sync_dir skills
sync_dir agents

# --- 2. Reconcile pinned third-party plugins ---
MANIFEST="$REPO_DIR/scripts/third-party-plugins.json"
if [ -f "$MANIFEST" ] && command -v claude >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
  while IFS= read -r line; do
    [ -n "$line" ] && WARNINGS+=("$line")
  done < <(python3 "$REPO_DIR/scripts/sync_plugins.py" "$MANIFEST" 2>/dev/null)
fi

# --- 3. Surface warnings as a single session-start message, if any ---
if [ "${#WARNINGS[@]}" -gt 0 ] && command -v python3 >/dev/null 2>&1; then
  JOINED="$(printf '⚠️ %s\n' "${WARNINGS[@]}")"
  python3 -c "import json,sys; print(json.dumps({'systemMessage': sys.argv[1]}))" "$JOINED"
fi

exit 0
